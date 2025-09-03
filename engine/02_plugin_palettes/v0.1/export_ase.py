import os
from pathlib import Path
import struct

"""
ADOBE ASE palette format module exporter v0.1
"""

def export_ase(colours, output_directory="palette_ase"):


    """
    Export each chart from the JSON as a .ase file compatible with Adobe, Affinity and Corel.
    """



    # Group colours by chart
    palettes = {}

    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)

    os.makedirs(output_directory, exist_ok=True)


    for chart, colour_list in palettes.items():

        filename = Path(output_directory) / f"{chart.replace(' ', '_')}.ase"
        
        with open(filename, "wb") as file:


        # FILE Header
            file.write(b'ASEF')                 # BIN ASE Signature
            file.write(struct.pack('>H', 1))    # <ver
            file.write(struct.pack('>H', 0))    # >ver
            file.write(struct.pack('>I', 0))    # blocks in viewer
            blocks = b''

            for colour in colour_list:
                # Name in UTF-16BE terminated with 0x0000

                name_utf16 = colour['code'].encode('utf-16-be') + b'\x00\x00'
                name_length = len(name_utf16)
                

                # Block type: 0x0001 = colour
                blocks += struct.pack('>H', 0x0001)
                
                # Block size = 2 bytes + name + 2 bytes (colour type) + 3 floats + 2 bytes
                block_size = name_length + 2 + 4*3 + 2
                blocks += struct.pack('>I', block_size)
                blocks += name_utf16
                

                # Colour model: "RGB "
                blocks += b'RGB '
                

                # 3 floats R,G,B in 0-1 range like CHANNEL/255 % 0
                blocks += struct.pack('>fff', 
                    colour['red']/255.0, 
                    colour['green']/255.0, 
                    colour['blue']/255.0)
                

                # La definicion para los limites de la paleta
                """
                0 -> No limit usage
                1 ->
                """
                blocks += struct.pack('>H', 0)


            # Go back and write the number of blocks
            file.seek(4)
            file.write(struct.pack('>H', 1))  # Version major
            file.write(struct.pack('>H', 0))  # Version minor
            file.write(struct.pack('>I', len(colour_list)))  # Number of blocks

            file.seek(0, 2)
            file.write(blocks)

        print(f"[ D0NE! ]  ASE file generated: {filename}")
