# Building Plan & Facade Generator (CV Edition)

Ein Python-Tool zur automatischen Generierung von Gebäudekonfigurationen und QCAD-Plänen aus 2D-Grundrissbildern und Fassadenfotos mithilfe von Computer Vision (OpenCV).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/philibertschlutzki/floorplan-generator)

## 🌟 Features

*   **Image-to-Config:** Verwandelt JPG/PNG Grundrisse oder Fassadenfotos in strukturierte QCAD-Pläne.
*   **Dual Mode:** Unterstützt sowohl **Grundrisse** (`--mode floorplan`) als auch **Fassaden** (`--mode facade`).
*   **Auto-Correction & Manual QA:** Automatische Perspektivkorrektur mit integriertem manuellen Korrektur-Workflow.
*   **Multi-Image Support:** Verarbeitet mehrere Bilder (z.B. 4 Fassadenansichten) in einem Durchgang.
*   **Browser-Ready:** Optimiert für GitHub Codespaces.

---

## ☁️ Quick Start: GitHub Codespaces

### 1. Umgebung starten
Klicke auf **"Open in GitHub Codespaces"**.

### 2. Bild hochladen
Lade deine Bilder (z.B. `front.jpg`, `side.jpg`) in das Projektverzeichnis hoch.

### 3. Generierung starten

**Für einen Grundriss (Einzelbild):**
```bash
python main.py --input plan.jpg --output mein_haus.dxf --mode floorplan
```

**Für Fassaden (Mehrere Bilder, z.B. 4 Seiten):**
```bash
python main.py --input front.jpg back.jpg left.jpg right.jpg --output meine_fassade.dxf --mode facade
```

### 4. Interaktiver Workflow
Das Tool führt dich durch den Prozess:
1.  **Perspektivkorrektur:** Es wird eine Vorschau angezeigt (`preview_rectified_X.jpg`). Du kannst bestätigen (`y`) oder manuell 4 Eckpunkte eingeben (`n`), um die Entzerrung zu korrigieren.
2.  **Maßeingabe:** Gib die realen Maße (Länge, Breite, Höhen) ein, um den Plan zu skalieren.
3.  **Ergebnis:** Die fertige `.dxf` Datei wird erstellt und enthält die entzerrten Bilder als Referenz sowie die generierten Linienzeichnungen.

---

## 🔧 Funktionen im Detail

### 1. Fassaden-Modus (`--mode facade`)
*   Ermöglicht das Hochladen von Fotos echter Gebäude.
*   Gleicht Verzerrungen (Perspektive) aus.
*   Ordnet mehrere Ansichten nebeneinander in einer QCAD-Zeichnung an.
*   Fügt das entzerrte Originalfoto als Hintergrundbild ein, um manuelles Nachzeichnen zu erleichtern.

### 2. Manuelle Korrektur (QA)
Wenn die automatische Erkennung des Gebäudes fehlschlägt, fragt das Tool nach den 4 Ecken:
```
Top-Left (x,y): 100, 200
Top-Right (x,y): ...
```
Dies garantiert, dass auch schwierige Fotos korrekt entzerrt werden.

---

## 🛠 Lokale Installation

```bash
git clone https://github.com/philibertschlutzki/floorplan-generator.git
cd floorplan-generator
pip install -r requirements.txt
```

**Hinweis:** Für die Anzeige von Vorschaufenstern wird eine grafische Umgebung benötigt. In Headless-Umgebungen (wie Codespaces) werden Vorschaubilder gespeichert, statt angezeigt.

---

## 📂 Projektstruktur

```
floorplan-generator/
├── cv_modules/              # Computer Vision Module
│   ├── image_preprocessor.py   # Entzerrung & Vorverarbeitung
│   ├── feature_detector.py     # Erkennung von Fenstern/Türen
│   └── ...
├── scripts/                 # QCAD Skripte
│   └── alpine_sennhutte_generator_improved.js # DXF Generator
├── main.py                  # Hauptprogramm
├── generate_from_image.py   # CV Pipeline Wrapper
└── README.md               # Diese Datei
```

---

## 🤝 Beitragen

Pull Requests sind willkommen! Bitte erstelle für neue Features einen eigenen Branch.

---

## 📝 Lizenz

MIT Lizenz.
