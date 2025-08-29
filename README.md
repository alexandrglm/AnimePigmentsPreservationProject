# Anime Cel Pigment References Preservation Project v1.1

## Technical Colour Workflow for Classic Anime/Cel Pigment Charts

A complete colorimetric database and processing pipeline for preserving and converting classic anime cel pigment charts to modern digital formats.

**Version:** 1.1 • **Date:** August 2025

### Supported Pigment Systems
- **スタック (STAC: Saito Tele-Anima Colors Co. Ltd.)**
- **太陽色彩 (TAIYO-SHIKISAI / ANIMATION PAINT)**
- **Cel-Vinyl Colour Charts**

---

##  Available Data Formats

| Format | File | Description |
|--------|------|-------------|
| **JSON** | `colours_complete.json` | Complete colorimetric database |
| **PDF** | `BOOK-v1-1_Anime_CEL_Pigments_References.pdf` | Professional reference book with embedded ICC profile |
| **Excel** | `ORIGINAL_Cel_Animation_Color_Charts.xlsx` | Original spectrophotometric measurements |


## Palette files for ADOBE, Unity, etc.

| No | Software   | Format                   | Notes / Import Path                                                                                                                                      |
| -- | ---------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | GIMP-gpl   | `.gpl` ASCII             | Import via `Windows → Dockable Dialogs → Palettes → Import Palette`                                                                                      |
| 2  | CSS        | `.css`                   | Generates variables: `--ColourName: rgb(R,G,B);`                                                                                                         |
| 3  | SCSS       | `.scss`                  | Generates variables: `$ColourName: rgb(R,G,B);`                                                                                                          |
| 4  | Unity      | `.cs` or `.unitypalette` | Colours as `Color(r,g,b,1)` floats 0–1                                                                                                                   |
| 5  | ASE        | `.ase` binary            | Compatible with almost any ADOBE software(Photoshop, Illustrator,...), also Affinity, Corel; RGB; type global=0                                                                              |
| 6  | TXT Simple | `.txt`                   | Each line: `R G B   ColourName`; compatible with Clip Studio, SAI, OpenToonz, Harmony                                                                    |
| 7  | Krita      | `.kpl` ZIP               | Contains `colorset.xml`, `profiles.xml`, `mimetype`; default sRGB profile; import via `Palette → Import Palette`; also Krita palettes with custom ICC profile added **(PSO Coated V3)** |

---

# ENGINE USAGE
---
## XLS Charts -> JSON Processor
### 1. Process Excel Charts → Generate JSON Database

Processes Excel colour charts and generates complete JSON database with CMYK conversions, Pantone matches, and equivalences.

```bash
python main.py [excel_file] [options]
```

#### Arguments
- `excel_file` *(optional)*: Excel file path (default: `ORIGINAL_Cel_Animation_Color_Charts.xlsx`)

#### Options
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <file>` | Output JSON file | `colours_complete.json` |
| `-i, --icc-profile <icc>` | ICC profile for CMYK conversion | `PSOcoated_v3.icc` |
| `-p, --pantone-csv <csv>` | Pantone LAB database CSV | `pantone_lab_2024.csv` |
| `--no-backup` | Don't backup existing output | |
| `-v, --verbose` | Enable verbose logging | |

#### Example
```bash
python ./engine/1-main.py ORIGINAL_Cel_Animation_Color_Charts.xlsx \
  -o colours_complete.json \
  -i PSOcoated_v3.icc \
  -p pantone_lab_2024.csv \
  -v
```

---
## 2 - PDF Reference Book Generator

- Allows custom ICC Profile use
- Allows prepending document at the start position
- Allows custom offset for a proper page numerartion

#### Usage
```bash
python ./engine/1-pdf_generator.py <json_file> [output_pdf] [options]
```

#### Arguments
- `json_file` *(required)*: Processed JSON data file
- `output_pdf` *(optional)*: Output PDF filename (default: `colour_cards.pdf`)

#### Options
| Option | Description | Default |
|--------|-------------|---------|
| `-j, --join <pdf>` | Prepend PDF (cover/intro) | |
| `--offset <n>` | Page numbering offset | `0` |
| `-i, --icc-profile <icc>` | ICC profile for embedding | `PSOcoated_v3.icc` |
| `-v, --verbose` | Enable verbose output | |

#### Example
```bash
python ./engine/2-pdf_generator.py colours_complete.json colour_cards.pdf \
  -j intro.pdf \
  --offset 10 \
  -i PSOcoated_v3.icc \
  -v
