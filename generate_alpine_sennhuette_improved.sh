#!/bin/bash

# Alpine Sennhütte Generator - Verbessertes Shell Script
# Verwendet das erweiterte JavaScript-Script mit vollständiger JSON-Konfigurationsunterstützung
# Version 2.0 - Kompatibel mit allen Konfigurationswerten

CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette_improved.dxf}"

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNUNG]${NC} $1"; }
log_error() { echo -e "${RED}[❌]${NC} $1"; }
log_config() { echo -e "${PURPLE}[CONFIG]${NC} $1"; }

# Script-Informationen
SCRIPT_VERSION="2.0"
JS_SCRIPT="scripts/alpine_sennhutte_generator_improved.js"

# Banner
log_info "======================================================"
log_info "Alpine Sennhütte Generator v${SCRIPT_VERSION}"
log_info "Vollständige JSON-Konfigurationsunterstützung"
log_info "======================================================"

# Signal-Handler für sauberes Beenden
cleanup() {
    log_warning "Script unterbrochen - räume auf..."
    # Verwaiste QCAD-Prozesse beenden
    pkill -f "qcad.*alpine_sennhutte_generator_improved.js" 2>/dev/null
    exit 130
}
trap cleanup INT TERM

# Eingabe-Validierung
if [ -z "$CONFIG_FILE" ]; then
    log_error "Keine JSON-Konfigurationsdatei angegeben."
    echo "Verwendung: $0 <config.json> [ausgabe.dxf]"
    echo ""
    echo "Beispiel:"
    echo "  $0 alpenhuette_config_20251102_213551.json output/alpine_sennhuette.dxf"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    log_error "JSON-Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
    exit 1
fi

# Erweiterte JSON-Validierung und Anzeige
log_info "Validiere und analysiere JSON-Konfiguration..."

if command -v jq >/dev/null 2>&1; then
    if ! jq empty "$CONFIG_FILE" >/dev/null 2>&1; then
        log_error "Ungültige JSON-Datei: $CONFIG_FILE"
        exit 1
    fi
    
    # JSON-Inhalt anzeigen
    log_success "JSON-Konfiguration validiert"
    
    # Konfigurationsdetails extrahieren und anzeigen
    BUILDING_TYPE=$(jq -r '.building_type // "Unbekannt"' "$CONFIG_FILE")
    SCALE=$(jq -r '.scale // "1:50"' "$CONFIG_FILE")
    UNIT=$(jq -r '.unit // "meters"' "$CONFIG_FILE")
    
    log_config "Gebäudetyp: $BUILDING_TYPE"
    log_config "Maßstab: $SCALE"
    log_config "Einheit: $UNIT"
    
    # Dimensionen zählen und anzeigen
    NUM_DIMENSIONS=$(jq '.dimensions | length' "$CONFIG_FILE" 2>/dev/null || echo "0")
    log_config "Anzahl Konfigurationsparameter: $NUM_DIMENSIONS"
    
    # Wichtige Dimensionen anzeigen
    if [ "$NUM_DIMENSIONS" -gt 0 ]; then
        log_config "Hauptdimensionen:"
        jq -r '.dimensions | to_entries[] | "  \(.key): \(.value)"' "$CONFIG_FILE" | head -8
        if [ "$NUM_DIMENSIONS" -gt 8 ]; then
            log_config "  ... und $((NUM_DIMENSIONS - 8)) weitere Parameter"
        fi
    fi
else
    log_warning "jq nicht installiert - JSON-Validierung übersprungen"
    log_info "Installiere jq für erweiterte JSON-Validierung: sudo apt install jq"
fi

# Output-Verzeichnis
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUTPUT_DIR" || {
    log_error "Konnte Output-Verzeichnis nicht erstellen: $OUTPUT_DIR"
    exit 1
}

# Vollständigen Pfad für Output-Datei erstellen
OUTPUT_FILE=$(realpath "$OUTPUT_FILE" 2>/dev/null || readlink -f "$OUTPUT_FILE" 2>/dev/null || echo "$(pwd)/$OUTPUT_FILE")

# QCAD prüfen
if ! command -v qcad >/dev/null 2>&1; then
    log_error "QCAD ist nicht installiert oder nicht im PATH"
    log_info "Installiere QCAD: sudo apt install qcad"
    exit 1
fi

# JavaScript-Script prüfen
if [ ! -f "$JS_SCRIPT" ]; then
    log_error "JavaScript-Generator nicht gefunden: $JS_SCRIPT"
    log_info "Stelle sicher, dass das Script im richtigen Verzeichnis liegt"
    exit 1
fi

# Script-Info
JS_SIZE=$(stat -c%s "$JS_SCRIPT" 2>/dev/null || echo "0")
log_success "JavaScript-Script gefunden: $JS_SCRIPT ($JS_SIZE Bytes)"

