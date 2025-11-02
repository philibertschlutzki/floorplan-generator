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
        try:
            self.doc = ezdxf.new(dxf_version)
            self.msp = self.doc.modelspace()
            print(f"Neues DXF-Dokument erstellt (Version: {dxf_version})")
        except Exception as e:
            print(f"Fehler beim Erstellen des DXF-Dokuments: {e}")
            raise
        
    def create_layers(self, layers_info: Dict[str, Dict]) -> None:
        """Erstellt die Layer basierend auf den strukturierten Daten"""
        try:
            for layer_name, layer_data in layers_info.items():
                if layer_name not in self.layers_created and layer_name != '0':  # Standard-Layer bereits vorhanden
                    try:
                        layer = self.doc.layers.new(
                            name=layer_name,
                            dxfattribs={
                                'color': layer_data.get('color', 7),
                                'linetype': layer_data.get('linetype', 'CONTINUOUS')
                            }
                        )
                        self.layers_created.add(layer_name)
                        print(f"Layer erstellt: {layer_name} (Farbe: {layer_data.get('color', 7)})")
                    except Exception as e:
                        print(f"Warnung: Konnte Layer '{layer_name}' nicht erstellen: {e}")
        except Exception as e:
            print(f"Fehler beim Erstellen der Layer: {e}")
    
    def reconstruct_from_structured_data(self, structured_data: Dict[str, Any]) -> bool:
        """Rekonstruiert DXF aus strukturierten Daten"""
        try:
            # Validiere Eingabedaten
            if not isinstance(structured_data, dict):
                print("Fehler: Strukturierte Daten müssen ein Dictionary sein")
                return False
            
            # Erstelle neues Dokument
            dxf_version = structured_data.get('metadata', {}).get('dxf_version', 'R2010')
            self.create_new_document(dxf_version)
            
            # Erstelle Layer
            if 'layers' in structured_data:
                print(f"Erstelle {len(structured_data['layers'])} Layer...")
                self.create_layers(structured_data['layers'])
            
            # Rekonstruiere Entities
            if 'entities' in structured_data:
                entities = structured_data['entities']
                print(f"Rekonstruiere {len(entities)} Entities...")
                
                success_count = 0
                for i, entity_data in enumerate(entities):
                    try:
                        self.create_entity_from_data(entity_data)
                        success_count += 1
                    except Exception as e:
                        print(f"Warnung: Entity {i+1} konnte nicht erstellt werden: {e}")
                        continue
                
                print(f"Erfolgreich {success_count} von {len(entities)} Entities erstellt")
            else:
                print("Warnung: Keine Entities in den strukturierten Daten gefunden")
            
            return True
            
        except Exception as e:
            print(f"Fehler bei der Rekonstruktion: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    def create_entity_from_data(self, entity_data: Dict[str, Any]) -> None:
        """Erstellt ein Entity basierend auf den strukturierten Daten"""
        entity_type = entity_data.get('type')
        if not entity_type:
            raise ValueError("Entity-Typ fehlt")
            
        layer = entity_data.get('layer', '0')
        color = entity_data.get('color', 'bylayer')
        
        # Grundlegende DXF-Attribute
        dxf_attribs = {'layer': layer}
        if color != 'bylayer' and isinstance(color, (int, str)):
            try:
                dxf_attribs['color'] = int(color) if isinstance(color, str) and color.isdigit() else color
            except:
                pass  # Verwende bylayer falls Konvertierung fehlschlägt
        
        if entity_type == 'LINE':
            start_point = entity_data.get('start_point')
            end_point = entity_data.get('end_point')
            
            if not start_point or not end_point:
                raise ValueError("Start- oder Endpunkt für Linie fehlt")
            
            # Stelle sicher, dass wir 3D-Punkte haben
            if len(start_point) == 2:
                start_point = list(start_point) + [0.0]
            if len(end_point) == 2:
                end_point = list(end_point) + [0.0]
            
            self.msp.add_line(
                start=start_point,
                end=end_point,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'CIRCLE':
            center = entity_data.get('center')
            radius = entity_data.get('radius')
            
            if not center or radius is None:
                raise ValueError("Zentrum oder Radius für Kreis fehlt")
            
            # Stelle sicher, dass wir einen 3D-Punkt haben
            if len(center) == 2:
                center = list(center) + [0.0]
            
            if radius <= 0:
                raise ValueError(f"Ungültiger Radius: {radius}")
            
            self.msp.add_circle(
                center=center,
                radius=radius,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'ARC':
            center = entity_data.get('center')
            radius = entity_data.get('radius')
            start_angle = entity_data.get('start_angle', 0)
            end_angle = entity_data.get('end_angle', 360)
            
            if not center or radius is None:
                raise ValueError("Zentrum oder Radius für Bogen fehlt")
            
            # Stelle sicher, dass wir einen 3D-Punkt haben
            if len(center) == 2:
                center = list(center) + [0.0]
            
            if radius <= 0:
                raise ValueError(f"Ungültiger Radius: {radius}")
            
            self.msp.add_arc(
                center=center,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                dxfattribs=dxf_attribs
            )
            
        elif entity_type == 'LWPOLYLINE':
            points = entity_data.get('points')
            is_closed = entity_data.get('is_closed', False)
            
            if not points or len(points) < 2:
                raise ValueError("Nicht genügend Punkte für Polylinie")
            
            # Konvertiere zu 2D-Punkten für LWPOLYLINE
            points_2d = []
            for point in points:
                if isinstance(point, (list, tuple)) and len(point) >= 2:
                    points_2d.append((point[0], point[1]))
                else:
                    raise ValueError(f"Ungültiger Punkt: {point}")
            
            polyline = self.msp.add_lwpolyline(
                points=points_2d,
                dxfattribs=dxf_attribs
            )
            if is_closed:
                polyline.close()
                
        elif entity_type == 'POLYLINE':
            vertices = entity_data.get('vertices', entity_data.get('points', []))
            is_closed = entity_data.get('is_closed', False)
            
            if not vertices or len(vertices) < 2:
                raise ValueError("Nicht genügend Vertices für Polylinie")
            
            # Stelle sicher, dass wir 3D-Punkte haben
            vertices_3d = []
            for vertex in vertices:
                if isinstance(vertex, (list, tuple)):
                    if len(vertex) == 2:
                        vertices_3d.append(list(vertex) + [0.0])
                    elif len(vertex) >= 3:
                        vertices_3d.append(vertex[:3])
                    else:
                        raise ValueError(f"Ungültiger Vertex: {vertex}")
                else:
                    raise ValueError(f"Ungültiger Vertex: {vertex}")
            
            polyline = self.msp.add_polyline3d(
                points=vertices_3d,
                dxfattribs=dxf_attribs
            )
            if is_closed:
                polyline.close()
                
        elif entity_type == 'TEXT':
            text_content = entity_data.get('text', '')
            position = entity_data.get('position')
            height = entity_data.get('height', 1.0)
            rotation = entity_data.get('rotation', 0)
            
            if not text_content or not position:
                raise ValueError("Text-Inhalt oder Position fehlt")
            
            # Stelle sicher, dass wir einen 3D-Punkt haben
            if len(position) == 2:
                position = list(position) + [0.0]
            
            text_attribs = dxf_attribs.copy()
            text_attribs.update({
                'height': max(height, 0.1),  # Mindestgröße
                'rotation': rotation
            })
            
            text_entity = self.msp.add_text(
                text=str(text_content),
                dxfattribs=text_attribs
            )
            text_entity.set_pos(position)
            
        elif entity_type == 'MTEXT':
            text_content = entity_data.get('text', '')
            position = entity_data.get('position')
            char_height = entity_data.get('char_height', 1.0)
            
            if not text_content or not position:
                raise ValueError("Text-Inhalt oder Position fehlt")
            
            # Stelle sicher, dass wir einen 3D-Punkt haben
            if len(position) == 2:
                position = list(position) + [0.0]
            
            text_attribs = dxf_attribs.copy()
            text_attribs.update({
                'char_height': max(char_height, 0.1),  # Mindestgröße
                'insert': position
            })
            
            self.msp.add_mtext(
                text=str(text_content),
                dxfattribs=text_attribs
            )
        else:
            print(f"Warnung: Unbekannter Entity-Typ '{entity_type}' wird übersprungen")
    
    def parse_natural_language(self, description: str) -> Dict[str, Any]:
        """Parst natürlichsprachige Beschreibung und extrahiert geometrische Informationen"""
        # Dies ist eine vereinfachte Implementierung
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
                    try:
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
                    except (ValueError, IndexError) as e:
                        print(f"Warnung: Konnte Linie nicht parsen: {line} - Fehler: {e}")
            
            # Parse Kreise
            elif current_section and 'kreise' in current_section:
                coord_pattern = r'Mittelpunkt \(([^)]+)\), Radius: ([\d.]+)'
                match = re.search(coord_pattern, line)
                if match:
                    try:
                        center_coords = [float(x.strip()) for x in match.group(1).split(',')]
                        radius = float(match.group(2))
                        
                        if len(center_coords) == 2:
                            center_coords.append(0.0)
                        
                        if radius > 0:
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
                    except (ValueError, IndexError) as e:
                        print(f"Warnung: Konnte Kreis nicht parsen: {line} - Fehler: {e}")
            
            # Parse Bögen
            elif current_section and ('bogen' in current_section or 'kreisbogen' in current_section):
                coord_pattern = r'Mittelpunkt \(([^)]+)\), Radius: ([\d.]+), von ([\d.]+)° bis ([\d.]+)°'
                match = re.search(coord_pattern, line)
                if match:
                    try:
                        center_coords = [float(x.strip()) for x in match.group(1).split(',')]
                        radius = float(match.group(2))
                        start_angle = float(match.group(3))
                        end_angle = float(match.group(4))
                        
                        if len(center_coords) == 2:
                            center_coords.append(0.0)
                        
                        if radius > 0:
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
                    except (ValueError, IndexError) as e:
                        print(f"Warnung: Konnte Bogen nicht parsen: {line} - Fehler: {e}")
            
            # Parse Text
            elif current_section and 'text' in current_section:
                text_pattern = r"Text \d+: '([^']+)' an Position \(([^)]+)\)"
                match = re.search(text_pattern, line)
                if match:
                    try:
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
                    except (ValueError, IndexError) as e:
                        print(f"Warnung: Konnte Text nicht parsen: {line} - Fehler: {e}")
        
        return extracted_data
    
    def save_dxf(self, filename: str) -> bool:
        """Speichert das DXF-Dokument"""
        try:
            if not self.doc:
                print("Fehler: Kein DXF-Dokument zum Speichern vorhanden")
                return False
            
            # Erstelle Verzeichnis falls nicht vorhanden
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            self.doc.saveas(filename)
            print(f"DXF-Datei erfolgreich gespeichert: {filename}")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python text_to_dxf.py <structured_data.json> [output.dxf]")
        print("  python text_to_dxf.py <description.txt> [output.dxf]")
        print("")
        print("Beispiele:")
        print("  python text_to_dxf.py data.json output.dxf")
        print("  python text_to_dxf.py description.txt reconstructed.dxf")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "reconstructed.dxf"
    
    if not os.path.exists(input_file):
        print(f"Fehler: Datei '{input_file}' nicht gefunden")
        sys.exit(1)
    
    print(f"Starte Konvertierung: {input_file} -> {output_file}")
    
    converter = TextToDXFConverter()
    
    # Bestimme den Dateityp
    if input_file.endswith('.json'):
        # Lade strukturierte Daten
        try:
            print("Lade strukturierte JSON-Daten...")
            with open(input_file, 'r', encoding='utf-8') as f:
                structured_data = json.load(f)
            
            print(f"JSON-Daten geladen: {len(structured_data.get('entities', []))} Entities")
            
            if converter.reconstruct_from_structured_data(structured_data):
                if converter.save_dxf(output_file):
                    print(f"\n✅ DXF-Datei erfolgreich rekonstruiert: {output_file}")
                    sys.exit(0)
                else:
                    print("\n❌ Fehler beim Speichern der DXF-Datei")
                    sys.exit(1)
            else:
                print("\n❌ Fehler bei der Rekonstruktion aus strukturierten Daten")
                sys.exit(1)
                
        except json.JSONDecodeError as e:
            print(f"Fehler beim Lesen der JSON-Datei: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unerwarteter Fehler bei JSON-Verarbeitung: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
    
    elif input_file.endswith('.txt'):
        # Lade natürlichsprachige Beschreibung
        try:
            print("Lade natürlichsprachige Beschreibung...")
            with open(input_file, 'r', encoding='utf-8') as f:
                description = f.read()
            
            print(f"Beschreibung geladen: {len(description)} Zeichen")
            
            # Parse die Beschreibung
            print("Parse natürlichsprachige Beschreibung...")
            structured_data = converter.parse_natural_language(description)
            
            print(f"Extrahiert: {len(structured_data.get('entities', []))} Entities")
            
            if converter.reconstruct_from_structured_data(structured_data):
                if converter.save_dxf(output_file):
                    print(f"\n✅ DXF-Datei aus natürlichsprachiger Beschreibung erstellt: {output_file}")
                    
                    # Speichere auch die extrahierten strukturierten Daten
                    json_output = output_file.replace('.dxf', '_extracted.json')
                    try:
                        with open(json_output, 'w', encoding='utf-8') as f:
                            json.dump(structured_data, f, indent=2, ensure_ascii=False)
                        print(f"Extrahierte Daten gespeichert in: {json_output}")
                    except Exception as e:
                        print(f"Warnung: Konnte extrahierte Daten nicht speichern: {e}")
                    
                    sys.exit(0)
                else:
                    print("\n❌ Fehler beim Speichern der DXF-Datei")
                    sys.exit(1)
            else:
                print("\n❌ Fehler bei der Rekonstruktion aus natürlichsprachiger Beschreibung")
                sys.exit(1)
                
        except Exception as e:
            print(f"Fehler beim Lesen der Textdatei: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
    
    else:
        print("Fehler: Unbekannter Dateityp. Unterstützt werden .json und .txt Dateien")
        print(f"Eingabedatei: {input_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()