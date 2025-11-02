#!/usr/bin/env python3
"""
Erweitertes Prompt-System zur 3D-Gebäudeerstellung (Isometrische Darstellung)
Erstellt komplette Gebäude mit vier Wänden, Dach und Boden
"""
import json
import subprocess
import os
from datetime import datetime

CONFIG_FILE = "/home/user/floorplan-generator/config/building_presets_3d.json"
SCRIPT_PATH = "/home/user/floorplan-generator/scripts/generate_building_3d.sh"

def load_presets():
    """Laden Sie voreingestellte 3D-Gebäudetypen"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def display_menu():
    """Zeigen Sie das erweiterte 3D-Hauptmenü an"""
    print("\n" + "="*60)
    print("QCAD 3D-Gebäude-Generator (Isometrische Darstellung)")
    print("="*60)
    print("\n1. Vordefinierte 3D-Gebäudetypen verwenden")
    print("2. Benutzerdefinierte 3D-Parameter eingeben")
    print("3. Mehrere 3D-Gebäude im Batch generieren")
    print("4. Erweiterte 3D-Konfiguration")
    print("5. Beenden")
    print()

def show_presets(presets):
    """Zeigen Sie verfügbare 3D-Voreinstellungen an"""
    print("\nVerfügbare 3D-Gebäudetypen:")
    print("-" * 60)
    for i, (key, value) in enumerate(presets.items(), 1):
        print(f"{i}. {key.upper()}")
        print(f"   {value['description']}")
        print(f"   Größe: {value['width']/1000:.1f}m x {value['depth']/1000:.1f}m")
        print(f"   Geschosse: {value['floors']}")
        print(f"   Wandhöhe: {value['wall_height']/1000:.1f}m")
        print(f"   Dachtyp: {value['roof_type']}")
        print()

def custom_3d_input():
    """Erweiterte benutzerdefinierte 3D-Parameter abfragen"""
    print("\nBenutzerdefinierte 3D-Gebäudeparameter:")
    print("-" * 60)
    
    # Grundparameter
    width = float(input("Breite (in Metern) [10]: ") or "10") * 1000
    depth = float(input("Tiefe (in Metern) [8]: ") or "8") * 1000
    floors = int(input("Anzahl der Geschosse [2]: ") or "2")
    
    # 3D-spezifische Parameter
    wall_height = float(input("Wandhöhe pro Geschoss (in Metern) [3.0]: ") or "3.0") * 1000
    
    print("\nDachtypen:")
    print("1. Flachdach")
    print("2. Satteldach")
    print("3. Walmdach")
    print("4. Pultdach")
    roof_choice = input("Dachtyp wählen [1]: ") or "1"
    
    roof_types = {
        "1": "flat",
        "2": "gable", 
        "3": "hip",
        "4": "shed"
    }
    roof_type = roof_types.get(roof_choice, "flat")
    
    roof_height = 0
    if roof_type != "flat":
        roof_height = float(input("Dachhöhe (in Metern) [2.5]: ") or "2.5") * 1000
    
    # Fenster und Türen
    window_count = int(input("Anzahl Fenster pro Wand [2]: ") or "2")
    door_count = int(input("Anzahl Türen [1]: ") or "1")
    
    # Materialien und Farben
    wall_color = input("Wandfarbe (RGB hex, z.B. #FF0000) [#CCCCCC]: ") or "#CCCCCC"
    roof_color = input("Dachfarbe (RGB hex) [#AA0000]: ") or "#AA0000"
    
    return {
        "width": int(width),
        "depth": int(depth),
        "floors": floors,
        "wall_height": int(wall_height),
        "roof_type": roof_type,
        "roof_height": int(roof_height),
        "window_count": window_count,
        "door_count": door_count,
        "wall_color": wall_color,
        "roof_color": roof_color,
        "foundation_height": 500  # 0.5m Standard-Fundamenthöhe
    }

def advanced_3d_config():
    """Erweiterte 3D-Konfigurationsoptionen"""
    print("\nErweiterte 3D-Konfiguration:")
    print("-" * 60)
    
    # Isometrische Projektionseinstellungen
    iso_angle = float(input("Isometrischer Winkel (Grad) [30]: ") or "30")
    view_scale = float(input("Darstellungsmaßstab [1.0]: ") or "1.0")
    
    # Detailgrad
    print("\nDetailgrad:")
    print("1. Einfach (nur Grundformen)")
    print("2. Standard (mit Fenstern und Türen)")
    print("3. Detailliert (mit Texturen und Schatten)")
    detail_level = input("Detailgrad wählen [2]: ") or "2"
    
    # Ausgabeformat
    print("\nAusgabeformat:")
    print("1. DXF")
    print("2. SVG") 
    print("3. PDF")
    output_format = input("Format wählen [1]: ") or "1"
    
    return {
        "iso_angle": iso_angle,
        "view_scale": view_scale,
        "detail_level": int(detail_level),
        "output_format": int(output_format)
    }

def generate_3d_building(params, config=None):
    """Generiert ein 3D-Gebäude mit den gegebenen Parametern"""
    cmd = [
        SCRIPT_PATH,
        f"--width={params['width']}",
        f"--depth={params['depth']}",
        f"--floors={params['floors']}",
        f"--wall-height={params.get('wall_height', 3000)}",
        f"--roof-type={params.get('roof_type', 'flat')}",
        f"--roof-height={params.get('roof_height', 0)}",
        f"--window-count={params.get('window_count', 2)}",
        f"--door-count={params.get('door_count', 1)}",
        f"--wall-color={params.get('wall_color', '#CCCCCC')}",
        f"--roof-color={params.get('roof_color', '#AA0000')}",
        f"--foundation-height={params.get('foundation_height', 500)}"
    ]
    
    # Erweiterte Konfiguration hinzufügen
    if config:
        cmd.extend([
            f"--iso-angle={config['iso_angle']}",
            f"--view-scale={config['view_scale']}",
            f"--detail-level={config['detail_level']}",
            f"--output-format={config['output_format']}"
        ])
    
    print("\n⏳ Generiere 3D-Gebäude...")
    try:
        subprocess.run(cmd, check=True)
        print("✓ 3D-Gebäude erfolgreich erstellt!")
        print("  - Alle vier Wände gezeichnet")
        print("  - Dachkonstruktion hinzugefügt")
        print("  - Fundament/Boden erstellt")
        print("  - Isometrische Darstellung angewendet")
    except subprocess.CalledProcessError as e:
        print(f"✗ Fehler beim Erstellen: {e}")

def batch_3d_generation():
    """Batch-Generierung mehrerer 3D-Gebäude"""
    print("\n3D-Batch-Generierung:")
    print("-" * 60)
    count = int(input("Wie viele 3D-Gebäude sollen generiert werden? [3]: ") or "3")
    
    # Gemeinsame erweiterte Konfiguration für alle Gebäude
    use_advanced = input("Erweiterte Konfiguration für alle verwenden? (j/n) [n]: ").lower() == 'j'
    config = None
    if use_advanced:
        config = advanced_3d_config()
    
    for i in range(count):
        print(f"\n--- 3D-Gebäude {i+1}/{count} ---")
        params = custom_3d_input()
        generate_3d_building(params, config)

def main():
    """Hauptfunktion"""
    try:
        presets = load_presets()
    except FileNotFoundError:
        print("⚠️  Warnung: 3D-Konfigurationsdatei nicht gefunden. Verwende Standardwerte.")
        presets = {}
    
    while True:
        display_menu()
        choice = input("Wählen Sie eine Option (1-5): ").strip()
        
        if choice == "1":
            if presets:
                show_presets(presets)
                preset_choice = input("Wählen Sie einen 3D-Gebäudetyp (Name): ").strip().lower()
                
                if preset_choice in presets:
                    params = presets[preset_choice]
                    generate_3d_building(params)
                else:
                    print("Ungültige Auswahl!")
            else:
                print("Keine Voreinstellungen verfügbar!")
                
        elif choice == "2":
            params = custom_3d_input()
            generate_3d_building(params)
            
        elif choice == "3":
            batch_3d_generation()
            
        elif choice == "4":
            config = advanced_3d_config()
            params = custom_3d_input()
            generate_3d_building(params, config)
            
        elif choice == "5":
            print("\nAuf Wiedersehen! 🏠")
            break
            
        else:
            print("Ungültige Auswahl!")

if __name__ == "__main__":
    main()