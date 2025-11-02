#!/usr/bin/env python3
"""
Test-Script für den DXF Workflow
Testet den kompletten Workflow mit verschiedenen Szenarien
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

def test_workflow():
    """Testet den DXF Workflow mit der Beispiel-DXF"""
    
    print("=== DXF WORKFLOW TEST ===")
    print()
    
    # URL der Test-DXF
    test_url = "https://github.com/philibertschlutzki/floorplan-generator/blob/main/output/alpine_sennhuette.dxf"
    
    # Temporäres Ausgabeverzeichnis
    temp_output = Path(tempfile.mkdtemp(prefix="workflow_test_"))
    print(f"Test-Ausgabeverzeichnis: {temp_output}")
    
    try:
        # Script-Verzeichnis
        script_dir = Path(__file__).parent
        workflow_script = script_dir / "dxf_workflow.py"
        
        if not workflow_script.exists():
            print(f"ERROR: dxf_workflow.py nicht gefunden: {workflow_script}")
            return False
        
        print(f"Führe Workflow aus: {workflow_script}")
        print(f"Test-URL: {test_url}")
        print()
        
        # Führe den Workflow aus
        result = subprocess.run([
            sys.executable, str(workflow_script),
            test_url, str(temp_output)
        ], capture_output=True, text=True, encoding='utf-8')
        
        print("=== WORKFLOW OUTPUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== WORKFLOW ERRORS ===")
            print(result.stderr)
        
        print(f"\nWorkflow Return Code: {result.returncode}")
        
        # Prüfe generierte Dateien
        expected_files = [
            "natural_description.txt",
            "structured_data.json", 
            "reconstructed.dxf",
            "difference_report.md",
            "workflow_report.md"
        ]
        
        print("\n=== GENERIERTE DATEIEN ===")
        all_files_exist = True
        for filename in expected_files:
            filepath = temp_output / filename
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"✅ {filename} ({size} bytes)")
            else:
                print(f"❌ {filename} (nicht gefunden)")
                all_files_exist = False
        
        # Zeige Inhalt der Reports
        workflow_report = temp_output / "workflow_report.md"
        if workflow_report.exists():
            print("\n=== WORKFLOW REPORT ===")
            with open(workflow_report, 'r', encoding='utf-8') as f:
                print(f.read())
        
        difference_report = temp_output / "difference_report.md"
        if difference_report.exists():
            print("\n=== DIFFERENCE REPORT ===")
            with open(difference_report, 'r', encoding='utf-8') as f:
                print(f.read())
        
        # Test-Ergebnis
        success = (result.returncode == 0) and all_files_exist
        
        print(f"\n=== TEST ERGEBNIS ===")
        print(f"Status: {'✅ ERFOLGREICH' if success else '❌ FEHLGESCHLAGEN'}")
        print(f"Return Code: {result.returncode}")
        print(f"Alle Dateien generiert: {all_files_exist}")
        
        return success
        
    except Exception as e:
        print(f"Test-Fehler: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        # Aufräumen (optional - für Debugging kann man das auskommentieren)
        try:
            import shutil
            shutil.rmtree(temp_output, ignore_errors=True)
            print(f"\nTest-Verzeichnis bereinigt: {temp_output}")
        except:
            print(f"\nWarnung: Konnte Test-Verzeichnis nicht bereinigen: {temp_output}")

def test_individual_modules():
    """Testet die einzelnen Module separat"""
    
    print("\n=== MODUL TESTS ===")
    
    script_dir = Path(__file__).parent
    
    modules = [
        ("dxf_to_text.py", "DXF zu Text Konverter"),
        ("text_to_dxf.py", "Text zu DXF Konverter")
    ]
    
    for module_file, description in modules:
        module_path = script_dir / module_file
        
        print(f"\nTeste {description}...")
        
        if not module_path.exists():
            print(f"❌ {module_file} nicht gefunden")
            continue
        
        # Teste ob das Modul importierbar ist
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                f"import sys; sys.path.append('{script_dir}'); import {module_file[:-3]}; print('OK')"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print(f"✅ {module_file} importierbar")
            else:
                print(f"❌ {module_file} Import-Fehler: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {module_file} Test-Fehler: {e}")

def main():
    """Hauptfunktion für Tests"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--modules-only":
        test_individual_modules()
    else:
        # Teste zuerst die Module
        test_individual_modules()
        
        # Dann den kompletten Workflow
        success = test_workflow()
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()