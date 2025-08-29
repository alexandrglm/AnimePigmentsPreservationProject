import os

"""
CSS/SaSS module exporter v0.1
"""

# CSS
def export_css(colours, output_directory="palette_css"):

    palettes = {}

    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)
        
    os.makedirs(output_directory, exist_ok=True)
    
    for chart, colour_list in palettes.items():

        filename = os.path.join(output_directory, f"{chart.replace(' ', '_')}.css")
        

        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"/* Palette: {chart} */\n")


            for colour in colour_list:
                file.write(f"--{colour['code']}: rgb({colour['red']}, {colour['green']}, {colour['blue']});\n")
                
        print(f"[ D0NE! ]  CSS file generated: {filename}")



# SCSS
def export_scss(colours, output_directory="palette_scss"):

    palettes = {}
    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)
        
    os.makedirs(output_directory, exist_ok=True)
    
    for chart, colour_list in palettes.items():
        filename = os.path.join(output_directory, f"{chart.replace(' ', '_')}.scss")
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"// Palette: {chart}\n")
            for colour in colour_list:
                file.write(f"${colour['code']}: rgb({colour['red']}, {colour['green']}, {colour['blue']});\n")
                
        print(f"[ D0NE! ]  SCSS file generated: {filename}")
