#!/usr/bin/env bash
set -Eeuo pipefail

# ===== generate_building_3d.sh =====
# Erweitertes Script zur 3D-Gebäudeerstellung mit isometrischer Darstellung

# Konfigurierbare Pfade
QCAD_PATH="${QCAD_PATH:-/usr/bin/qcad}"
SCRIPT_PATH="${SCRIPT_PATH:-/home/user/floorplan-generator/scripts/building_generator_3d.js}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/user/floorplan-generator/output}"

# Erweiterte 3D-Parameter
BUILDING_WIDTH=10000
BUILDING_DEPTH=8000
BUILDING_FLOORS=2
WALL_HEIGHT=3000
ROOF_TYPE="flat"
ROOF_HEIGHT=0
WINDOW_COUNT=2
DOOR_COUNT=1
WALL_COLOR="#CCCCCC"
ROOF_COLOR="#AA0000"
FOUNDATION_HEIGHT=500
ISO_ANGLE=30
VIEW_SCALE=1.0
DETAIL_LEVEL=2
OUTPUT_FORMAT=1
OUTPUT_FILE=""

usage() {
  cat <<'USAGE'
Verwendung: generate_building_3d.sh [OPTIONEN]

3D-Grundparameter:
  --width NUM           Gebäudebreite in Einheiten (Default: 10000)
  --depth NUM           Gebäudetiefe in Einheiten (Default: 8000)
  --floors NUM          Anzahl der Geschosse (Default: 2)
  --wall-height NUM     Wandhöhe pro Geschoss (Default: 3000)
  
Dachkonfiguration:
  --roof-type TYPE      Dachtyp: flat, gable, hip, shed (Default: flat)
  --roof-height NUM     Dachhöhe (Default: 0)
  
Fenster und Türen:
  --window-count NUM    Anzahl Fenster pro Wand (Default: 2)
  --door-count NUM      Anzahl Türen (Default: 1)
  
Farben (Hex-Format):
  --wall-color COLOR    Wandfarbe (Default: #CCCCCC)
  --roof-color COLOR    Dachfarbe (Default: #AA0000)
  
Erweiterte Optionen:
  --foundation-height NUM   Fundamenthöhe (Default: 500)
  --iso-angle NUM          Isometrischer Winkel (Default: 30)
  --view-scale NUM         Darstellungsmaßstab (Default: 1.0)
  --detail-level NUM       Detailgrad 1-3 (Default: 2)
  --output-format NUM      Format 1=DXF, 2=SVG, 3=PDF (Default: 1)
  --output FILE            Ziel-Datei (Default: auto)
  -h, --help              Hilfe anzeigen

Beispiel:
  generate_building_3d.sh --width=12000 --depth=8000 --floors=2 \\
                          --roof-type=gable --roof-height=2500 \\
                          --wall-color=#F5F5DC --roof-color=#8B4513
USAGE
}

# Erweiterte Argumentverarbeitung
while [[ $# -gt 0 ]]; do
  case "$1" in
    --width=*)         BUILDING_WIDTH="${1#*=}"; shift ;;
    --depth=*)         BUILDING_DEPTH="${1#*=}"; shift ;;
    --floors=*)        BUILDING_FLOORS="${1#*=}"; shift ;;
    --wall-height=*)   WALL_HEIGHT="${1#*=}"; shift ;;
    --roof-type=*)     ROOF_TYPE="${1#*=}"; shift ;;
    --roof-height=*)   ROOF_HEIGHT="${1#*=}"; shift ;;
    --window-count=*)  WINDOW_COUNT="${1#*=}"; shift ;;
    --door-count=*)    DOOR_COUNT="${1#*=}"; shift ;;
    --wall-color=*)    WALL_COLOR="${1#*=}"; shift ;;
    --roof-color=*)    ROOF_COLOR="${1#*=}"; shift ;;
    --foundation-height=*) FOUNDATION_HEIGHT="${1#*=}"; shift ;;
    --iso-angle=*)     ISO_ANGLE="${1#*=}"; shift ;;
    --view-scale=*)    VIEW_SCALE="${1#*=}"; shift ;;
    --detail-level=*)  DETAIL_LEVEL="${1#*=}"; shift ;;
    --output-format=*) OUTPUT_FORMAT="${1#*=}"; shift ;;
    --output=*)        OUTPUT_FILE="${1#*=}"; shift ;;
    
    # Alternate syntax ohne =
    --width)           BUILDING_WIDTH="$2"; shift 2 ;;
    --depth)           BUILDING_DEPTH="$2"; shift 2 ;;
    --floors)          BUILDING_FLOORS="$2"; shift 2 ;;
    --wall-height)     WALL_HEIGHT="$2"; shift 2 ;;
    --roof-type)       ROOF_TYPE="$2"; shift 2 ;;
    --roof-height)     ROOF_HEIGHT="$2"; shift 2 ;;
    --window-count)    WINDOW_COUNT="$2"; shift 2 ;;
    --door-count)      DOOR_COUNT="$2"; shift 2 ;;
    --wall-color)      WALL_COLOR="$2"; shift 2 ;;
    --roof-color)      ROOF_COLOR="$2"; shift 2 ;;
    --foundation-height) FOUNDATION_HEIGHT="$2"; shift 2 ;;
    --iso-angle)       ISO_ANGLE="$2"; shift 2 ;;
    --view-scale)      VIEW_SCALE="$2"; shift 2 ;;
    --detail-level)    DETAIL_LEVEL="$2"; shift 2 ;;
    --output-format)   OUTPUT_FORMAT="$2"; shift 2 ;;
    --output)          OUTPUT_FILE="$2"; shift 2 ;;
    
    -h|--help)         usage; exit 0 ;;
    *)                 echo "Unbekannte Option: $1" >&2; usage; exit 1 ;;
  esac
