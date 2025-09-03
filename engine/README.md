# Anime Cel Pigment References Preservation Project v1.1

## Core Processing Engine

A complete colorimetric processing pipeline for converting classic anime cel pigment charts to modern digital formats with CMYK conversions, Pantone matching, and cross-chart equivalences.

**Version:** 1.1 • **Date:** September 2025

---

## 🚀 Engine Overview

#### PATH: `./engine/01-colour_engines-pdf`

The engine consists of two main components:

1. **`1-main.py`** - Complete processing pipeline orchestrator
2. **`2-pdf_generator.py`** - Professional PDF colour reference generator

---

## 🔧 1. Main Processing Pipeline (`1-main.py`)

The core orchestrator that coordinates all processing modules to create a complete colour database from Excel charts.

### Usage

```bash
python ./engine/01-colour_engines-pdf/1-main.py [excel_file] [options]
```

### Arguments

- `excel_file` *(optional)*: Excel file path (default: `ORIGINAL_Cel_Animation_Color_Charts.xlsx`)

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <file>` | Output JSON file | `colours_complete.json` |
| `-i, --icc-profile <icc>` | ICC profile for CMYK conversion | `PSOcoated_v3.icc` |
| `-p, --pantone-csv <csv>` | Pantone LAB database CSV | `pantone_lab_2024.csv` |
| `--no-backup` | Don't backup existing output | |
| `-v, --verbose` | Enable verbose logging | |

### Examples

**Basic processing:**
```bash
python ./engine/01-colour_engines-pdf/1-main.py
```

**Full processing with custom files:**
```bash
python ./engine/01-colour_engines-pdf/1-main.py ORIGINAL_Cel_Animation_Color_Charts.xlsx \
  -o colours_complete.json \
  -i PSOcoated_v3.icc \
  -p pantone_lab_2024.csv \
  -v
```

### Processing Pipeline Steps

The engine performs the following processing steps automatically:

1. **Input Validation** - Validates all required files exist
2. **Excel Parsing** - Extracts colour data from Excel sheets using `excel_parser.py`
3. **CMYK Processing** - Converts LAB to CMYK using ICC profiles via `colour_processor.py`
4. **Pantone Matching** - Finds closest Pantone matches using ΔE00 via `pantone_matcher.py`
5. **Equivalences Processing** - Adds cross-chart colour equivalences via `equivalences.py`
6. **Output Generation** - Saves complete JSON database with metadata

### Required Modules

The pipeline depends on these Python modules (must be in same directory):

- `excel_parser.py` - Excel colour chart parser
- `colour_processor.py` - CMYK conversion and colour space transformations
- `pantone_matcher.py` - Pantone colour matching using CIE ΔE00
- `equivalences.py` - Cross-chart equivalences processor

### JSON Output Structure

```json
{
  "1": {
    "original_data": {
      "chart": "STAC",
      "code": "A-1",
      "L": 25.4, "a": -1.5, "b": -5.0,
      "R": 55, "G": 61, "B": 68,
      "hex_srgb": "#373D44",
      "hex_prophoto": "#363C43"
    },
    "computed_data": {
      "C": 9.41, "M": 5.88, "Y": 14.12, "K": 0.00,
      "cmyk_delta_e00": 2.150,
      "pantone_name": "Cool Gray 11 C",
      "pantone_code": "PANTONE Cool Gray 11 C",
      "pantone_delta_e00": 3.245
    },
    "correspondences": {
      "has_equivalences": true,
      "equivalences": {
        "TAIYO": ["T-101", "T-102"]
      }
    }
  },
  "metadata": {
    "source_file": "ORIGINAL_Cel_Animation_Color_Charts.xlsx",
    "processing_date": "2025-09-03T14:30:00",
    "total_processing_time_seconds": 45.7,
    "final_statistics": {
      "cmyk_success_rate": 98.5,
      "pantone_match_rate": 89.2,
      "equivalences_rate": 67.8
    }
  }
}
```

---

## 📄 2. PDF Reference Generator (`2-pdf_generator.py`)

Generates professional PDF colour reference books from processed JSON data with embedded ICC profiles and complete colorimetric information.

### Usage

```bash
python ./engine/01-colour_engines-pdf/2-pdf_generator.py <json_file> [output_pdf] [options]
```

### Arguments

- `json_file` *(required)*: Processed JSON data file from main pipeline
- `output_pdf` *(optional)*: Output PDF filename (default: `colour_cards.pdf`)

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-j, --join <pdf>` | Prepend PDF document (cover/intro) | |
| `--offset <n>` | Page numbering offset | `0` |
| `-i, --icc-profile <icc>` | ICC profile for embedding | `PSOcoated_v3.icc` |
| `-v, --verbose` | Enable verbose output | |

