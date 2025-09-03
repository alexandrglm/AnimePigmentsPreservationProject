# Technical Decisions: Colour in the Anime Cel Pigment Preservation Project

*Technical analysis of the decisions, calculations, and colorimetric methodologies implemented in project v1.1*

---

How would you describe, in technical terms, a colour? 

The RGB numbers your monitor displays are rather like a specific translation for that device, but the "real" colour exists independently of any screen or printer.

In this world , each pigment had an **absolute colour** - a unique colorimetric identity measurable with spectrophotometers.   

In this case, to preserve the historical information faithfully, a**device-independent** colour space is needed.

---

### CIE L*a*b*: The DNA of Colour

CIE L*a*b*, as the "genetic code" of  any visible colour, have three components:

- **L*** (Lightness): How bright or dark it is (0-100)
- **a***: Green-red axis (-128 to +127)
- **b***: Blue-yellow axis (-128 to +127)

This space is calibrated according to **average human perception** (CIE 2° standard observer under D50 illuminant).   

That is, a difference of 1 unit in LAB represents roughly the same perceptual difference regardless of which colours we're comparing.

---

## Delta E CIE2000

Delta E is the "perceptual distance" between two colours. But it's not a simple mathematical subtraction - it's far more sophisticated.

### Why CIE2000 Rather Than Basic Delta E?

Traditional Delta E `(√[(ΔL)² + (Δa)² + (Δb)²])`has a problem: it treats all regions of colour space equally, but our eye doesn't work that way. It's more sensitive to certain changes than others.

**CIE2000 introduces perceptual corrections:**

1. **Lightness correction (SL)**: We're less sensitive to changes in mid-greys
2. **Chroma correction (SC)**: Changes in saturation are perceived differently depending on base saturation
3. **Hue correction (SH)**: Certain hues (like blues) are more "slippery" than others
4. **Interaction term (RT)**: Simultaneous changes in chroma and hue are amplified in certain regions

```
ΔE < 1.0  → "Excellent" (imperceptible)
1.0-3.0   → "Good" (barely perceptible)
3.0-6.0   → "Acceptable" (visible but usable)
6.0-10.0  → "Problematic" (clearly visible)
> 10.0    → "Unacceptable" (significant shift)
```

These thresholds aren't arbitrary - they come from **psychophysical studies** where human observers evaluated colour differences under controlled conditions.

---

## 🖨️ Printing Calibration:  ICC for CMYK

CMYK isn't actually a colour space - it's an **instruction set for printers**.   

The same `C=50%`, `M=30%`, `Y=80%`, `K=0%` will produce different colours on different papers with different inks.

That's the reason of existance for the `ICC - International Colour Consortium` profiles.

---

## The ICC Profile

For this project, **PSO Coated v3** has been chosen as our CMYK reference for several critical reasons:

1. Minded the **original cel materials (vinyl/acetate)** authenticity, **were inherently reflective and coated surfaces**, directly matching the glossy finish typical of animation reference materials.

2. Traditional anime pigments, their characteristics, were formulated to produce glossy, reflective finishes that enhanced colour saturation and vibrancy.

3. Specific ICC profile requirements are essential for preserving the most precise colour reproduction when transferring to paper through commercial printing processes.

**Crucially**, this approach enables the project's PDF generation phase to support both **embedded ICC workflow** (using the reference PSO Coated v3 profile) or  **custom ICC substitution** for pre-press or direct printing applications, adapting the entire project to specific printing house requirements and paper stocks.

---

### CMYK Matching - Pipeline

The **`LAB → CMYK`** transformation follows this pathway:

```
Original LAB values → PIL LAB Image → ICC Transform → CMYK Values
```

But here's the clever bit:  

> **Colour processing pipeline immediately converts back to LAB and calculate Delta E**. 

This gives the more **conversion accuracy** - how much colour shift occurs in the print translation, the better, ensuring a production-quality accuracy.

---

## Pantone Matching - Pipeline

Nearly everyone knows PANTONE these days, and any designer worth their salt would recognise that PANTONE 186 C is one of their signature reds, practically from memory.

Whilst PANTONE offers standardised colour charts - which, in this author's humble opinion, represent both a commercial constraint and rather a clever money-making scheme - matching specific colours remains a challenging endeavour.

Anyway, here follows the approach  used to identify the closest PANTONE tone, based on the LAB values that Pantone themselves provide on their website (*values updated to 2024; PANTONE owns their brand and colour formulations*):

For each anime pigment:

1. **Calculate Delta E CIE2000** against all ~2,000 Pantone colours
2. **Find minimum difference**
3. **Apply quality thresholds** (Matching rate preserved under ΔE 2.5)

Traditional anime pigments were formulated for **artistic effect**, not commercial printing.  

Some colours - particularly fluorescents, metallics, and highly saturated hues - simply don't exist in the Pantone universe.   

When a, for examplw, ΔE of 8.5 value for a match is reported, we're being honest:

> **"This is the closest Pantone, but it's still noticeably different."**

---

## 📊 Quality Metrics

Our processing engine tracks several key metrics:

### CMYK Conversion Success Rate: 98.5%

