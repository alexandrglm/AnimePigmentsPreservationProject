import os

"""
UNITY .C-sharp .cs (and compatibles) paletteformat module exporter v0.1
"""



def export_unity(colours, output_directory="palette_unity"):

    palettes = {}

    for colour in colours:

        palettes.setdefault(colour["chart"], []).append(colour)
        
    os.makedirs(output_directory, exist_ok=True)
    

    for chart, colour_list in palettes.items():

        filename = os.path.join(output_directory, f"{chart.replace(' ', '_')}.cs")
        

        with open(filename, "w", encoding="utf-8") as file:

            file.write(f"// Palette: {chart}\n")
            file.write("using UnityEngine;\n\n")
            file.write(f"public static class {chart.replace(' ', '_')}_Palette {{\n")
            

            for colour in colour_list:

                file.write(f"    public static readonly Color32 {colour['code']} = new Color32({colour['red']},{colour['green']},{colour['blue']},255);\n")
                
            file.write("}\n")
            
        print(f"[ D0NE !] Unity .cs file generated: {filename}")
