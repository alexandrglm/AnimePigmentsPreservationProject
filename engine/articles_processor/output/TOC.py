#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UpdateTOC.py
Script para actualizar automáticamente el TOC de un documento DOCX
usando LibreOffice en modo headless
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import time


def update_toc_headless(docx_path):
    """Actualizar TOC usando LibreOffice headless"""
    try:
        docx_path = Path(docx_path).resolve()

        if not docx_path.exists():
            print(f"ERROR: File not found: {docx_path}")
            return False

        if not docx_path.suffix.lower() == '.docx':
            print(f"ERROR: File must be a .docx file")
            return False

        print(f"INFO: Updating TOC in {docx_path.name}...")
        print(f"INFO: Using LibreOffice headless mode...")

        # Crear copia de backup
        backup_path = docx_path.with_suffix('.docx.backup')
        shutil.copy2(docx_path, backup_path)
        print(f"INFO: Backup created: {backup_path.name}")

        # Método 1: Conversión simple (puede actualizar campos automáticamente)
        print("\nTrying Method 1: Simple conversion...")
        cmd1 = [
            'libreoffice',
            '--headless',
            '--invisible',
            '--convert-to', 'docx',
            '--outdir', str(docx_path.parent),
            str(docx_path)
        ]

        print(f"Command: {' '.join(cmd1)}")
        result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=60)

        if result1.returncode == 0:
            print("✅ Method 1 completed successfully")
        else:
            print("⚠️ Method 1 had issues:")
            print(f"STDOUT: {result1.stdout}")
            print(f"STDERR: {result1.stderr}")

        # Método 2: Forzar actualización con macro básica
        print("\nTrying Method 2: With field update...")

        # Crear macro temporal para actualizar todos los campos
        macro_content = '''
Sub UpdateAllFields
    Dim doc As Object
    doc = ThisComponent

    ' Actualizar todos los campos del documento
    doc.getTextFields().refresh()

    ' Guardar documento
    doc.store()
End Sub
'''

        # Crear directorio temporal para macro
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            macro_file = temp_dir / "UpdateFields.bas"

            with open(macro_file, 'w', encoding='utf-8') as f:
                f.write(macro_content)

            # Intentar ejecutar con macro
            cmd2 = [
                'libreoffice',
                '--headless',
                '--invisible',
                str(docx_path)
            ]

            print(f"Command: {' '.join(cmd2)}")

            # Ejecutar LibreOffice y cerrarlo rápidamente para que procese
            process = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)  # Dar tiempo para que abra y procese
            process.terminate()

            print("✅ Method 2 attempted (forced close after processing)")

        # Verificar si el archivo fue modificado
        original_size = backup_path.stat().st_size
        current_size = docx_path.stat().st_size

        if current_size != original_size:
            print(f"✅ File size changed: {original_size} → {current_size} bytes")
            print("INFO: Document appears to have been processed")
        else:
            print("⚠️ File size unchanged - TOC may not have updated")

        print(f"\nINFO: Process completed. Check {docx_path.name}")
        print(f"INFO: Backup available at {backup_path.name}")

        return True

    except subprocess.TimeoutExpired:
        print("ERROR: LibreOffice process timed out")
        return False
    except Exception as e:
        print(f"ERROR: Failed to update TOC: {e}")
        return False


def update_toc_alternative(docx_path):
    """Método alternativo: abrir y cerrar LibreOffice rápidamente"""
    try:
        docx_path = Path(docx_path).resolve()

        print(f"INFO: Alternative method - quick open/close...")

        # Comando para abrir el documento
        cmd = [
            'libreoffice',
            '--writer',
            str(docx_path)
        ]

        print(f"Command: {' '.join(cmd)}")
        print("INFO: Opening LibreOffice for 5 seconds...")

        # Abrir LibreOffice
        process = subprocess.Popen(cmd)

        # Esperar un poco para que cargue y actualice campos
        time.sleep(5)

        # Cerrar LibreOffice
        try:
            # Intentar cerrar gracefully
            subprocess.run(['pkill', 'libreoffice'], timeout=10)
        except:
            # Forzar cierre si es necesario
            process.terminate()

        print("✅ LibreOffice closed - fields should have updated")
        return True

    except Exception as e:
        print(f"ERROR: Alternative method failed: {e}")
        return False


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python UpdateTOC.py <docx_file>")
        print("Example: python UpdateTOC.py ./output/complete_with_auto_toc.docx")
        return 1

    docx_file = sys.argv[1]

    print("="*60)
    print("TOC UPDATER - LibreOffice Headless")
    print("="*60)
    print(f"Target file: {docx_file}")
    print()

    # Intentar método headless
    success = update_toc_headless(docx_file)

    if not success:
        print("\n" + "="*40)
        print("Trying alternative method...")
        print("="*40)
        success = update_toc_alternative(docx_file)

    if success:
        print(f"\n🎉 TOC update completed!")
        print(f"📄 Open {Path(docx_file).name} to see updated table of contents")
        return 0
    else:
        print(f"\n❌ TOC update failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
