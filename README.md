# Anime Cel Pigment References Preservation Project v1.1

## Technical Colour Workflow for Almost Any Classic Anime / Cel Pigment Charts

This document consolidates sources, specifications, decisions, and reference code to generate sRGB, CMYK samples and identify closest Pantone Colours from CIE L*a*b* values for:

* **スタック (STAC: Saito Tele-Anima Colors Co. Ltd.)**
* **太陽色彩 (TAIYO-SHIKISAI / 太陽色彩株式会社 ANIMATION. PAINT)**
* **Cel-Vinyl Colour Charts**

**Version:** 1.1 • **Date:** August, 2025

---

# AVAILABLE DATA

1. JSON format -> colours\_complete.json
2. BOOK PDF (with embedded PSCoated v3 ICC profile) -> BOOK-v1-1\_Anime\_CEL\_Pigments\_References\_Project-AlexandrGomez.pdf
3. EXCEL Original with the original spectrophotometric measurements used -> ORIGINAL\_Cel\_Animation\_Color\_Charts.xlsx

---

# ENGINE USAGE

## 1. Processing Pipeline (`main.py`)

This script processes the original Excel colour charts and generates a complete JSON database.

```bash
python main.py [excel_file] [options]
```

**Arguments:**

* `excel_file` *(optional)*: Path to the Excel file with colour charts. Default: `ORIGINAL_Cel_Animation_Color_Charts.xlsx`

**Options:**

* `-o, --output <file>`: Output JSON file. Default: `colours_complete.json`
* `-i, --icc-profile <icc>`: ICC profile for CMYK conversion. Default: `PSOcoated_v3.icc`
* `-p, --pantone-csv <csv>`: Pantone LAB database CSV. Default: `pantone_lab_2024.csv`
* `--no-backup`: Do not create backup of existing output file
* `-v, --verbose`: Enable verbose logging

**Example:**

```bash
python main.py ORIGINAL_Cel_Animation_Color_Charts.xlsx -o colours_complete.json -i PSOcoated_v3.icc -p pantone_lab_2024.csv -v
```

---

## 2. PDF Generator (`pdf_generator.py`)

This script generates professional PDF colour cards from the processed JSON data.

```bash
python pdf_generator.py <json_file> [output_pdf] [options]
```

**Arguments:**

* `json_file` *(required)*: Input JSON file with processed colour data
* `output_pdf` *(optional)*: Output PDF filename. Default: `colour_cards.pdf`

**Options:**

* `-j, --join <pdf>`: Prepend another PDF before the colour cards (e.g. cover, introduction)
* `--offset <n>`: Page numbering offset for merged documents. Default: `0`
* `-i, --icc-profile <icc>`: ICC profile for CMYK embedding. Default: `PSOcoated_v3.icc`
* `-v, --verbose`: Enable verbose output

**Example:**

```bash
python pdf_generator.py colours_complete.json colour_cards.pdf -j intro.pdf --offset 10 -i PSOcoated_v3.icc -v
```

---

## Workflow

1. Process Excel file → Generate JSON:

   ```bash
   python main.py ORIGINAL_Cel_Animation_Color_Charts.xlsx -o colours_complete.json
   ```
2. Generate professional PDF from JSON:

   ```bash
   python pdf_generator.py colours_complete.json colour_cards.pdf
   ```


---

# TECHNICAL DECISSIONS
---

## 1. Sources (LAB, RGB, Hex sRGB, Hex ProPhoto, HSL)

The colour specifications originate from captures and measurements performed on pigment charts for cels (vinyl).

The original dataset (without Pantone and CMYK conversions) was sourced from the Kanzenshuu community forum:

**Excel Colour List Source:**  
https://www.kanzenshuu.com/forum/viewtopic.php?t=19448

> ***I am grateful for the work carried out, which has made it possible to perform the rest of the conversions and cataloguing presented in this document***

### Original Measuring Devices Specifications
##### (From Analogic to Digital data 

