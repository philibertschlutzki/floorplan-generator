# Alpine Sennhütte Floorplan Generator

🏠 **Automatisierte Generierung von DXF-Grundrissen für Alpine Sennhütten mit QCAD**

![Version](https://img.shields.io/badge/version-2.0-blue)
![QCAD](https://img.shields.io/badge/QCAD-compatible-green)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📜 Überblick

Dieses Repository enthält Tools zur automatisierten Generierung von technischen Zeichnungen (DXF-Format) für Alpine Sennhütten. Das System verwendet QCAD als CAD-Engine und ermöglicht vollständig konfigurierbare Grundrisse durch JSON-Konfigurationsdateien.

## ✨ Features

- 📄 **Vollständige JSON-Konfiguration**: Alle 20+ Bauelemente sind konfigurierbar
- 🎨 **Detaillierte Zeichnungen**: Stützmauern, Holzbalken, Fenster, Tür, Dach und Veranda
- 📏 **Maßstab-Unterstützung**: Flexibler Maßstab (Standard 1:50)
- 🛠️ **Robuste Ausführung**: Multiple Strategien für verschiedene Systemkonfigurationen
- 📁 **DXF-Export**: Kompatibel mit allen gängigen CAD-Programmen
- 🖥️ **Headless-Operation**: Läuft ohne grafische Oberfläche

## 📝 Unterstützte Konfigurationsparameter

### Grunddimensionen
- `foundation_length` / `foundation_width`: Fundament-Abmessungen
- `stone_section_height` / `stone_wall_thickness`: Steinbereich
- `wood_section_height` / `log_diameter`: Holzbereich mit Balkenstruktur

### Öffnungen
- `door_width` / `door_height` / `door_distance_from_edge`: Tür-Konfiguration
- `wood_window_width` / `wood_window_height` / `num_wood_windows`: Fenster

### Dach
- `roof_pitch_angle`: Dachneigung in Grad
- `roof_overhang`: Dachüberstand
- `roof_material`: Material-Beschreibung

### Veranda (optional)
- `porch_width` / `porch_depth` / `porch_height`: Veranda-Dimensionen

### Optik
- `stone_finish`: Steinoberfläche (z.B. "rauer Naturstein")
- `color_description`: Farbbeschreibung

## 📦 Installation

### Voraussetzungen

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install qcad xvfb jq

# Arch Linux
sudo pacman -S qcad xorg-server-xvfb jq

# Fedora
sudo dnf install qcad xorg-x11-server-Xvfb jq
```

### Repository klonen

```bash
git clone https://github.com/philibertschlutzki/floorplan-generator.git
cd floorplan-generator
```

### Ausführungsrechte setzen

```bash
chmod +x generate_alpine_sennhuette_improved.sh
chmod +x generate_alpine_sennhuette.sh  # Für das ursprüngliche Script
```

## 🚀 Verwendung

### Schnellstart

```bash
# Mit der bereitgestellten Beispiel-Konfiguration
./generate_alpine_sennhuette_improved.sh alpenhuette_config_20251102_213551.json

# Mit eigener Ausgabedatei
./generate_alpine_sennhuette_improved.sh alpenhuette_config_20251102_213551.json meine_huette.dxf
```

### Eigene Konfiguration erstellen

```json
{
  "timestamp": "2025-11-02T21:35:51.733160",
  "building_type": "Alpine Sennhütte",
  "dimensions": {
    "foundation_length": 10.0,
    "foundation_width": 8.0,
    "stone_section_height": 2.0,
    "stone_wall_thickness": 1.2,
    "door_width": 1.8,
    "door_height": 2.0,
    "door_distance_from_edge": 0.5,
    "wood_section_height": 3.0,
    "log_diameter": 0.25,
    "wood_window_width": 1.2,
    "wood_window_height": 1.2,
    "num_wood_windows": 4,
    "roof_pitch_angle": 40.0,
    "roof_overhang": 0.8,
    "roof_material": "rotes Blech",
    "porch_width": 3.0,
    "porch_depth": 1.5,
    "porch_height": 2.5,
    "stone_finish": "rauer Naturstein",
    "color_description": "grauer Stein"
  },
  "scale": "1:50",
  "unit": "meters"
}
```

## 📁 Dateien im Repository

### Haupt-Scripts

| Datei | Beschreibung | Status |
|-------|--------------|--------|
| `generate_alpine_sennhuette_improved.sh` | **Empfohlen** - Erweiterte Version mit vollständiger JSON-Unterstützung | ✅ Aktiv |
| `generate_alpine_sennhuette.sh` | Original-Version mit Basis-Funktionalität | ℹ️ Legacy |

### JavaScript-Generatoren

| Datei | Beschreibung | Features |
|-------|--------------|----------|
| `scripts/alpine_sennhutte_generator_improved.js` | **Empfohlen** - Alle 20 JSON-Parameter | Vollständig |
| `scripts/alpine_sennhutte_generator_fixed.js` | Basis-Version mit 7 Parametern | Minimal |

### Konfiguration

| Datei | Beschreibung |
|-------|-------------|
| `alpenhuette_config_20251102_213551.json` | Beispiel-Konfiguration mit allen Parametern |

## 🛠️ Erweiterte Optionen

### Debug-Modus

```bash
# Mit detaillierter Ausgabe
DEBUG=1 ./generate_alpine_sennhuette_improved.sh config.json
```

### Manuelle QCAD-Ausführung

```bash
# Direkte Ausführung für Debugging
qcad -platform offscreen scripts/alpine_sennhutte_generator_improved.js \
     --config="alpenhuette_config_20251102_213551.json" \
     --output="output/test.dxf"
```

### Verschiedene Ausgabeformate testen

```bash
# DXF 2013 (Standard)
./generate_alpine_sennhutte_improved.sh config.json output.dxf

# Für ältere CAD-Software
./generate_alpine_sennhutte_improved.sh config.json output_2007.dxf
```

## 📊 Performance-Optimierung

### Systemanforderungen

- **RAM**: Mindestens 512 MB frei
- **CPU**: Beliebig (single-threaded)
- **Festplatte**: 50 MB frei für temporäre Dateien

### Optimierung für schwache Systeme

```bash
# Niedrigere Display-Auflösung
XVFB_ARGS="-screen 0 800x600x16" ./generate_alpine_sennhuette_improved.sh config.json

# Speicher-Monitoring
free -h && ./generate_alpine_sennhutte_improved.sh config.json
```

## 🔍 Fehlerbehebung

### Häufige Probleme

#### 1. "QCAD nicht gefunden"
```bash
# Installation prüfen
qcad --version

# PATH erweitern
export PATH=$PATH:/opt/qcad/bin
```

#### 2. "Xvfb nicht verfügbar"
```bash
# Installation
sudo apt install xvfb

# Alternative: Ohne Xvfb
QT_QPA_PLATFORM=offscreen ./generate_alpine_sennhutte_improved.sh config.json
```

#### 3. "JSON-Parsing Fehler"
```bash
# JSON validieren
jq . config.json

# Syntax prüfen
python3 -m json.tool config.json
```

#### 4. "Ausgabedatei zu klein"
```bash
# Schreibrechte prüfen
ls -la output/

# Speicherplatz prüfen
df -h

# Manueller Test
touch output/test.dxf && rm output/test.dxf
```

### Logs und Debugging

```bash
# Erweiterte Logs
DEBUG=1 VERBOSE=1 ./generate_alpine_sennhutte_improved.sh config.json 2>&1 | tee debug.log

# QCAD-Logs prüfen
ls -la /tmp/qcad* 2>/dev/null

# System-Ressourcen überwachen
while true; do free -h; sleep 5; done &
./generate_alpine_sennhutte_improved.sh config.json
kill %1
```

## 📝 Beispiel-Ausgabe

Bei erfolgreicher Ausführung erhalten Sie:

```
[INFO] ======================================================
[INFO] Alpine Sennhütte Generator v2.0
[INFO] Vollständige JSON-Konfigurationsunterstützung
[INFO] ======================================================
[✓] JSON-Konfiguration validiert
[CONFIG] Gebäudetyp: Alpine Sennhütte
[CONFIG] Maßstab: 1:50
[CONFIG] Anzahl Konfigurationsparameter: 20
[✓] ERFOLG: output/alpine_sennhuette_improved.dxf (2847 Bytes)
[✓] Alle 20 Konfigurationsparameter wurden berücksichtigt!
```

## 👥 Beitragen

### Pull Requests willkommen!

1. Fork erstellen
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

### Entwicklung

```bash
# Tests ausführen
./test_all_configs.sh

# Linter
shellcheck *.sh
jshint scripts/*.js
```

## 📈 Roadmap

- [ ] 🏢 Weitere Gebäudetypen (Almhütte, Jagdhütte)
- [ ] 💰 3D-Export (STL/OBJ)
- [ ] 🎨 Farb-Unterstützung in DXF
- [ ] 🗺️ Interaktive Web-Oberfläche
- [ ] 🔌 API-Integration
- [ ] 📱 Mobile App

## 📋 Changelog

### Version 2.0 (2025-11-02)
- ✨ Vollständige JSON-Konfigurationsunterstützung (20 Parameter)
- 🗺️ Erweiterte Zeichnungsfunktionen (Wandstärke, Balkenstruktur)
- 🛠️ Verbesserte Fehlerbehandlung und Debugging
- 📊 Performance-Optimierung
- 📁 Umfassendes README und Dokumentation

### Version 1.0 (2025-11-01)
- 🎉 Erste funktionierende Version
- 📄 Basis-DXF-Export
- 📝 7 Konfigurationsparameter
- 🛠️ QCAD-Integration

## 📜 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- [QCAD](https://qcad.org/) für die excellente CAD-Engine
- Community-Beiträge und Feedback
- Schweizer Alpin-Architektur als Inspiration

---

**🏠 Bauen Sie Ihre Traumhütte - automatisiert und präzise!**

*Für Fragen und Support: [Issues](https://github.com/philibertschlutzki/floorplan-generator/issues) erstellen*