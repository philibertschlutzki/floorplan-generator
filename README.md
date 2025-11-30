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

Die einfachste Art, das Tool zu nutzen, ist direkt hier im Browser. Keine Installation auf deinem PC notwendig!

### 1. Umgebung starten
Klicke oben auf den Button **"Open in GitHub Codespaces"**.
*   GitHub erstellt einen virtuellen Computer für dich.
*   Es werden automatisch alle nötigen Bibliotheken (OpenCV, NumPy) installiert.
*   *Hinweis: Der erste Start kann ca. 2 Minuten dauern.*

### 2. Bild hochladen
Ziehe dein Grundriss-Bild (z.B. `plan.jpg`) einfach per Drag & Drop in die Dateiliste links im Editor.

### 3. Generierung starten
Gib unten im Terminal folgenden Befehl ein:

```
python generate_from_image.py --input plan.jpg --output mein_haus.json
```

*Optional mit Skalierung (Pixel pro Meter):*
```
python generate_from_image.py --input plan.jpg --output mein_haus.json --scale 100
```

### 4. Ergebnisse nutzen
*   Die Datei `mein_haus.json` erscheint in der Dateiliste.
*   Rechtsklick -> **Download**, um sie zu sichern.

---

## 🛠 Lokale Installation (Experten)

Voraussetzungen: Python 3.8+, pip

```
git clone https://github.com/philibertschlutzki/floorplan-generator.git
cd floorplan-generator
pip install -r requirements.txt
```

## 🧪 Tests ausführen

Um die Funktionalität der Bilderkennung zu prüfen:

```
python -m unittest discover tests
```

## 📂 Projektstruktur

*   `cv_modules/`: Kernlogik für Computer Vision (Bildanalyse).
*   `validation/`: Prüft, ob generierte Wände/Türen physikalisch sinnvoll sind.
*   `generate_from_image.py`: Das Hauptskript zur Ausführung.
*   `archive/`: Alte Skripte (Legacy).
