# Script 4: Haupt-Workflow-Script
workflow_script = '''#!/usr/bin/env python3
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
                self.log(f"Download erfolgreich: {self.original_file}")
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
            
            # Erstelle temporäre Script-Datei
            script_file = self.temp_dir / "dxf_to_text.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(dxf_to_text_script)
            
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
                if temp_struct.exists():
                    temp_struct.rename(self.structured_file)
                
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
            
            # Erstelle temporäre Script-Datei
            script_file = self.temp_dir / "text_to_dxf.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(text_to_dxf_script)
            
            # Führe Script mit strukturierten Daten aus
            result = subprocess.run([
                sys.executable, str(script_file), 
                str(self.structured_file), str(self.reconstructed_file)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.log("Text zu DXF Konvertierung erfolgreich")
                return True
            else:
                self.log(f"Text zu DXF Konvertierung fehlgeschlagen: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei Text zu DXF Konvertierung: {e}", "ERROR")
            return False
    
    def run_difference_analysis(self) -> bool:
        """Führt Differenz-Analyse aus"""
        try:
            self.log("Starte Differenz-Analyse...")
            
            # Erstelle temporäre Script-Datei
            script_file = self.temp_dir / "dxf_diff_analyzer.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(diff_analyzer_script)
            
            # Führe Differenz-Analyse aus
            result = subprocess.run([
                sys.executable, str(script_file),
                str(self.original_file), str(self.reconstructed_file),
                str(self.difference_report)
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.log("Differenz-Analyse erfolgreich")
                return True
            else:
                self.log(f"Differenz-Analyse fehlgeschlagen: {result.stderr}", "ERROR")
                return False
                
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
            report.append("")
            
            # Datei-Statistiken
            if self.description_file.exists():
                desc_size = self.description_file.stat().st_size
                report.append(f"- Beschreibungs-Datei: {desc_size} bytes")
            
            if self.structured_file.exists():
                struct_size = self.structured_file.stat().st_size
                report.append(f"- Strukturierte Daten: {struct_size} bytes")
            
            if self.reconstructed_file.exists():
                recon_size = self.reconstructed_file.stat().st_size
                report.append(f"- Rekonstruierte DXF: {recon_size} bytes")
                
            if self.original_file and self.original_file.exists():
                orig_size = self.original_file.stat().st_size
                report.append(f"- Original DXF: {orig_size} bytes")
            
            # Schreibe Report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("\\n".join(report))
            
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
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "./dxf_workflow_output"
    
    # Starte Workflow
    workflow = DXFWorkflowManager(input_url, output_directory)
    
    success = workflow.run_complete_workflow()
    
    if success:
        print(f"\\n🎉 Workflow erfolgreich abgeschlossen!")
        print(f"📂 Ausgabedateien in: {workflow.output_dir}")
        sys.exit(0)
    else:
        print(f"\\n❌ Workflow fehlgeschlagen!")
        print(f"📋 Logs siehe: {workflow.output_dir}/workflow_report.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

print("Script 4 (Workflow Manager) erstellt...")