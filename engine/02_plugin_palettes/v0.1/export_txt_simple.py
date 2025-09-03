import os

"""
TXT palette module exporter v0.1

Accepted software:

- Clip Studio Paint
- PaintTool SAID
- OpenToonz / Harmony

CSV structure is:

R G B   ColourName

"""

def export_txt_simple(colours, output_directory="palette_txt"):

    palettes = {}

    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)
        
    os.makedirs(output_directory, exist_ok=True)
    


    for chart, colour_list in palettes.items():
        filename = os.path.join(output_directory, f"{chart.replace(' ', '_')}.txt")
        

        with open(filename, "w", encoding="utf-8") as file:

            for colour in colour_list:

                file.write(f"{colour['code']}: {colour['red']},{colour['green']},{colour['blue']}\n")
                
        print(f"[ D0NE! ] Simple TXT file generated: {filename}")
