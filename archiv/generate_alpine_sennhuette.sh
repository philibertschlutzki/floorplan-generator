#!/bin/bash

# Alpine Sennhütte Generator - Optimiertes Shell Script
# Fokus auf die funktionierenden Strategien mit besserem Timeout

CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette.dxf}"

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNUNG]${NC} $1"; }
log_error() { echo -e "${RED}[❌]${NC} $1"; }

# Signal-Handler für sauberes Beenden
cleanup() {
    log_warning "Script unterbrochen - räume auf..."
    # Verwaiste QCAD-Prozesse beenden
    pkill -f "qcad.*alpine_sennhutte_generator_fixed.js" 2>/dev/null
    exit 130
}
trap cleanup INT TERM

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

# JSON-Validierung
if command -v jq >/dev/null 2>&1; then
    if ! jq empty "$CONFIG_FILE" >/dev/null 2>&1; then
        log_error "Ungültige JSON-Datei: $CONFIG_FILE"
        exit 1
    fi
    log_success "JSON-Konfiguration validiert"
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
    exit 1
fi

# Script prüfen
SCRIPT_PATH="scripts/alpine_sennhutte_generator_fixed.js"
if [ ! -f "$SCRIPT_PATH" ]; then
    log_error "JavaScript-Generator nicht gefunden: $SCRIPT_PATH"
    exit 1
fi

# Info
log_info "=== Alpine Sennhütte Generator (Optimiert) ==="
log_info "Konfiguration: $CONFIG_FILE"
log_info "Ausgabe: $OUTPUT_FILE"
log_info "Script: $SCRIPT_PATH"