| Measuring Device | Date Created | Notes |
|------------------|--------------|--------|
| Epson Perfection v600 | 2021-12-27 | 48-bit scanning, ProPhoto RGB embedded ICC profile |
| ColourMunki Photo | 2024-05-23 | Spectrophotometric remeasurement D50/2° standard observer |
| X-Rite i1Pro 2 | 2025-04-09 | Final wide-gamut capture addressing metamerism issues |

### Technical Scanning and Conversion Specifications

* Many pigment colours exceed sRGB gamut boundaries. Accurate display requires Rec.2020 compatible monitors (limited availability as of 2021).

* Original charts scanned at 48-bit depth, saved as TIFF with embedded ProPhoto RGB ICC profile for maximum colour fidelity.

* Spectrophotometric remeasurement provided device-independent CIE L*a*b* values as ground truth references.

* Derived sRGB values computed from L*a*b* coordinates with gamut clipping applied when colours fall outside sRGB boundaries.

* Neutral reference points standardized:  
  **BLACK at LAB(6,0,0) → sRGB(19,19,19)**  
  **WHITE at LAB(95,0,0) → sRGB(240,240,240)**

* STAC ↔ Taiyo-Shikisai conversion implemented via Toei Animation in-house lookup table (not physically equivalent colours).

* Physical chart aging and yellowing affected low-saturation/high-lightness samples. Retrobright treatment applied to restore accuracy.

### Database Evolution Timeline

| Date | Update Description |
|------|-------------------|
| **2025-08-24** | **Consolidation for STAC / TAIYO / USA CARTOON colour charts by including real CMYK values (using a PSOcoated V3 ICC colour profile). All the colour charts catalogued in one document as faithfully as possible to the original values, both in print (CMYK) and digitally on screen (sRGB).** |
| ***From here backwards, it corresponds to the original Excel work provided in the forum*** | |
| 2022-05-18 | Integration of older STAC chart scan. Colour code nomenclature updates. Deprecated codes mapping established |
| 2022-07-25 | ProPhoto RGB hexadecimal values added for workflow convenience |
| 2023-01-19 | Complete X-Colour chart digitization |
| 2023-01-20 | STAC A-Colour (those created by TOEI for USA animes) chart integration |
| 2023-01-27 | sRGB HSL values computed and added for UI/web design applications |
| 2023-02-21 | STAC ↔ Taiyo-Shikisai conversion table implemented from Toei reference |
| 2023-04-30 | Taiyo-Shikisai 595-Colour edition 8-booklet comprehensive scan |
| 2024-01-15 | Extended STAC ↔ Taiyo-Shikisai mapping with additional missing entries |
| 2024-05-13 | STAC spectrophotometric recapture replacing scanner-based measurements |
| 2024-05-15 | Sun Colour spectrophotometric update scanner version retained as reference |
| 2024-05-29 | X-Colour and A-Colour post-retrobright recapture with enhanced accuracy |
| 2025-02-01 | Cel-Vinyl chart addition wide-gamut colours beyond instrument limits |
| 2025-04-09 | Comprehensive i1Pro2 recapture metamerism correction for violet/pink hues |

---

## 2. ICC Profiles and European Selection (ECI/FOGRA)

For European commercial offset printing on coated substrates, the workflow employs **PSO Coated v3** (European Colour Initiative) as the primary CMYK destination profile.

This profile represents current industry standards for high-quality commercial printing and supersedes historical FOGRA39 in contemporary workflows.

Screen display maintains sRGB IEC61966-2-1 ICC profile compliance for maximum device compatibility and consistent colour reproduction across standard monitors.

### Technical Profile Specifications

* **CMYK Output Profile:** PSO Coated v3 (ECI) - European commercial coated paper standard

* **Colour Reference Space:** CIE L*a*b* D50/2° standard observer (device-independent ground truth)

* **RGB Working Space:** sRGB IEC61966-2-1 for display, ProPhoto RGB for archival/editing

* **Gamut Management:** Out-of-gamut colours handled via ICC profile rendering intent (perceptual/relative colorimetric)

* **Alternative Substrates:** FOGRA52 (uncoated), PSO Uncoated v3 (uncoated), FOGRA51 (newsprint)

