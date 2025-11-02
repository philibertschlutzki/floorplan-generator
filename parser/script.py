# Erstelle ein umfassendes Script-System für DXF zu Natürlichsprache und zurück
# Zuerst installieren wir die benötigten Bibliotheken

# DXF zu Natürlichsprache Konverter
import io
import re
import sys

# Script 1: DXF zu Natürlichsprache Konverter
dxf_to_text_script = '''#!/usr/bin/env python3
"""
DXF zu Natürlichsprache Konverter
Analysiert DXF-Dateien und erstellt natürlichsprachige Beschreibungen der geometrischen Elemente
"""

import sys
import os
try:
    import ezdxf
    from ezdxf import recover
    from ezdxf.math import Vec3
except ImportError:
    print("Fehler: ezdxf ist nicht installiert. Installieren Sie es mit: pip install ezdxf")
    sys.exit(1)

import json
import math
from typing import Dict, List, Tuple, Any

class DXFToTextConverter:
    def __init__(self):
        self.layers = {}
        self.entities = []
        self.metadata = {}
        self.text_description = []
        
    def load_dxf(self, filepath: str) -> bool:
        """Lädt eine DXF-Datei und verarbeitet sie"""
        try:
            # Versuche die Datei zu laden, mit Error Recovery falls nötig
            try:
                doc = ezdxf.readfile(filepath)
            except ezdxf.DXFStructureError:
                print(f"Warnung: DXF-Struktur-Fehler. Versuche Recovery...")
                doc, auditor = recover.readfile(filepath)
                if auditor.has_errors:
                    print(f"Gefundene Fehler: {len(auditor.errors)}")
                    
            self.metadata = {
                'dxf_version': doc.dxfversion,
                'filename': os.path.basename(filepath),
                'units': getattr(doc.header, 'get', lambda x, default: default)('$INSUNITS', 'unknown')
            }
            
            # Analysiere Layers
            for layer in doc.layers:
                self.layers[layer.dxf.name] = {
                    'color': layer.dxf.color,
                    'linetype': layer.dxf.linetype,
                    'lineweight': getattr(layer.dxf, 'lineweight', 'default')
                }
            
            # Analysiere Entities im Modelspace
            msp = doc.modelspace()
            for entity in msp:
                self.analyze_entity(entity)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Laden der DXF-Datei: {e}")
            return False
    
    def analyze_entity(self, entity) -> None:
        """Analysiert ein einzelnes DXF-Entity und fügt es zur Beschreibung hinzu"""
        entity_info = {
            'type': entity.dxftype(),
            'layer': entity.dxf.layer,
            'color': getattr(entity.dxf, 'color', 'bylayer'),
            'handle': entity.dxf.handle
        }
        
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = (Vec3(end) - Vec3(start)).magnitude
            
            entity_info.update({
                'start_point': (round(start.x, 3), round(start.y, 3), round(start.z, 3)),
                'end_point': (round(end.x, 3), round(end.y, 3), round(end.z, 3)),
                'length': round(length, 3)
            })
            
        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            circumference = 2 * math.pi * radius
            area = math.pi * radius * radius
            
            entity_info.update({
                'center': (round(center.x, 3), round(center.y, 3), round(center.z, 3)),
                'radius': round(radius, 3),
                'diameter': round(radius * 2, 3),
                'circumference': round(circumference, 3),
                'area': round(area, 3)
            })
            
        elif entity.dxftype() == 'ARC':
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            
            # Berechne Bogenlänge
            angle_diff = end_angle - start_angle
            if angle_diff < 0:
                angle_diff += 360
            arc_length = (angle_diff / 360) * 2 * math.pi * radius
            
            entity_info.update({
                'center': (round(center.x, 3), round(center.y, 3), round(center.z, 3)),
                'radius': round(radius, 3),
                'start_angle': round(start_angle, 3),
                'end_angle': round(end_angle, 3),
                'arc_length': round(arc_length, 3)
            })
            
        elif entity.dxftype() == 'LWPOLYLINE':
            points = []
            for point in entity.get_points():
                points.append((round(point[0], 3), round(point[1], 3)))
            
            # Berechne Gesamtlänge
            total_length = 0
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i + 1]
                length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                total_length += length
            
            entity_info.update({
                'points': points,
                'point_count': len(points),
                'is_closed': entity.closed,
                'total_length': round(total_length, 3)
            })
            
        elif entity.dxftype() == 'TEXT':
            text_content = entity.dxf.text
            insert_point = entity.dxf.insert
            height = entity.dxf.height
            rotation = getattr(entity.dxf, 'rotation', 0)
            
            entity_info.update({
                'text': text_content,
                'position': (round(insert_point.x, 3), round(insert_point.y, 3), round(insert_point.z, 3)),
                'height': round(height, 3),
                'rotation': round(rotation, 3)
            })
            
        elif entity.dxftype() == 'MTEXT':
            text_content = entity.plain_text()
            insert_point = entity.dxf.insert
            char_height = entity.dxf.char_height
            
            entity_info.update({
                'text': text_content,
                'position': (round(insert_point.x, 3), round(insert_point.y, 3), round(insert_point.z, 3)),
                'char_height': round(char_height, 3)
            })
            
        elif entity.dxftype() == 'POLYLINE':
            vertices = []
            for vertex in entity.vertices:
                point = vertex.dxf.location
                vertices.append((round(point.x, 3), round(point.y, 3), round(point.z, 3)))
            
            entity_info.update({
                'vertices': vertices,
                'vertex_count': len(vertices),
                'is_closed': entity.is_closed
            })
            
        elif entity.dxftype() == 'RECTANGLE' or entity.dxftype() == 'SOLID':
            # Für rechteckige oder gefüllte Bereiche
            if hasattr(entity.dxf, 'insert'):
                insert_point = entity.dxf.insert
                entity_info.update({
                    'position': (round(insert_point.x, 3), round(insert_point.y, 3), round(insert_point.z, 3))
                })
        
        self.entities.append(entity_info)
    
    def generate_natural_language_description(self) -> str:
        """Generiert eine natürlichsprachige Beschreibung der DXF-Datei"""
        description = []
        
        # Header-Information
        description.append(f"# Beschreibung der DXF-Datei: {self.metadata['filename']}")
        description.append(f"DXF-Version: {self.metadata['dxf_version']}")
        description.append(f"Anzahl Layers: {len(self.layers)}")
        description.append(f"Anzahl geometrische Elemente: {len(self.entities)}")
        description.append("")
        
        # Layer-Beschreibung
        if self.layers:
            description.append("## Layer-Struktur:")
            for layer_name, layer_info in self.layers.items():
                description.append(f"- Layer '{layer_name}': Farbe {layer_info['color']}, Linientyp {layer_info['linetype']}")
            description.append("")
        
        # Entitäts-Analyse
        entity_types = {}
        for entity in self.entities:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity)
        
        description.append("## Geometrische Elemente:")
        
        # Linien
        if 'LINE' in entity_types:
            lines = entity_types['LINE']
            description.append(f"### Linien ({len(lines)} Stück):")
            for i, line in enumerate(lines[:10]):  # Zeige max. 10 Linien
                start = line['start_point']
                end = line['end_point']
                length = line['length']
                description.append(f"- Linie {i+1}: Von Punkt ({start[0]}, {start[1]}) zu Punkt ({end[0]}, {end[1]}), Länge: {length} Einheiten")
            if len(lines) > 10:
                description.append(f"  ... und {len(lines) - 10} weitere Linien")
            description.append("")
        
        # Kreise
        if 'CIRCLE' in entity_types:
            circles = entity_types['CIRCLE']
            description.append(f"### Kreise ({len(circles)} Stück):")
            for i, circle in enumerate(circles):
                center = circle['center']
                radius = circle['radius']
                description.append(f"- Kreis {i+1}: Mittelpunkt ({center[0]}, {center[1]}), Radius: {radius} Einheiten")
            description.append("")
        
        # Bögen
        if 'ARC' in entity_types:
            arcs = entity_types['ARC']
            description.append(f"### Kreisbögen ({len(arcs)} Stück):")
            for i, arc in enumerate(arcs):
                center = arc['center']
                radius = arc['radius']
                start_angle = arc['start_angle']
                end_angle = arc['end_angle']
                description.append(f"- Bogen {i+1}: Mittelpunkt ({center[0]}, {center[1]}), Radius: {radius}, von {start_angle}° bis {end_angle}°")
            description.append("")
        
        # Polylinien
        if 'LWPOLYLINE' in entity_types or 'POLYLINE' in entity_types:
            polylines = entity_types.get('LWPOLYLINE', []) + entity_types.get('POLYLINE', [])
            description.append(f"### Polylinien ({len(polylines)} Stück):")
            for i, poly in enumerate(polylines):
                if 'points' in poly:
                    points = poly['points']
                    is_closed = poly.get('is_closed', False)
                    description.append(f"- Polylinie {i+1}: {len(points)} Punkte, {'geschlossen' if is_closed else 'offen'}")
                elif 'vertices' in poly:
                    vertices = poly['vertices']
                    is_closed = poly.get('is_closed', False)
                    description.append(f"- Polylinie {i+1}: {len(vertices)} Eckpunkte, {'geschlossen' if is_closed else 'offen'}")
            description.append("")
        
        # Text-Elemente
        text_entities = entity_types.get('TEXT', []) + entity_types.get('MTEXT', [])
        if text_entities:
            description.append(f"### Text-Elemente ({len(text_entities)} Stück):")
            for i, text in enumerate(text_entities):
                position = text['position']
                content = text['text']
                description.append(f"- Text {i+1}: '{content}' an Position ({position[0]}, {position[1]})")
            description.append("")
        
        # Zusammenfassung der räumlichen Ausdehnung
        if self.entities:
            x_coords = []
            y_coords = []
            
            for entity in self.entities:
                if 'start_point' in entity:
                    x_coords.extend([entity['start_point'][0], entity['end_point'][0]])
                    y_coords.extend([entity['start_point'][1], entity['end_point'][1]])
                elif 'center' in entity:
                    x_coords.append(entity['center'][0])
                    y_coords.append(entity['center'][1])
                elif 'position' in entity:
                    x_coords.append(entity['position'][0])
                    y_coords.append(entity['position'][1])
                elif 'points' in entity:
                    for point in entity['points']:
                        x_coords.append(point[0])
                        y_coords.append(point[1])
                elif 'vertices' in entity:
                    for vertex in entity['vertices']:
                        x_coords.append(vertex[0])
                        y_coords.append(vertex[1])
            
            if x_coords and y_coords:
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)
                width = max_x - min_x
                height = max_y - min_y
                
                description.append("## Räumliche Ausdehnung:")
                description.append(f"- X-Bereich: {min_x} bis {max_x} (Breite: {round(width, 3)})")
                description.append(f"- Y-Bereich: {min_y} bis {max_y} (Höhe: {round(height, 3)})")
                description.append(f"- Gesamtfläche des Bounding-Rechtecks: {round(width * height, 3)} Quadrateinheiten")
        
        return "\\n".join(description)
    
    def export_structured_data(self) -> Dict[str, Any]:
        """Exportiert die strukturierten Daten für die Rückkonvertierung"""
        return {
            'metadata': self.metadata,
            'layers': self.layers,
            'entities': self.entities,
            'natural_description': self.generate_natural_language_description()
        }

def main():
    if len(sys.argv) != 2:
        print("Verwendung: python dxf_to_text.py <dxf-datei>")
        sys.exit(1)
    
    dxf_file = sys.argv[1]
    
    if not os.path.exists(dxf_file):
        print(f"Fehler: Datei '{dxf_file}' nicht gefunden")
        sys.exit(1)
    
    converter = DXFToTextConverter()
    
    if converter.load_dxf(dxf_file):
        # Generiere natürlichsprachige Beschreibung
        description = converter.generate_natural_language_description()
        
        # Speichere Beschreibung in Textdatei
        output_file = os.path.splitext(dxf_file)[0] + "_description.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(description)
        
        print(f"Natürlichsprachige Beschreibung gespeichert in: {output_file}")
        
        # Speichere strukturierte Daten für Rückkonvertierung
        structured_file = os.path.splitext(dxf_file)[0] + "_structured.json"
        structured_data = converter.export_structured_data()
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Strukturierte Daten gespeichert in: {structured_file}")
        
        # Zeige Vorschau der Beschreibung
        print("\\n" + "="*60)
        print("VORSCHAU DER NATÜRLICHSPRACHIGEN BESCHREIBUNG:")
        print("="*60)
        print(description[:1000] + "..." if len(description) > 1000 else description)
    else:
        print("Fehler beim Verarbeiten der DXF-Datei")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

print("Script 1 (DXF zu Natürlichsprache) erstellt...")