# Palette Creator – Documentation

## Overview

`Palette Creator` is a Python-based tool to generate colour palettes from JSON data into multiple formats compatible with software used in illustration, animation, manga, and design workflows.

>**Notice** that the **source values MUST the RGB ones **; if you want to use palettes directly for printing in CMYK, you must specify the CMYK values calculated from Lab-type values.

>**ICC Profiles can be embebbed ONLY when using Krita**

It supports:

| No | Software   | Format                   | Notes / Import Path                                                                                                                                      |
| -- | ---------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | GIMP-gpl   | `.gpl` ASCII             | Import via `Windows → Dockable Dialogs → Palettes → Import Palette`                                                                                      |
| 2  | CSS        | `.css`                   | Generates variables: `--ColourName: rgb(R,G,B);`                                                                                                         |
| 3  | SCSS       | `.scss`                  | Generates variables: `$ColourName: rgb(R,G,B);`                                                                                                          |
| 4  | Unity      | `.cs` or `.unitypalette` | Colours as `Color(r,g,b,1)` floats 0–1                                                                                                                   |
| 5  | ASE        | `.ase` binary            | Compatible with Photoshop, Illustrator, Affinity, Corel; RGB; type global=0                                                                              |
| 6  | TXT Simple | `.txt`                   | Each line: `R G B   ColourName`; compatible with Clip Studio, SAI, OpenToonz, Harmony                                                                    |
| 7  | Krita      | `.kpl` ZIP               | Contains `colorset.xml`, `profiles.xml`, `mimetype`; default sRGB profile; import via `Palette → Import Palette`; supports embedding custom ICC profiles |

Each palette is generated per **chart** defined in the JSON, with colour names and RGB values.

---

## Installation

1. Ensure Python 3.8+ is installed.
2. Clone this repository.
3. Install required dependencies (for GIMP/Unity/SCSS/CSS/Krita modules, all use standard Python; ASE module is standalone):

```bash
pip install swatch
```

---

## Usage

From the shell:

```bash
python3 1-palette_generator.py <path_to_json_file>
```

The program will:

1. Load the JSON file.
2. List the total colours and charts.
3. Show a menu of software options:

```
1: GIMP-gpl
2: CSS
3: SCSS
4: Unity
5: ASE .ase (Photoshop/Affinity/Corel)
6: TXT Simple .txt (Clip Studio/SAI/OpenToonz/Harmony)
7: Krita (.kpl)
```

4. For GIMP .gpl palettes, shell prompts for the number of **columns** (will be shown in GIMP) (default: 8).
5. For Krita `.kpl` palettes, the shell prompts whether to embed a **custom ICC profile** (optional). If no profile is provided, a default empty ICC or sRGB is used.
6. Generates palettes in the corresponding format, one file per chart.

---

## JSON Format Requirements

* Each colour entry must have numeric key.
* Required fields per colour:

```json
"original_data": {
    "chart": "Chart Name",
    "code": "ColourName",
    "R": 0–255,
    "G": 0–255,
    "B": 0–255
}
```

* Non-numeric keys (e.g., `metadata`) are ignored.

---

## Output

* Palettes are generated **per chart** in subfolders (`paletas_gimp`, `paletas_ase`, `paletas_kpl`, etc.).
* Files are named: `<chart_name>.<extension>`, spaces replaced by underscores.

---

## Notes

* ASE binary generation uses built-in Python struct module; no external library required.
* For printing or colour matching, RGB may differ slightly from CMYK output; consider ICC profile conversion for accurate printing.
* Krita `.kpl` files optionally support embedding a custom ICC profile; other formats do not support ICC embedding.
* All variable names are derived from JSON `code` and sanitized for each format.

---

## Recommended Import Paths / Tips

| Software                                | Recommended Import Path / Notes                                              |
| --------------------------------------- | ---------------------------------------------------------------------------- |
| GIMP                                    | `Windows → Dockable Dialogs → Palettes → Import Palette`, select `.gpl` file |
| Krita                                   | `Palette → Import Palette`, select `.kpl` file; optionally embed custom ICC  |
| Photoshop                               | `Window → Swatches → Load Swatches`, select `.ase` file                      |
| Illustrator                             | `Swatches Panel → Open Swatch Library → Other Library`, select `.ase` file   |
| Affinity Designer                       | `Swatches → Import Palette`, select `.ase` file                              |
| CorelDRAW                               | `Window → Colour Palettes → Open Palette`, select `.ase` file                |
| Clip Studio / SAI / OpenToonz / Harmony | Open the `.txt` file as simple palette, or import via palette editor         |
| Unity                                   | Place palette file in project folder, use C# script or asset importer        |

---

