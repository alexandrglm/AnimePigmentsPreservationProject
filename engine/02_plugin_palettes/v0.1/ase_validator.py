#!/usr/bin/env python3
import struct
import sys
from pathlib import Path


"""A simple .ASE validator, more or less than head <filename> shell usage; it ensures binary format and proper content
"""

def read_utf16be_string(file):
    """Read a UTF-16BE null-terminated string from file"""

    characters = []


    while True:
        char_bytes = file.read(2)

        if len(char_bytes) < 2:
            break


        if char_bytes == b'\x00\x00':
            break

        characters.append(char_bytes)

    return b''.join(characters).decode('utf-16-be')




def validate_ase_file(file_path):
    """Validate and display contents of an ASE file"""


    file_path = Path(file_path)


    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")

        return



    with open(file_path, "rb") as file:

        header = file.read(4)

        if header != b'ASEF':
            print("[ERROR] Not a valid ASE file (missing ASEF signature)")
            return

        version_major, version_minor = struct.unpack(">HH", file.read(4))

        number_of_blocks = struct.unpack(">I", file.read(4))[0]



        print(f"ASE File: {file_path.name}")
        print(f"Version: {version_major}.{version_minor}")
        print(f"Number of blocks (colours): {number_of_blocks}\n")


        for i in range(number_of_blocks):

            block_type = struct.unpack(">H", file.read(2))[0]
            block_length = struct.unpack(">I", file.read(4))[0]


            if block_type != 0x0001:  # Only process colour blocks

                file.read(block_length)
                continue

            colour_name = read_utf16be_string(file)

            remaining_bytes = block_length - (len(colour_name.encode('utf-16-be')) + 2)

            colour_model = file.read(4).decode('ascii')

            red, green, blue = struct.unpack(">fff", file.read(12))

            colour_type = struct.unpack(">H", file.read(2))[0]
            print(f"{i+1:03d}: {colour_name} | Model: {colour_model} | RGB: {red:.3f}, {green:.3f}, {blue:.3f} | Type: {colour_type}")



if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python ase_validator.py <file.ase>")
        sys.exit(1)

    ase_file = sys.argv[1]
    validate_ase_file(ase_file)
