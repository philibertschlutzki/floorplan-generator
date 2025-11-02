#!/usr/bin/env python3
"""
Natürlichsprache zu DXF Konverter
Rekonstruiert DXF-Dateien aus natürlichsprachigen Beschreibungen und strukturierten Daten
"""

import sys
import os
import json
import re
import math
try:
    import ezdxf
    from ezdxf.math import Vec3
except ImportError:
    print("Fehler: ezdxf ist nicht installiert. Installieren Sie es mit: pip install ezdxf")
    sys.exit(1)

from typing import Dict, List, Tuple, Any, Optional

class TextToDXFConverter:
    def __init__(self):
        self.doc = None
        self.msp = None
        self.layers_created = set()
        
    def create_new_document(self, dxf_version: str = 'R2010') -> None:
        """Erstellt ein neues DXF-Dokument"""
        self.doc = ezdxf.new(dxf_version)
        self.msp = self.doc.modelspace()
        
    def create_layers(self, layers_info: Dict[str, Dict]) -> None:
        """Erstellt die Layer basierend auf den strukturierten Daten"""
        for layer_name, layer_data in layers_info.items():
            if layer_name not in self.layers_created:
                layer = self.doc.layers.new(
                    name=layer_name,
                    dxfattribs={
                        'color': layer_data.get('color', 7),
                        'linetype': layer_data.get('linetype', 'CONTINUOUS')
                    }
                )
                self.layers_created.add(layer_name)
    
    def reconstruct_from_structured_data(self, structured_data: Dict[str, Any]) -> bool:
        """Rekonstruiert DXF aus strukturierten Daten"""
        try:
            # Erstelle neues Dokument
            dxf_version = structured_data.get('metadata', {}).get('dxf_version', 'R2010')
            self.create_new_document(dxf_version)
            
            # Erstelle Layer
            if 'layers' in structured_data:
                self.create_layers(structured_data['layers'])
            
            # Rekonstruiere Entities
            if 'entities' in structured_data:
                for entity_data in structured_data['entities']:
                    self.create_entity_from_data(entity_data)
            
            return True
            
        except Exception as e:
            print(f"Fehler bei der Rekonstruktion: {e}")
            return False
    
    def create_entity_from_data(self, entity_data: Dict[str, Any]) -> None:
        """Erstellt ein Entity basierend auf den strukturierten Daten"""
        entity_type = entity_data.get('type')
        layer = entity_data.get('layer', '0')
        color = entity_data.get('color', 'bylayer')
        
        # Grundlegende DXF-Attribute
        dxf_attribs = {'layer': layer}
        if color != 'bylayer':
            dxf_attribs['color'] = color
        
        if entity_type == 'LINE':
            start_point = entity_data['start_point']
            end_point = entity_data['end_point']
            self.msp.add_line(
                start=start_point,
                end=end_point,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'CIRCLE':
            center = entity_data['center']
            radius = entity_data['radius']
            self.msp.add_circle(
                center=center,
                radius=radius,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'ARC':
            center = entity_data['center']
            radius = entity_data['radius']
            start_angle = entity_data['start_angle']
            end_angle = entity_data['end_angle']
            self.msp.add_arc(
                center=center,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'LWPOLYLINE':
            points = entity_data['points']
            is_closed = entity_data.get('is_closed', False)
            polyline = self.msp.add_lwpolyline(
                points=points,
                dxfattribs=dxf_attribs
            )
            if is_closed:
                polyline.close()
                
        elif entity_type == 'POLYLINE':
            vertices = entity_data['vertices']
            is_closed = entity_data.get('is_closed', False)
            polyline = self.msp.add_polyline3d(
                points=vertices,
                dxfattribs=dxf_attribs
            )
            if is_closed:
                polyline.close()
                
        elif entity_type == 'TEXT':
            text_content = entity_data['text']
            position = entity_data['position']
            height = entity_data.get('height', 1.0)
            rotation = entity_data.get('rotation', 0)
            
            text_attribs = dxf_attribs.copy()
            text_attribs.update({
                'height': height,
                'rotation': rotation
            })
            
            self.msp.add_text(
                text=text_content,
                dxfattribs=text_attribs
            ).set_pos(position)
            
        elif entity_type == 'MTEXT':
            text_content = entity_data['text']
            position = entity_data['position']
            char_height = entity_data.get('char_height', 1.0)
            
            text_attribs = dxf_attribs.copy()
            text_attribs.update({
                'char_height': char_height,
                'insert': position
            })
            
            self.msp.add_mtext(
                text=text_content,
                dxfattribs=text_attribs
            )
    
    def parse_natural_language(self, description: str) -> Dict[str, Any]:
        """Parst natürlichsprachige Beschreibung und extrahiert geometrische Informationen"""
        # Dies is eine vereinfachte Implementierung
        # In der Praxis würde man hier NLP-Techniken oder LLMs verwenden
        
        extracted_data = {
            'metadata': {'dxf_version': 'R2010', 'filename': 'reconstructed.dxf'},
            'layers': {'0': {'color': 7, 'linetype': 'CONTINUOUS'}},
            'entities': []
        }
        
        lines = description.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Erkenne Sektionen
            if line.startswith('###'):
                current_section = line.replace('#', '').strip().lower()
                continue
            
            # Parse Linien
            if current_section and 'linien' in current_section:
                # Suche nach Koordinaten-Mustern
                coord_pattern = r'Von Punkt \(([^)]+)\) zu Punkt \(([^)]+)\)'
                match = re.search(coord_pattern, line)
                if match:
                    start_coords = [float(x.strip()) for x in match.group(1).split(',')]
                    end_coords = [float(x.strip()) for x in match.group(2).split(',')]
                    
                    # Füge Z-Koordinate hinzu falls nicht vorhanden
                    if len(start_coords) == 2:
                        start_coords.append(0.0)
                    if len(end_coords) == 2:
                        end_coords.append(0.0)
                    
                    entity = {
                        'type': 'LINE',
                        'layer': '0',
                        'color': 'bylayer',
                        'start_point': start_coords,
                        'end_point': end_coords,
                        'length': math.sqrt(sum((end_coords[i] - start_coords[i])**2 for i in range(3)))
                    }
                    extracted_data['entities'].append(entity)
            
            # Parse Kreise
            elif current_section and 'kreise' in current_section:
                coord_pattern = r'Mittelpunkt \(([^)]+)\), Radius: ([\d.]+)'
                match = re.search(coord_pattern, line)
                if match:
                    center_coords = [float(x.strip()) for x in match.group(1).split(',')]
                    radius = float(match.group(2))
                    
                    if len(center_coords) == 2:
                        center_coords.append(0.0)
                    
                    entity = {
                        'type': 'CIRCLE',
                        'layer': '0',
                        'color': 'bylayer',
                        'center': center_coords,
                        'radius': radius,
                        'diameter': radius * 2,
                        'circumference': 2 * math.pi * radius,
                        'area': math.pi * radius * radius
                    }
                    extracted_data['entities'].append(entity)
            
            # Parse Bögen
            elif current_section and 'bogen' in current_section or 'kreisbogen' in current_section:
                coord_pattern = r'Mittelpunkt \(([^)]+)\), Radius: ([\d.]+), von ([\d.]+)° bis ([\d.]+)°'
                match = re.search(coord_pattern, line)
                if match:
                    center_coords = [float(x.strip()) for x in match.group(1).split(',')]
                    radius = float(match.group(2))
                    start_angle = float(match.group(3))
                    end_angle = float(match.group(4))
                    
                    if len(center_coords) == 2:
                        center_coords.append(0.0)
                    
                    entity = {
                        'type': 'ARC',
                        'layer': '0',
                        'color': 'bylayer',
                        'center': center_coords,
                        'radius': radius,
                        'start_angle': start_angle,
                        'end_angle': end_angle
                    }
                    extracted_data['entities'].append(entity)
            
            # Parse Text
            elif current_section and 'text' in current_section:
                text_pattern = r"Text \d+: '([^']+)' an Position \(([^)]+)\)"
                match = re.search(text_pattern, line)
                if match:
                    text_content = match.group(1)
                    position_coords = [float(x.strip()) for x in match.group(2).split(',')]
                    
                    if len(position_coords) == 2:
                        position_coords.append(0.0)
                    
                    entity = {
                        'type': 'TEXT',
                        'layer': '0',
                        'color': 'bylayer',
                        'text': text_content,
                        'position': position_coords,
                        'height': 1.0,
                        'rotation': 0.0
                    }
                    extracted_data['entities'].append(entity)
        
        return extracted_data
    
    def save_dxf(self, filename: str) -> bool:
        """Speichert das DXF-Dokument"""
        try:
            self.doc.saveas(filename)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python text_to_dxf.py <structured_data.json> [output.dxf]")
        print("  python text_to_dxf.py <description.txt> [output.dxf]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "reconstructed.dxf"
    
    if not os.path.exists(input_file):
        print(f"Fehler: Datei '{input_file}' nicht gefunden")
        sys.exit(1)
    
    converter = TextToDXFConverter()
    
    # Bestimme den Dateityp
    if input_file.endswith('.json'):
        # Lade strukturierte Daten
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                structured_data = json.load(f)
            
            if converter.reconstruct_from_structured_data(structured_data):
                if converter.save_dxf(output_file):
                    print(f"DXF-Datei erfolgreich rekonstruiert: {output_file}")
                else:
                    print("Fehler beim Speichern der DXF-Datei")
                    sys.exit(1)
            else:
                print("Fehler bei der Rekonstruktion aus strukturierten Daten")
                sys.exit(1)
                
        except json.JSONDecodeError as e:
            print(f"Fehler beim Lesen der JSON-Datei: {e}")
            sys.exit(1)
    
    elif input_file.endswith('.txt'):
        # Lade natürlichsprachige Beschreibung
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                description = f.read()
            
            # Parse die Beschreibung
            structured_data = converter.parse_natural_language(description)
            
            if converter.reconstruct_from_structured_data(structured_data):
                if converter.save_dxf(output_file):
                    print(f"DXF-Datei aus natürlichsprachiger Beschreibung erstellt: {output_file}")
                    
                    # Speichere auch die extrahierten strukturierten Daten
                    json_output = output_file.replace('.dxf', '_extracted.json')
                    with open(json_output, 'w', encoding='utf-8') as f:
                        json.dump(structured_data, f, indent=2, ensure_ascii=False)
                    print(f"Extrahierte Daten gespeichert in: {json_output}")
                else:
                    print("Fehler beim Speichern der DXF-Datei")
                    sys.exit(1)
            else:
                print("Fehler bei der Rekonstruktion aus natürlichsprachiger Beschreibung")
                sys.exit(1)
                
        except Exception as e:
            print(f"Fehler beim Lesen der Textdatei: {e}")
            sys.exit(1)
    
    else:
        print("Fehler: Unbekannter Dateityp. Unterstützt werden .json und .txt Dateien")
        sys.exit(1)

if __name__ == "__main__":
    main()