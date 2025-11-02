#!/bin/bash

# Alpine Sennhütte Generator - Shell Script
# Ruft das korrigierte QCAD JavaScript auf

CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette.dxf}"

# Eingabe-Validierung
if [ -z "$CONFIG_FILE" ]; then
    echo "Fehler: Keine JSON-Konfigurationsdatei angegeben."
    echo "Verwendung: $0 <config.json> [ausgabe.dxf]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Fehler: JSON-Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
    exit 1
fi

# Output-Verzeichnis erstellen falls nötig
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Erstelle Output-Verzeichnis: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Debug-Informationen
echo "=== Alpine Sennhütte Generator ==="
echo "Konfiguration: $CONFIG_FILE"
echo "Ausgabe: $OUTPUT_FILE"
echo "QCAD Script: scripts/alpine_sennhuette_generator_fixed.js"
echo "Arbeitsverzeichnis: $(pwd)"
echo ""

# QCAD mit dem korrigierten Script aufrufen
echo "Starte QCAD..."
qcad -autostart scripts/alpine_sennhuette_generator_fixed.js \
     --config="$CONFIG_FILE" \
     --output="$OUTPUT_FILE"

# Ergebnis prüfen
EXIT_CODE=$?
echo ""
echo "=== Ergebnis ==="
echo "QCAD Exit-Code: $EXIT_CODE"

if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
    echo "Ausgabedatei erstellt: $OUTPUT_FILE ($FILE_SIZE Bytes)"
    
    if [ "$FILE_SIZE" -gt 0 ]; then
        echo "✓ Erfolgreich! Die Alpine Sennhütte wurde generiert."
        exit 0
    else
        echo "❌ Ausgabedatei ist leer."
        exit 1
    fi
else
    echo "❌ Ausgabedatei wurde nicht erstellt: $OUTPUT_FILE"
    echo "Mögliche Ursachen:"
    echo "- QCAD ist nicht installiert oder nicht im PATH"
    echo "- JavaScript-Fehler im Generator-Script"
    echo "- Ungültiger Ausgabepfad oder fehlende Schreibberechtigung"
    exit 1
fi