# DXF Parser & Workflow

Dieses Verzeichnis enthält Tools zur Verarbeitung von DXF-Dateien mit natürlichsprachigen Beschreibungen.

## Übersicht

Der Workflow ermöglicht es:
1. **DXF-Dateien** von URLs herunterzuladen
2. **DXF → Natürlichsprache**: Geometrische Inhalte in verständlicher Form beschreiben
3. **Natürlichsprache → DXF**: Aus Beschreibungen neue DXF-Dateien erstellen
4. **Differenz-Analyse**: Original und Rekonstruktion vergleichen

## Hauptdateien

### Workflow-Manager
- **`dxf_workflow.py`** - Kompletter automatisierter Workflow
- **`test_workflow.py`** - Test-Script für Qualitätssicherung

### Kern-Module
- **`dxf_to_text.py`** - Konvertiert DXF → natürlichsprachige Beschreibung
- **`text_to_dxf.py`** - Rekonstruiert DXF aus strukturierten Daten

### Zusätzliche Scripts
- **`script.py`** bis **`script_4.py`** - Verschiedene Utility-Scripts
- **`requirements.txt`** - Python-Abhängigkeiten

## Installation

```bash
# Installiere Abhängigkeiten
pip install -r requirements.txt

# Oder einzelne Pakete:
pip install ezdxf numpy pyparsing urllib3 requests
```

## Verwendung

### Kompletter Workflow

```bash
# Grundlegende Verwendung
python dxf_workflow.py <dxf-url> [output-directory]

# Beispiel
python dxf_workflow.py https://github.com/user/repo/blob/main/file.dxf ./output
```

**Workflow-Schritte:**
1. ✅ DXF-Datei Download von URL
2. ✅ DXF → Natürlichsprachige Beschreibung
3. ✅ Natürlichsprachige Beschreibung → DXF Rekonstruktion
4. ✅ Differenz-Analyse zwischen Original und Rekonstruktion
5. ✅ Erstellung eines Gesamt-Reports

### Einzelne Module

#### DXF zu Text
```bash
python dxf_to_text.py input.dxf
# Erstellt: input_description.txt, input_structured.json
```

#### Text zu DXF
```bash
# Aus strukturierten Daten
python text_to_dxf.py structured_data.json output.dxf

# Aus natürlichsprachiger Beschreibung
python text_to_dxf.py description.txt output.dxf
```

### Tests ausführen

```bash
# Kompletter Test mit Beispiel-DXF
python test_workflow.py

# Nur Modul-Tests
python test_workflow.py --modules-only
```

## Ausgabedateien

Der Workflow erstellt folgende Dateien:

| Datei | Beschreibung |
|-------|-------------|
| `natural_description.txt` | Natürlichsprachige Beschreibung der DXF |
| `structured_data.json` | Strukturierte Daten für Rekonstruktion |
| `reconstructed.dxf` | Rekonstruierte DXF-Datei |
| `difference_report.md` | Vergleich Original vs. Rekonstruktion |
| `workflow_report.md` | Gesamt-Report mit Logs |

## Beispiel-Workflow

```bash
# Test mit der Alpine Senhütte DXF
python dxf_workflow.py \
  https://github.com/philibertschlutzki/floorplan-generator/blob/main/output/alpine_sennhuette.dxf \
  ./output
```

**Erwartete Ausgabe:**
```
[2025-11-02 21:21:17] INFO: === STARTE DXF WORKFLOW ===
[2025-11-02 21:21:17] INFO: Starte Download von: https://github.com/...
[2025-11-02 21:21:18] INFO: Download erfolgreich: /tmp/dxf_workflow_xyz/alpine_sennhuette.dxf (23510 bytes)
[2025-11-02 21:21:20] INFO: Beschreibung erstellt: output/natural_description.txt
[2025-11-02 21:21:20] INFO: Strukturierte Daten erstellt: output/structured_data.json
[2025-11-02 21:21:22] INFO: Rekonstruierte DXF erstellt: output/reconstructed.dxf
[2025-11-02 21:21:23] INFO: === WORKFLOW ERFOLGREICH ABGESCHLOSSEN ===

🎉 Workflow erfolgreich abgeschlossen!
📂 Ausgabedateien in: ./output
```

## Fehlerbehebung

### Häufige Probleme

1. **`ezdxf` nicht installiert**
   ```bash
   pip install ezdxf
   ```

2. **GitHub URL funktioniert nicht**
   - Verwende "Raw" URLs oder "Blob" URLs
   - Das Script konvertiert automatisch zu Raw URLs

3. **Leere DXF-Rekonstruktion**
   - Prüfe `structured_data.json` auf gültige Entities
   - Verwende `--debug` Flag für detaillierte Logs

4. **Workflow-Report fehlt**
   - Jetzt wird der Report auch bei Fehlern erstellt
   - Prüfe Schreibrechte im Output-Verzeichnis

### Debug-Informationen

Die verbesserte Version bietet:
- **Detailliertes Logging** mit Zeitstempel
- **Traceback-Ausgabe** bei Fehlern
- **Validierung** der Ein- und Ausgabedateien
- **Fehlertolerante** Workflow-Ausführung

## Verbesserungen

### Version 2.0 (November 2025)

✅ **Behobene Probleme:**
- Text zu DXF Konvertierung schlägt nicht mehr fehl
- Workflow-Report wird immer erstellt
- Bessere Fehlerbehandlung und -ausgabe
- Verwendung separater Module statt Inline-Code
- Detaillierte Validierung der Eingabedaten

✅ **Neue Features:**
- Test-Script für automatisierte Qualitätssicherung
- Verbesserte Entity-Unterstützung (LWPOLYLINE, ARC, TEXT)
- Robuste GitHub URL-Behandlung
- Temporäre Datei-Verwaltung

## Unterstützte DXF-Entities

| Entity | DXF → Text | Text → DXF | Beschreibung |
|--------|-------------|-------------|-------------|
| LINE | ✅ | ✅ | Gerade Linien |
| CIRCLE | ✅ | ✅ | Kreise |
| ARC | ✅ | ✅ | Kreisbögen |
| LWPOLYLINE | ✅ | ✅ | Leichte Polylinien |
| POLYLINE | ✅ | ✅ | 3D Polylinien |
| TEXT | ✅ | ✅ | Einzeiliger Text |
| MTEXT | ✅ | ✅ | Mehrzeiliger Text |

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.