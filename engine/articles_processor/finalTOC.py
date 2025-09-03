#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import tempfile
import shutil
import zipfile
import subprocess
import xml.etree.ElementTree as ET

from pathlib import Path


class SmartMergerWithAutoTOC:
    """Merger basado en FinalPartOne con TOC automático añadido"""

    def __init__(self):
        self.articles_dir = Path("./output/00_single_articles/")
        self.output_dir = Path("./output/")
        self.page_counts_file = self.output_dir / "articles_page_counts.json"
        self.articles_data = []

        # XML namespaces para Word
        self.namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }

        # Register namespaces
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def load_articles_list(self):
        """Cargar lista de artículos desde JSON"""
        try:
            if not self.page_counts_file.exists():
                raise FileNotFoundError(f"Page counts file not found: {self.page_counts_file}")

            with open(self.page_counts_file, 'r', encoding='utf-8') as f:
                self.articles_data = json.load(f)

            print(f"[INFO]: Found {len(self.articles_data)} articles to merge")
            return True

        except Exception as e:
            print(f"ERROR: Could not load articles list: {e}")
            return False

    def extract_docx_xml(self, docx_path):
        """Extraer XML de un archivo DOCX"""
        try:
            with zipfile.ZipFile(docx_path, 'r') as zip_file:
                document_xml = zip_file.read('word/document.xml')
                return ET.fromstring(document_xml)
        except Exception as e:
            print(f"ERROR: Could not extract XML from {docx_path}: {e}")
            return None

    def get_body_content(self, doc_root):
        """Extraer contenido del body de un documento XML"""
        try:
            body = doc_root.find('.//w:body', self.namespaces)
            if body is not None:
                return list(body)
            return []
        except Exception as e:
            print(f"ERROR: Could not extract body content: {e}")
            return []

    def create_auto_toc_field(self):
        """Crear field TOC automático usando la estructura de LibreOffice"""
        # Título "Table of Contents"
        toc_title = ET.Element(f"{{{self.namespaces['w']}}}p")

        # Propiedades del párrafo título
        title_props = ET.SubElement(toc_title, f"{{{self.namespaces['w']}}}pPr")
        title_style = ET.SubElement(title_props, f"{{{self.namespaces['w']}}}pStyle")
        title_style.set(f"{{{self.namespaces['w']}}}val", "TOCHeading")

        title_run = ET.SubElement(toc_title, f"{{{self.namespaces['w']}}}r")
        title_text = ET.SubElement(title_run, f"{{{self.namespaces['w']}}}t")
        title_text.text = "Table of Contents"

        # Párrafo del field TOC automático
        toc_field = ET.Element(f"{{{self.namespaces['w']}}}p")

        # Propiedades del párrafo TOC
        field_props = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}pPr")
        field_style = ET.SubElement(field_props, f"{{{self.namespaces['w']}}}pStyle")
        field_style.set(f"{{{self.namespaces['w']}}}val", "TOC1")

        # Tabs para alineación con puntos
        tabs = ET.SubElement(field_props, f"{{{self.namespaces['w']}}}tabs")
        tab_clear = ET.SubElement(tabs, f"{{{self.namespaces['w']}}}tab")
        tab_clear.set(f"{{{self.namespaces['w']}}}val", "clear")
        tab_clear.set(f"{{{self.namespaces['w']}}}pos", "9638")
        tab_right = ET.SubElement(tabs, f"{{{self.namespaces['w']}}}tab")
        tab_right.set(f"{{{self.namespaces['w']}}}val", "right")
        tab_right.set(f"{{{self.namespaces['w']}}}pos", "9637")
        tab_right.set(f"{{{self.namespaces['w']}}}leader", "dot")

        # Field begin
        field_begin = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}r")
        fld_char_begin = ET.SubElement(field_begin, f"{{{self.namespaces['w']}}}fldChar")
        fld_char_begin.set(f"{{{self.namespaces['w']}}}fldCharType", "begin")

        # Field instruction - usar H2 (ArticleH2) para generar TOC
        field_instr = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}r")
        instr_props = ET.SubElement(field_instr, f"{{{self.namespaces['w']}}}rPr")
        instr_style = ET.SubElement(instr_props, f"{{{self.namespaces['w']}}}rStyle")
        instr_style.set(f"{{{self.namespaces['w']}}}val", "IndexLink")

        instr_text = ET.SubElement(field_instr, f"{{{self.namespaces['w']}}}instrText")
        instr_text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        # TOC usando estilo ArticleH2
        instr_text.text = ' TOC \\f \\o "1-9" \\t "ArticleH2,1" \\h'

        # Field separate
        field_sep = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}r")
        sep_props = ET.SubElement(field_sep, f"{{{self.namespaces['w']}}}rPr")
        sep_style = ET.SubElement(sep_props, f"{{{self.namespaces['w']}}}rStyle")
        sep_style.set(f"{{{self.namespaces['w']}}}val", "IndexLink")
        fld_char_sep = ET.SubElement(field_sep, f"{{{self.namespaces['w']}}}fldChar")
        fld_char_sep.set(f"{{{self.namespaces['w']}}}fldCharType", "separate")

        # Placeholder content (se actualizará automáticamente)
        placeholder = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}r")
        placeholder_props = ET.SubElement(placeholder, f"{{{self.namespaces['w']}}}rPr")
        placeholder_style = ET.SubElement(placeholder_props, f"{{{self.namespaces['w']}}}rStyle")
        placeholder_style.set(f"{{{self.namespaces['w']}}}val", "IndexLink")
        placeholder_text = ET.SubElement(placeholder, f"{{{self.namespaces['w']}}}t")
        placeholder_text.text = "Actualizar campos (F9) para generar índice"

        # Field end
        field_end = ET.SubElement(toc_field, f"{{{self.namespaces['w']}}}r")
        end_props = ET.SubElement(field_end, f"{{{self.namespaces['w']}}}rPr")
        end_style = ET.SubElement(end_props, f"{{{self.namespaces['w']}}}rStyle")
        end_style.set(f"{{{self.namespaces['w']}}}val", "IndexLink")
        fld_char_end = ET.SubElement(field_end, f"{{{self.namespaces['w']}}}fldChar")
        fld_char_end.set(f"{{{self.namespaces['w']}}}fldCharType", "end")

        return [toc_title, toc_field]

    def create_page_break_element(self):
        """Crear elemento de salto de página"""
        page_break_para = ET.Element(f"{{{self.namespaces['w']}}}p")
        run_elem = ET.SubElement(page_break_para, f"{{{self.namespaces['w']}}}r")
        break_elem = ET.SubElement(run_elem, f"{{{self.namespaces['w']}}}br")
        break_elem.set(f"{{{self.namespaces['w']}}}type", "page")
        return page_break_para

    def add_auto_ref_bookmark_to_h2(self, title_paragraph, bookmark_id):
        """Añadir bookmark automático al título H2 para referencias del TOC"""
        try:
            # Generar nombre de bookmark único
            bookmark_name = f"__RefHeading___Toc{bookmark_id}_AutoGenerated"

            # Crear bookmark start
            bookmark_start = ET.Element(f"{{{self.namespaces['w']}}}bookmarkStart")
            bookmark_start.set(f"{{{self.namespaces['w']}}}id", str(bookmark_id))
            bookmark_start.set(f"{{{self.namespaces['w']}}}name", bookmark_name)

            # Crear bookmark end
            bookmark_end = ET.Element(f"{{{self.namespaces['w']}}}bookmarkEnd")
            bookmark_end.set(f"{{{self.namespaces['w']}}}id", str(bookmark_id))

            # Insertar bookmark_start al principio del párrafo
            title_paragraph.insert(0, bookmark_start)

            # Insertar bookmark_end al final del párrafo
            title_paragraph.append(bookmark_end)

            return True

        except Exception as e:
            print(f"ERROR: Could not add auto bookmark to H2: {e}")
            return False

    def convert_to_pdf_with_bookmarks(self, input_docx_path, output_pdf_path):
        """Convertir DOCX a PDF preservando bookmarks - usando método del proyecto"""
        try:
            input_docx = Path(input_docx_path)
            output_pdf = Path(output_pdf_path)

            print(f"[INFO]: Converting {input_docx.name} to PDF with bookmarks...")

            # Usar el método exacto de ArticlesDocx.py
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                str(input_docx.name)  # Solo el nombre, no el path completo
            ]

            print(f"DEBUG: Running command: {' '.join(cmd)}")
            print(f"DEBUG: Working directory: {input_docx.parent}")

            # Ejecutar desde el directorio donde está el archivo (como en el proyecto)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90,  # Mismo timeout que el proyecto
                cwd=str(input_docx.parent)  # Trabajar desde donde está el DOCX
            )

            print(f"DEBUG: LibreOffice exit code: {result.returncode}")
            if result.stdout:
                print(f"DEBUG: STDOUT: {result.stdout}")
            if result.stderr:
                print(f"DEBUG: STDERR: {result.stderr}")

            # LibreOffice genera el PDF con el mismo nombre base en el mismo directorio
            generated_pdf = input_docx.with_suffix('.pdf')

            print(f"DEBUG: Looking for generated PDF: {generated_pdf}")

            if generated_pdf.exists():
                # Si el nombre es diferente al deseado, mover/renombrar
                if generated_pdf != output_pdf:
                    if output_pdf.exists():
                        output_pdf.unlink()
                    shutil.move(str(generated_pdf), str(output_pdf))
                    print(f"DEBUG: Moved {generated_pdf.name} to {output_pdf}")

                print(f"[OK]  PDF created: {output_pdf.name}")
                print(f"📖 PDF includes navigation bookmarks from TOC")
                return True
            else:
                print(f"ERROR: PDF was not generated: {generated_pdf}")
                print(f"DEBUG: Files in directory {input_docx.parent}:")
                for f in input_docx.parent.iterdir():
                    if f.suffix.lower() == '.pdf':
                        print(f"  Found PDF: {f.name}")
                return False

        except subprocess.TimeoutExpired:
            print("ERROR: LibreOffice conversion timed out (90 seconds)")
            return False
        except Exception as e:
            print(f"ERROR: PDF conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def interactive_user_review(self, pre_toc_path):
        """Proceso interactivo: abrir LibreOffice, esperar edición, generar final"""
        try:
            print("\n" + "="*60)
            print("INTERACTIVE USER REVIEW PROCESS")
            print("="*60)

            # 1. Abrir LibreOffice Writer con el documento
            print(f"[INFO]: Opening {pre_toc_path.name} in LibreOffice Writer...")
            print("[INFO]: The TOC field is ready but needs to be updated manually")

            cmd = [
                'libreoffice',
                '--writer',
                str(pre_toc_path)
            ]

            process = subprocess.Popen(cmd)
            print(f"[OK]  LibreOffice Writer opened with PID: {process.pid}")

            # 2. Instrucciones para el usuario
            print("\n📝 USER INSTRUCTIONS:")
            print("="*40)
            print("1. Right-click on 'Table of Contents' --> Update Index")
            print("2. Review and edit the document as needed")
            print("3. Save the document (Ctrl+S) when satisfied")
            print("4. KEEP LibreOffice Writer OPEN")
            print("5. Return to this terminal and confirm completion")
            print()

            # 3. Esperar confirmación del usuario
            while True:
                user_input = input("📋 Have you updated TOC and saved? (y/n): ").lower().strip()

                if user_input in ['y', 'yes', 'sí', 'si']:
                    break
                elif user_input in ['n', 'no']:
                    print("⏳ Take your time. Press Enter when ready...")
                    input("Press Enter to continue...")
                    continue
                else:
                    print("Please answer 'y' for yes or 'n' for no")

            # 4. Solicitar nombres de archivo final
            print("\n" + "="*40)
            print("FINAL FILE NAMING")
            print("="*40)

            while True:
                final_docx_name = input("[OK]  Enter final DOCX filename (without .docx): ").strip()
                if final_docx_name:
                    if not final_docx_name.endswith('.docx'):
                        final_docx_name += '.docx'
                    break
                print("Please enter a filename")

            while True:
                final_pdf_name = input("[OK]  Enter final PDF filename (without .pdf): ").strip()
                if final_pdf_name:
                    if not final_pdf_name.endswith('.pdf'):
                        final_pdf_name += '.pdf'
                    break
                print("Please enter a filename")

            # 5. Paths finales
            final_docx_path = self.output_dir / final_docx_name
            final_pdf_path = self.output_dir / final_pdf_name

            # 6. Copiar el archivo editado al nombre final
            print(f"\n[INFO]: Creating final files...")
            shutil.copy2(str(pre_toc_path), str(final_docx_path))
            print(f"[OK]  Final DOCX: {final_docx_path.name}")

            # 7. Convertir a PDF con bookmarks
            print(f"\n[INFO]: Starting PDF conversion...")
            pdf_success = self.convert_to_pdf_with_bookmarks(final_docx_path, final_pdf_path)

            if pdf_success:
                print(f"[OK]  Final PDF: {final_pdf_path.name}")
                print(f"🔖 PDF includes navigation bookmarks")
            else:
                print(f"[WARN]  PDF conversion failed, but DOCX is ready")

            # 8. Notificar al usuario que puede cerrar LibreOffice
            print(f"\n[OK]  PROCESS COMPLETED!")
            print(f"[OK]  Final DOCX: {final_docx_name}")
            if pdf_success:
                print(f"[OK]  Final PDF: {final_pdf_name}")
            print(f"💡 You can now close LibreOffice Writer")

            return final_docx_path, final_pdf_path if pdf_success else None

        except Exception as e:
            print(f"ERROR: Interactive review failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def merge_all_articles_with_auto_toc(self, pre_toc_filename="PRE-TOC_user_pending.docx"):
        """
        Fusionar artículos usando la metodología de FinalPartOne + TOC automático
        Genera archivo PRE-TOC para revisión manual del usuario
        """
        print("="*60)
        print("FINALPARTONE WITH INTERACTIVE TOC REVIEW")
        print("="*60)

        # Cargar lista de artículos
        if not self.load_articles_list():
            return False

        try:
            # Usar article_001.docx como base (igual que FinalPartOne)
            base_article_path = self.articles_dir / "article_001.docx"
            if not base_article_path.exists():
                print(f"ERROR: Base article not found: {base_article_path}")
                return False

            print(f"[INFO]: Using {base_article_path.name} as base document (FinalPartOne method)...")

            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)

                # Copiar article_001.docx como base
                base_zip = temp_dir / "base.zip"
                shutil.copy2(base_article_path, base_zip)

                # Extraer DOCX
                with zipfile.ZipFile(base_zip, 'r') as zip_file:
                    zip_file.extractall(temp_dir / "docx_content")

                docx_content_dir = temp_dir / "docx_content"

                # Cargar document.xml del documento base
                doc_xml_path = docx_content_dir / "word" / "document.xml"
                doc_tree = ET.parse(doc_xml_path)
                doc_root = doc_tree.getroot()
                doc_body = doc_root.find('.//w:body', self.namespaces)

                if doc_body is None:
                    raise ValueError("[WARN] Could not find body in base document")

                # Obtener contenido original del article_001
                original_content = list(doc_body)

                # Limpiar el body
                doc_body.clear()

                # 1. AÑADIR TOC AUTOMÁTICO al principio
                print("[INFO]: Adding automatic TOC at the beginning...")
                toc_elements = self.create_auto_toc_field()
                for toc_elem in toc_elements:
                    doc_body.append(toc_elem)

                # Salto de página después del TOC
                doc_body.append(self.create_page_break_element())

                # 2. AÑADIR CONTENIDO DE ARTICLE_001 (con bookmark automático en H2)
                print(f"[INFO]: Adding {base_article_path.name} content with auto H2 bookmark...")

                # Buscar el título H2 (segunda línea con contenido) y añadir bookmark
                content_paragraphs_found = 0
                bookmark_id = 1

                for element in original_content:
                    if element.tag.endswith('}p'):
                        # Verificar si tiene texto
                        text_elements = element.findall(f'.//{{{self.namespaces["w"]}}}t')
                        if any(t.text and t.text.strip() for t in text_elements):
                            content_paragraphs_found += 1

                            # La segunda línea con contenido es el título H2
                            if content_paragraphs_found == 2:
                                self.add_auto_ref_bookmark_to_h2(element, bookmark_id)
                                bookmark_id += 1
                                print(f"  --> Added auto bookmark to H2 title")

                    doc_body.append(element)

                # 3. AÑADIR RESTO DE ARTÍCULOS (002-203)
                for article_info in self.articles_data[1:]:  # Skip article_001 ya procesado
                    article_number = article_info['article_number']
                    article_file = self.articles_dir / f"article_{article_number:03d}.docx"

                    if not article_file.exists():
                        print(f"[WARN]: Article file not found: {article_file}")
                        continue

                    print(f"[INFO]: Adding {article_file.name} with auto H2 bookmark...")

                    # Salto de página antes del siguiente artículo
                    doc_body.append(self.create_page_break_element())

                    # Extraer contenido del artículo
                    article_root = self.extract_docx_xml(article_file)
                    if article_root is None:
                        continue

                    article_content = self.get_body_content(article_root)

                    # Buscar título H2 y añadir bookmark automático
                    content_paragraphs_found = 0

                    for element in article_content:
                        # Skip sectPr
                        if element.tag.endswith('}sectPr'):
                            continue

                        if element.tag.endswith('}p'):
                            # Verificar si tiene texto
                            text_elements = element.findall(f'.//{{{self.namespaces["w"]}}}t')
                            if any(t.text and t.text.strip() for t in text_elements):
                                content_paragraphs_found += 1

                                # La segunda línea con contenido es el título H2
                                if content_paragraphs_found == 2:
                                    self.add_auto_ref_bookmark_to_h2(element, bookmark_id)
                                    bookmark_id += 1
                                    print(f"  --> Added auto bookmark to H2 title")

                        doc_body.append(element)

                # Guardar document.xml modificado
                doc_tree.write(doc_xml_path, encoding='utf-8', xml_declaration=True)

                # Recrear archivo DOCX (PRE-TOC para revisión)
                pre_toc_path = self.output_dir / pre_toc_filename
                with zipfile.ZipFile(pre_toc_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in docx_content_dir.rglob('*'):
                        if file_path.is_file():
                            archive_path = file_path.relative_to(docx_content_dir)
                            zip_file.write(file_path, archive_path)

                print(f"\n[OK]  PRE-TOC DOCUMENT CREATED!")
                print(f"[OK]  Generated: {pre_toc_path}")
                print(f" Features:")
                print(f"   • Automatic TOC field ready for update")
                print(f"   • All {len(self.articles_data)} articles merged")
                print(f"   • H2 bookmarks for navigation")
                print(f"   • Based on {base_article_path.name} styling")

                # Iniciar proceso interactivo de revisión
                final_docx, final_pdf = self.interactive_user_review(pre_toc_path)

                if final_docx:
                    print(f"\n[D0NE]  COMPLETE SUCCESS!")
                    print(f"[OK]  Final DOCX: {final_docx.name}")
                    if final_pdf:
                        print(f"[OK]  Final PDF: {final_pdf.name}")
                    print(f"[OK]  All files saved in: {self.output_dir}")
                    return True
                else:
                    print(f"\n[WARN]  Interactive review was cancelled or failed")
                    print(f"[OK]  PRE-TOC file available: {pre_toc_path}")
                    return False

        except Exception as e:
            print(f"ERROR: Merge with auto TOC failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("="*60)
    print("SMART MERGER WITH INTERACTIVE TOC REVIEW")
    print("="*60)
    print("This script will:")
    print("1. Merge all articles with automatic TOC field")
    print("2. Open LibreOffice for you to update TOC manually")
    print("3. Wait for your confirmation")
    print("4. Generate final DOCX and PDF files")
    print("="*60)
    print()

    # Create merger and run
    merger = SmartMergerWithAutoTOC()

    try:
        success = merger.merge_all_articles_with_auto_toc()

        if success:
            print(f"\n[D0NE]  All processes completed successfully!")
            return 0
        else:
            print(f"\n❌ Process was incomplete")
            return 1

    except KeyboardInterrupt:
        print("\n[WARN]  Process cancelled by user")
        return 130

    except Exception as e:
        print(f"\n[WARN]  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
