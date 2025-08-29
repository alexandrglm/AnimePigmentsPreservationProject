import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path



"""
KRITA .kpl (XML-alike) module exporter v0.2

Check custom fields like:

- Custom ICC importer -> y/N -> y: hHandles custom ICC profiles


Retaked:
- Embebbed ICC profile MUST follow krita's default specs! (d0ne)
"""

def export_krita(colours, output_directory="palette_kpl", icc_file_path=None):
    """

    Paths/VArs:

    - icc_profile -> display name for the profile in XML (ignored if icc_file_path provided)
    - icc_file_path -> optional path to a custom ICC file to embed
    """
    palettes = {}

    for col in colours:
        palettes.setdefault(col['chart'], []).append(col)

    os.makedirs(output_directory, exist_ok=True)



    for chart, clist in palettes.items():
        filepath = Path(output_directory) / f"{chart.replace(' ', '_')}.kpl"
        with zipfile.ZipFile(filepath, 'w') as kpl:


            # 1. MUST BE mimetype
            kpl.writestr('mimetype', 'application/x-krita-palette')

            # 2. MUST BE colorset.xml
            rows = str((len(clist) + 7) // 8)
            cs = ET.Element('ColorSet', {
                'name': chart,
                'version': '2.0',
                'columns': '8',
                'rows': rows,
                'readonly': 'false'
            })


            for c in clist:
                e = ET.SubElement(cs, 'ColorSetEntry', {
                    'name': c['code'],
                    'id': c['code'],
                    'bitdepth': 'F32',
                    'spot': 'false'
                })
                rgb = ET.SubElement(e, 'RGB', {
                    'r': str(c['red']/255.0),
                    'g': str(c['green']/255.0),
                    'b': str(c['blue']/255.0)
                })
            kpl.writestr('colorset.xml', ET.tostring(cs, encoding='utf-8'))


            # 3. MUST BE profiles.xml
            """
            MUST INCLUDE THE ICC PROFILE USED INFO AND OR DEFAULT!
            Otherwise .kpl palette won't work
            """
            if icc_file_path and os.path.isfile(icc_file_path):
                icc_name = Path(icc_file_path).stem
                icc_filename = Path(icc_file_path).name

            else:
                icc_name = 'sRGB'
                icc_filename = 'sRGB.icc'

            profiles = ET.Element('Profiles')

            prof = ET.SubElement(profiles, 'Profile', {
                'name': icc_name,
                'filename': icc_filename,
                'colorModelId': 'RGBA',
                'colorDepthId': 'F32'
            })

            kpl.writestr('profiles.xml', ET.tostring(profiles, encoding='utf-8'))



            # 4. embed ICC file

            if icc_file_path and os.path.isfile(icc_file_path):

                with open(icc_file_path, 'rb') as f:
                    kpl.writestr(icc_filename, f.read())

            else:
                kpl.writestr(icc_filename, b'')

        print(f"[ D0NE! ] KPL file generated: {filepath}")
