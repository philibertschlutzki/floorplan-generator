#!/bin/bash

# Alpine Sennhütte Generator - Shell Script
# Headless-optimierte Version mit robuster Fehlerbehandlung
# Behebt Speicherzugriffsfehler durch korrekte QCAD-Parameter

CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette.dxf}"

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌]${NC} $1"
}

# Eingabe-Validierung
if [ -z "$CONFIG_FILE" ]; then
    log_error "Keine JSON-Konfigurationsdatei angegeben."
    echo "Verwendung: $0 <config.json> [ausgabe.dxf]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    log_error "JSON-Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
    exit 1
fi

# Konfigurationsdatei validieren
if ! command -v jq >/dev/null 2>&1; then
    log_warning "jq nicht installiert - JSON-Validierung übersprungen"
else
    if ! jq empty "$CONFIG_FILE" >/dev/null 2>&1; then
        log_error "Ungültige JSON-Datei: $CONFIG_FILE"
        exit 1
    fi
    log_success "JSON-Konfiguration validiert"
fi

# Output-Verzeichnis erstellen falls nötig
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    log_info "Erstelle Output-Verzeichnis: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR" || {
        log_error "Konnte Output-Verzeichnis nicht erstellen: $OUTPUT_DIR"
        exit 1
    }
fi

# QCAD-Installation prüfen
if ! command -v qcad >/dev/null 2>&1; then
    log_error "QCAD ist nicht installiert oder nicht im PATH"
    log_info "Installation mit: sudo apt install qcad"
    exit 1
fi

# QCAD-Version ermitteln
QCAD_VERSION=$(qcad --version 2>/dev/null | head -n1 || echo "unbekannt")
log_info "QCAD Version: $QCAD_VERSION"

# Script-Datei prüfen
SCRIPT_PATH="scripts/alpine_sennhuette_generator_fixed.js"
if [ ! -f "$SCRIPT_PATH" ]; then
    log_error "JavaScript-Generator nicht gefunden: $SCRIPT_PATH"
    exit 1
fi

# Debug-Informationen
echo ""
log_info "=== Alpine Sennhütte Generator (Headless) ==="
log_info "Konfiguration: $CONFIG_FILE"
log_info "Ausgabe: $OUTPUT_FILE"
log_info "QCAD Script: $SCRIPT_PATH"
log_info "Arbeitsverzeichnis: $(pwd)"
echo ""

# System-Umgebung prüfen
if [ -n "$DISPLAY" ]; then
    log_warning "X11 Display erkannt: $DISPLAY"
    log_info "Versuche dennoch Headless-Modus..."
else
    log_info "Headless-Umgebung erkannt (kein DISPLAY)"
fi

# Alte Ausgabedatei löschen falls vorhanden
if [ -f "$OUTPUT_FILE" ]; then
    log_info "Lösche vorherige Ausgabedatei: $OUTPUT_FILE"
    rm "$OUTPUT_FILE"
fi

# QCAD Headless-Strategien definieren
declare -a QCAD_STRATEGIES=(
    # Strategie 1: Vollständig headless mit offscreen platform
    "qcad -platform offscreen -style plastique -autostart"
    # Strategie 2: Minimal headless ohne style
    "qcad -platform offscreen -autostart"
    # Strategie 3: Mit explizitem minimal platform
    "qcad -platform minimal -autostart"
    # Strategie 4: Xvfb virtueller X-Server (falls installiert)
    "xvfb-run -a qcad -autostart"
    # Strategie 5: Standard mit QT-Optimierungen
    "QT_QPA_PLATFORM=offscreen QT_AUTO_SCREEN_SCALE_FACTOR=0 qcad -autostart"
)

# Xvfb-Verfügbarkeit prüfen
if ! command -v xvfb-run >/dev/null 2>&1; then
    log_warning "xvfb-run nicht verfügbar - einige Strategien werden übersprungen"
    # Entferne Xvfb-Strategie aus Array
    unset QCAD_STRATEGIES[3]
fi

# QCAD mit verschiedenen Strategien versuchen
SUCCESS=false
STRATEGY_NUM=0