# Alte Ausgabedatei löschen
[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE"

# OPTIMIERTE QCAD-STRATEGIEN (nur die vielversprechendsten)
declare -a STRATEGIES=(
    # Strategie 1: Xvfb (meist am stabilsten)
    "xvfb-run -a -s '-screen 0 1024x768x24' qcad -autostart"
    # Strategie 2: Qt Offscreen mit Umgebungsvariablen  
    "QT_QPA_PLATFORM=offscreen QT_LOGGING_RULES='*.debug=false' qcad -autostart"
    # Strategie 3: QCAD minimal
    "qcad -platform minimal -style fusion -autostart"
    # Strategie 4: Vollständig headless
    "QT_QPA_PLATFORM=offscreen QT_AUTO_SCREEN_SCALE_FACTOR=0 QT_FONT_DPI=96 qcad -platform offscreen -autostart"
)

# Xvfb-Verfügbarkeit prüfen
if ! command -v xvfb-run >/dev/null 2>&1; then
    log_warning "xvfb-run nicht verfügbar - installiere mit: sudo apt install xvfb"
    unset STRATEGIES[0]  # Entferne Xvfb-Strategie
fi

# Funktion für sicheren QCAD-Start
run_qcad_strategy() {
    local strategy="$1"
    local strategy_num="$2"
    
    # Command zusammenbauen
    local FULL_COMMAND="$strategy '$SCRIPT_PATH' --config='$CONFIG_FILE' --output='$OUTPUT_FILE'"
    
    log_info "Befehl: $FULL_COMMAND"
    
    # Erweiterte Timeout-Behandlung (30 Sekunden)
    timeout 30s bash -c "$FULL_COMMAND" 2>&1 &
    local QCAD_PID=$!
    
    # Warte auf Prozess mit Live-Monitoring
    local count=0
    while kill -0 $QCAD_PID 2>/dev/null; do
        sleep 1
        count=$((count + 1))
        
        # Alle 5 Sekunden Status prüfen
        if [ $((count % 5)) -eq 0 ]; then
            log_info "Läuft... (${count}s)"
            
            # Frühe Erfolgserkennung
            if [ -f "$OUTPUT_FILE" ]; then
                local FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
                if [ "$FILE_SIZE" -gt 100 ]; then
                    log_success "Datei während Ausführung erstellt!"
                    break
                fi
            fi
        fi
        
        # Timeout prüfen (30s)
        if [ $count -ge 30 ]; then
            log_warning "Timeout erreicht - beende Prozess"
            kill -TERM $QCAD_PID 2>/dev/null
            sleep 2
            kill -KILL $QCAD_PID 2>/dev/null
            break
        fi
    done
    
    # Warte auf Prozess-Ende
    wait $QCAD_PID 2>/dev/null
    local EXIT_CODE=$?
    
    log_info "Exit-Code: $EXIT_CODE"
    return $EXIT_CODE
}

# QCAD mit optimierten Strategien versuchen
SUCCESS=false
STRATEGY_NUM=0

for strategy in "${STRATEGIES[@]}"; do
    if [ -z "$strategy" ]; then
        continue
    fi
    
    STRATEGY_NUM=$((STRATEGY_NUM + 1))
    log_info "=== Strategie $STRATEGY_NUM ==="
    
    # Strategy ausführen
    run_qcad_strategy "$strategy" "$STRATEGY_NUM"
    EXIT_CODE=$?
    
    # Erfolgs-Prüfung
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
        
        if [ "$FILE_SIZE" -gt 100 ]; then
            log_success "Strategie $STRATEGY_NUM erfolgreich!"
            log_success "Datei: $OUTPUT_FILE ($FILE_SIZE Bytes)"
            SUCCESS=true
            break
        else
            log_warning "Datei zu klein: $FILE_SIZE Bytes"
            rm -f "$OUTPUT_FILE"
        fi
    fi
    
    # Fehler-Analyse
    case $EXIT_CODE in
        0)
            log_warning "Strategie $STRATEGY_NUM: Erfolgreich beendet, aber keine gültige Ausgabedatei"
            ;;
        124)
            log_warning "Strategie $STRATEGY_NUM: Timeout (30s)"
            ;;
        139)
            log_warning "Strategie $STRATEGY_NUM: Speicherzugriffsfehler"
            ;;
        143)
            log_warning "Strategie $STRATEGY_NUM: SIGTERM (unterbrochen)"
            ;;
        *)
            log_warning "Strategie $STRATEGY_NUM: Unbekannter Fehler (Exit: $EXIT_CODE)"
            ;;
    esac
    
    echo ""
done

# Endergebnis
echo ""
log_info "=== ENDERGEBNIS ==="

if [ "$SUCCESS" = true ]; then
    FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null)
    log_success "✅ Alpine Sennhütte erfolgreich generiert!"
    log_success "📁 Datei: $OUTPUT_FILE ($FILE_SIZE Bytes)"
    
    # Datei-Info
    if command -v file >/dev/null 2>&1; then
        FILE_TYPE=$(file "$OUTPUT_FILE" 2>/dev/null | cut -d: -f2)
        log_info "🔍 Typ:$FILE_TYPE"
    fi
    
    # DXF-Header prüfen
    if head -n 5 "$OUTPUT_FILE" 2>/dev/null | grep -q "DXF\|SECTION"; then
        log_success "🔍 Gültiger DXF-Header erkannt"
    else
        log_warning "🔍 DXF-Header nicht erkannt - Datei öffnen prüfen"
    fi
    
    exit 0
else
    log_error "❌ Alle Strategien fehlgeschlagen!"
    echo ""
    log_error "Empfohlene Maßnahmen:"
    echo "  1. Installiere Xvfb: sudo apt install xvfb"
    echo "  2. Prüfe QCAD: qcad --version"
    echo "  3. Teste manuell: qcad -platform offscreen"
    echo "  4. Prüfe Logs in /tmp für weitere Hinweise"
    echo "  5. System-RAM prüfen: free -h"
    echo "  6. Schreibrechte prüfen: ls -la $(dirname \"$OUTPUT_FILE\")"
    
    exit 1
fi