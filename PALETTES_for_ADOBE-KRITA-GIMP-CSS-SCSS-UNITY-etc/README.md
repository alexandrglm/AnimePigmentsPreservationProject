# Palette files

Each palette was generated per **chart** defined in the colours JSON included/generated inside the scope of this project, with colour names and RGB values.


| No | Software   | Format                   | Notes / Import Path                                                                                                                                      |
| -- | ---------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | GIMP-gpl   | `.gpl` ASCII             | Import via `Windows → Dockable Dialogs → Palettes → Import Palette`                                                                                      |
| 2  | CSS        | `.css`                   | Generates variables: `--ColourName: rgb(R,G,B);`                                                                                                         |
| 3  | SCSS       | `.scss`                  | Generates variables: `$ColourName: rgb(R,G,B);`                                                                                                          |
| 4  | Unity      | `.cs` or `.unitypalette` | Colours as `Color(r,g,b,1)` floats 0–1                                                                                                                   |
| 5  | ASE        | `.ase` binary            | Compatible with Photoshop, Illustrator, Affinity, Corel; RGB; type global=0                                                                              |
| 6  | TXT Simple | `.txt`                   | Each line: `R G B   ColourName`; compatible with Clip Studio, SAI, OpenToonz, Harmony                                                                    |
| 7  | Krita      | `.kpl` ZIP               | Contains `colorset.xml`, `profiles.xml`, `mimetype`; default sRGB profile; import via `Palette → Import Palette`; also Krita palettes with custom ICC profile added **(PSO Coated V3)** |



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