**What it means**: Nearly all colours convert to CMYK successfully **Why some fail**: Occasionally corrupted LAB data or out-of-gamut colours

### Mean Delta E < 3.0: Production Quality

**What it means**: Average colour shift during CMYK conversion is barely perceptible **Industry context**: Professional printing tolerates up to ±3.0 ΔE

### Pantone Match Rate > 80%

**What it means**: Four out of five anime colours have a reasonable Pantone equivalent **The missing 20%**: Highly saturated or special-effect pigments

---

## 🔬 Technical Implementation Decisions

### Precision Levels

| Data Type  | Precision  |                                                     |
| ---------- | ---------- | --------------------------------------------------- |
| LAB Values | 1 decimal  | Industry standard; matches spectrophotometer output |
| CMYK       | 2 decimals | Print industry requirement for process control      |
| Delta E    | 3 decimals | <1.0 threshold needs sub-decimal precision          |

### Rendering Intent: Relative Colorimetric

We use **Relative Colorimetric** with **Black Point Compensation** because:

- Preserves spot colours exactly (crucial for brand colours)
- Maps out-of-gamut colours to gamut boundary (better than clipping)
- Maintains colour relationships across the gamut

### Gamut Limitations

Many anime pigments exceed sRGB boundaries. Your monitor nor any printing simply **cannot display** them accurately.   

So, both sRGB and ProPhoto RGB values are provided:

- **sRGB**: What your monitor shows (clipped if necessary)
- **ProPhoto RGB**: Wider gamut for professional workflows

---

## 🔧 Processing Pipeline

### 1. Excel Parsing

- Extract LAB, RGB, and metadata from spectrophotometer measurements
- Validate data integrity (check for missing or corrupted values)
- Normalise colour codes and chart names

### 2. CMYK Processing

- **Colour space conversion**: LAB → CMYK via ICC transform
- **Accuracy calculation**: CMYK → LAB → Delta E measurement
- **Quality assessment**: Classify conversion quality

### 3. Pantone Matching

- **Brute force comparison**: Test against ~2,000 Pantone colours
- **Delta E CIE2000 calculation**: Computationally expensive but perceptually accurate
- **Best match selection**: Find minimum Delta E within acceptable thresholds

### 4. Self-Equivalences Processing

- Cross-reference colour codes between charts (STAC ↔ TAIYO-SHIKISAI)
- Historical mapping from production documentation
- Validate equivalences using colour similarity

### 5. Data Preservation

* XLSX sources are updated with the newest computed valued

* A JSON schema database, ready for further developments, are saved:
  
  ```json
  {
    "1": {
      "original_data": {
        "chart": "STAC - Base Chart",
        "code": "WHITE",
        "L": 92.5,
        "a": -1.4,
        "b": 7.4,
        "R": 235,
        "G": 234,
        "B": 219,
        "hex_srgb": "#EBEADB",
        "hex_prophoto": "#e3e4d5",
        "H": 56.0,
        "S": 7.0,
        "L_hsl": 92.0
      },
      "computed_data": {
        "C": 9.41,
        "M": 5.88,
        "Y": 14.12,
        "K": 0.0,
        "cmyk_delta_e00": 0.891,
        "pantone_name": "9064 C",
        "pantone_code": "13005",
        "pantone_delta_e00": 2.555
      },
      "correspondences": {
        "has_equivalences": false,
        "equivalences": {}
      }
    },
    "2": {
      "original_data": {
        "chart": "STAC - Base Chart",
        "code": "1",
        "L": 78.4,
  ...
      }
     }
  }
  ```

---

## But, in the end.... What's the biggest picture?

This isn't just about preserving old colours - it's about **maintaining artistic intent** across technological transitions.   

When a 1980s animator chose "STAC A-1" for a character's skin tone, they made an aesthetic decision.   

This project wants to ensure that decision remains intact whether you're viewing on a modern monitor, printing on contemporary paper, or specifying colours for digital recreation.

Every Delta E calculation, every ICC transformation, every Pantone match is a small act of **cultural preservation**. It's a bridge between the analogue craft tradition of cel animation and the digital tools of modern production.

---

## 📚 Standards and References

### Compliance Standards

- **CIE Publication 15:2004** - The mathematical foundation of modern colorimetry
- **ISO 12647-2:2013** - Print process control (why our CMYK values matter)
- **ICC.1:2010** - Colour management architecture (how our profiles work)

### Community Wisdom

The project draws from years of collective knowledge shared in:

- **Kanzenshuu forums** - Source for STAC/TAIYO charts spectrophotometry.
- **Nekomataya resources** - More TAIYO resources preservation.
- Some [**Anime Style Magazine**](https://animestyle.jp/column/) articles, are included in the scope of the project, to understand the colour process, the Colour Direction/Inspection guidelines in classic anime production, as well as for the sheer enjoyment of reading them :)

This analysis represents the intersection of art, science, and nostalgia - preserving the tools that created the visual language of anime so that anyone who wishes may study it, appreciate it, and continue building upon it.

---

**2025 - Anime Cel Pigment References Preservation Project**
