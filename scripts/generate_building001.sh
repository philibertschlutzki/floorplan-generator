#!/usr/bin/env bash
set -Eeuo pipefail

# Automatisch generiertes Script basierend auf Benutzerangaben
# Generiert am: 2025-11-02 12:46:41

# Pfad-Konfiguration
QCAD_PATH="${QCAD_PATH:-/home/user/bin/qcad}"
SCRIPT_PATH="${SCRIPT_PATH:-/home/user/floorplan-generator/scripts/building_generator.js}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/user/floorplan-generator/output}"

# 1m = 1000 QCAD-Einheiten
BUILDING_WIDTH=7000           # Antwort Frage 2: 7m → 7000 Einheiten
BUILDING_DEPTH=8000           # Antwort Frage 3: 8m → 8000 Einheiten
BUILDING_FLOORS=2             # Antwort Frage 4: 2 Geschosse
OUTPUT_FILE="entwurf_0001"    # Antwort Frage 11

# Raumlayout
# Individueller Raum: ein einzelner Raum, Wandstärke 1m (1000 Einheiten)
ROOM_LAYOUT="single_room_wall_1000"  # Antwort Frage 6/7

# Türen & Fenster
ENTRANCE_DOORS=1              # Antwort Frage 8: 1 Eingangstür
WINDOW_PLACEMENT="standard"   # Antwort Frage 9: automatische Außenwandplatzierung

# Labels
ROOM_LABELS="true"            # Antwort Frage 12: Ja, mit Raumbeschriftungen

# Übergabe der Parameter an das QCAD-JavaScript-Backend
"$QCAD_PATH" \
  -autostart \
  -script "$SCRIPT_PATH" \
  -- \
  --width "$BUILDING_WIDTH" \
  --depth "$BUILDING_DEPTH" \
  --floors "$BUILDING_FLOORS" \
  --rooms "$ROOM_LAYOUT" \
  --doors "$ENTRANCE_DOORS" \
  --windows "$WINDOW_PLACEMENT" \
  --wallThickness 1000 \
  --labels "$ROOM_LABELS" \
  --output "$OUTPUT_DIR/$OUTPUT_FILE.dxf"

echo "Gebäude-Entwurf als $OUTPUT_DIR/$OUTPUT_FILE.dxf erfolgreich erstellt."