for strategy in "${QCAD_STRATEGIES[@]}"; do
    if [ -z "$strategy" ]; then
        continue
    fi
    
    STRATEGY_NUM=$((STRATEGY_NUM + 1))
    log_info "=== Strategie $STRATEGY_NUM: $strategy ==="
    
    # Command mit Argumenten zusammenbauen
    FULL_COMMAND="$strategy $SCRIPT_PATH --config='$CONFIG_FILE' --output='$OUTPUT_FILE'"
    
    log_info "Führe aus: $FULL_COMMAND"
    
    # Timeout für QCAD-Ausführung (60 Sekunden)
    timeout 60s bash -c "$FULL_COMMAND" 2>&1
    EXIT_CODE=$?
    
    log_info "Exit-Code: $EXIT_CODE"
    
    # Erfolg prüfen
    if [ $EXIT_CODE -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
        
        if [ "$FILE_SIZE" -gt 100 ]; then  # Mindestens 100 Bytes für gültige DXF
            log_success "Strategie $STRATEGY_NUM erfolgreich! Datei: $OUTPUT_FILE ($FILE_SIZE Bytes)"
            SUCCESS=true
            break
        else
            log_warning "Strategie $STRATEGY_NUM: Ausgabedatei zu klein ($FILE_SIZE Bytes)"
            rm -f "$OUTPUT_FILE"  # Leere Datei löschen
        fi
    elif [ $EXIT_CODE -eq 124 ]; then
        log_warning "Strategie $STRATEGY_NUM: Timeout nach 60 Sekunden erreicht"
    elif [ $EXIT_CODE -eq 139 ]; then
        log_warning "Strategie $STRATEGY_NUM: Speicherzugriffsfehler (Segmentation Fault)"
    else
        log_warning "Strategie $STRATEGY_NUM fehlgeschlagen (Exit-Code: $EXIT_CODE)"
    fi
    
    echo ""
done

# Endgültiges Ergebnis
echo ""
log_info "=== ENDERGEBNIS ==="

if [ "$SUCCESS" = true ]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
    log_success "✅ Alpine Sennhütte erfolgreich generiert!"
    log_success "📁 Ausgabedatei: $OUTPUT_FILE ($FILE_SIZE Bytes)"
    
    # Zusätzliche Datei-Informationen
    if command -v file >/dev/null 2>&1; then
        FILE_TYPE=$(file "$OUTPUT_FILE" 2>/dev/null || echo "unbekannt")
        log_info "🔍 Dateityp: $FILE_TYPE"
    fi
    
    # Kurze Vorschau der DXF (erste paar Zeilen)
    if [ -r "$OUTPUT_FILE" ]; then
        log_info "🔍 DXF-Vorschau (erste 3 Zeilen):"
        head -n 3 "$OUTPUT_FILE" 2>/dev/null | sed 's/^/    /'
    fi
    
    exit 0
else
    log_error "❌ Alle QCAD-Strategien fehlgeschlagen!"
    echo ""
    log_error "Mögliche Lösungsansätze:"
    echo "  1. QCAD-Installation prüfen: sudo apt install qcad"
    echo "  2. Xvfb installieren: sudo apt install xvfb"
    echo "  3. Schreibberechtigung prüfen für: $OUTPUT_DIR"
    echo "  4. QCAD manuell testen: qcad --version"
    echo "  5. Script-Pfad prüfen: $SCRIPT_PATH"
    echo ""
    log_error "Debug-Informationen:"
    echo "  - Arbeitsverzeichnis: $(pwd)"
    echo "  - Konfigurationsdatei: $CONFIG_FILE ($(stat -f%z "$CONFIG_FILE" 2>/dev/null || stat -c%s "$CONFIG_FILE" 2>/dev/null || echo "0") Bytes)"
    echo "  - Output-Verzeichnis: $OUTPUT_DIR ($(ls -ld "$OUTPUT_DIR" 2>/dev/null || echo "nicht verfügbar"))"
    echo "  - DISPLAY: ${DISPLAY:-"(nicht gesetzt)"}"
    echo "  - USER: ${USER:-"unbekannt"}"
    echo "  - PATH: $PATH"
    
    exit 1
fi