done

# Validierung
re='^[0-9]+$'
float_re='^[0-9]+\.?[0-9]*$'

[[ "$BUILDING_WIDTH"  =~ $re ]] || { echo "Ungültige Breite: $BUILDING_WIDTH" >&2; exit 2; }
[[ "$BUILDING_DEPTH"  =~ $re ]] || { echo "Ungültige Tiefe: $BUILDING_DEPTH" >&2; exit 2; }
[[ "$BUILDING_FLOORS" =~ $re ]] || { echo "Ungültige Geschosse: $BUILDING_FLOORS" >&2; exit 2; }
[[ "$WALL_HEIGHT"     =~ $re ]] || { echo "Ungültige Wandhöhe: $WALL_HEIGHT" >&2; exit 2; }
[[ "$ROOF_HEIGHT"     =~ $re ]] || { echo "Ungültige Dachhöhe: $ROOF_HEIGHT" >&2; exit 2; }

# Dachtyp validieren
case "$ROOF_TYPE" in
  flat|gable|hip|shed) ;;
  *) echo "Ungültiger Dachtyp: $ROOF_TYPE (erlaubt: flat, gable, hip, shed)" >&2; exit 2 ;;
esac

# QCAD-Binary finden
if ! command -v "$QCAD_PATH" >/dev/null 2>&1; then
  if command -v qcad >/dev/null 2>&1; then
    QCAD_PATH="$(command -v qcad)"
  else
    echo "QCAD nicht gefunden. Installiere QCAD oder setze QCAD_PATH." >&2
    exit 3
  fi
fi

# Script prüfen
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "3D-Generator-Script nicht gefunden: $SCRIPT_PATH" >&2
  exit 4
fi

# Ausgabeverzeichnis sicherstellen
mkdir -p "$OUTPUT_DIR"

# Ziel-Datei bestimmen
if [[ -z "$OUTPUT_FILE" ]]; then
  TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
  case "$OUTPUT_FORMAT" in
    1) EXT="dxf" ;;
    2) EXT="svg" ;;
    3) EXT="pdf" ;;
    *) EXT="dxf" ;;
  esac
  OUTPUT_FILE="$OUTPUT_DIR/building_3d_${TIMESTAMP}.${EXT}"
fi

echo "=== 3D-Gebäudegenerierung startet ==="
echo "Dimensionen: ${BUILDING_WIDTH} x ${BUILDING_DEPTH}"
echo "Geschosse: ${BUILDING_FLOORS}, Wandhöhe: ${WALL_HEIGHT}"
echo "Dach: ${ROOF_TYPE} (Höhe: ${ROOF_HEIGHT})"
echo "Fenster: ${WINDOW_COUNT}/Wand, Türen: ${DOOR_COUNT}"
echo "Farben: Wand=${WALL_COLOR}, Dach=${ROOF_COLOR}"
echo "Isometrischer Winkel: ${ISO_ANGLE}°, Maßstab: ${VIEW_SCALE}"
echo "Ausgabedatei: $OUTPUT_FILE"

# QCAD mit allen Parametern ausführen
"$QCAD_PATH" -autostart "$SCRIPT_PATH" \
  --width="$BUILDING_WIDTH" \
  --depth="$BUILDING_DEPTH" \
  --floors="$BUILDING_FLOORS" \
  --wall-height="$WALL_HEIGHT" \
  --roof-type="$ROOF_TYPE" \
  --roof-height="$ROOF_HEIGHT" \
  --window-count="$WINDOW_COUNT" \
  --door-count="$DOOR_COUNT" \
  --wall-color="$WALL_COLOR" \
  --roof-color="$ROOF_COLOR" \
  --foundation-height="$FOUNDATION_HEIGHT" \
  --iso-angle="$ISO_ANGLE" \
  --view-scale="$VIEW_SCALE" \
  --detail-level="$DETAIL_LEVEL" \
  --output-format="$OUTPUT_FORMAT" \
  --output="$OUTPUT_FILE"

rc=$?
if [[ $rc -ne 0 ]]; then
  echo "QCAD meldete Fehlercode $rc" >&2
  exit $rc
fi

echo "=== 3D-Gebäude erfolgreich erstellt! ==="
echo "✓ Vier Wände gezeichnet"
echo "✓ Dachkonstruktion hinzugefügt"
echo "✓ Fundament/Boden erstellt"
echo "✓ Isometrische Darstellung angewendet"
echo "Datei gespeichert: $OUTPUT_FILE"