Through the original script, using the Pantone-to-Lab CSV, it is possible to choose the ICC profile in use.

**NOTE:** This will positively affect the final colour displayed in CMYK; as an advantage, it allows adapting the document to any printing house in the world that may require any other type of ICC.

---

## 3. LAB ↔ CMYK Conversion Based on ICC Profiles

The colour space conversion implements a two-stage transformation pipeline to ensure compatibility with standard imaging libraries:

(i) CIE L*a*b* → sRGB intermediate conversion, followed by  
(ii) sRGB → CMYK conversion using **PSO Coated v3.icc** profile.

This approach provides robust input/output profile handling within Pillow/ImageCMS framework.

### Python Implementation Using Pillow/ImageCms

```python
# LAB → CMYK conversion via PSO Coated v3 ICC profile
# Two-stage transformation: LAB → sRGB → CMYK
from PIL import Image, ImageCms
import os

def lab_to_cmyk_pso(L, a, b, srgb_profile_path, cmyk_profile_path):
    """
    Convert CIE L*a*b* values to CMYK using PSO Coated v3 profile
    
    Parameters:
    L, a, b: CIE L*a*b* coordinates (D50/2°)
    srgb_profile_path: Path to sRGB ICC profile
    cmyk_profile_path: Path to PSO Coated v3 ICC profile
    
    Returns:
    tuple: CMYK values normalized (0.0-1.0)
    """
    
    # Validate input ranges
    L = max(0, min(100, L))
    a = max(-128, min(127, a))
    b = max(-128, min(127, b))
    
    # Create single-pixel LAB image
    # PIL LAB format: L(0-100) → (0-255), a,b(-128,127) → (0-255)
    lab_image = Image.new("LAB", (1, 1))
    lab_pixel = (
        int(L * 255 / 100),    # L: 0-100 → 0-255
        int(a + 128),          # a: -128,127 → 0,255
        int(b + 128)           # b: -128,127 → 0,255
    )
    lab_image.putpixel((0, 0), lab_pixel)
    
    # Stage 1: LAB → sRGB transformation
    lab_profile = ImageCms.createProfile("LAB")
    srgb_profile = ImageCms.getOpenProfile(srgb_profile_path)
    
    lab_to_srgb_transform = ImageCms.buildTransformFromOpenProfiles(
        lab_profile, srgb_profile,
        "LAB", "RGB",
        renderingIntent=ImageCms.INTENT_RELATIVE_COLORIMETRIC
    )
    
    srgb_image = ImageCms.applyTransform(lab_image, lab_to_srgb_transform)
    
    # Stage 2: sRGB → CMYK transformation
    cmyk_profile = ImageCms.getOpenProfile(cmyk_profile_path)
    
    srgb_to_cmyk_transform = ImageCms.buildTransformFromOpenProfiles(
        srgb_profile, cmyk_profile,
        "RGB", "CMYK",
        renderingIntent=ImageCms.INTENT_RELATIVE_COLORIMETRIC
    )
    
    cmyk_image = ImageCms.applyTransform(srgb_image, srgb_to_cmyk_transform)
    
    # Extract and normalize CMYK values
    C, M, Y, K = cmyk_image.getpixel((0, 0))
    cmyk_normalized = tuple(round(x / 255.0, 4) for x in (C, M, Y, K))
    
    return cmyk_normalized

# Usage example
if __name__ == "__main__":
    # Sample LAB coordinates (deep red pigment)
    L_sample, a_sample, b_sample = 30.8, 48.0, 7.0
    
    # ICC profile paths (ensure files exist)
    srgb_icc = "sRGB_IEC61966-2-1.icc"
    pso_v3_icc = "PSOcoated_v3.icc"
    
    try:
        cmyk_result = lab_to_cmyk_pso(
            L_sample, a_sample, b_sample,
            srgb_icc, pso_v3_icc
        )
        print(f"LAB({L_sample}, {a_sample}, {b_sample})")
        print(f"CMYK (PSO Coated v3): {cmyk_result}")
        
    except FileNotFoundError as e:
        print(f"ICC profile not found: {e}")
    except Exception as e:
        print(f"Conversion error: {e}")
```

