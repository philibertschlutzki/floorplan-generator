# Gebäudeplan-Generator Konfiguration

**Datum:** 2025-11-02 12:46:41

## Anweisungen für Perplexity AI

Bitte beantworte alle folgenden Fragen zur Erstellung eines Gebäudeplans. Basierend auf deinen Antworten wird ein QCAD-kompatibles Generierungsscript erstellt.

---

## 1. Grundlegende Gebäudeparameter

### Gebäudetyp auswählen oder eigene Parameter definieren:

**Verfügbare Voreinstellungen:**
- Keine Voreinstellungen verfügbar

**Frage 1:** Möchtest du eine Voreinstellung verwenden oder eigene Parameter definieren?
- Antwort: [VOREINSTELLUNG_NAME] oder [EIGENE_PARAMETER]

### Bei eigenen Parametern:

**Frage 2:** Gebäudebreite in Metern?
- Antwort: [ZAHL] (Standard: 10m)

**Frage 3:** Gebäudetiefe in Metern?
- Antwort: [ZAHL] (Standard: 8m)

**Frage 4:** Anzahl der Geschosse?
- Antwort: [ZAHL] (Standard: 2)

---

## 2. Raumlayout und Funktionalität

**Frage 5:** Welche Art von Raumlayout bevorzugst du?
- [EINFACH] - Grundlegende Raumaufteilung mit 4 Haupträumen
- [KOMPLEX] - Erweiterte Raumaufteilung mit mehreren Bereichen
- [INDIVIDUELL] - Spezifische Raumanforderungen definieren

### Bei individueller Raumlayout:

**Frage 6:** Welche spezifischen Räume sollen enthalten sein?
- Antwort: [Liste der gewünschten Räume]

**Frage 7:** Gibt es besondere Anforderungen an die Raumgrößen?
- Antwort: [Spezifische Größenangaben pro Raum]

---

## 3. Türen und Fenster

**Frage 8:** Anzahl der Eingangstüren?
- Antwort: [ZAHL] (Standard: 1)

**Frage 9:** Fensterplatzierung?
- [STANDARD] - Automatische Platzierung an Außenwänden
- [SPEZIFISCH] - Manuelle Festlegung der Positionen

### Bei spezifischer Fensterplatzierung:

**Frage 10:** Beschreibe die gewünschte Fensterverteilung:
- Antwort: [Detaillierte Beschreibung]

---

## 4. Ausgabe-Einstellungen

**Frage 11:** Gewünschter Dateiname für die DXF-Ausgabe?
- Antwort: [DATEINAME] (leer für automatische Benennung)

**Frage 12:** Zusätzliche Beschriftungen oder Labels gewünscht?
- [JA] - Mit Raumbeschriftungen
- [NEIN] - Nur geometrische Elemente

---

## 5. Script-Generierung

**Wichtig:** Nachdem du alle Fragen beantwortet hast, erstelle bitte ein komplettes `generate_building.sh` Script mit folgender Struktur:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# Automatisch generiertes Script basierend auf Benutzerangaben
# Generiert am: 2025-11-02 12:46:41

# Pfad-Konfiguration
QCAD_PATH="${QCAD_PATH:-/usr/bin/qcad}"
SCRIPT_PATH="${SCRIPT_PATH:-/home/user/floorplan-generator/scripts/building_generator.js}"
OUTPUT_DIR="${OUTPUT_DIR:-/home/user/floorplan-generator/output}"

# Parameter basierend auf Benutzerangaben
BUILDING_WIDTH=[WERT_AUS_ANTWORTEN]
BUILDING_DEPTH=[WERT_AUS_ANTWORTEN]
BUILDING_FLOORS=[WERT_AUS_ANTWORTEN]
OUTPUT_FILE="[WERT_AUS_ANTWORTEN]"
ROOM_LAYOUT="[WERT_AUS_ANTWORTEN]"

# Validierung und Ausführung
[REST_DES_SCRIPTS_WIE_IM_ORIGINAL]
```

Bitte fülle alle [WERT_AUS_ANTWORTEN] Platzhalter mit den entsprechenden Werten aus den Antworten oben aus.

---

## Hinweise

- Alle Maße werden intern in QCAD-Einheiten (1m = 1000 Einheiten) umgerechnet
- Die generierten DXF-Dateien sind mit AutoCAD und anderen CAD-Programmen kompatibel
- Das Script verwendet das bestehende JavaScript-Backend für die eigentliche Generierung

**Nach Beantwortung aller Fragen wird automatisch ein ausführbares Script generiert, das den gewünschten Gebäudeplan erstellt.**
