import os

"""
GIMP .gpl palette exporter v0.1


Check custom fields like:

- Columns -> The number of colours will be shown at the same time when using the pallete unside GIMPs
"""


def export_gimp(colours, columns=8, output_directory="palette_gpl"):

    palettes = {}


    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)
        
    os.makedirs(output_directory, exist_ok=True)
    


    for chart, colour_list in palettes.items():

        filename = os.path.join(output_directory, f"{chart.replace(' ', '_')}.gpl")
        


        with open(filename, "w", encoding="utf-8") as file:
            file.write("GIMP Palette\n")
            file.write(f"Name: {chart}\n")
            file.write(f"Columns: {columns}\n")
            file.write("#\n")
            
            for colour in colour_list:

                file.write(f"{colour['red']:3d} {colour['green']:3d} {colour['blue']:3d}\t{colour['code']}\n")
                
        print(f"[ D0NE! ] GIMP palette generated: {filename}")