---

## 4. Closest Pantone Calculation from L*a*b* (ΔE00)

Pantone colour matching employs CIE ΔE00 (CIEDE2000) colour difference formula to quantify perceptual colour differences between target CIE L*a*b* coordinates and Pantone Solid Coated (C) reference library.

The algorithm identifies the Pantone colour with minimum ΔE00 value, providing the closest perceptual match.

CIEDE2000 (ΔE00) represents the most advanced colour difference formula, incorporating corrections for lightness, chroma, and hue perception non-linearities, particularly in blue and gray regions where human visual system exhibits reduced discrimination sensitivity.

### Pure Python CIEDE2000 Implementation

```python
# CIEDE2000 (ΔE00) Pure Python Implementation
# Complete implementation of CIE ΔE00 colour difference formula
# Reference: CIE Technical Report 142:2001

import math
import csv
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Lab:
    """CIE L*a*b* colour representation"""
    L: float  # Lightness (0-100)
    a: float  # Green-Red axis (-128 to +127)
    b: float  # Blue-Yellow axis (-128 to +127)

def delta_e_cie2000(lab1: Lab, lab2: Lab, 
                   kL: float = 1.0, kC: float = 1.0, kH: float = 1.0) -> float:
    """
    Calculate CIEDE2000 colour difference (ΔE00) between two L*a*b* colours
    
    Parameters:
    lab1, lab2: Lab colour objects
    kL, kC, kH: Parametric factors for lightness, chroma, hue (typically 1.0)
    
    Returns:
    float: CIEDE2000 colour difference value
    """
    
    L1, a1, b1 = lab1.L, lab1.a, lab1.b
    L2, a2, b2 = lab2.L, lab2.a, lab2.b
    
    # Step 1: Calculate C1, C2, C̄
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    C_bar = (C1 + C2) / 2.0
    
    # Step 2: Calculate G
    G = 0.5 * (1 - math.sqrt(C_bar**7 / (C_bar**7 + 25**7)))
    
    # Step 3: Calculate a'1, a'2, C'1, C'2
    a1_prime = a1 * (1 + G)
    a2_prime = a2 * (1 + G)
    C1_prime = math.sqrt(a1_prime**2 + b1**2)
    C2_prime = math.sqrt(a2_prime**2 + b2**2)
    
    # Step 4: Calculate h'1, h'2
    def calculate_hue_angle(a_prime, b):
        if a_prime == 0 and b == 0:
            return 0
        hue = math.degrees(math.atan2(b, a_prime))
        return hue % 360
    
    h1_prime = calculate_hue_angle(a1_prime, b1)
    h2_prime = calculate_hue_angle(a2_prime, b2)
    
    # Step 5: Calculate ΔL', ΔC', Δh', ΔH'
    delta_L_prime = L2 - L1
    delta_C_prime = C2_prime - C1_prime
    
    # Calculate Δh'
    if C1_prime * C2_prime == 0:
        delta_h_prime = 0
    elif abs(h2_prime - h1_prime) <= 180:
        delta_h_prime = h2_prime - h1_prime
    elif h2_prime - h1_prime > 180:
        delta_h_prime = h2_prime - h1_prime - 360
    else:
        delta_h_prime = h2_prime - h1_prime + 360
    
    # Calculate ΔH'
    delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * \
                   math.sin(math.radians(delta_h_prime / 2))
    
    # Step 6: Calculate L̄', C̄', h̄'
    L_bar_prime = (L1 + L2) / 2.0
    C_bar_prime = (C1_prime + C2_prime) / 2.0
    
    if C1_prime * C2_prime == 0:
        h_bar_prime = h1_prime + h2_prime
    elif abs(h1_prime - h2_prime) <= 180:
        h_bar_prime = (h1_prime + h2_prime) / 2.0
    elif abs(h1_prime - h2_prime) > 180 and (h1_prime + h2_prime) < 360:
        h_bar_prime = (h1_prime + h2_prime + 360) / 2.0
    else:
        h_bar_prime = (h1_prime + h2_prime - 360) / 2.0
    
    # Step 7: Calculate T
    T = (1 - 0.17 * math.cos(math.radians(h_bar_prime - 30)) +
         0.24 * math.cos(math.radians(2 * h_bar_prime)) +
         0.32 * math.cos(math.radians(3 * h_bar_prime + 6)) -
         0.20 * math.cos(math.radians(4 * h_bar_prime - 63)))
    
    # Step 8: Calculate SL, SC, SH
    SL = 1 + (0.015 * (L_bar_prime - 50)**2) / \
        math.sqrt(20 + (L_bar_prime - 50)**2)
    SC = 1 + 0.045 * C_bar_prime
    SH = 1 + 0.015 * C_bar_prime * T
    
    # Step 9: Calculate RT
    delta_theta = 30 * math.exp(-((h_bar_prime - 275) / 25)**2)
    RC = 2 * math.sqrt(C_bar_prime**7 / (C_bar_prime**7 + 25**7))
    RT = -RC * math.sin(2 * math.radians(delta_theta))
    
    # Step 10: Calculate ΔE00
    delta_E00 = math.sqrt(
        (delta_L_prime / (kL * SL))**2 +
        (delta_C_prime / (kC * SC))**2 +
        (delta_H_prime / (kH * SH))**2 +
        RT * (delta_C_prime / (kC * SC)) * (delta_H_prime / (kH * SH))
    )
    
    return delta_E00

def find_closest_pantone(target_L: float, target_a: float, target_b: float,
                        pantone_csv_path: str = "pantone_solid_coated.csv") -> \
                        Optional[Tuple[str, str, float]]:
    """
    Find closest Pantone Solid Coated colour using CIEDE2000
    
    Parameters:
    target_L, target_a, target_b: Target CIE L*a*b* coordinates
    pantone_csv_path: Path to Pantone database CSV file
    
    CSV Format: PANTONE_NAME, UNIQUE_CODE, L, a, b
    Example: "PANTONE Red 032 C", "RED032C", 47.51, 68.42, 48.23
    
    Returns:
    tuple: (pantone_name, unique_code, delta_e00) or None if no matches
    """
    
    target_lab = Lab(float(target_L), float(target_a), float(target_b))
    best_match = None
    min_delta_e = float('inf')
    
    try:
        with open(pantone_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Filter for Coated colours only
                if not row['PANTONE_NAME'].strip().endswith(' C'):
                    continue
                
                try:
                    pantone_lab = Lab(
                        float(row['L']),
                        float(row['a']),
                        float(row['b'])
                    )
                    
                    delta_e = delta_e_cie2000(target_lab, pantone_lab)
                    
                    if delta_e < min_delta_e:
                        min_delta_e = delta_e
                        best_match = (
                            row['PANTONE_NAME'].strip(),
                            row['UNIQUE_CODE'].strip(),
                            round(delta_e, 3)
                        )
                        
                except (ValueError, KeyError) as e:
                    continue  # Skip malformed entries
                    
    except FileNotFoundError:
        print(f"Pantone database file not found: {pantone_csv_path}")
        return None
    
    return best_match

# Usage example and interpretation
if __name__ == "__main__":
    # Example: Find closest Pantone for a red pigment
    sample_L, sample_a, sample_b = 42.3, 58.1, 29.7
    
    closest = find_closest_pantone(sample_L, sample_a, sample_b)
    
    if closest:
        name, code, delta_e = closest
        print(f"Target LAB: ({sample_L}, {sample_a}, {sample_b})")
        print(f"Closest Pantone: {name}")
        print(f"Code: {code}")
        print(f"ΔE00: {delta_e}")
        
        # Perceptual interpretation
        if delta_e < 1.0:
            quality = "imperceptible difference"
        elif delta_e < 2.0:
            quality = "barely perceptible"
        elif delta_e < 5.0:
            quality = "noticeable but acceptable"
        else:
            quality = "clearly different colours"
            
        print(f"Quality assessment: {quality}")
    else:
        print("No Pantone match found")
```

