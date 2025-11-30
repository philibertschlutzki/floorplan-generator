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
        self.workflow_success = {
            'download': False,
            'dxf_to_text': False,
            'text_to_dxf': False,
            'difference_analysis': False,
            'workflow_report': False
        }
        
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
                self.workflow_success['download'] = True
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
            
            # Verwende das separate dxf_to_text.py Modul
            script_path = Path(__file__).parent / "dxf_to_text.py"
            
            if not script_path.exists():
                self.log(f"dxf_to_text.py nicht gefunden: {script_path}", "ERROR")
                return False
            
            # Führe das separate Script aus
            result = subprocess.run([
                sys.executable, str(script_path), str(self.original_file)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                # Kopiere Ausgabedateien zum finalen Ziel
                base_name = self.original_file.stem
                temp_desc = self.original_file.parent / f"{base_name}_description.txt"
                temp_struct = self.original_file.parent / f"{base_name}_structured.json"
                
                if temp_desc.exists():
                    with open(temp_desc, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(self.description_file, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    self.log(f"Beschreibung erstellt: {self.description_file}")
                    
                if temp_struct.exists():
                    with open(temp_struct, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(self.structured_file, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    self.log(f"Strukturierte Daten erstellt: {self.structured_file}")
                
                self.log("DXF zu Text Konvertierung erfolgreich")
                self.workflow_success['dxf_to_text'] = True
                return True
            else:
                self.log(f"DXF zu Text Konvertierung fehlgeschlagen: {result.stderr}", "ERROR")
                self.log(f"Stdout: {result.stdout}", "DEBUG")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei DXF zu Text Konvertierung: {e}", "ERROR")
            return False
    
    def run_text_to_dxf(self) -> bool:
        """Führt Text zu DXF Konvertierung aus"""
        try:
            self.log("Starte Natürlichsprache zu DXF Konvertierung...")
            
            # Prüfe ob die strukturierten Daten vorhanden sind
            if not self.structured_file.exists():
                self.log(f"Strukturierte Daten nicht gefunden: {self.structured_file}", "ERROR")
                return False
            
            # Verwende das separate text_to_dxf.py Modul
            script_path = Path(__file__).parent / "text_to_dxf.py"
            
            if not script_path.exists():
                self.log(f"text_to_dxf.py nicht gefunden: {script_path}", "ERROR")
                return False
            
            # Führe das separate Script aus
            result = subprocess.run([
                sys.executable, str(script_path), 
                str(self.structured_file), str(self.reconstructed_file)
            ], capture_output=True, text=True, encoding='utf-8')
            
            self.log(f"Text zu DXF Konvertierung - Return Code: {result.returncode}", "DEBUG")
            self.log(f"Stdout: {result.stdout}", "DEBUG")
            if result.stderr:
                self.log(f"Stderr: {result.stderr}", "DEBUG")
            
            if result.returncode == 0 and self.reconstructed_file.exists():
                self.log(f"Rekonstruierte DXF erstellt: {self.reconstructed_file}")
                self.workflow_success['text_to_dxf'] = True
                return True
            else:
                self.log(f"Text zu DXF Konvertierung fehlgeschlagen: {result.stderr}", "ERROR")
                if result.stdout:
                    self.log(f"Zusätzliche Ausgabe: {result.stdout}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei Text zu DXF Konvertierung: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
    
    def run_difference_analysis(self) -> bool:
        """Führt vereinfachte Differenz-Analyse aus"""
        try:
            self.log("Starte Differenz-Analyse...")
            
            # Einfache Analyse durch Dateigrößen-Vergleich
            orig_size = self.original_file.stat().st_size if self.original_file and self.original_file.exists() else 0
            recon_size = self.reconstructed_file.stat().st_size if self.reconstructed_file.exists() else 0
            
            size_diff = abs(orig_size - recon_size)
            size_diff_percent = (size_diff / max(orig_size, 1)) * 100
            
            # Analysiere Inhalte falls möglich
            content_analysis = "Keine detaillierte Inhaltsanalyse verfügbar"
            if self.structured_file.exists():
                try:
                    with open(self.structured_file, 'r', encoding='utf-8') as f:
                        structured_data = json.load(f)
                    entity_count = len(structured_data.get('entities', []))
                    layer_count = len(structured_data.get('layers', {}))
                    content_analysis = f"Entities: {entity_count}, Layer: {layer_count}"
                except:
                    pass
            
            report = f"""# DXF Differenz-Analyse Report
Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ZUSAMMENFASSUNG
- Original-Datei: {orig_size} bytes
- Rekonstruierte Datei: {recon_size} bytes
- Größen-Differenz: {size_diff} bytes ({size_diff_percent:.2f}%)
- Inhalt: {content_analysis}

## ANALYSE
{"✅ Dateien sind identisch in der Größe!" if size_diff == 0 else f"⚠️ Dateien unterscheiden sich um {size_diff} bytes"}

## WORKFLOW STATUS
- Download: {'✅ Erfolgreich' if self.workflow_success['download'] else '❌ Fehlgeschlagen'}
- DXF → Text: {'✅ Erfolgreich' if self.workflow_success['dxf_to_text'] else '❌ Fehlgeschlagen'}  
- Text → DXF: {'✅ Erfolgreich' if self.workflow_success['text_to_dxf'] else '❌ Fehlgeschlagen'}
- Differenz-Analyse: ✅ Abgeschlossen

## DATEIEN
- Original: {self.original_file.name if self.original_file else 'N/A'} ({orig_size} bytes)
- Beschreibung: {self.description_file.name}
- Strukturiert: {self.structured_file.name} 
- Rekonstruiert: {self.reconstructed_file.name} ({recon_size} bytes)
"""
            
            with open(self.difference_report, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log("Differenz-Analyse erfolgreich")
            self.workflow_success['difference_analysis'] = True
            return True
                
        except Exception as e:
            self.log(f"Fehler bei Differenz-Analyse: {e}", "ERROR")
            return False
    
    def create_workflow_report(self) -> bool:
        """Erstellt einen Workflow-Report"""
        try:
            report_file = self.output_dir / "workflow_report.md"
            
            # Bestimme Gesamtstatus
            all_success = all(self.workflow_success.values())
            
            report = []
            report.append("# DXF Workflow Report")
            report.append(f"Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append(f"**Status:** {'✅ Erfolgreich' if all_success else '❌ Mit Fehlern'}")
            report.append(f"**Input URL:** {self.input_url}")
            report.append(f"**Output Directory:** {self.output_dir}")
            report.append("")
            
            report.append("## Workflow-Schritte")
            report.append(f"1. {'✅' if self.workflow_success['download'] else '❌'} DXF-Datei Download")
            report.append(f"2. {'✅' if self.workflow_success['dxf_to_text'] else '❌'} DXF → Natürlichsprachige Beschreibung")
            report.append(f"3. {'✅' if self.workflow_success['text_to_dxf'] else '❌'} Natürlichsprachige Beschreibung → DXF Rekonstruktion")
            report.append(f"4. {'✅' if self.workflow_success['difference_analysis'] else '❌'} Differenz-Analyse zwischen Original und Rekonstruktion")
            report.append("")
            
            report.append("## Generierte Dateien")
            if self.description_file.exists():
                report.append(f"- **Natürlichsprachige Beschreibung:** `{self.description_file.name}`")
            if self.structured_file.exists():
                report.append(f"- **Strukturierte Daten:** `{self.structured_file.name}`")
            if self.reconstructed_file.exists():
                report.append(f"- **Rekonstruierte DXF:** `{self.reconstructed_file.name}`")
            if self.difference_report.exists():
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
            self.workflow_success['workflow_report'] = True
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
                self.log("Workflow gestoppt: Download fehlgeschlagen", "ERROR")
                self.create_workflow_report()  # Erstelle Report auch bei Fehlern
                return False
            
            # Schritt 2: DXF → Text
            if not self.run_dxf_to_text():
                self.log("Workflow gestoppt: DXF zu Text Konvertierung fehlgeschlagen", "ERROR")
                self.create_workflow_report()  # Erstelle Report auch bei Fehlern
                return False
            
            # Schritt 3: Text → DXF
            if not self.run_text_to_dxf():
                self.log("Workflow gestoppt: Text zu DXF Konvertierung fehlgeschlagen", "ERROR")
                self.create_workflow_report()  # Erstelle Report auch bei Fehlern
                return False
            
            # Schritt 4: Differenz-Analyse
            if not self.run_difference_analysis():
                self.log("Warnung: Differenz-Analyse fehlgeschlagen, aber Workflow wird fortgesetzt", "WARNING")
            
            # Schritt 5: Workflow-Report
            if not self.create_workflow_report():
                self.log("Warnung: Workflow-Report konnte nicht erstellt werden", "WARNING")
            
            self.log("=== WORKFLOW ERFOLGREICH ABGESCHLOSSEN ===")
            self.log(f"Alle Ausgabedateien in: {self.output_dir}")
            
            return True
            
        except Exception as e:
            self.log(f"Schwerwiegender Workflow-Fehler: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            self.create_workflow_report()  # Erstelle Report auch bei Fehlern
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