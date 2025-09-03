#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkReader.py
Script básico para leer todos los bookmarks de un archivo DOCX
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def read_bookmarks(docx_path):
    """Leer todos los bookmarks de un archivo DOCX"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            # Leer document.xml
            document_xml = zip_file.read('word/document.xml')
            root = ET.fromstring(document_xml)

        # Namespace de Word
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        # Buscar todos los bookmarkStart
        bookmarks = []
        bookmark_starts = root.findall('.//w:bookmarkStart', ns)

        for bookmark in bookmark_starts:
            bookmark_id = bookmark.get(f'{{{ns["w"]}}}id')
            bookmark_name = bookmark.get(f'{{{ns["w"]}}}name')

            if bookmark_name and bookmark_name != '_GoBack':  # Skip Word's internal bookmark
                bookmarks.append({
                    'id': bookmark_id,
                    'name': bookmark_name
                })

        return bookmarks

    except Exception as e:
        print(f"ERROR: Could not read bookmarks from {docx_path}: {e}")
        return []


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python BookmarkReader.py <docx_file>")
        print("Example: python BookmarkReader.py ./output/complete_collection.docx")
        return 1

    docx_file = Path(sys.argv[1])

    if not docx_file.exists():
        print(f"ERROR: File not found: {docx_file}")
        return 1

    if not docx_file.suffix.lower() == '.docx':
        print(f"ERROR: File must be a .docx file")
        return 1

    print(f"Reading bookmarks from: {docx_file}")
    print("=" * 50)

    bookmarks = read_bookmarks(docx_file)

    if bookmarks:
        print(f"Found {len(bookmarks)} bookmarks:")
        print()
        for i, bookmark in enumerate(bookmarks, 1):
            print(f"{i:3d}. ID: {bookmark['id']:2s} | Name: {bookmark['name']}")
    else:
        print("No bookmarks found in this document.")

    print("=" * 50)
    print("In LibreOffice Writer:")
    print("• Navigate → Go to Page → Select 'Other Objects' → Select bookmark name")
    print("• Or: Insert → Cross-reference → Reference to: Bookmark")

    return 0


if __name__ == "__main__":
    sys.exit(main())
