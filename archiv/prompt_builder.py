#!/usr/bin/env python3
"""
Interaktives Prompt-System zur Gebäudeerstellung
"""
import json
import subprocess
import os
from datetime import datetime

CONFIG_FILE = "/home/user/floorplan-generator/config/building_presets.json"
SCRIPT_PATH = "/home/user/floorplan-generator/scripts/generate_building.sh"

def load_presets():
    """Laden Sie voreingestellte Gebäudetypen"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def display_menu():
    """Zeigen Sie das Hauptmenü an"""
    print("\n" + "="*50)
    print("QCAD Gebäude-Generator")
    print("="*50)
    print("\n1. Vordefinierte Gebäudetypen verwenden")
    print("2. Benutzerdefinierte Parameter eingeben")
    print("3. Mehrere Gebäude im Batch generieren")
    print("4. Beenden")
    print()

def show_presets(presets):
    """Zeigen Sie verfügbare Voreinstellungen an"""
    print("\nVerfügbare Gebäudetypen:")
    print("-" * 50)
    for i, (key, value) in enumerate(presets.items(), 1):
        print(f"{i}. {key.upper()}")
        print(f"   {value['description']}")
        print(f"   Größe: {value['width']/1000:.1f}m x {value['depth']/1000:.1f}m")
        print(f"   Geschosse: {value['floors']}")
        print()

def custom_input():
    """Benutzerdefinierte Parameter abfragen"""
    print("\nBenutzerdefinierte Gebäudeparameter:")
    print("-" * 50)
    
    width = float(input("Breite (in Metern) [10]: ") or "10") * 1000
    depth = float(input("Tiefe (in Metern) [8]: ") or "8") * 1000
    floors = int(input("Anzahl der Geschosse [2]: ") or "2")
    
    return {
        "width": int(width),
        "depth": int(depth),
        "floors": floors
    }

def generate_building(params):
    """Generiert ein Gebäude mit den gegebenen Parametern"""
    cmd = [
        SCRIPT_PATH,
        f"--width={params['width']}",
        f"--depth={params['depth']}",
        f"--floors={params['floors']}"
    ]
    
    print("\n⏳ Generiere Gebäude...")
    try:
        subprocess.run(cmd, check=True)
        print("✓ Gebäude erfolgreich erstellt!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Fehler beim Erstellen: {e}")

def batch_generation():
    """Batch-Generierung mehrerer Gebäude"""
    print("\nBatch-Generierung:")
    print("-" * 50)
    count = int(input("Wie viele Gebäude sollen generiert werden? [3]: ") or "3")
    
    for i in range(count):
        print(f"\n--- Gebäude {i+1}/{count} ---")
        params = custom_input()
        generate_building(params)

def main():
    """Hauptfunktion"""
    presets = load_presets()
    
    while True:
        display_menu()
        choice = input("Wählen Sie eine Option (1-4): ").strip()
        
        if choice == "1":
            show_presets(presets)
            preset_choice = input("Wählen Sie einen Gebäudetyp (Name): ").strip().lower()
            
            if preset_choice in presets:
                params = presets[preset_choice]
                generate_building(params)
            else:
                print("Ungültige Auswahl!")
                
        elif choice == "2":
            params = custom_input()
            generate_building(params)
            
        elif choice == "3":
            batch_generation()
            
        elif choice == "4":
            print("\nAuf Wiedersehen!")
            break
            
        else:
            print("Ungültige Auswahl!")

if __name__ == "__main__":
    main()
