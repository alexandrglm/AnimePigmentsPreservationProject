#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
new_Taito_unified.py
Unified TAIYO color extractor that generates JSON compatible with the full processing pipeline
"""

import re
import json
import chardet
from datetime import datetime
from pathlib import Path

def detect_and_read_file(file_path):
    """
    Detect file encoding and read the file with proper encoding handling
    """
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()

        detected = chardet.detect(raw_data)
        print(f"Detected encoding: {detected['encoding']} (confidence: {detected['confidence']:.2f})")

        encodings_to_try = [
            detected['encoding'],
            'utf-8',
            'utf-8-sig',
            'latin-1',
            'cp1252',
            'euc-jp',
            'shift_jis',
            'iso-8859-1'
        ]

        # Remove None and duplicates
        encodings_to_try = list(dict.fromkeys([enc for enc in encodings_to_try if enc]))

        for encoding in encodings_to_try:
            try:
                print(f"Trying encoding: {encoding}")
                content = raw_data.decode(encoding, errors='replace')
                print(f"Successfully read file with {encoding} encoding")
                return content
            except (UnicodeDecodeError, LookupError) as e:
                print(f"Failed with {encoding}: {e}")
                continue

        # Last resort: read as binary and decode with errors='replace'
        print("Using fallback method with error replacement")
        return raw_data.decode('utf-8', errors='replace')

    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def clean_color_code(code):
    """
    Clean and normalize color codes, replacing problematic characters
    """
    code = code.strip()

    # Replace common problematic characters with "Code"
    problematic_patterns = [
        r'ï¿½+',  # Replace any sequence of ï¿½ characters
        r'å³¨ï¿½ï¿½',  # Specific problematic sequence
        r'[^\x00-\x7F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+',  # Non-ASCII except Japanese
    ]

    for pattern in problematic_patterns:
        if re.search(pattern, code):
            return "Code"

    # Additional filters
    invalid_codes = [
        'XYZ', 'L*a*b*', 'LHC', 'RGB', ' ', '',
        '2å±ž', '10å±ž', '2Â°', '10Â°'
    ]

    if code in invalid_codes or len(code) == 0:
        return None

    return code

def rgb_to_hex(r, g, b):
    """Convert RGB values to hex format"""
    try:
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return f"#{r:02X}{g:02X}{b:02X}"
    except:
        return ""

def calculate_hsl_from_rgb(r, g, b):
    """Calculate HSL values from RGB (basic approximation)"""
    try:
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val

        # Lightness
        l = (max_val + min_val) / 2.0

        if diff == 0:
            h = 0
            s = 0
        else:
            # Saturation
            if l < 0.5:
                s = diff / (max_val + min_val)
            else:
                s = diff / (2.0 - max_val - min_val)

            # Hue
            if max_val == r_norm:
                h = ((g_norm - b_norm) / diff) % 6
            elif max_val == g_norm:
                h = (b_norm - r_norm) / diff + 2
            else:
                h = (r_norm - g_norm) / diff + 4

            h = h * 60

        return round(h, 1), round(s * 100, 1), round(l * 100, 1)
    except:
        return 0.0, 0.0, 0.0

def create_unified_color_entry(chart_name, code, family, observer, measurements, color_index):
    """
    Create a unified color entry compatible with the processing pipeline

    Args:
        chart_name: Name of the color chart
        code: Color code
        family: Color family
        observer: Observer type
        measurements: Dictionary with measurement data
        color_index: Unique color index

    Returns:
        dict: Complete color entry with all required fields
    """

    # Safely extract values with defaults
    def safe_float(val, default=0.0):
        try:
            return float(val)
        except:
            return default

    def safe_int(val, default=0):
        try:
            return int(float(val))
        except:
            return default

    def safe_string(val, default=""):
        try:
            return str(val) if val is not None else default
        except:
            return default

    # Extract measurement data
    X = safe_float(measurements.get('X', 0))
    Y = safe_float(measurements.get('Y', 0))
    Z = safe_float(measurements.get('Z', 0))
    L = safe_float(measurements.get('L', 0))
    a = safe_float(measurements.get('a', 0))
    b = safe_float(measurements.get('b', 0))
    L_lhc = safe_float(measurements.get('L_lhc', 0))
    H_original = safe_float(measurements.get('H', 0))
    C = safe_float(measurements.get('C', 0))
    R = safe_int(measurements.get('R', 0))
    G = safe_int(measurements.get('G', 0))
    B = safe_int(measurements.get('B', 0))

    # Generate hex values
    hex_srgb = rgb_to_hex(R, G, B)
    hex_prophoto = hex_srgb  # Same as sRGB for TAIYO data

    # Calculate HSL values from RGB
    H_hsl, S_hsl, L_hsl = calculate_hsl_from_rgb(R, G, B)

    # Validate RGB values
    has_valid_rgb = (R >= 0 and G >= 0 and B >= 0 and
                     R <= 255 and G <= 255 and B <= 255)

    # Create complete color entry
    color_entry = {
        "original_data": {
            # Chart information
            "chart": chart_name,
            "code": safe_string(code),
            "family": safe_string(family),
            "observer": safe_string(observer),

            # CIE values
            "X": X,
            "Y": Y,
            "Z": Z,
            "L": L,
            "a": a,
            "b": b,

            # RGB values
            "R": R,
            "G": G,
            "B": B,

            # Hex values
            "hex_srgb": hex_srgb,
            "hex_prophoto": hex_prophoto,

            # HSL values (calculated from RGB)
            "H": H_hsl,
            "S": S_hsl,
            "L_hsl": L_hsl,

            # Additional TAIYO-specific data
            "L_lhc": L_lhc,
            "H_original": H_original,  # Original H value from TAIYO
            "C_original": C,           # Original C value from TAIYO
            "has_valid_rgb": has_valid_rgb,

            # Missing fields from Excel format (set to defaults)
            "illuminant": "Standard illuminant",
            "observer_angle": observer,
            "measurement_conditions": f"TAIYO measurement, {observer}"
        },

        "computed_data": {
            # CMYK conversion (to be filled by colour_processor)
            "C": 0.0,
            "M": 0.0,
            "Y": 0.0,
            "K": 0.0,
            "cmyk_delta_e00": 0.0,

            # Pantone matching (to be filled by pantone_matcher)
            "pantone_name": "",
            "pantone_code": "",
            "pantone_delta_e00": 0.0,

            # Additional computed fields
            "observer_type": f"{observer} standard observer",
            "illuminant": "Standard illuminant",
            "color_space": "CIE LAB",
            "measurement_geometry": "TAIYO standard"
        },

        "correspondences": {
            # Equivalences (to be filled by equivalences processor)
            "has_equivalences": False,
            "equivalences": {}
        }
    }

    return color_entry

def extract_taiyo_colors_unified(html_file_path, output_json_path):
    """
    Extract all color measurement data from TAIYO HTML file with unified JSON structure
    """
    try:
        # Read the HTML file with encoding detection
        html_content = detect_and_read_file(html_file_path)
        if html_content is None:
            return None

        print(f"HTML file loaded, length: {len(html_content)}")

        # Extract all color codes (filtering out headers and invalid codes)
        color_code_pattern = r'<b>([^<]+)</b>'
        all_matches = re.findall(color_code_pattern, html_content)

        color_codes = []
        for code in all_matches:
            cleaned_code = clean_color_code(code)
            if cleaned_code:
                color_codes.append(cleaned_code)

        print(f"Color codes found: {len(color_codes)}")
        print(f"Sample codes: {color_codes[:10]}")

        # Extract family information by analyzing sections
        family_data = {}
        sections = re.split(r'<hr[^>]*>', html_content)

        for section in sections:
            # Look for family number
            family_match = re.search(r'<th align="left">(\d{2})</th>', section)
            if family_match:
                family_number = family_match.group(1)

                # Extract color codes from this section
                section_codes = []
                section_code_matches = re.findall(r'<b>([^<]+)</b>', section)

                for code in section_code_matches:
                    cleaned_code = clean_color_code(code)
                    if cleaned_code:
                        section_codes.append(cleaned_code)

                if section_codes:  # Only add families that have codes
                    family_data[family_number] = section_codes

        print(f"Families found: {len(family_data)}")

        # Create a mapping from color code to family
        code_to_family = {}
        for family_num, codes in family_data.items():
            for code in codes:
                code_to_family[code] = family_num

        # Extract all measurement data with more flexible pattern
        measurement_pattern = r'([\d.]+)\s+([\d.]+)\s+([\d.]+)<br[^>]*>([\d.]+)\s+([-]?[\d.]+)\s+([-]?[\d.]+)<br[^>]*>([\d.]+)\s+([\d.]+)\s+([\d.]+)%<br[^>]*>([-]?\d+)\s+([-]?\d+)\s+([-]?\d+)'

        measurement_matches = re.findall(measurement_pattern, html_content)

        measurements = []
        for match in measurement_matches:
            try:
                measurements.append({
                    'X': float(match[0]),
                    'Y': float(match[1]),
                    'Z': float(match[2]),
                    'L': float(match[3]),
                    'a': float(match[4]),
                    'b': float(match[5]),
                    'L_lhc': float(match[6]),
                    'H': float(match[7]),
                    'C': float(match[8]),
                    'R': int(match[9]),
                    'G': int(match[10]),
                    'B': int(match[11])
                })
            except ValueError as e:
                print(f"Skipping invalid measurement: {match} - Error: {e}")
                continue

        print(f"Measurements found: {len(measurements)}")

        # Create unified color data structure
        colors = {}
        color_index = 1
        chart_name = "TAIYO - Animation Color Measurement Data"

        # Handle case where we might not have equal numbers of codes and measurements
        num_unique_colors = min(len(color_codes), len(measurements) // 2 if len(measurements) >= 2 else len(measurements))

        for i in range(num_unique_colors):
            code = color_codes[i] if i < len(color_codes) else f"Color_{i+1}"
            family = code_to_family.get(code, "unknown")

            # Process 2° observer data (assuming first half or odd indices)
            if i * 2 < len(measurements):
                m2 = measurements[i * 2]

                colors[str(color_index)] = create_unified_color_entry(
                    chart_name=chart_name,
                    code=code,
                    family=family,
                    observer="2° observer",
                    measurements=m2,
                    color_index=color_index
                )
                color_index += 1

            # Process 10° observer data (assuming second half or even indices)
            if (i * 2 + 1) < len(measurements):
                m10 = measurements[i * 2 + 1]

                colors[str(color_index)] = create_unified_color_entry(
                    chart_name=chart_name,
                    code=code,
                    family=family,
                    observer="10° observer",
                    measurements=m10,
                    color_index=color_index
                )
                color_index += 1

        print(f"Successfully created {len(colors)} unified color entries")

        # Add metadata compatible with processing pipeline
        metadata = {
            "source_file": str(Path(html_file_path).name),
            "source_path": str(Path(html_file_path).absolute()),
            "generation_date": datetime.now().isoformat(),
            "total_colors": len(colors),
            "sheets_processed": 1,  # HTML file counts as 1 sheet
            "sheets_skipped": 0,
            "substitutions_made": 0,
            "icc_profile": "",  # Will be filled by colour_processor
            "processing_status": "excel_parsed",  # Compatible with pipeline

            # TAIYO-specific metadata
            "data_source": "TAIYO HTML measurement data",
            "families_found": len(family_data),
            "unique_color_codes": len(set(color_codes)),
            "observer_types": ["2° observer", "10° observer"],
            "measurement_conditions": "TAIYO Animation Color Measurement",
            "encoding_detected": "auto-detected",

            # Pipeline compatibility flags
            "cmyk_processed": 0,
            "cmyk_failed": 0,
            "pantone_processed": 0,
            "pantone_matched": 0,
            "pantone_failed": 0,
            "equivalences_processed": 0,
            "equivalences_found": 0,
            "equivalences_failed": 0,
            "correspondence_entries": 0,

            # Processing timestamps (empty, will be filled by pipeline)
            "cmyk_conversion_date": "",
            "pantone_matching_date": "",
            "equivalences_processing_date": "",
            "processing_complete": False
        }

        # Create final JSON structure with metadata
        json_output = {
            **colors,  # All color entries with numeric IDs
            'metadata': metadata
        }

        # Save to JSON
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_output, json_file, indent=2, ensure_ascii=False)

        print(f"Unified data saved to {output_json_path}")

        # Show statistics
        invalid_rgb_count = sum(1 for color in colors.values()
                              if not color['original_data']['has_valid_rgb'])

        print(f"\nStatistics:")
        print(f"- Total entries: {len(colors)}")
        print(f"- Unique color codes: {len(set(color_codes))}")
        print(f"- Entries with invalid RGB: {invalid_rgb_count}")
        print(f"- Families processed: {len(family_data)}")

        # Show sample entries with family information
        print(f"\nFirst 6 entries:")
        for i, (key, color) in enumerate(list(colors.items())[:6]):
            code = color['original_data']['code']
            family = color['original_data']['family']
            observer = color['original_data']['observer']
            hex_color = color['original_data']['hex_srgb']
            valid = color['original_data']['has_valid_rgb']
            print(f"{key}: {code} (Family {family}, {observer}) - {hex_color} - Valid: {valid}")

        # Show family distribution
        family_counts = {}
        for color in colors.values():
            family = color['original_data']['family']
            if family in family_counts:
                family_counts[family] += 1
            else:
                family_counts[family] = 1

        print(f"\nFamily distribution:")
        sorted_families = sorted(family_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
        for family, count in sorted_families:
            print(f"  Family {family}: {count} entries")

        print(f"\nJSON structure is now compatible with the full processing pipeline!")
        print(f"Ready for: colour_processor.py -> pantone_matcher.py -> equivalences.py")

        return json_output

    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Main function to extract TAIYO colors with unified JSON structure
    """
    input_file = "TAIYO.html"
    output_file = "taiyo_unified_colors.json"

    print("TAIYO Animation Color Data Extractor (UNIFIED)")
    print("=" * 60)
    print("Generates JSON compatible with the full processing pipeline")
    print("=" * 60)

    # Check if chardet is available
    try:
        import chardet
        print("✓ chardet library available for encoding detection")
    except ImportError:
        print("⚠ chardet not available. Install with: pip install chardet")
        print("  Proceeding with fallback encoding detection...")

    colors = extract_taiyo_colors_unified(input_file, output_file)

    if colors:
        print("\n✓ Extraction completed successfully!")
        print(f"Check {output_file} for the complete unified color data.")
        print("\nNext steps:")
        print("1. Run colour_processor.py to add CMYK data")
        print("2. Run pantone_matcher.py to add Pantone matches")
        print("3. Run equivalences.py to add cross-chart equivalences")
        print("4. Run pdf_generator.py to create PDF color cards")
    else:
        print("✗ Extraction failed.")

if __name__ == "__main__":
    main()
