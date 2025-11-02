#!/bin/bash
CONFIG_FILE="$1"
OUTPUT_FILE="${2:-output/alpine_sennhuette.dxf}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "JSON-Konfigurationsdatei nicht gefunden: $CONFIG_FILE"
    exit 1
fi

qcad -autostart scripts/alpine_sennhuette_generator.js \
     --config="$CONFIG_FILE" \
     --output="$OUTPUT_FILE"

