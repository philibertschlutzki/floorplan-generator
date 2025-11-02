#!/bin/bash

# Verbessertes QCAD Alpine Sennnhütte Generator Skript
# Behebt die Probleme des ursprünglichen Skripts

CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette.dxf}"

# Eingabevalidierung
if [ $# -eq 0 ]; then
    echo "Verwendung: $0 <JSON-Konfigurationsdatei> [Ausgabedatei]"
    echo "Beispiel: $0 alpenhuette_config_20251102_165511.json output/meine_huette.dxf"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ JSON-Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
    echo "Stellen Sie sicher, dass der Pfad korrekt ist."
    exit 1
fi

# Prüfe ob QCAD verfügbar ist
if ! command -v qcad &> /dev/null; then
    echo "❌ QCAD ist nicht im PATH verfügbar."
    echo "Installieren Sie QCAD oder fügen Sie es zum PATH hinzu:"
    echo "export PATH=\$PATH:/pfad/zu/qcad"
    exit 1
fi

# Erstelle Output-Verzeichnis falls es nicht existiert
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "✓ Ausgabeverzeichnis erstellt: $OUTPUT_DIR"
fi

# Validiere JSON-Datei
if ! python3 -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "❌ Ungültiges JSON-Format in: $CONFIG_FILE"
    exit 1
fi

echo "=== QCAD Alpine Sennhütte Generator ==="
echo "Konfiguration: $CONFIG_FILE"
echo "Ausgabedatei:  $OUTPUT_FILE"
echo ""

# QCAD mit verbessertem Skript starten
# Verwende absolute Pfade für bessere Kompatibilität
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_ABS="$(readlink -f "$CONFIG_FILE")"
OUTPUT_ABS="$(readlink -f "$OUTPUT_FILE")"

echo "Starte QCAD..."
qcad -autostart "$SCRIPT_DIR/scripts/alpine_sennhuette_generator_fixed.js" \
     --config="$CONFIG_ABS" \
     --output="$OUTPUT_ABS" \
     -no-gui \
     -quit

# Prüfe Ergebnis
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Alpine Sennhütte erfolgreich generiert!"
    echo "📁 Ausgabedatei: $OUTPUT_FILE"
    
    # Zeige Dateigröße
    SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || stat -f%z "$OUTPUT_FILE" 2>/dev/null)
    echo "📊 Dateigröße: ${SIZE} Bytes"
else
    echo "❌ Fehler bei der Generierung der Alpine Sennhütte"
    echo "Prüfen Sie die QCAD-Installation und die Konfigurationsdatei"
    exit 1
fi

echo ""
echo "=== Fertig ==="