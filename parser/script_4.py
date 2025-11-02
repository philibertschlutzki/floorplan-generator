# Erstelle die requirements.txt Datei
requirements_txt = '''# DXF Processing Requirements
ezdxf>=1.0.0
numpy>=1.20.0
pyparsing>=2.4.0
typing-extensions>=3.7.0
fontTools>=4.0.0

# Für URL Downloads
urllib3>=1.26.0
requests>=2.25.0

# Für JSON und Datenverarbeitung (normalerweise in Python Standard Library)
# json (built-in)
# os (built-in)
# sys (built-in)
# math (built-in)
# subprocess (built-in)
# tempfile (built-in)
# pathlib (built-in)
# datetime (built-in)
'''

setup_py = '''#!/usr/bin/env python3
"""
Setup Script für DXF Workflow Tools
Installiert alle benötigten Abhängigkeiten
"""

import subprocess
import sys
import os

def install_requirements():
    """Installiert alle Requirements"""
    requirements = [
        "ezdxf>=1.0.0",
        "numpy>=1.20.0", 
        "pyparsing>=2.4.0",
        "typing-extensions>=3.7.0",
        "fontTools>=4.0.0",
        "urllib3>=1.26.0",
        "requests>=2.25.0"
    ]
    
    print("Installiere benötigte Python-Pakete...")
    
    for requirement in requirements:
        try:
            print(f"Installiere: {requirement}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", requirement
            ])
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Installieren von {requirement}: {e}")
            return False
    
    print("✅ Alle Abhängigkeiten erfolgreich installiert!")
    return True

def create_scripts():
    """Erstellt alle Script-Dateien"""
    scripts = {
        "dxf_to_text.py": dxf_to_text_script,
        "text_to_dxf.py": text_to_dxf_script, 
        "dxf_diff_analyzer.py": diff_analyzer_script,
        "dxf_workflow.py": workflow_script
    }
    
    for filename, content in scripts.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Mache Dateien ausführbar (Unix/Linux/macOS)
            if os.name != 'nt':  # Nicht Windows
                os.chmod(filename, 0o755)
            
            print(f"✅ {filename} erstellt")
        except Exception as e:
            print(f"❌ Fehler beim Erstellen von {filename}: {e}")
            return False
    
    return True

def main():
    print("=== DXF Workflow Tools Setup ===")
    print()
    
    # Installiere Requirements
    if not install_requirements():
        print("❌ Setup fehlgeschlagen: Konnte Abhängigkeiten nicht installieren")
        sys.exit(1)
    
    # Erstelle Script-Dateien
    if not create_scripts():
        print("❌ Setup fehlgeschlagen: Konnte Scripts nicht erstellen")
        sys.exit(1)
    
    # Erstelle requirements.txt
    try:
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements_txt)
        print("✅ requirements.txt erstellt")
    except Exception as e:
        print(f"⚠️  Warnung: Konnte requirements.txt nicht erstellen: {e}")
    
    print()
    print("🎉 Setup erfolgreich abgeschlossen!")
    print()
    print("Verfügbare Scripts:")
    print("1. dxf_to_text.py      - Konvertiert DXF zu natürlichsprachiger Beschreibung")
    print("2. text_to_dxf.py      - Rekonstruiert DXF aus Beschreibung")
    print("3. dxf_diff_analyzer.py - Analysiert Unterschiede zwischen DXF-Dateien")
    print("4. dxf_workflow.py     - Kompletter Workflow (empfohlen)")
    print()
    print("Beispiel-Verwendung:")
    print("python dxf_workflow.py https://github.com/philibertschlutzki/floorplan-generator/blob/main/output/building_1762086268523.dxf ./output")

if __name__ == "__main__":
    main()
'''

print("Requirements und Setup-Script erstellt...")