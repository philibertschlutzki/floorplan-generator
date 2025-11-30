#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpine Sennhütte Generator
Angepasstes Script zur Generierung von Gebäudeplänen für Alphütten/Sennhütten
Basierend auf der Struktur: Steinfundament + Holzoberbau + Steildach
"""

import json
from datetime import datetime


class AlpenhuetteBuilder:
    """Builder-Klasse für Alpine Sennhütten mit Stein/Holz-Konstruktion"""
    
    def __init__(self):
        self.building_config = {}
        self.prompts = []
        
    def collect_dimensions(self):
        """
        Interaktive Abfrage aller Gebäudedimensionen
        """
        print("=" * 70)
        print("ALPINE SENNHÜTTE - DIMENSIONEN ERFASSUNG")
        print("=" * 70)
        print("\nBitte geben Sie die Masse in Metern ein (Dezimaltrennzeichen: Punkt)\n")
        
        # GRUNDFLÄCHE
        print("--- GRUNDFLÄCHE ---")
        self.building_config['foundation_length'] = float(
            input("Länge des Steinfundaments (m): ")
        )
        self.building_config['foundation_width'] = float(
            input("Breite des Steinfundaments (m): ")
        )
        
        # STEINTEIL (Erdgeschoss)
        print("\n--- STEINTEIL (Fundament und Erdgeschoss) ---")
        self.building_config['stone_section_height'] = float(
            input("Höhe des Steinteils vom Boden bis Holzübergang (m): ")
        )
        self.building_config['stone_wall_thickness'] = float(
            input("Dicke der Steinmauern (m): ")
        )
        
        # TÜRE UNTEN
        print("\n--- HAUPTTÜRE (Steinbereich) ---")
        self.building_config['door_width'] = float(
            input("Breite der Türe (m): ")
        )
        self.building_config['door_height'] = float(
            input("Höhe der Türe (m): ")
        )
        self.building_config['door_distance_from_edge'] = float(
            input("Abstand der Türe von der Kante (m): ")
        )
        
        # HOLZBEREICH (Obergeschoss)
        print("\n--- HOLZBEREICH (Blockbauweise) ---")
        self.building_config['wood_section_height'] = float(
            input("Höhe des Holzbereichs (m): ")
        )
        self.building_config['log_diameter'] = float(
            input("Durchmesser der Blockbauholzstämme (m): ")
        )
        
        # FENSTER IM HOLZBEREICH
        print("\n--- FENSTER IM HOLZBEREICH ---")
        self.building_config['wood_window_width'] = float(
            input("Breite der oberen Fenster (m): ")
        )
        self.building_config['wood_window_height'] = float(
            input("Höhe der oberen Fenster (m): ")
        )
        num_windows = int(input("Anzahl der Fenster im Holzbereich: "))
        self.building_config['num_wood_windows'] = num_windows
        
        # DACH
        print("\n--- STEILDACH ---")
        self.building_config['roof_pitch_angle'] = float(
            input("Dachneigung in Grad (typisch 35-45°): ")
        )
        self.building_config['roof_overhang'] = float(
            input("Dachüberstand an der Vorderseite (m): ")
        )
        self.building_config['roof_material'] = input(
            "Dacheindeckung (z.B. 'rotes Blech', 'Schiefer', 'Holzschindeln'): "
        )
        
        # VORBAU / UNTERSTAND
        print("\n--- VORBAU / UNTERSTAND (optional) ---")
        has_porch = input("Gibt es einen Vorbau/Unterstand? (j/n): ").lower() == 'j'
        if has_porch:
            self.building_config['porch_width'] = float(
                input("Breite des Vorbaus (m): ")
            )
            self.building_config['porch_depth'] = float(
                input("Tiefe des Vorbaus (m): ")
            )
            self.building_config['porch_height'] = float(
                input("Höhe des Vorbaus (m): ")
            )
        else:
            self.building_config['porch_width'] = 0
            self.building_config['porch_depth'] = 0
            self.building_config['porch_height'] = 0
            
        # BESONDERHEITEN
        print("\n--- BESONDERHEITEN ---")
        self.building_config['stone_finish'] = input(
            "Oberflächenfinish des Steins (z.B. 'rauer Naturstein', 'Mörtelstruktur'): "
        )
        self.building_config['color_description'] = input(
            "Farbliche Beschreibung (z.B. 'graubrauner Stein, dunkelbraunes Holz'): "
        )
        
        print("\n✓ Alle Dimensionen erfasst!\n")
        
    def generate_cad_prompt(self):
        """
        Generiert einen detaillierten Prompt für CAD-Generierung
        """
        config = self.building_config
        
        prompt = f"""
Generiere eine technische 3D-Zeichnung einer Alpinen Sennhütte mit folgenden Spezifikationen:

GRUNDFORM:
- Grundfläche: {config['foundation_length']:.2f}m (Länge) × {config['foundation_width']:.2f}m (Breite)

STEINTEIL (Fundament & Erdgeschoss):
- Höhe: {config['stone_section_height']:.2f}m
- Mauerstärke: {config['stone_wall_thickness']:.2f}m
- Material: Naturstein
- Oberflächenfinish: {config['stone_finish']}
- Farbe: {config['color_description']}

HAUPTEINGANG (Türe unten):
- Breite: {config['door_width']:.2f}m
- Höhe: {config['door_height']:.2f}m
- Position: {config['door_distance_from_edge']:.2f}m von der Kante
- Material: Dunkelbraunes Holz mit Metallbeschlag

HOLZBEREICH (Blockbauweise):
- Höhe: {config['wood_section_height']:.2f}m
- Stammdurchmesser: {config['log_diameter']:.2f}m
- Konstruktion: Handwerklich gefügte Blockbauweise
- Farbe: Dunkelbraun bis anthrazit

