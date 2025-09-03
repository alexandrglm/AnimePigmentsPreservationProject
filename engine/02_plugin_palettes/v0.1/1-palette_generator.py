#!/usr/bin/env python3
"""
This programme is compatible with XLS -> JSON parser from https://github.com/alexandrglm/AnimePigmentsPreservationProject as is intended
to create usable palettes from those anime pigments chart references.
Check it out for further explanations.
"""
import os, sys
import json

from export_gimp import export_gimp
from export_css import export_css, export_scss
from export_unity import export_unity
from export_ase import export_ase
from export_krita import export_krita
from export_txt_simple import export_txt_simple



class PaletteExporter:
    """Handles palette export operations for various software formats"""

    def __init__(self):
        self.colours = []

    def load_json_palette(self, json_file):
        """
        Load and parse colour data from JSON file. JSON file MUST be like:
        "original_data": {
            "chart": "Chart Name",
            "code": "ColourName",
            "R": 0–255,
            "G": 0–255,
            "B": 0–255
        }
        """
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        numeric_keys = [k for k in data.keys() if k.isdigit()]
        self.colours = []

        for key in sorted(numeric_keys, key=lambda x: int(x)):
            colour_data = data[key]
            self.colours.append({
                "chart": colour_data["original_data"]["chart"],
                "code": colour_data["original_data"]["code"],
                "red": int(colour_data["original_data"]["R"]),
                "green": int(colour_data["original_data"]["G"]),
                "blue": int(colour_data["original_data"]["B"])
            })

        return self.colours

    def export_gimp_format(self):
        """Export as GIMP palette with user-specified columns"""
        column_input = input("Number of columns in GIMP-gpl (default 8): ")
        columns = int(column_input) if column_input.strip().isdigit() else 8
        export_gimp(self.colours, columns)

    def export_css_format(self):
        """Export as CSS custom properties"""
        export_css(self.colours)

    def export_scss_format(self):
        """Export as SCSS variables"""
        export_scss(self.colours)

    def export_unity_format(self):
        """Export as Unity C# class"""
        export_unity(self.colours)

    def export_ase_format(self):
        """Export as ASE file for Adobe/Affinity/Corel"""
        export_ase(self.colours)

    def export_txt_format(self):
        """Export as simple text file"""
        export_txt_simple(self.colours)

    def export_krita_format(self):
        """Export as Krita KPL file, allow custom ICC"""

        use_custom = input("Embed custom ICC profile? (y/N): ").lower() == 'y'

        icc_path = None

        if use_custom:

            icc_path = input("Path to ICC file: ").strip()

            if not os.path.isfile(icc_path):

                print(f" [ ERROR!!! ] ICC file not found: {icc_path}, please enter a valid ICC PATH or ./FILENAME")
                return  # o sys.exit(1) si quieres detener todo

        export_krita(self.colours, icc_file_path=icc_path)



class FormatMenu:
    """Manages the format selection menu and export dispatch"""

    def __init__(self):
        self.formats = {
            1: {"name": "GIMP-gpl", "method": "export_gimp_format"},
            2: {"name": "CSS", "method": "export_css_format"},
            3: {"name": "SCSS", "method": "export_scss_format"},
            4: {"name": "Unity", "method": "export_unity_format"},
            5: {"name": "ASE .ase (Photoshop/Affinity/Corel)", "method": "export_ase_format"},
            6: {"name": "TXT Simple .txt (Clip Studio/SAI/OpenToonz/Harmony)", "method": "export_txt_format"},
            7: {"name": "Krita (.kpl)", "method": "export_krita_format"},
        }

    def display_menu(self):
        """Display the format selection menu"""
        print("Please select the software to generate the palette for:")
        for number, format_info in self.formats.items():
            print(f"{number}: {format_info['name']}")

    def get_user_choice(self):
        """Get and validate user's format choice"""
        try:
            choice = int(input("Enter number: "))
            if choice not in self.formats:
                raise ValueError
            return choice
        except ValueError:
            print("Invalid option selected")
            sys.exit(1)

    def execute_export(self, choice, exporter):
        """Execute the chosen export method"""
        method_name = self.formats[choice]["method"]
        export_method = getattr(exporter, method_name)
        export_method()

class PaletteGenerator:
    """Main application class that coordinates palette generation"""

    def __init__(self):
        self.exporter = PaletteExporter()
        self.menu = FormatMenu()

    def validate_arguments(self):
        """Validate command line arguments"""
        if len(sys.argv) != 2:
            print("Usage: palette_generator.py <file.json>")
            sys.exit(1)

        json_file = sys.argv[1]
        if not os.path.isfile(json_file):
            print(f"[ERROR] File not found: {json_file}")
            sys.exit(1)

        return json_file

    def run(self):
        """Main execution flow"""
        json_file = self.validate_arguments()

        colours = self.exporter.load_json_palette(json_file)
        print(f"JSON file loaded: {json_file} | Total colours: {len(colours)}\n")

        self.menu.display_menu()
        choice = self.menu.get_user_choice()
        self.menu.execute_export(choice, self.exporter)

#
def main():

    app = PaletteGenerator()
    app.run()

if __name__ == "__main__":
    main()