### Examples

**Basic PDF generation:**
```bash
python ./engine/01-colour_engines-pdf/2-pdf_generator.py colours_complete.json
```

**Professional book with cover and custom ICC:**
```bash
python ./engine/2-pdf_generator.py colours_complete.json colour_reference_book.pdf \
  -j cover_intro.pdf \
  --offset 10 \
  -i PSOcoated_v3.icc \
  -v
```

### PDF Features

- **Visual index pages** with colour swatches organised by chart
- **Individual colour pages** with complete colorimetric data
- **ICC profile embedding** for print accuracy
- **Pantone matching data** and CMYK conversion values
- **Cross-chart equivalences** when available
- **Professional typography** with custom fonts
- **Metadata embedding** for archival purposes

### PDF Structure

1. **Index Pages** - Visual grid of all colours grouped by chart
2. **Chart Sections** - Individual pages for each colour containing:
   - Large colour swatch (sRGB and ProPhoto RGB)
   - Complete colorimetric data (LAB, CMYK, RGB, HSL, Hex)
   - Pantone match information with ΔE00 values
   - Cross-chart equivalences
   - CMYK conversion accuracy metrics

---

## ⚙️ Technical Workflow

### Colour Processing Pipeline

1. **CIE L\*a\*b*** (device-independent reference)
2. **LAB → CMYK** via ICC profile transformation
3. **LAB → RGB** for display compatibility  
4. **Pantone Matching** using CIE ΔE00 minimisation

### Quality Benchmarks

| Metric | Target | Current Performance |
|--------|--------|-------------------|
| CMYK Mean ΔE | < 3.0 | ✅ Acceptable for production |
| Excellent Rate | > 60% | ✅ Most colours imperceptible |
| Problematic Rate | < 10% | ✅ Minimal visible shifts |
| Pantone Match Rate | > 80% | ✅ Industry completeness |

---

## 📋 Dependencies

### Required Files

- `ORIGINAL_Cel_Animation_Color_Charts.xlsx` - Source colour data
- `PSOcoated_v3.icc` - ICC profile for CMYK conversion
- `pantone_lab_2024.csv` - Pantone colour database
- Font files: `1.ttf`, `2.ttf`, `3.ttf` - Custom typography

### Python Libraries

**Core Processing:**
- `pandas`, `openpyxl` - Excel processing
- `PIL`, `ImageCms` - Colour transformation
- `colormath` - Delta E calculations

**PDF Generation:**
- `reportlab` - PDF creation
- `pikepdf` - ICC profile embedding

---

## ⚠️ Technical Limitations

### Gamut Considerations
- Many pigment colours exceed sRGB gamut boundaries
- Accurate display requires wide-gamut monitors
- Out-of-gamut colours undergo clipping with potential shifts

### Viewing Conditions
- Results optimised for D50/2° standard observer
- Commercial printing introduces ±2-3 ΔE00 variation
- Colour appearance varies with illuminant and observer

---

## 🔗 Standards Compliance

- **CIE Publication 15:2004** - Colorimetry, 3rd Edition
- **ISO 12647-2:2013** - Process control for offset lithographic processes
- **ICC.1:2010** - Colour management architecture and profile format

---

## 📈 Processing Summary Output

The engine provides comprehensive processing statistics:

```
🚀 STARTING COLOR PROCESSING PIPELINE
===============================================================================
📊 PROCESSING RESULTS:
   Total Colors Processed: 847
   Source File: ORIGINAL_Cel_Animation_Color_Charts.xlsx
   Output File: colours_complete.json
   Total Processing Time: 45.7 seconds

📈 SUCCESS RATES:
   CMYK Conversion: 98.5%
   Pantone Matching: 89.2%
   Equivalences Found: 67.8%

🔧 PROCESSING DETAILS:
   ICC Profile: PSOcoated_v3.icc
   Pantone Database: pantone_lab_2024.csv
   Correspondence Entries: 124

⚙️ PROCESSING STEPS:
   ✅ Input Validation: SUCCESS (0.1s)
   ✅ Excel Parsing: SUCCESS (2.3s)
   ✅ CMYK Processing: SUCCESS (18.4s)
   ✅ Pantone Matching: SUCCESS (21.2s)
   ✅ Equivalences Processing: SUCCESS (3.7s)

===============================================================================
🎉 PIPELINE COMPLETED SUCCESSFULLY!
```

---

**This engine is dedicated to preserving traditional cel animation materials and techniques with modern colorimetric accuracy.**

**2025 - Anime Cel Pigment References Preservation Project**
