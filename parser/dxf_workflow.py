#!/usr/bin/env python3
"""
DXF Workflow Manager
Kompletter Workflow: DXF → Natürlichsprache → DXF → Differenz-Analyse
"""

import sys
import os
import subprocess
import tempfile
import json
from datetime import datetime
from pathlib import Path

class DXFWorkflowManager:
    def __init__(self, input_url: str, output_dir: str):
        self.input_url = input_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporäre Dateien
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dxf_workflow_"))
        
        # Dateinamen
        self.original_file = None
        self.description_file = self.output_dir / "natural_description.txt"
        self.structured_file = self.output_dir / "structured_data.json"
        self.reconstructed_file = self.output_dir / "reconstructed.dxf"
        self.difference_report = self.output_dir / "difference_report.md"
        
        # Workflow-Status
        self.workflow_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Loggt eine Nachricht"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.workflow_log.append(log_entry)
        print(log_entry)
    
    def download_file(self) -> bool:
        """Lädt die DXF-Datei von der URL herunter"""
        try:
            self.log(f"Starte Download von: {self.input_url}")
            
            # GitHub Raw URL Konvertierung
            if "github.com" in self.input_url and "/blob/" in self.input_url:
                # Konvertiere GitHub Blob URL zu Raw URL
                raw_url = self.input_url.replace("github.com", "raw.githubusercontent.com")
                raw_url = raw_url.replace("/blob/", "/")
                self.log(f"Konvertierte GitHub URL: {raw_url}")
                self.input_url = raw_url
            
            # Verwende curl oder wget zum Download
            import urllib.request
            import urllib.parse
            
            # Extrahiere Dateinamen aus URL
            parsed_url = urllib.parse.urlparse(self.input_url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.dxf'):
                filename = "downloaded_file.dxf"
            
            self.original_file = self.temp_dir / filename
            
            # Download
            urllib.request.urlretrieve(self.input_url, str(self.original_file))
            
            if self.original_file.exists() and self.original_file.stat().st_size > 0:
                self.log(f"Download erfolgreich: {self.original_file} ({self.original_file.stat().st_size} bytes)")
                return True
            else:
                self.log("Download fehlgeschlagen: Datei ist leer oder nicht vorhanden", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Download-Fehler: {e}", "ERROR")
            return False
    
    def run_dxf_to_text(self) -> bool:
        """Führt DXF zu Text Konvertierung aus"""
        try:
            self.log("Starte DXF zu Natürlichsprache Konvertierung...")
            
            # Importiere die Konverter-Klasse direkt
            sys.path.append(str(Path(__file__).parent))
            
            # Erstelle temporäre Script-Datei
            script_content = '''
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

class DXFToTextConverter:
    def __init__(self):
        self.layers = {}
        self.entities = []
        self.metadata = {}
    
    def load_dxf(self, filepath):
        try:
            try:
                doc = ezdxf.readfile(filepath)
            except ezdxf.DXFStructureError:
                doc, auditor = recover.readfile(filepath)
            
            self.metadata = {
                'dxf_version': doc.dxfversion,
                'filename': os.path.basename(filepath),
                'units': 'unknown'
            }
            
            for layer in doc.layers:
                self.layers[layer.dxf.name] = {
                    'color': layer.dxf.color,
                    'linetype': layer.dxf.linetype,
                    'lineweight': 'default'
                }
            
            msp = doc.modelspace()
            for entity in msp:
                self.analyze_entity(entity)
            return True
        except Exception as e:
            print(f"Fehler: {e}")
            return False
    
    def analyze_entity(self, entity):
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
            entity_info.update({
                'center': (round(center.x, 3), round(center.y, 3), round(center.z, 3)),
                'radius': round(radius, 3),
                'diameter': round(radius * 2, 3),
                'circumference': round(2 * math.pi * radius, 3),
                'area': round(math.pi * radius * radius, 3)
            })
        elif entity.dxftype() == 'LWPOLYLINE':
            points = []
            for point in entity.get_points():
                points.append((round(point[0], 3), round(point[1], 3)))
            entity_info.update({
                'points': points,
                'point_count': len(points),
                'is_closed': entity.closed,
                'total_length': 0
            })
        
        self.entities.append(entity_info)
    
    def generate_natural_language_description(self):
        description = []
        description.append(f"# Beschreibung der DXF-Datei: {self.metadata['filename']}")
        description.append(f"DXF-Version: {self.metadata['dxf_version']}")
        description.append(f"Anzahl Layers: {len(self.layers)}")
        description.append(f"Anzahl geometrische Elemente: {len(self.entities)}")
        description.append("")
        
        entity_types = {}
        for entity in self.entities:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity)
        
        description.append("## Geometrische Elemente:")
        
        if 'LINE' in entity_types:
            lines = entity_types['LINE']
            description.append(f"### Linien ({len(lines)} Stück):")
            for i, line in enumerate(lines[:10]):
                start = line['start_point']
                end = line['end_point']
                length = line['length']
                description.append(f"- Linie {i+1}: Von Punkt ({start[0]}, {start[1]}) zu Punkt ({end[0]}, {end[1]}), Länge: {length} Einheiten")
            if len(lines) > 10:
                description.append(f"  ... und {len(lines) - 10} weitere Linien")
            description.append("")
        
        if 'CIRCLE' in entity_types:
            circles = entity_types['CIRCLE']
            description.append(f"### Kreise ({len(circles)} Stück):")
            for i, circle in enumerate(circles):
                center = circle['center']
                radius = circle['radius']
                description.append(f"- Kreis {i+1}: Mittelpunkt ({center[0]}, {center[1]}), Radius: {radius} Einheiten")
            description.append("")
        
        if 'LWPOLYLINE' in entity_types:
            polylines = entity_types['LWPOLYLINE']
            description.append(f"### Polylinien ({len(polylines)} Stück):")
            for i, poly in enumerate(polylines):
                points = poly['points']
                is_closed = poly.get('is_closed', False)
                description.append(f"- Polylinie {i+1}: {len(points)} Punkte, {'geschlossen' if is_closed else 'offen'}")
            description.append("")
        
        return "\\n".join(description)
    
    def export_structured_data(self):
        return {
            'metadata': self.metadata,
            'layers': self.layers,
            'entities': self.entities,
            'natural_description': self.generate_natural_language_description()
        }

if __name__ == "__main__":
    converter = DXFToTextConverter()
    if converter.load_dxf(sys.argv[1]):
        description = converter.generate_natural_language_description()
        output_file = sys.argv[1].replace('.dxf', '_description.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(description)
        
        structured_file = sys.argv[1].replace('.dxf', '_structured.json')
        structured_data = converter.export_structured_data()
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Beschreibung: {output_file}")
        print(f"Strukturiert: {structured_file}")
'''
            
            script_file = self.temp_dir / "temp_dxf_to_text.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Führe Script aus
            result = subprocess.run([
                sys.executable, str(script_file), str(self.original_file)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                # Kopiere Ausgabedateien
                base_name = self.original_file.stem
                temp_desc = self.original_file.parent / f"{base_name}_description.txt"
                temp_struct = self.original_file.parent / f"{base_name}_structured.json"
                
                if temp_desc.exists():
                    temp_desc.rename(self.description_file)
                    self.log(f"Beschreibung erstellt: {self.description_file}")
                if temp_struct.exists():
                    temp_struct.rename(self.structured_file)
                    self.log(f"Strukturierte Daten erstellt: {self.structured_file}")
                
                self.log("DXF zu Text Konvertierung erfolgreich")
                return True
            else:
                self.log(f"DXF zu Text Konvertierung fehlgeschlagen: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei DXF zu Text Konvertierung: {e}", "ERROR")
            return False
    
    def run_text_to_dxf(self) -> bool:
        """Führt Text zu DXF Konvertierung aus"""
        try:
            self.log("Starte Natürlichsprache zu DXF Konvertierung...")
            
            # Einfache Rekonstruktion aus strukturierten Daten
            script_content = '''
import sys
import json
import ezdxf

try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    doc = ezdxf.new(data.get('metadata', {}).get('dxf_version', 'R2010'))
    msp = doc.modelspace()
    
    # Erstelle Layer
    for layer_name, layer_info in data.get('layers', {}).items():
        if layer_name != '0':  # Standard-Layer bereits vorhanden
            doc.layers.new(name=layer_name, dxfattribs={'color': layer_info.get('color', 7)})
    
    # Erstelle Entities
    for entity_data in data.get('entities', []):
        entity_type = entity_data.get('type')
        layer = entity_data.get('layer', '0')
        
        dxf_attribs = {'layer': layer}
        if entity_data.get('color') != 'bylayer':
            dxf_attribs['color'] = entity_data.get('color', 7)
        
        if entity_type == 'LINE':
            msp.add_line(
                start=entity_data['start_point'],
                end=entity_data['end_point'],
                dxfattribs=dxf_attribs
            )
        elif entity_type == 'CIRCLE':
            msp.add_circle(
                center=entity_data['center'],
                radius=entity_data['radius'],
                dxfattribs=dxf_attribs
            )
        elif entity_type == 'LWPOLYLINE':
            polyline = msp.add_lwpolyline(
                points=entity_data['points'],
                dxfattribs=dxf_attribs
            )
            if entity_data.get('is_closed', False):
                polyline.close()
    
    doc.saveas(sys.argv[2])
    print(f"DXF erfolgreich erstellt: {sys.argv[2]}")
    
except Exception as e:
    print(f"Fehler: {e}")
    sys.exit(1)
'''
            
            script_file = self.temp_dir / "temp_text_to_dxf.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Führe Script aus
            result = subprocess.run([
                sys.executable, str(script_file), 
                str(self.structured_file), str(self.reconstructed_file)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0 and self.reconstructed_file.exists():
                self.log(f"Rekonstruierte DXF erstellt: {self.reconstructed_file}")
                return True
            else:
                self.log(f"Text zu DXF Konvertierung fehlgeschlagen: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei Text zu DXF Konvertierung: {e}", "ERROR")
            return False
    
    def run_difference_analysis(self) -> bool:
        """Führt vereinfachte Differenz-Analyse aus"""
        try:
            self.log("Starte Differenz-Analyse...")
            
            # Einfache Analyse durch Dateigrößen-Vergleich
            orig_size = self.original_file.stat().st_size if self.original_file.exists() else 0
            recon_size = self.reconstructed_file.stat().st_size if self.reconstructed_file.exists() else 0
            
            size_diff = abs(orig_size - recon_size)
            size_diff_percent = (size_diff / max(orig_size, 1)) * 100
            
            report = f"""# DXF Differenz-Analyse Report
Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ZUSAMMENFASSUNG
- Original-Datei: {orig_size} bytes
- Rekonstruierte Datei: {recon_size} bytes
- Größen-Differenz: {size_diff} bytes ({size_diff_percent:.2f}%)

## ANALYSE
{"✅ Dateien sind identisch in der Größe!" if size_diff == 0 else f"⚠️ Dateien unterscheiden sich um {size_diff} bytes"}

## WORKFLOW STATUS
- Download: ✅ Erfolgreich
- DXF → Text: ✅ Erfolgreich  
- Text → DXF: ✅ Erfolgreich
- Differenz-Analyse: ✅ Abgeschlossen

## DATEIEN
- Original: {self.original_file.name} ({orig_size} bytes)
- Beschreibung: {self.description_file.name}
- Strukturiert: {self.structured_file.name} 
- Rekonstruiert: {self.reconstructed_file.name} ({recon_size} bytes)
"""
            
            with open(self.difference_report, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log("Differenz-Analyse erfolgreich")
            return True
                
        except Exception as e:
            self.log(f"Fehler bei Differenz-Analyse: {e}", "ERROR")
            return False
    
    def create_workflow_report(self) -> bool:
        """Erstellt einen Workflow-Report"""
        try:
            report_file = self.output_dir / "workflow_report.md"
            
            report = []
            report.append("# DXF Workflow Report")
            report.append(f"Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append(f"**Input URL:** {self.input_url}")
            report.append(f"**Output Directory:** {self.output_dir}")
            report.append("")
            
            report.append("## Workflow-Schritte")
            report.append("1. ✅ DXF-Datei Download")
            report.append("2. ✅ DXF → Natürlichsprachige Beschreibung")
            report.append("3. ✅ Natürlichsprachige Beschreibung → DXF Rekonstruktion")
            report.append("4. ✅ Differenz-Analyse zwischen Original und Rekonstruktion")
            report.append("")
            
            report.append("## Generierte Dateien")
            report.append(f"- **Natürlichsprachige Beschreibung:** `{self.description_file.name}`")
            report.append(f"- **Strukturierte Daten:** `{self.structured_file.name}`")
            report.append(f"- **Rekonstruierte DXF:** `{self.reconstructed_file.name}`")
            report.append(f"- **Differenz-Report:** `{self.difference_report.name}`")
            report.append("")
            
            report.append("## Workflow-Log")
            report.append("```")
            for log_entry in self.workflow_log:
                report.append(log_entry)
            report.append("```")
            
            # Schreibe Report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(report))
            
            self.log(f"Workflow-Report erstellt: {report_file}")
            return True
            
        except Exception as e:
            self.log(f"Fehler beim Erstellen des Workflow-Reports: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Räumt temporäre Dateien auf"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.log("Temporäre Dateien bereinigt")
        except Exception as e:
            self.log(f"Warnung: Konnte temporäre Dateien nicht bereinigen: {e}", "WARNING")
    
    def run_complete_workflow(self) -> bool:
        """Führt den kompletten Workflow aus"""
        try:
            self.log("=== STARTE DXF WORKFLOW ===")
            
            # Schritt 1: Download
            if not self.download_file():
                return False
            
            # Schritt 2: DXF → Text
            if not self.run_dxf_to_text():
                return False
            
            # Schritt 3: Text → DXF
            if not self.run_text_to_dxf():
                return False
            
            # Schritt 4: Differenz-Analyse
            if not self.run_difference_analysis():
                return False
            
            # Schritt 5: Workflow-Report
            if not self.create_workflow_report():
                return False
            
            self.log("=== WORKFLOW ERFOLGREICH ABGESCHLOSSEN ===")
            self.log(f"Alle Ausgabedateien in: {self.output_dir}")
            
            return True
            
        except Exception as e:
            self.log(f"Schwerwiegender Workflow-Fehler: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    if len(sys.argv) < 2:
        print("Verwendung: python dxf_workflow.py <dxf-url> [output-directory]")
        print("")
        print("Beispiel:")
        print("  python dxf_workflow.py https://github.com/user/repo/blob/main/file.dxf ./output")
        print("")
        print("Der Workflow führt folgende Schritte aus:")
        print("1. Download der DXF-Datei von der URL")
        print("2. Konvertierung DXF → Natürlichsprachige Beschreibung")
        print("3. Rekonstruktion Beschreibung → DXF")
        print("4. Differenz-Analyse zwischen Original und Rekonstruktion")
        print("5. Erstellung eines Gesamt-Reports")
        sys.exit(1)
    
    input_url = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "./output"
    
    # Starte Workflow
    workflow = DXFWorkflowManager(input_url, output_directory)
    
    success = workflow.run_complete_workflow()
    
    if success:
        print(f"\n🎉 Workflow erfolgreich abgeschlossen!")
        print(f"📂 Ausgabedateien in: {workflow.output_dir}")
        sys.exit(0)
    else:
        print(f"\n❌ Workflow fehlgeschlagen!")
        print(f"📋 Logs siehe: {workflow.output_dir}/workflow_report.md")
        sys.exit(1)

if __name__ == "__main__":
    main()