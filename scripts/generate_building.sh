#!/usr/bin/env bash
set -Eeuo pipefail

# ===== generate_building.sh =====
# Wrapper-Script zur Automatisierung der Gebäudeerstellung

# Konfigurierbare Pfade (können per Umgebung überschrieben werden)
QCAD_PATH="${QCAD_PATH:-/usr/bin/qcad}"
SCRIPT_PATH="${SCRIPT_PATH:-/home/user/floorplan-generator/scripts/building_generator.js}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/user/floorplan-generator/output}"

# Standardparameter
BUILDING_WIDTH=10000
BUILDING_DEPTH=8000
BUILDING_FLOORS=2
OUTPUT_FILE=""

usage() {
  cat <<'USAGE'
Verwendung: generate_building.sh [OPTIONEN]

  --width NUM    | --width=NUM     Gebäudebreite in Einheiten (Default: 10000)
  --depth NUM    | --depth=NUM     Gebäudetiefe in Einheiten (Default: 8000)
  --floors NUM   | --floors=NUM    Anzahl der Geschosse (Default: 2)
  --output FILE  | --output=FILE   Ziel-DXF-Datei (Default: output/building_<TS>.dxf)
  -h, --help                        Hilfe anzeigen

Beispiel:
  generate_building.sh --width=7000 --depth=6000 --floors=2
USAGE
}

# Argumente parsen (unterstützt --opt=Wert und --opt Wert)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --width=*)  BUILDING_WIDTH="${1#*=}"; shift ;;
    --depth=*)  BUILDING_DEPTH="${1#*=}"; shift ;;
    --floors=*) BUILDING_FLOORS="${1#*=}"; shift ;;
    --output=*) OUTPUT_FILE="${1#*=}"; shift ;;
    --width)    BUILDING_WIDTH="$2"; shift 2 ;;
    --depth)    BUILDING_DEPTH="$2"; shift 2 ;;
    --floors)   BUILDING_FLOORS="$2"; shift 2 ;;
    --output)   OUTPUT_FILE="$2"; shift 2 ;;
    -h|--help)  usage; exit 0 ;;
    *)          echo "Unbekannte Option: $1" >&2; usage; exit 1 ;;
  esac
done

# Grundlegende Validierung
re='^[0-9]+$'
[[ "$BUILDING_WIDTH"  =~ $re ]] || { echo "Ungültige Breite: $BUILDING_WIDTH" >&2; exit 2; }
[[ "$BUILDING_DEPTH"  =~ $re ]] || { echo "Ungültige Tiefe: $BUILDING_DEPTH" >&2; exit 2; }
[[ "$BUILDING_FLOORS" =~ $re ]] || { echo "Ungültige Geschosse: $BUILDING_FLOORS" >&2; exit 2; }

# QCAD-Binary finden
if ! command -v "$QCAD_PATH" >/dev/null 2>&1; then
  if command -v qcad >/dev/null 2>&1; then
    QCAD_PATH="$(command -v qcad)"
  else
    echo "QCAD nicht gefunden (QCAD_PATH=$QCAD_PATH). Pfad prüfen oder QCAD_PATH setzen." >&2
    exit 3
  fi
fi

# Autostart-Script prüfen
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "Autostart-Script nicht gefunden: $SCRIPT_PATH" >&2
  exit 4
fi

# Ausgabeverzeichnis sicherstellen
mkdir -p "$OUTPUT_DIR"

# Ziel-Datei bestimmen
if [[ -z "$OUTPUT_FILE" ]]; then
  TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
  OUTPUT_FILE="$OUTPUT_DIR/building_${TIMESTAMP}.dxf"
fi

echo "Generiere Gebäude: ${BUILDING_WIDTH} x ${BUILDING_DEPTH}, Geschosse: ${BUILDING_FLOORS}"
echo "Ausgabedatei: $OUTPUT_FILE"
echo "QCAD-Binary: $QCAD_PATH"
echo "Autostart-Script: $SCRIPT_PATH"

# QCAD ausführen (Autostart-Mechanismus)
"$QCAD_PATH" -autostart "$SCRIPT_PATH" \
  --width="$BUILDING_WIDTH" \
  --depth="$BUILDING_DEPTH" \
  --floors="$BUILDING_FLOORS" \
  --output="$OUTPUT_FILE"

rc=$?
if [[ $rc -ne 0 ]]; then
  echo "QCAD meldete Fehlercode $rc" >&2
  exit $rc
fi

echo "Erfolg: Datei gespeichert unter $OUTPUT_FILE"

