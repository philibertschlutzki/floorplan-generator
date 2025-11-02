# DXF Workflow Tools - Komplettes Script-System

Dieses System erstellt ein vollständiges Script-Set, das eine DXF-Datei von einer URL lädt, sie in eine natürlichsprachige Beschreibung umwandelt, aus dieser Beschreibung eine neue DXF-Datei rekonstruiert und anschließend die Unterschiede zwischen Original und Rekonstruktion analysiert.

## 🎯 Überblick

Das System besteht aus vier Hauptkomponenten:

1. **DXF → Natürlichsprache Konverter** (`dxf_to_text.py`)
2. **Natürlichsprache → DXF Konverter** (`text_to_dxf.py`) 
3. **Workflow Manager** (`dxf_workflow.py`) - **Hauptscript**
4. **Requirements** (`requirements.txt`)

## 🚀 Schnellstart

### Installation der Abhängigkeiten

```bash
pip install -r requirements.txt
```

### Hauptverwendung (Empfohlen)

Führen Sie den kompletten Workflow mit einem Befehl aus:

```bash
python dxf_workflow.py https://github.com/philibertschlutzki/floorplan-generator/blob/main/output/building_1762086268523.dxf ./output
```

## 📋 Detaillierte Funktionen

### 1. DXF zu Natürlichsprache (`dxf_to_text.py`)

**Funktionalität:**
- Lädt und analysiert DXF-Dateien mit der ezdxf-Bibliothek
- Extrahiert geometrische Elemente (Linien, Kreise, Polylinien, Text, etc.)
- Erstellt natürlichsprachige Beschreibungen der Geometrie
- Exportiert strukturierte JSON-Daten für Rückkonvertierung

**Unterstützte DXF-Entities:**
- LINE (Linien mit Start-/Endpunkten und Länge)
- CIRCLE (Kreise mit Mittelpunkt, Radius, Umfang, Fläche)
- ARC (Kreisbögen mit Winkelinformationen)
- LWPOLYLINE/POLYLINE (Mehrpunkt-Linien)
- TEXT/MTEXT (Textbeschriftungen)
- Layer-Informationen (Farben, Linientypen)

**Ausgaben:**
- `*_description.txt` - Natürlichsprachige Beschreibung
- `*_structured.json` - Strukturierte Daten für Rekonstruktion

### 2. Natürlichsprache zu DXF (`text_to_dxf.py`)

**Funktionalität:**
- Rekonstruiert DXF-Dateien aus strukturierten JSON-Daten
- Parst natürlichsprachige Beschreibungen (vereinfacht)
- Erstellt Layer und geometrische Entities
- Bewahrt DXF-Versionskompatibilität

**Eingaben:**
- Strukturierte JSON-Daten (empfohlen)
- Natürlichsprachige Textbeschreibungen

**Ausgaben:**
- Rekonstruierte DXF-Datei
- Extrahierte JSON-Daten (bei Textinput)

### 3. Workflow Manager (`dxf_workflow.py`)

**Hauptfunktionen:**
- **Automatischer Download:** Unterstützt GitHub URLs (automatische Raw-URL Konvertierung)
- **Vollständiger Workflow:** Führt alle Schritte automatisch aus
- **Fehlerbehandlung:** Robuste Fehlerbehandlung und Logging
- **Temporäre Dateien:** Sichere Bereinigung nach Abschluss
- **Umfassende Reports:** Detaillierte Protokollierung aller Schritte

**Workflow-Schritte:**
1. Download der DXF-Datei von URL
2. Konvertierung DXF → Natürlichsprache
3. Rekonstruktion Natürlichsprache → DXF
4. Differenz-Analyse Original vs. Rekonstruktion
5. Erstellung von Workflow- und Differenz-Reports

## 🔧 Technische Details

### Architektur

```
Input URL → Download → DXF Analysis → Natural Language → DXF Reconstruction → Difference Analysis → Reports
```

### Abhängigkeiten

- **ezdxf:** DXF-Datei Verarbeitung
- **numpy:** Mathematische Berechnungen
- **Standard Python Libraries:** json, os, sys, math, subprocess, etc.

### Fehlerbehandlung

- DXF Recovery bei beschädigten Dateien
- Robuste URL-Behandlung (GitHub Blob → Raw Konvertierung)
- Umfassende Ausnahmebehandlung
- Detailliertes Logging aller Operationen