### ΔE00 Interpretation and Technical Considerations

* **ΔE00 < 1.0:** Imperceptible difference under standard viewing conditions
* **ΔE00 1.0-2.0:** Barely perceptible to trained observers under optimal conditions
* **ΔE00 2.0-5.0:** Noticeable difference but acceptable for commercial applications
* **ΔE00 5.0-10.0:** Clear colour difference, requires attention in critical applications
* **ΔE00 > 10.0:** Distinctly different colours, unsuitable for colour matching

### Technical Limitations and Accuracy Considerations

* Some colours exceed Pantone Solid Coated gamut boundaries, resulting in ΔE00 > 5.0
* Colour matches valid under D50 illuminant may vary under different light sources
* Pantone physical standards have ±1.5 ΔE00 manufacturing tolerance
* **Spectral Considerations:** Fluorescent or metallic pigments cannot be accurately matched to conventional Pantone colours
* Individual colour perception differences may affect practical colour matching results

> **Calculations performed here maintain values below ΔE00 3.0, making the conversions as faithful as possible in most cases.**

---

## 5. CMYK-Calibrated PDF/ePUB Document

For professional colour documentation **requiring both screen display and print reproduction**, the recommended format presents dual colour swatches (sRGB and real CMYK simulation) accompanied by comprehensive technical data tables, ensuring accurate colour communication across digital and print media workflows.