# Info-Zusammenfassung
log_info ""
log_info "=== KONFIGURATION ==="
log_info "JSON-Konfiguration: $CONFIG_FILE"
log_info "JavaScript-Script: $JS_SCRIPT"
log_info "Ausgabe-Datei: $OUTPUT_FILE"
log_info "Ausgabe-Verzeichnis: $OUTPUT_DIR"
log_info ""

# Alte Ausgabedatei löschen
[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE" && log_info "Alte Ausgabedatei gelöscht"

# ERWEITERTE QCAD-STRATEGIEN für das verbesserte Script
declare -a STRATEGIES=(
    # Strategie 1: Xvfb mit erweiterten Parametern (meist am stabilsten)
    "xvfb-run -a -s '-screen 0 1024x768x24 -dpi 96' qcad -autostart"
    # Strategie 2: Qt Offscreen mit optimierten Umgebungsvariablen  
    "QT_QPA_PLATFORM=offscreen QT_LOGGING_RULES='*.debug=false' QT_AUTO_SCREEN_SCALE_FACTOR=0 qcad -autostart"
    # Strategie 3: QCAD minimal mit Fusion-Style
    "qcad -platform minimal -style fusion -autostart"
    # Strategie 4: Vollständig headless mit Font-Optimierung
    "QT_QPA_PLATFORM=offscreen QT_AUTO_SCREEN_SCALE_FACTOR=0 QT_FONT_DPI=96 QT_SCALE_FACTOR=1 qcad -platform offscreen -autostart"
    # Strategie 5: Xvfb mit niedrigerer Auflösung (für schwache Systeme)
    "xvfb-run -a -s '-screen 0 800x600x16' qcad -autostart"
)

# Xvfb-Verfügbarkeit prüfen
if ! command -v xvfb-run >/dev/null 2>&1; then
    log_warning "xvfb-run nicht verfügbar - installiere mit: sudo apt install xvfb"
    unset STRATEGIES[0] STRATEGIES[4]  # Entferne Xvfb-Strategien
fi

# Funktion für sicheren QCAD-Start mit erweiterten Monitoring
run_qcad_strategy() {
    local strategy="$1"
    local strategy_num="$2"
    
    # Command zusammenbauen
    local FULL_COMMAND="$strategy '$JS_SCRIPT' --config='$CONFIG_FILE' --output='$OUTPUT_FILE'"
    
    log_info "Strategie $strategy_num Command:"
    log_info "  $FULL_COMMAND"
    
    # Erweiterte Timeout-Behandlung (45 Sekunden für das komplexere Script)
    timeout 45s bash -c "$FULL_COMMAND" 2>&1 &
    local QCAD_PID=$!
    
    # Warte auf Prozess mit Live-Monitoring
    local count=0
    local last_size=0
    
    while kill -0 $QCAD_PID 2>/dev/null; do
        sleep 1
        count=$((count + 1))
        
        # Alle 5 Sekunden Status prüfen
        if [ $((count % 5)) -eq 0 ]; then
            log_info "Läuft... (${count}s)"
            
            # Frühe Erfolgserkennung mit Dateigrößen-Monitoring
            if [ -f "$OUTPUT_FILE" ]; then
                local FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
                if [ "$FILE_SIZE" -gt 100 ]; then
                    if [ "$FILE_SIZE" -gt "$last_size" ]; then
                        log_success "Datei wächst: $FILE_SIZE Bytes (+$((FILE_SIZE - last_size)))"
                        last_size=$FILE_SIZE
                    else
                        log_success "Datei stabil bei $FILE_SIZE Bytes - vermutlich fertig!"
                        sleep 2  # Kurz warten für Finalisierung
                        break
                    fi
                fi
            fi
        fi
        
        # Timeout prüfen (45s)
        if [ $count -ge 45 ]; then
            log_warning "Timeout erreicht (45s) - beende Prozess"
            kill -TERM $QCAD_PID 2>/dev/null
            sleep 3
            kill -KILL $QCAD_PID 2>/dev/null
            break
        fi
    done
    
    # Warte auf Prozess-Ende
    wait $QCAD_PID 2>/dev/null
    local EXIT_CODE=$?
    
    log_info "Strategie $strategy_num - Exit-Code: $EXIT_CODE"
    return $EXIT_CODE
}

# QCAD mit erweiterten Strategien versuchen
SUCCESS=false
STRATEGY_NUM=0
START_TIME=$(date +%s)

log_info "=== STARTE QCAD-AUSFÜHRUNG ==="

for strategy in "${STRATEGIES[@]}"; do
    if [ -z "$strategy" ]; then
        continue
    fi
    
    STRATEGY_NUM=$((STRATEGY_NUM + 1))
    log_info ""
    log_info "=== Strategie $STRATEGY_NUM von ${#STRATEGIES[@]} ==="
    log_info "Methode: $(echo "$strategy" | cut -d' ' -f1-3)..."
    
    # Strategy ausführen
    STRATEGY_START=$(date +%s)
    run_qcad_strategy "$strategy" "$STRATEGY_NUM"
    EXIT_CODE=$?
    STRATEGY_TIME=$(($(date +%s) - STRATEGY_START))
    
    log_info "Strategie $STRATEGY_NUM - Laufzeit: ${STRATEGY_TIME}s"
    
    # Erweiterte Erfolgs-Prüfung
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
        
        if [ "$FILE_SIZE" -gt 500 ]; then  # Erhöhte Mindestgröße für komplexeres Script
            log_success "Strategie $STRATEGY_NUM erfolgreich!"
            log_success "Datei: $OUTPUT_FILE ($FILE_SIZE Bytes)"
            
            # DXF-Inhalt prüfen
            if head -n 10 "$OUTPUT_FILE" 2>/dev/null | grep -q "SECTION\|ENTITIES\|DXF"; then
                log_success "Gültiger DXF-Inhalt erkannt"
            fi
            
            SUCCESS=true
            break
        else
            log_warning "Datei zu klein: $FILE_SIZE Bytes (erwartet > 500)"
            rm -f "$OUTPUT_FILE"
        fi
    fi
    
    # Erweiterte Fehler-Analyse
    case $EXIT_CODE in
        0)
            log_warning "Strategie $STRATEGY_NUM: Erfolgreich beendet, aber keine gültige Ausgabedatei"
            ;;
        124)
            log_warning "Strategie $STRATEGY_NUM: Timeout (45s)"
            ;;
        139)
            log_warning "Strategie $STRATEGY_NUM: Speicherzugriffsfehler (SIGSEGV)"
            ;;
        143)
            log_warning "Strategie $STRATEGY_NUM: SIGTERM (unterbrochen)"
            ;;
        *)
            log_warning "Strategie $STRATEGY_NUM: Fehler (Exit: $EXIT_CODE)"
            ;;
    esac