### Ausgabedateien

Nach erfolgreichem Workflow erhalten Sie:

1. **`natural_description.txt`** - Menschenlesbare Beschreibung der DXF-Geometrie
2. **`structured_data.json`** - Maschinenlesbare strukturierte Daten
3. **`reconstructed.dxf`** - Rekonstruierte DXF-Datei
4. **`difference_report.md`** - Analyse der Unterschiede zwischen Original und Rekonstruktion
5. **`workflow_report.md`** - Komplettes Protokoll des Workflow-Prozesses

## 🎯 Anwendungsfälle

### Für Ingenieure und CAD-Anwender
- **Dokumentation:** Automatische Erstellung von Baubeschreibungen aus DXF-Plänen
- **Qualitätskontrolle:** Verifikation von CAD-Datenintegrität
- **Archivierung:** Langfristige Speicherung von CAD-Informationen in lesbarer Form

### Für Entwickler
- **CAD-Integration:** Brücke zwischen CAD-Systemen und anderen Anwendungen
- **Datenanalytik:** Extraktion geometrischer Informationen für weitere Verarbeitung
- **Automatisierung:** Batch-Verarbeitung von CAD-Dateien

### Für Forschung
- **NLP in CAD:** Erforschung natürlichsprachiger CAD-Beschreibungen
- **Geometrie-Analyse:** Automatische Analyse von Konstruktionsmustern
- **Datenvalidierung:** Überprüfung von CAD-zu-Text-zu-CAD Konvertierungen

## ⚙️ Erweiterte Verwendung

### Einzelscript-Verwendung

```bash
# Nur DXF zu Text
python dxf_to_text.py input.dxf

# Nur Text zu DXF (aus JSON)
python text_to_dxf.py structured_data.json output.dxf

# Nur Text zu DXF (aus Natürlichsprache)
python text_to_dxf.py description.txt output.dxf
```

### Konfiguration

Das System kann durch Modifikation der Script-Parameter angepasst werden:
- Toleranzwerte für Geometrie-Vergleiche
- Unterstützte DXF-Entity-Typen
- Ausgabeformate und -detail

## 🔄 Workflow-Status

Das System protokolliert alle Operationen mit Zeitstempel:

```
[2025-11-02 20:04:32] INFO: === STARTE DXF WORKFLOW ===
[2025-11-02 20:04:32] INFO: Starte Download von: https://...
[2025-11-02 20:04:33] INFO: Download erfolgreich: /tmp/building_1762086268523.dxf
[2025-11-02 20:04:33] INFO: Starte DXF zu Natürlichsprache Konvertierung...
[2025-11-02 20:04:34] INFO: DXF zu Text Konvertierung erfolgreich
[2025-11-02 20:04:34] INFO: Starte Natürlichsprache zu DXF Konvertierung...
[2025-11-02 20:04:35] INFO: Text zu DXF Konvertierung erfolgreich
[2025-11-02 20:04:35] INFO: Starte Differenz-Analyse...
[2025-11-02 20:04:35] INFO: Differenz-Analyse erfolgreich
[2025-11-02 20:04:35] INFO: === WORKFLOW ERFOLGREICH ABGESCHLOSSEN ===
```

## 🛠️ Troubleshooting

### Häufige Probleme

1. **ezdxf Installation:** `pip install ezdxf`
2. **GitHub URLs:** Das System konvertiert automatisch `/blob/` zu Raw URLs
3. **DXF-Fehler:** Eingebaute Recovery-Funktionen für beschädigte Dateien
4. **Speicherplatz:** Temporäre Dateien werden automatisch bereinigt

### Erweiterte Fehlerdiagnose

Alle Logs werden in den Workflow-Reports gespeichert für detaillierte Fehleranalyse.

## 🎉 Fazit

Dieses Script-System bietet eine vollständige Lösung für die bidirektionale Konvertierung zwischen DXF-CAD-Dateien und natürlichsprachigen Beschreibungen. Es ist besonders wertvoll für:

- **Automatisierte CAD-Dokumentation**
- **Qualitätssicherung in CAD-Workflows** 
- **Integration von CAD-Daten in andere Systeme**
- **Langfristige Archivierung von CAD-Informationen**

Das System ist erweiterbar und kann für spezifische Anwendungsfälle angepasst werden.