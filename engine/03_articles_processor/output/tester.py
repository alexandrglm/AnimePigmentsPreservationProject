#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def read_bookmarks_with_position(docx_path):
    """Leer todos los bookmarks de un archivo DOCX con su posición aproximada"""
    bookmarks = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            root = ET.fromstring(document_xml)

        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        # Enumerar párrafos
        for p_idx, p in enumerate(root.findall('.//w:p', ns), 1):
            # Buscar bookmarks dentro del párrafo
            for bookmark in p.findall('.//w:bookmarkStart', ns):
                bookmark_id = bookmark.get(f'{{{ns["w"]}}}id')
                bookmark_name = bookmark.get(f'{{{ns["w"]}}}name')
                if bookmark_name and bookmark_name != '_GoBack':
                    # Posición aproximada: párrafo y posición de bookmark dentro del párrafo
                    children = list(p)
                    pos_in_p = children.index(bookmark) + 1
                    bookmarks.append({
                        'id': bookmark_id,
                        'name': bookmark_name,
                        'paragraph': p_idx,
                        'position_in_paragraph': pos_in_p
                    })

    except Exception as e:
        print(f"ERROR reading {docx_path}: {e}")

    return bookmarks

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <docx_file>")
        return 1

    docx_file = Path(sys.argv[1])
    if not docx_file.exists() or docx_file.suffix.lower() != '.docx':
        print("File not found or not a .docx")
        return 1

    bookmarks = read_bookmarks_with_position(docx_file)

    print(f"Reading bookmarks from: {docx_file}")
    print("="*50)
    print(f"Found {len(bookmarks)} bookmarks:\n")
    for i, bm in enumerate(bookmarks, 1):
        print(f"{i:3d}. ID: {bm['id']:2s} | Name: {bm['name']:20s} | Paragraph: {bm['paragraph']:3d} | Pos: {bm['position_in_paragraph']:2d}")

    print("="*50)
    print("In LibreOffice Writer: Go to Edit → Bookmarks… or Insert → Cross-reference → Bookmark")

if __name__ == "__main__":
    sys.exit(main())