Future EPUB implementation should embed RGB colour swatches with sRGB ICC profile metadata while maintaining numeric colour data in accessible text format.

PDF/X standards are reserved for pre-press applications requiring embedded CMYK colour spaces.

### Recommended Data Structure Per Colour Sample

| Field | Description | Technical Specifications |
|-------|-------------|-------------------------|
| Visual Swatch (sRGB) | Screen-optimized colour display | sRGB IEC61966-2-1<br>Gamma 2.2, D65 white point |
| Visual Swatch (CMYK) | Print simulation preview | PSO Coated v3 profile<br>Relative colorimetric intent |
| CIE L*a*b* Reference | Device-independent colour coordinates | D50/2° standard observer<br>Primary colour reference |
| CMYK Values (PSO Coated v3) | European commercial print values | Normalized 0.0-1.0 range<br>Coated paper substrate |
| sRGB/Hex Values | Digital design workflow data | 0-255 integer range<br>Hexadecimal notation |
| HSL Values | User interface colour specification | Hue (0-360°), Saturation (%)<br>Lightness (%) in sRGB space |
| Closest Pantone C (ΔE00) | Physical colour matching reference | CIEDE2000 colour difference<br>Pantone Solid Coated library |

### Implementation Guidelines

* **PDF Format:** Embed ICC profiles, use PDF/X-4 for prepress, include spot colour definitions for Pantone references
* **EPUB Format:** RGB images with embedded sRGB profile, CSS colour specifications, accessible numeric data tables
* **Web Display:** sRGB colour swatches, CSS HSL/RGB values, responsive design for mobile colour evaluation
* **Print Proofing:** CMYK separations with embedded PSO Coated v3 profile, overprint preview enabled

### Quality Assurance and Validation Requirements

* Verify sRGB display under D65 illuminant, validate CMYK proofs under D50 viewing conditions
* Document out-of-gamut colours with appropriate warning indicators and clipping notes
* Test colour reproduction across different operating systems and display technologies
* Include textual colour descriptions and numeric values for vision-impaired users

### Warnings and Technical Limitations

* Colours exceeding sRGB/CMYK gamut boundaries undergo automatic clipping with potential colour shift
* Results are computational approximations; physical verification with Pantone Colour Bridge required
* Colour appearance depends on illuminant and observer; maintain D50/2° reference standards
* Commercial printing introduces ±2-3 ΔE00 variation; specify acceptable tolerance ranges

---
**— End of Technical Documentation —**
---
### Best Valuable Sources

* https://www.kanzenshuu.com/forum/viewtopic.php?t=19448
* http://www.style.fm/as/05_column/tsujita/tsujita_bn.shtml
* https://animestyle.jp/column/
* https://www.nekomataya.info/
---
# ***Work done out of love for colour and the preservation of handmade anime!***