```
---

## 3 - Palette files generator for ADOBE, Krita, Corel, PaintTool SAI, etc...

#### Usage
```bash
python ./engine/plugin_palettes/1-palette_generator.py <json_file> [options]
```

#### Arguments
- `json_file` *(required)*: JSON palette file containing colour charts
- `[options]` *(optional)*: Flags and parameters for specific export formats

#### Options
| Option | Description | Default |
|--------|-------------|---------|
| `-f, --format <num>` | Choose software export format:<br>1: GIMP-gpl, 2: CSS, 3: SCSS, 4: Unity, 5: ASE, 6: TXT, 7: Krita | 1 |
| `-c, --columns <n>` | Number of columns for GIMP `.gpl` palettes | 8 |
| `-i, --icc-profile <icc>` | Embed custom ICC profile (Krita `.kpl` only) | `sRGB.icc` |
| `-v, --verbose` | Enable verbose output | Off |

#### Examples
- **Export all palettes to Krita `.kpl` with a custom ICC:**
  ```bash
  python ./engine/plugin_palettes/1-palette_generator.py colours.json -f 7 -i PSOcoated_v3.icc
  ```

  **Export GIMP `.gpl` with 12 columns:**
  ```bash
  python ./engine/plugin_palettes/1-palette_generator.py colours.json -f 1 -c 12
  ```

  **Export ASE for Photoshop/Affinity/Corel:**
  ```bash
  python 1-palette_generator.py colours.json -f 5
  ```
---
# PROJECT TECHNICAL DECISSIONS

## 📊 Data Sources & Evolution

### Original Sources
- **Excel Colour List**: [Kanzenshuu Forum](https://www.kanzenshuu.com/forum/viewtopic.php?t=19448)
- **Community Contributors**: Grateful acknowledgment to the original measurement work

### Measuring Equipment Evolution

| Date | Device | Notes |
|------|--------|-------|
| 2021-12-27 | Epson Perfection v600 | 48-bit scanning, ProPhoto RGB ICC profile |
| 2024-05-23 | ColourMunki Photo | Spectrophotometric remeasurement, D50/2° observer |
| 2025-04-09 | X-Rite i1Pro 2 | Final wide-gamut capture, metamerism correction |

### Database Timeline

| Date | Update |
|------|--------|
| **2025-08-24** | **Complete CMYK and PANTONE integration with PSOcoated V3 ICC profile** |
| 2024-05-13 | STAC spectrophotometric recapture |
| 2023-02-21 | STAC ↔ Taiyo-Shikisai conversion table from Toei reference |
| 2022-07-25 | ProPhoto RGB hexadecimal values added |
| 2022-05-18 | Older STAC chart integration and deprecated code mapping |

---

## 🎨 Technical Specifications

### Colour Space Standards
- **Reference Space**: CIE L*a*b* D50/2° standard observer
- **RGB Working Space**: sRGB IEC61966-2-1 (display), ProPhoto RGB (archival)
- **CMYK Profile**: PSO Coated v3 (ECI) - European commercial standard
- **Pantone Matching**: CIE ΔE00 (CIEDE2000) for perceptual accuracy

### Precision Requirements

| Data Type | Precision | Rationale |
|-----------|-----------|-----------|
| LAB Values | 1 decimal | Industry standard |
| RGB Values | Integer | 8-bit colour depth |
| CMYK Percentages | 2 decimals | Print industry requirement |
| Delta E CIE2000 | 3 decimals | <1.0 imperceptible threshold |
| Hex Values | Standard | #RRGGBB format, uppercase |

### Quality Thresholds (ΔE CIE2000)

| Range | Classification | Description |
|-------|----------------|-------------|
| < 1.0 | Excellent | Imperceptible difference |
| 1.0-3.0 | Good | Barely perceptible |
| 3.0-6.0 | Acceptable | Noticeable but usable |
| 6.0-10.0 | Problematic | Clearly visible |
| > 10.0 | Unacceptable | Significant colour shift |

---

## 🔬 Technical Decisions

### ICC Profile Selection
- **Primary**: PSO Coated v3 (ECI/FOGRA standards)
- **Rendering Intent**: Relative Colorimetric with Black Point Compensation
- **Rationale**: ISO 12647-2 standard for offset printing, preserves spot colours exactly

### Colour Conversion Pipeline
1. **CIE L*a*b*** (device-independent reference)
2. **LAB → CMYK** via ICC profile transformation
3. **LAB → RGB** for display compatibility
4. **Pantone Matching** using CIE ΔE00 minimization

### Data Structure
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
  }
}
```

---

## ⚠️ Technical Limitations

### Gamut Considerations
- Many pigment colours exceed sRGB gamut boundaries
- Accurate display requires Rec.2020 compatible monitors
- Out-of-gamut colours undergo clipping with potential shifts

### Viewing Conditions
- Results optimized for D50/2° standard observer
- Commercial printing introduces ±2-3 ΔE00 variation
- Colour appearance varies with illuminant and observer

### Material Considerations
- Physical chart aging affects low-saturation samples
- Fluorescent/metallic pigments cannot match conventional Pantones
- Individual colour perception differences may affect practical results

---

## Quality Benchmarks

| Metric | Target | Current Performance |
|--------|--------|-------------------|
| CMYK Mean ΔE | < 3.0 | ✅ Acceptable for production |
| Excellent Rate | > 60% | ✅ Most colours imperceptible |
| Problematic Rate | < 10% | ✅ Minimal visible shifts |
| Pantone Match Rate | > 80% | ✅ Industry completeness |

---

## Dependencies

### Required Files
- `ORIGINAL_Cel_Animation_Color_Charts.xlsx`
- `PSOcoated_v3.icc`
- `pantone_lab_2024.csv`
- Font files: `1.ttf`, `2.ttf`, `3.ttf`

### Python Libraries
- `pandas`, `openpyxl` (Excel processing)
- `PIL`, `ImageCms` (colour transformation)
- `reportlab` (PDF generation)
- `pikepdf` (ICC embedding)
- `colormath` (Delta E calculations)
- `swatch` (Binary parser for Adobe colour palettes)

---

## References & Standards

### Standards Compliance
- **CIE Publication 15:2004** - Colorimetry, 3rd Edition
- **ISO 12647-2:2013** - Process control for offset lithographic processes
- **ICC.1:2010** - Colour management architecture and profile format

### Community Resources
- [Kanzenshuu Forum](https://www.kanzenshuu.com/forum/viewtopic.php?t=19448)
- [AnimeStype Column](https://animestyle.jp/column/)
- [Nekomataya Info](https://www.nekomataya.info/)

---

# **This work is made with love for colour, dedicated to preserving traditional cel animation materials and techniques!**

**2025 - Anime Cel Pigment References Preservation Project**  