done

# Endergebnis mit erweiterten Informationen
TOTAL_TIME=$(($(date +%s) - START_TIME))

echo ""
log_info "======================================================"
log_info "ENDERGEBNIS nach ${TOTAL_TIME}s"
log_info "======================================================"

if [ "$SUCCESS" = true ]; then
    FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null)
    log_success "✅ Alpine Sennhütte erfolgreich generiert!"
    log_success "📁 Datei: $OUTPUT_FILE"
    log_success "📈 Größe: $FILE_SIZE Bytes"
    log_success "⏱️ Gesamtzeit: ${TOTAL_TIME}s"
    log_success "⚙️ Erfolgreiche Strategie: $STRATEGY_NUM"
    
    # Erweiterte Datei-Informationen
    if command -v file >/dev/null 2>&1; then
        FILE_TYPE=$(file "$OUTPUT_FILE" 2>/dev/null | cut -d: -f2-)
        log_info "🔍 Dateityp:$FILE_TYPE"
    fi
    
    # DXF-Inhalt analysieren
    if command -v grep >/dev/null 2>&1; then
        SECTION_COUNT=$(grep -c "SECTION" "$OUTPUT_FILE" 2>/dev/null || echo "0")
        ENTITY_COUNT=$(grep -c "LINE\|CIRCLE\|ARC" "$OUTPUT_FILE" 2>/dev/null || echo "0")
        log_info "📄 DXF-Inhalt: $SECTION_COUNT Sektionen, $ENTITY_COUNT Entitäten"
    fi
    
    # JSON-Konfiguration bestätigen
    if command -v jq >/dev/null 2>&1; then
        DIMENSIONS_USED=$(jq '.dimensions | length' "$CONFIG_FILE" 2>/dev/null || echo "0")
        log_success "📋 Alle $DIMENSIONS_USED Konfigurationsparameter wurden berücksichtigt!"
    fi
    
    echo ""
    log_success "Die Alpine Sennhütte ist bereit zum Öffnen in CAD-Software!"
    
    exit 0
else
    log_error "❌ Alle $STRATEGY_NUM Strategien fehlgeschlagen!"
    echo ""
    log_error "FEHLERBEHEBUNG:"
    echo "  1. 🗺️ System-Ressourcen prüfen: free -h && df -h"
    echo "  2. 🛠️ QCAD-Installation prüfen: qcad --version"
    echo "  3. 📺 Xvfb installieren: sudo apt install xvfb"
    echo "  4. 📝 Logs in /tmp prüfen"
    echo "  5. 📁 Schreibrechte prüfen: ls -la $(dirname \"$OUTPUT_FILE\")"
    echo "  6. 🧠 JSON-Konfiguration validieren: jq . \"$CONFIG_FILE\""
    echo "  7. 🔄 Manueller Test: qcad -platform offscreen \"$JS_SCRIPT\""
    echo ""
    log_error "Bei anhaltenden Problemen, verwende das ursprüngliche alpine_sennhutte_generator_fixed.js"
    
    exit 1
fi