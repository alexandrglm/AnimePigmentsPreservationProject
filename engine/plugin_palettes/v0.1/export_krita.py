import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path



"""
KRITA .kpl (XML-alike) module exporter v0.1

Check custom fields like:

- Custom ICC importer -> y/N -> y: hHandles custom ICC profiles

"""

def export_krita(colours, output_directory="palette_kpl", icc_profile='sRGB', icc_file_path=None):
    """

    Paths/VArs:

    - icc_profile -> display name for the profile in XML (ignored if icc_file_path provided)
    - icc_file_path -> optional path to a custom ICC file to embed
    """

    palettes = {}

    for colour in colours:
        palettes.setdefault(colour["chart"], []).append(colour)

    os.makedirs(output_directory, exist_ok=True)



    for chart, colour_list in palettes.items():
        filename = Path(output_directory) / f"{chart.replace(' ', '_')}.kpl"


        with zipfile.ZipFile(filename, 'w') as kpl_file:

            # krita custom mimetype from docs
            kpl_file.writestr('mimetype', 'application/x-krita-palette')

            # MUST BE colorset.xml
            colour_set_xml = ET.Element('ColorSet',
                rows=str(len(colour_list)//8+1),
                columns='8',
                name=chart,
                version='2.0')

            for colour in colour_list:
                colour_entry = ET.SubElement(colour_set_xml, 'ColorEntry')
                colour_entry.set('name', colour['code'])
                colour_entry.set('rgb', f"{colour['red']},{colour['green']},{colour['blue']}")

            colour_set_xml_string = ET.tostring(colour_set_xml, encoding='utf-8', method='xml')
            kpl_file.writestr('colorset.xml', colour_set_xml_string)



            # ICC PATH or NOT
            if icc_file_path and os.path.isfile(icc_file_path):
                icc_filename = Path(icc_file_path).name
                icc_name = Path(icc_file_path).stem


            else:
                icc_filename = f'{icc_profile}.icc'
                icc_name = icc_profile

            # MUST BE profiles.xml
            profiles_xml = ET.Element('Profiles')
            profile = ET.SubElement(profiles_xml, 'Profile',
                name=icc_name,
                filename=icc_filename,
                colorModelId='RGBA',
                colorDepthId='F32')
            profiles_xml_string = ET.tostring(profiles_xml, encoding='utf-8', method='xml')
            kpl_file.writestr('profiles.xml', profiles_xml_string)



            # CUSTOM ICC EMBEDDING
            if icc_file_path and os.path.isfile(icc_file_path):

                with open(icc_file_path, 'rb') as f:

                    kpl_file.writestr(icc_filename, f.read())


            else:

                kpl_file.writestr(icc_filename, b'')


        print(f"[ D0NE! ] KPL file generated: {filename}")
