# Script 3: Differenz-Analyse zwischen Original und Rekonstruktion
diff_analyzer_script = '''#!/usr/bin/env python3
"""
DXF Differenz-Analyse
Vergleicht Original-DXF mit rekonstruierter DXF und erstellt Differenz-Report
"""

import sys
import os
import json
import math
try:
    import ezdxf
    from ezdxf import recover
    from ezdxf.math import Vec3
except ImportError:
    print("Fehler: ezdxf ist nicht installiert. Installieren Sie es mit: pip install ezdxf")
    sys.exit(1)

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

class DXFDifferenceAnalyzer:
    def __init__(self, tolerance: float = 0.001):
        self.tolerance = tolerance
        self.original_entities = []
        self.reconstructed_entities = []
        self.differences = []
        
    def load_dxf_entities(self, filepath: str) -> List[Dict[str, Any]]:
        """Lädt alle Entities aus einer DXF-Datei"""
        entities = []
        
        try:
            try:
                doc = ezdxf.readfile(filepath)
            except ezdxf.DXFStructureError:
                doc, auditor = recover.readfile(filepath)
                if auditor.has_errors:
                    print(f"Warnung: DXF-Recovery für {filepath} mit {len(auditor.errors)} Fehlern")
            
            msp = doc.modelspace()
            for entity in msp:
                entity_data = self.extract_entity_data(entity)
                if entity_data:
                    entities.append(entity_data)
                    
        except Exception as e:
            print(f"Fehler beim Laden von {filepath}: {e}")
            
        return entities
    
    def extract_entity_data(self, entity) -> Optional[Dict[str, Any]]:
        """Extrahiert normalisierte Daten aus einem Entity"""
        entity_data = {
            'type': entity.dxftype(),
            'layer': entity.dxf.layer,
            'handle': entity.dxf.handle
        }
        
        try:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                entity_data.update({
                    'start': self.normalize_point(start),
                    'end': self.normalize_point(end),
                    'length': round((Vec3(end) - Vec3(start)).magnitude, 6)
                })
                
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                entity_data.update({
                    'center': self.normalize_point(center),
                    'radius': round(radius, 6)
                })
                
            elif entity.dxftype() == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                entity_data.update({
                    'center': self.normalize_point(center),
                    'radius': round(radius, 6),
                    'start_angle': round(start_angle, 6),
                    'end_angle': round(end_angle, 6)
                })
                
            elif entity.dxftype() == 'LWPOLYLINE':
                points = []
                for point in entity.get_points():
                    points.append(self.normalize_point_2d(point))
                entity_data.update({
                    'points': points,
                    'closed': entity.closed
                })
                
            elif entity.dxftype() == 'POLYLINE':
                vertices = []
                for vertex in entity.vertices:
                    vertices.append(self.normalize_point(vertex.dxf.location))
                entity_data.update({
                    'vertices': vertices,
                    'closed': entity.is_closed
                })
                
            elif entity.dxftype() == 'TEXT':
                entity_data.update({
                    'text': entity.dxf.text,
                    'position': self.normalize_point(entity.dxf.insert),
                    'height': round(entity.dxf.height, 6),
                    'rotation': round(getattr(entity.dxf, 'rotation', 0), 6)
                })
                
            elif entity.dxftype() == 'MTEXT':
                entity_data.update({
                    'text': entity.plain_text(),
                    'position': self.normalize_point(entity.dxf.insert),
                    'char_height': round(entity.dxf.char_height, 6)
                })
                
            else:
                # Für unbekannte Entity-Typen
                entity_data['raw_data'] = 'unknown_entity_type'
                
            return entity_data
            
        except Exception as e:
            print(f"Fehler beim Extrahieren von Entity {entity.dxftype()}: {e}")
            return None
    
    def normalize_point(self, point) -> Tuple[float, float, float]:
        """Normalisiert einen 3D-Punkt auf definierte Genauigkeit"""
        return (round(point.x, 6), round(point.y, 6), round(point.z, 6))
    
    def normalize_point_2d(self, point) -> Tuple[float, float]:
        """Normalisiert einen 2D-Punkt auf definierte Genauigkeit"""
        return (round(point[0], 6), round(point[1], 6))
    
    def compare_entities(self, original_entities: List[Dict], reconstructed_entities: List[Dict]) -> None:
        """Vergleicht zwei Listen von Entities und findet Unterschiede"""
        self.differences = []
        
        # Erstelle Index für schnellere Suche
        reconstructed_index = self.create_entity_index(reconstructed_entities)
        original_index = self.create_entity_index(original_entities)
        
        # Prüfe Original-Entities gegen Rekonstruierte
        for orig_entity in original_entities:
            matching_entities = self.find_matching_entities(orig_entity, reconstructed_entities)
            
            if not matching_entities:
                self.differences.append({
                    'type': 'missing_in_reconstructed',
                    'entity': orig_entity,
                    'description': f"Entity {orig_entity['type']} (Handle: {orig_entity['handle']}) fehlt in rekonstruierter Datei"
                })
            elif len(matching_entities) == 1:
                # Genauer Vergleich
                differences = self.compare_single_entity(orig_entity, matching_entities[0])
                if differences:
                    self.differences.extend(differences)
            else:
                self.differences.append({
                    'type': 'multiple_matches',
                    'entity': orig_entity,
                    'matches': matching_entities,
                    'description': f"Mehrere passende Entities für {orig_entity['type']} gefunden"
                })
        
        # Prüfe Rekonstruierte-Entities gegen Original (für zusätzliche Entities)
        for recon_entity in reconstructed_entities:
            matching_entities = self.find_matching_entities(recon_entity, original_entities)
            
            if not matching_entities:
                self.differences.append({
                    'type': 'additional_in_reconstructed',
                    'entity': recon_entity,
                    'description': f"Zusätzliches Entity {recon_entity['type']} in rekonstruierter Datei"
                })
    
    def create_entity_index(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """Erstellt einen Index für Entities nach Typ"""
        index = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in index:
                index[entity_type] = []
            index[entity_type].append(entity)
        return index
    
    def find_matching_entities(self, target_entity: Dict, entity_list: List[Dict]) -> List[Dict]:
        """Findet passende Entities in einer Liste"""
        matches = []
        target_type = target_entity['type']
        
        for entity in entity_list:
            if entity['type'] == target_type:
                if self.entities_match(target_entity, entity):
                    matches.append(entity)
        
        return matches
    
    def entities_match(self, entity1: Dict, entity2: Dict) -> bool:
        """Prüft ob zwei Entities als gleich betrachtet werden können"""
        if entity1['type'] != entity2['type']:
            return False
        
        entity_type = entity1['type']
        
        if entity_type == 'LINE':
            return (self.points_close(entity1['start'], entity2['start']) and 
                   self.points_close(entity1['end'], entity2['end'])) or \\
                   (self.points_close(entity1['start'], entity2['end']) and 
                   self.points_close(entity1['end'], entity2['start']))
        
        elif entity_type == 'CIRCLE':
            return (self.points_close(entity1['center'], entity2['center']) and 
                   abs(entity1['radius'] - entity2['radius']) < self.tolerance)
        
        elif entity_type == 'ARC':
            return (self.points_close(entity1['center'], entity2['center']) and 
                   abs(entity1['radius'] - entity2['radius']) < self.tolerance and
                   abs(entity1['start_angle'] - entity2['start_angle']) < self.tolerance and
                   abs(entity1['end_angle'] - entity2['end_angle']) < self.tolerance)
        
        elif entity_type in ['LWPOLYLINE', 'POLYLINE']:
            points1 = entity1.get('points', entity1.get('vertices', []))
            points2 = entity2.get('points', entity2.get('vertices', []))
            
            if len(points1) != len(points2):
                return False
            
            # Prüfe vorwärts und rückwärts
            forward_match = all(self.points_close(p1, p2) for p1, p2 in zip(points1, points2))
            backward_match = all(self.points_close(p1, p2) for p1, p2 in zip(points1, reversed(points2)))
            
            return forward_match or backward_match
        
        elif entity_type in ['TEXT', 'MTEXT']:
            return (entity1['text'] == entity2['text'] and 
                   self.points_close(entity1['position'], entity2['position']))
        
        return False
    
    def points_close(self, point1: Tuple, point2: Tuple) -> bool:
        """Prüft ob zwei Punkte innerhalb der Toleranz liegen"""
        if len(point1) != len(point2):
            # Erweitere 2D-Punkte zu 3D
            if len(point1) == 2:
                point1 = point1 + (0.0,)
            if len(point2) == 2:
                point2 = point2 + (0.0,)
        
        return all(abs(p1 - p2) < self.tolerance for p1, p2 in zip(point1, point2))
    
    def compare_single_entity(self, orig_entity: Dict, recon_entity: Dict) -> List[Dict]:
        """Detaillierter Vergleich zweier passender Entities"""
        differences = []
        entity_type = orig_entity['type']
        
        # Layer-Vergleich
        if orig_entity['layer'] != recon_entity['layer']:
            differences.append({
                'type': 'layer_difference',
                'entity_type': entity_type,
                'original': orig_entity,
                'reconstructed': recon_entity,
                'description': f"Layer unterschiedlich: '{orig_entity['layer']}' vs '{recon_entity['layer']}'"
            })
        
        # Geometrie-spezifische Vergleiche
        if entity_type == 'LINE':
            if not self.points_close(orig_entity['start'], recon_entity['start']):
                differences.append({
                    'type': 'coordinate_difference',
                    'entity_type': entity_type,
                    'field': 'start_point',
                    'original': orig_entity['start'],
                    'reconstructed': recon_entity['start'],
                    'description': f"Startpunkt unterschiedlich: {orig_entity['start']} vs {recon_entity['start']}"
                })
        
        elif entity_type == 'CIRCLE':
            if abs(orig_entity['radius'] - recon_entity['radius']) >= self.tolerance:
                differences.append({
                    'type': 'dimension_difference',
                    'entity_type': entity_type,
                    'field': 'radius',
                    'original': orig_entity['radius'],
                    'reconstructed': recon_entity['radius'],
                    'description': f"Radius unterschiedlich: {orig_entity['radius']} vs {recon_entity['radius']}"
                })
        
        elif entity_type in ['TEXT', 'MTEXT']:
            if orig_entity['text'] != recon_entity['text']:
                differences.append({
                    'type': 'text_difference',
                    'entity_type': entity_type,
                    'original': orig_entity['text'],
                    'reconstructed': recon_entity['text'],
                    'description': f"Text unterschiedlich: '{orig_entity['text']}' vs '{recon_entity['text']}'"
                })
        
        return differences
    
    def generate_report(self) -> str:
        """Generiert einen detaillierten Differenz-Report"""
        report = []
        report.append("# DXF DIFFERENZ-ANALYSE REPORT")
        report.append(f"Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Toleranz: {self.tolerance}")
        report.append("")
        
        # Statistiken
        total_original = len(self.original_entities)
        total_reconstructed = len(self.reconstructed_entities)
        total_differences = len(self.differences)
        
        report.append("## ZUSAMMENFASSUNG")
        report.append(f"- Original Entities: {total_original}")
        report.append(f"- Rekonstruierte Entities: {total_reconstructed}")
        report.append(f"- Gefundene Unterschiede: {total_differences}")
        report.append(f"- Übereinstimmungsrate: {((max(total_original, total_reconstructed) - total_differences) / max(total_original, total_reconstructed) * 100):.2f}%" if max(total_original, total_reconstructed) > 0 else "N/A")
        report.append("")
        
        # Kategorisiere Unterschiede
        diff_categories = {}
        for diff in self.differences:
            category = diff['type']
            if category not in diff_categories:
                diff_categories[category] = []
            diff_categories[category].append(diff)
        
        if diff_categories:
            report.append("## KATEGORIEN DER UNTERSCHIEDE")
            for category, diffs in diff_categories.items():
                report.append(f"### {category.upper().replace('_', ' ')} ({len(diffs)} Fälle)")
                for i, diff in enumerate(diffs[:10], 1):  # Zeige max. 10 pro Kategorie
                    report.append(f"{i}. {diff['description']}")
                if len(diffs) > 10:
                    report.append(f"   ... und {len(diffs) - 10} weitere Fälle")
                report.append("")
        else:
            report.append("## ERGEBNIS")
            report.append("✅ Keine Unterschiede gefunden! Die Rekonstruktion ist identisch mit dem Original.")
            report.append("")
        
        # Entity-Typ Statistiken
        original_types = {}
        reconstructed_types = {}
        
        for entity in self.original_entities:
            entity_type = entity['type']
            original_types[entity_type] = original_types.get(entity_type, 0) + 1
        
        for entity in self.reconstructed_entities:
            entity_type = entity['type']
            reconstructed_types[entity_type] = reconstructed_types.get(entity_type, 0) + 1
        
        report.append("## ENTITY-TYP STATISTIKEN")
        all_types = set(original_types.keys()) | set(reconstructed_types.keys())
        
        report.append("| Entity-Typ | Original | Rekonstruiert | Differenz |")
        report.append("|------------|----------|---------------|-----------|")
        
        for entity_type in sorted(all_types):
            orig_count = original_types.get(entity_type, 0)
            recon_count = reconstructed_types.get(entity_type, 0)
            diff_count = recon_count - orig_count
            diff_str = f"{diff_count:+}" if diff_count != 0 else "0"
            report.append(f"| {entity_type} | {orig_count} | {recon_count} | {diff_str} |")
        
        report.append("")
        
        # Detaillierte Differenz-Liste (wenn nicht zu lang)
        if len(self.differences) <= 50:
            report.append("## DETAILLIERTE UNTERSCHIEDE")
            for i, diff in enumerate(self.differences, 1):
                report.append(f"### Unterschied {i}: {diff['type']}")
                report.append(f"**Beschreibung:** {diff['description']}")
                
                if 'original' in diff and 'reconstructed' in diff:
                    report.append("**Original:**")
                    report.append(f"```json")
                    report.append(json.dumps(diff['original'], indent=2, ensure_ascii=False))
                    report.append("```")
                    report.append("**Rekonstruiert:**")
                    report.append(f"```json")
                    report.append(json.dumps(diff['reconstructed'], indent=2, ensure_ascii=False))
                    report.append("```")
                
                report.append("")
        
        return "\\n".join(report)
    
    def analyze_files(self, original_file: str, reconstructed_file: str) -> bool:
        """Analysiert zwei DXF-Dateien und erstellt Differenz-Report"""
        print(f"Lade Original-Datei: {original_file}")
        self.original_entities = self.load_dxf_entities(original_file)
        
        print(f"Lade rekonstruierte Datei: {reconstructed_file}")
        self.reconstructed_entities = self.load_dxf_entities(reconstructed_file)
        
        if not self.original_entities and not self.reconstructed_entities:
            print("Fehler: Beide Dateien sind leer oder konnten nicht geladen werden")
            return False
        
        print("Führe Differenz-Analyse durch...")
        self.compare_entities(self.original_entities, self.reconstructed_entities)
        
        return True

def main():
    if len(sys.argv) < 3:
        print("Verwendung: python dxf_diff_analyzer.py <original.dxf> <reconstructed.dxf> [output_report.md] [tolerance]")
        print("")
        print("Beispiel:")
        print("  python dxf_diff_analyzer.py original.dxf reconstructed.dxf report.md 0.001")
        sys.exit(1)
    
    original_file = sys.argv[1]
    reconstructed_file = sys.argv[2]
    output_report = sys.argv[3] if len(sys.argv) > 3 else "difference_report.md"
    tolerance = float(sys.argv[4]) if len(sys.argv) > 4 else 0.001
    
    # Prüfe ob Dateien existieren
    if not os.path.exists(original_file):
        print(f"Fehler: Original-Datei '{original_file}' nicht gefunden")
        sys.exit(1)
    
    if not os.path.exists(reconstructed_file):
        print(f"Fehler: Rekonstruierte Datei '{reconstructed_file}' nicht gefunden")
        sys.exit(1)
    
    # Führe Analyse durch
    analyzer = DXFDifferenceAnalyzer(tolerance=tolerance)
    
    if analyzer.analyze_files(original_file, reconstructed_file):
        # Generiere Report
        report = analyzer.generate_report()
        
        # Speichere Report
        try:
            with open(output_report, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\\n✅ Differenz-Analyse abgeschlossen!")
            print(f"📊 Report gespeichert in: {output_report}")
            print(f"🔍 Gefundene Unterschiede: {len(analyzer.differences)}")
            
            if len(analyzer.differences) == 0:
                print("🎉 Perfekte Übereinstimmung!")
            else:
                print(f"⚠️  {len(analyzer.differences)} Unterschiede gefunden.")
        
        except Exception as e:
            print(f"Fehler beim Speichern des Reports: {e}")
            sys.exit(1)
    else:
        print("Fehler bei der Differenz-Analyse")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

print("Script 3 (Differenz-Analyse) erstellt...")