FENSTER IM HOLZBEREICH:
- Anzahl: {config['num_wood_windows']}
- Grösse pro Fenster: {config['wood_window_width']:.2f}m (B) × {config['wood_window_height']:.2f}m (H)
- Stil: Kleine, rustikale Fenster

DACH:
- Neigung: {config['roof_pitch_angle']:.1f}°
- Überstand: {config['roof_overhang']:.2f}m
- Material: {config['roof_material']}
- Stil: Typisches Alpensteildach

VORBAU:
- Status: {'Vorhanden' if config['porch_width'] > 0 else 'Nicht vorhanden'}
{f"- Dimensionen: {config['porch_width']:.2f}m (B) × {config['porch_depth']:.2f}m (T) × {config['porch_height']:.2f}m (H)" if config['porch_width'] > 0 else ""}

ZUSÄTZLICHE DETAILS:
- Gesamthöhe (inkl. Dach): {config['stone_section_height'] + config['wood_section_height'] + (config['foundation_length']/2 * (config['roof_pitch_angle']**0.5/10)):.2f}m (ungefähr)
- Baustil: Alpine Sennhütte mit traditioneller Steinmeisselarbeit und Blockbauweise
- Perspektive: Isometrische 3D-Ansicht + Grundriss 1:50
"""
        return prompt.strip()
    
    def generate_qcad_script_prompt(self):
        """
        Generiert einen Prompt für QCad-Script-Erstellung
        """
        config = self.building_config
        
        prompt = f"""
Generiere ein QCad JavaScript-Script, das folgende Alpine Sennhütte zeichnet (Massstab 1:50):

DIMENSIONEN (in mm für QCad, Massstab 1:50):
- Grundfläche: {config['foundation_length']*1000/50:.1f}mm × {config['foundation_width']*1000/50:.1f}mm
- Steinbereich Höhe: {config['stone_section_height']*1000/50:.1f}mm
- Holzbereich Höhe: {config['wood_section_height']*1000/50:.1f}mm
- Türe: {config['door_width']*1000/50:.1f}mm (B) × {config['door_height']*1000/50:.1f}mm (H)
- Dachwinkel: {config['roof_pitch_angle']:.1f}°

GEFORDERTE ZEICHNUNGSELEMENTE:
1. Grundriss: Steinbereich (rechteck), Türenöffnung, Fensterposition
2. Schnitt: Steinbereich, Holzbereich, Dachform (Satteldach)
3. Vorderansicht: Komplette Fassade mit allen Details
4. Isometrische 3D-Darstellung (soweit möglich)

Material-Schraffuren:
- Stein: Diagonal-Muster
- Holz: Vertikale Linien mit Blockstruktur
- Dach: Ziegelmuster

Das Script sollte Layer verwenden und parametrisiert sein für einfache Anpassungen.
"""
        return prompt.strip()
    
    def generate_dxf_output_config(self):
        """
        Generiert Konfiguration für DXF-Export
        """
        return {
            "version": "R2010",
            "units": "METRIC",
            "scale": 1/50,  # 1:50
            "layers": {
                "Fundament": {"color": "8", "linetype": "CONTINUOUS"},
                "Stein": {"color": "7", "linetype": "CONTINUOUS"},
                "Holz": {"color": "5", "linetype": "CONTINUOUS"},
                "Dach": {"color": "1", "linetype": "CONTINUOUS"},
                "Fenster": {"color": "3", "linetype": "DASHED"},
                "Türen": {"color": "2", "linetype": "CONTINUOUS"},
                "Masslinien": {"color": "9", "linetype": "CONTINUOUS"},
            }
        }
    
    def save_configuration(self, filename=None):
        """
        Speichert die Gebäudekonfiguration als JSON
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alpenhuette_config_{timestamp}.json"
        
        config_data = {
            "timestamp": datetime.now().isoformat(),
            "building_type": "Alpine Sennhütte",
            "dimensions": self.building_config,
            "scale": "1:50",
            "unit": "meters"
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Konfiguration gespeichert: {filename}")
        return filename
    
    def generate_full_report(self):
        """
        Generiert einen kompletten Bericht mit allen Prompts
        """
        print("\n" + "=" * 70)
        print("GENERIERTE PROMPTS FÜR CAD-ERSTELLUNG")
        print("=" * 70)
        
        print("\n--- PROMPT 1: CAD-GENERIERUNG (z.B. für Midjourney, DALL-E) ---\n")
        cad_prompt = self.generate_cad_prompt()
        print(cad_prompt)
        
        print("\n\n--- PROMPT 2: QCAD-SCRIPT-ERSTELLUNG ---\n")
        qcad_prompt = self.generate_qcad_script_prompt()
        print(qcad_prompt)
        
        print("\n\n--- KONFIGURATION FÜR DXF-EXPORT ---\n")
        dxf_config = self.generate_dxf_output_config()
        print(json.dumps(dxf_config, indent=2))
        
        # Speichern
        self.save_configuration()
        
        print("\n" + "=" * 70)
        print("✓ Alle Prompts wurden generiert und sind einsatzbereit!")
        print("=" * 70)


def main():
    """Hauptprogramm"""
    builder = AlpenhuetteBuilder()
    
    try:
        builder.collect_dimensions()
        builder.generate_full_report()
    except KeyboardInterrupt:
        print("\n\n✗ Abgebrochen durch Benutzer")
    except ValueError as e:
        print(f"\n✗ Fehler bei der Eingabe: {e}")
        print("Bitte nur Zahlen eingeben (Dezimaltrennzeichen: Punkt)")
    except Exception as e:
        print(f"\n✗ Fehler: {e}")


if __name__ == "__main__":
    main()
