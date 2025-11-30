# Floorplan Generator (CV Edition)

Ein Python-Tool zur automatischen Generierung von Gebäudekonfigurationen (JSON) aus 2D-Grundrissbildern mithilfe von Computer Vision (OpenCV).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/philibertschlutzki/floorplan-generator)

## 🌟 Features

*   **Image-to-Config:** Verwandelt JPG/PNG Grundrisse direkt in strukturierte JSON-Daten.
*   **Auto-Detection:** Erkennt Wände, Raumgrößen und Öffnungen automatisch.
*   **Browser-Ready:** Vollständig optimiert für die Ausführung in der Cloud (GitHub Codespaces).
*   **Modular:** Trennung von Bildverarbeitung, Validierung und Generierung.

---

## ☁️ Quick Start: GitHub Codespaces

Die einfachste Art, das Tool zu nutzen, ist direkt hier im Browser. **Keine Installation auf deinem PC notwendig!**

### 1. Umgebung starten
Klicke oben auf den Button **"Open in GitHub Codespaces"**.
*   GitHub erstellt einen virtuellen Computer für dich.
*   Es werden automatisch alle nötigen Bibliotheken (OpenCV, NumPy) installiert.
*   *Hinweis: Der erste Start kann ca. 2-3 Minuten dauern.*

### 2. Warten bis Setup abgeschlossen ist
Das Terminal zeigt den Fortschritt an. Warte, bis diese Meldung erscheint:
```
✅ Setup Complete!
```

### 3. Bild hochladen
Ziehe dein Grundriss-Bild (z.B. `plan.jpg`) einfach per Drag & Drop in die Dateiliste links im Editor.

### 4. Generierung starten
Gib unten im Terminal folgenden Befehl ein:

```bash
python generate_from_image.py --input plan.jpg --output mein_haus.json
```

*Optional mit Skalierung (Pixel pro Meter):*
```bash
python generate_from_image.py --input plan.jpg --output mein_haus.json --scale 100
```

### 5. Ergebnisse nutzen
*   Die Datei `mein_haus.json` erscheint in der Dateiliste.
*   Rechtsklick → **Download**, um sie zu sichern.

---

## 🔧 Problembehandlung

### Fehler: "ImportError: libGL.so.1: cannot open shared object file"

Dieses Problem tritt auf, wenn die OpenCV-Bibliothek versucht, grafische Komponenten zu laden, die in Cloud-Umgebungen nicht verfügbar sind.

**Automatische Lösung (empfohlen):**
Das Projekt verwendet seit dem neuesten Update `opencv-python-headless`, welches keine grafischen Bibliotheken benötigt. Falls du den Fehler trotzdem siehst:

1. **Abhängigkeiten neu installieren:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **Tests erneut ausführen:**
   ```bash
   python -m unittest discover tests
   ```

**Manuelle Lösung (falls automatisch nicht funktioniert):**
Falls die automatische Installation fehlschlägt, installiere die fehlenden Systembibliotheken manuell:

```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### Tests schlagen fehl mit "No module named 'cv2'"

OpenCV wurde nicht korrekt installiert. Führe aus:

```bash
pip install opencv-python-headless>=4.8.0
```

### Codespace startet nicht oder friert ein

1. Gehe zu [github.com/codespaces](https://github.com/codespaces)
2. Lösche den bestehenden Codespace
3. Erstelle einen neuen mit dem "Open in GitHub Codespaces" Button

---

## 🛠 Lokale Installation (Experten)

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)
- Git

### Installation

```bash
git clone https://github.com/philibertschlutzki/floorplan-generator.git
cd floorplan-generator
pip install -r requirements.txt
```

### Wichtige Hinweise zur lokalen Installation

**Für Cloud/Server-Umgebungen (ohne Display):**
Das Projekt verwendet standardmäßig `opencv-python-headless`, das keine GUI-Funktionen hat. Dies ist ideal für:
- GitHub Codespaces
- Docker Container
- Server ohne grafische Oberfläche
- CI/CD Pipelines

**Für lokale Desktop-Entwicklung (mit Display):**
Wenn du OpenCV GUI-Funktionen wie `cv2.imshow()` nutzen möchtest, kannst du in der `requirements.txt` die headless-Version durch die normale Version ersetzen:

```
# Ändere diese Zeile:
opencv-python-headless>=4.8.0

# Zu:
opencv-python>=4.8.0
```

Dann neu installieren:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 🧪 Tests ausführen

Um die Funktionalität der Bilderkennung zu prüfen:

```bash
python -m unittest discover tests
```

Oder mit pytest (empfohlen für detaillierte Ausgabe):

```bash
pytest tests/ -v
```

### Erwartetes Ergebnis

Bei erfolgreicher Installation sollten alle Tests durchlaufen:
```
======================================================================
Ran X tests in Y.ZZZs

OK
```

Falls Tests fehlschlagen, siehe Abschnitt **Problembehandlung** oben.

---

## 📂 Projektstruktur

```
floorplan-generator/
├── cv_modules/              # Kernlogik für Computer Vision
│   ├── image_preprocessor.py   # Bildvorverarbeitung
│   ├── feature_detector.py     # Erkennung von Wänden/Türen
│   ├── dimension_extractor.py  # Maßextraktion
│   └── config_generator.py     # JSON-Generierung
├── validation/              # Validierung der Ergebnisse
├── tests/                   # Unit- und Integrationstests
├── .devcontainer/           # Codespaces-Konfiguration
├── generate_from_image.py   # Hauptskript
├── requirements.txt         # Python-Abhängigkeiten
└── README.md               # Diese Datei
```

---

## 💡 Tipps für beste Ergebnisse

### Bildqualität
- **Auflösung:** Mindestens 1000x1000 Pixel
- **Format:** PNG oder JPG
- **Kontrast:** Klare Linien zwischen Wänden und Hintergrund
- **Farbe:** Schwarz-Weiß oder mit klaren Farbunterschieden

### Skalierung
Wenn du die `--scale` Option verwendest:
- Messe in deinem Bild, wie viele Pixel einem Meter entsprechen
- Beispiel: Wenn eine 5m lange Wand 500 Pixel lang ist, dann `--scale 100`

---

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:
1. Forke das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/NeuesFunktion`)
3. Committe deine Änderungen (`git commit -m 'Füge neue Funktion hinzu'`)
4. Push zum Branch (`git push origin feature/NeuesFunktion`)
5. Öffne einen Pull Request

---

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

---

## 🔗 Weitere Ressourcen

- [OpenCV Dokumentation](https://docs.opencv.org/)
- [GitHub Codespaces Dokumentation](https://docs.github.com/codespaces)
- [Python unittest Dokumentation](https://docs.python.org/3/library/unittest.html)