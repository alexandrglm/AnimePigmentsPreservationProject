# Anime Cel Pigment References - Document Processing Suite

Complete pipeline for converting Markdown articles to professional DOCX documents with automatic table of contents and PDF generation.

## Prerequisites

- **Python 3.x** with packages: `python-docx`, `pypdf`
- **LibreOffice** (for PDF conversion)
- **Directory structure**: `./todos/` containing `article_XXX.md` files

## Quick Start

### 1. Convert Markdown to Individual DOCX Files

```bash
python articlesProcessor.py ./todos/
```

**What it does:**
- Converts each `article_XXX.md` to `article_XXX.docx`
- Applies professional styling from `stylesCustom.py`
- Generates PDF for page counting
- Creates `articles_page_counts.json`

**Output:** `./output/00_single_articles/` with individual DOCX/PDF files

### 2. Merge All Articles with Interactive TOC

```bash
python finalTOC.py
```

**Interactive process:**
1. Generates `PRE-TOC_user_pending.docx`
2. Opens LibreOffice Writer automatically
3. **You:** Right-click "Table of Contents" → Update Index → Save
4. **You:** Return to terminal, confirm completion
5. **You:** Enter final filenames
6. Script generates final DOCX + PDF with bookmarks

---

## Detailed Usage

### articlesProcessor.py

**Basic usage:**
```bash
python articlesProcessor.py <markdown_directory> [output_directory]
```

**Options:**
```bash
python articlesProcessor.py ./todos/ -v --extract-titles
python articlesProcessor.py ./todos/ ./custom_output/ -io 5 -to 2
```

**Parameters:**
- `markdown_directory` - Path to markdown files (required)
- `output_directory` - Output path (optional, defaults to `./output/`)
- `-io INDEX_OFFSET` - Article index offset
- `-to TITLE_OFFSET` - Title offset
- `--extract-titles` - Extract article titles
- `-v` - Verbose output
- `-h` - Help

### finalTOC.py

**Basic usage:**
```bash
python finalTOC.py
```

**Process flow:**
1. **Automatic merging**: Uses `article_001.docx` as base template
2. **TOC generation**: Creates automatic table of contents field
3. **Interactive review**: Opens LibreOffice for manual TOC update
4. **Final output**: Generates named DOCX + PDF with navigation bookmarks

**Features:**
- Preserves all styling from `stylesCustom.py`
- Each article starts on new page
- TOC automatically references H2 titles
- PDF includes clickable bookmarks

### Utility Scripts

#### BookmarkReader.py
```bash
python BookmarkReader.py <docx_file>
```
Lists all bookmarks in a DOCX file for navigation reference.

#### UpdateTOC.py
```bash
python UpdateTOC.py <docx_file>
```
Attempts to update TOC fields using LibreOffice headless mode.

---

## File Structure

### Input Requirements
```
./todos/
├── article_001.md
├── article_002.md
├── article_003.md
└── ...
```

### Generated Output
```
./output/
├── 00_single_articles/
│   ├── article_001.docx
│   ├── article_001.pdf
│   └── ...
├── articles_page_counts.json
├── PRE-TOC_user_pending.docx
├── your_final_name.docx
└── your_final_name.pdf
```

---

## Complete Workflow

### Standard Process
```bash
# 1. Convert all markdown files to DOCX
python articlesProcessor.py ./todos/ -v

# 2. Merge with interactive TOC
python finalTOC.py
```

### Advanced Options
```bash
# Custom output directory and verbose logging
python articlesProcessor.py ./todos/ ./custom_output/ -v --extract-titles

# Check bookmarks in final document
python BookmarkReader.py ./output/final_collection.docx

# Force TOC update (if needed)
python UpdateTOC.py ./output/final_collection.docx
```

---

## Styling Configuration

All visual styling is controlled by `stylesCustom.py`:
- **Fonts**: BPG Serif, BPG Gorda, Amiri
- **Colours**: Dark blue headers, dark red subtitles
- **Spacing**: Unified paragraph and header spacing
- **Margins**: Professional A4 layout

Styles are automatically applied and preserved throughout the entire pipeline.

---

## Troubleshooting

### Common Issues

**LibreOffice not found:**
```bash
# Ubuntu/Debian
sudo apt install libreoffice

# macOS
brew install --cask libreoffice
```
##### Windows compatibility
LibreOffice shell required.


**Missing Python packages:**
```bash
pip install python-docx pypdf
```

**TOC not updating:**
- Use interactive mode in `finalTOC.py`
- Manual method: Right-click TOC → Update Index in LibreOffice

**PDF generation fails:**
- Ensure LibreOffice is installed and accessible
- Check file permissions in output directory

### Debug Information

Add `-v` flag to any script for verbose logging and detailed error information.

---

## Output Features

### DOCX Documents
- Professional typography with custom fonts
- Consistent styling across all articles
- Automatic table of contents with page references
- Page breaks between articles
- Preserved markdown formatting (headers, lists, code blocks)

### PDF Documents
- Clickable navigation bookmarks
- Preserved formatting and fonts
- Print-ready layout
- Bookmarks correspond to article titles (H2 headings)

---

**2025 - Anime Cel Pigment References Preservation Project**
