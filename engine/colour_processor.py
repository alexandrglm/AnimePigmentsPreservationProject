#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
colour_processor.py
Module for colour space conversions (LAB → CMYK) and Delta E calculations
"""

import json
import math
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageCms
from colormath.color_objects import LabColor
import os


class ColourProcessor:
    """Processor for ColourProcessingPipeline space conversions and Delta E calculations"""

    def __init__(self, icc_profile_path="PSOcoated_v3.icc"):
        self.icc_profile_path = icc_profile_path
        self.conversion_log = []
        self.transform = None
        self._initialize_colour_transform()

    def _initialize_colour_transform(self):
        """Initialize colour transformation from LAB to CMYK using ICC profile"""
        try:
            if not os.path.exists(self.icc_profile_path):
                raise FileNotFoundError(f"ICC profile not found: {self.icc_profile_path}")

            # Create LAB profile
            lab_profile = ImageCms.createProfile("LAB")

            # Load CMYK ICC profile
            cmyk_profile = ImageCms.getOpenProfile(self.icc_profile_path)

            # Create transformation: LAB → CMYK with Relative Colorimetric intent
            # Handle different PIL/Pillow versions
            try:
                # Try newer version format
                rendering_intent = ImageCms.Intent.RELATIVE_COLORIMETRIC
                flags = ImageCms.Flags.BLACKPOINTCOMPENSATION
            except AttributeError:
                try:
                    # Try older version format
                    rendering_intent = ImageCms.INTENT_RELATIVE_COLORIMETRIC
                    flags = ImageCms.FLAGS["BLACKPOINTCOMPENSATION"]
                except AttributeError:
                    # Fallback to numeric values
                    rendering_intent = 1  # Relative Colorimetric
                    flags = 0x2000  # Black Point Compensation

            self.transform = ImageCms.buildTransformFromOpenProfiles(
                lab_profile,
                cmyk_profile,
                "LAB",
                "CMYK",
                renderingIntent=rendering_intent,
                flags=flags
            )

            print(f"INFO: Colour transform initialized with ICC profile: {self.icc_profile_path}")

        except Exception as e:
            print(f"ERROR: Failed to initialize colour transform: {e}")
            self.transform = None
            raise

    def lab_to_cmyk(self, L, a, b):
        """
        Convert LAB values to CMYK using ICC profile

        Args:
            L: Lightness (0-100)
            a: Green-Red axis (-128 to +127)
            b: Blue-Yellow axis (-128 to +127)

        Returns:
            tuple: (C, M, Y, K) percentages (0-100)
        """
        try:
            if self.transform is None:
                raise RuntimeError("Colour transform not initialized")

            # Validate input values
            L_val = max(0, min(100, float(L)))
            a_val = max(-128, min(127, float(a)))
            b_val = max(-128, min(127, float(b)))

            # Create 1x1 LAB image
            # PIL LAB format: L=0-255, a=0-255 (128=neutral), b=0-255 (128=neutral)
            lab_image = Image.new("LAB", (1, 1))
            lab_image.putpixel((0, 0), (
                int(L_val * 2.55),      # L* 0-100 → 0-255
                int(a_val + 128),       # a* -128..127 → 0-255
                int(b_val + 128)        # b* -128..127 → 0-255
            ))

            # Apply colour transformation
            cmyk_image = ImageCms.applyTransform(lab_image, self.transform)

            # Extract CMYK values (0-255)
            c, m, y, k = cmyk_image.getpixel((0, 0))

            # Convert to percentages (0-100)
            c_percent = (c / 255.0) * 100.0
            m_percent = (m / 255.0) * 100.0
            y_percent = (y / 255.0) * 100.0
            k_percent = (k / 255.0) * 100.0

            return c_percent, m_percent, y_percent, k_percent

        except Exception as e:
            print(f"WARNING: LAB to CMYK conversion failed for L={L}, a={a}, b={b}: {e}")
            return 0.0, 0.0, 0.0, 100.0  # Default to black

    def cmyk_to_lab(self, c, m, y, k):
        """
        Convert CMYK values back to LAB using ICC profile (for Delta E calculation)

        Args:
            c, m, y, k: CMYK percentages (0-100)

        Returns:
            tuple: (L, a, b) values
        """
        try:
            if self.transform is None:
                raise RuntimeError("Colour transform not initialized")

            # Create reverse transform: CMYK → LAB
            lab_profile = ImageCms.createProfile("LAB")
            cmyk_profile = ImageCms.getOpenProfile(self.icc_profile_path)

            # Handle different PIL/Pillow versions for reverse transform
            try:
                rendering_intent = ImageCms.Intent.RELATIVE_COLORIMETRIC
                flags = ImageCms.Flags.BLACKPOINTCOMPENSATION
            except AttributeError:
                try:
                    rendering_intent = ImageCms.INTENT_RELATIVE_COLORIMETRIC
                    flags = ImageCms.FLAGS["BLACKPOINTCOMPENSATION"]
                except AttributeError:
                    rendering_intent = 1  # Relative Colorimetric
                    flags = 0x2000  # Black Point Compensation

            reverse_transform = ImageCms.buildTransformFromOpenProfiles(
                cmyk_profile,
                lab_profile,
                "CMYK",
                "LAB",
                renderingIntent=rendering_intent,
                flags=flags
            )

            # Create 1x1 CMYK image
            cmyk_image = Image.new("CMYK", (1, 1))
            cmyk_image.putpixel((0, 0), (
                int((c / 100.0) * 255),  # C% → 0-255
                int((m / 100.0) * 255),  # M% → 0-255
                int((y / 100.0) * 255),  # Y% → 0-255
                int((k / 100.0) * 255)   # K% → 0-255
            ))

            # Apply reverse transformation
            lab_image = ImageCms.applyTransform(cmyk_image, reverse_transform)

            # Extract LAB values
            l_pil, a_pil, b_pil = lab_image.getpixel((0, 0))

            # Convert from PIL format back to standard LAB
            L = l_pil / 2.55          # 0-255 → 0-100
            a = a_pil - 128           # 0-255 → -128..127
            b = b_pil - 128           # 0-255 → -128..127

            return L, a, b

        except Exception as e:
            print(f"WARNING: CMYK to LAB conversion failed for C={c}, M={m}, Y={y}, K={k}: {e}")
            return 0.0, 0.0, 0.0  # Default to black

    def calculate_delta_e_cie2000(self, lab1, lab2):
        """
        Calculate Delta E CIE2000 between two LAB colours

        Args:
            lab1: tuple (L, a, b) - reference colour
            lab2: tuple (L, a, b) - comparison colour

        Returns:
            float: Delta E CIE2000 value
        """
        try:
            L1, a1, b1 = lab1
            L2, a2, b2 = lab2

            # Weighting factors
            kL = kC = kH = 1.0

            # Step 1: Calculate C1, C2
            C1 = math.sqrt(a1**2 + b1**2)
            C2 = math.sqrt(a2**2 + b2**2)
            C_avg = (C1 + C2) / 2.0

            # Step 2: Calculate G
            G = 0.5 * (1 - math.sqrt(C_avg**7 / (C_avg**7 + 25**7)))

            # Step 3: Calculate a'
            a1_prime = a1 * (1 + G)
            a2_prime = a2 * (1 + G)

            # Step 4: Calculate C'
            C1_prime = math.sqrt(a1_prime**2 + b1**2)
            C2_prime = math.sqrt(a2_prime**2 + b2**2)

            # Step 5: Calculate h'
            h1_prime = math.degrees(math.atan2(b1, a1_prime)) % 360 if C1_prime != 0 else 0
            h2_prime = math.degrees(math.atan2(b2, a2_prime)) % 360 if C2_prime != 0 else 0

            # Step 6: Calculate ΔL', ΔC', Δh'
            delta_L_prime = L2 - L1
            delta_C_prime = C2_prime - C1_prime

            if C1_prime * C2_prime == 0:
                delta_h_prime = 0
            elif abs(h2_prime - h1_prime) <= 180:
                delta_h_prime = h2_prime - h1_prime
            elif h2_prime - h1_prime > 180:
                delta_h_prime = h2_prime - h1_prime - 360
            else:
                delta_h_prime = h2_prime - h1_prime + 360

            delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime / 2))

            # Step 7: Calculate average L', C', h'
            L_avg_prime = (L1 + L2) / 2.0
            C_avg_prime = (C1_prime + C2_prime) / 2.0

            if C1_prime * C2_prime == 0:
                h_avg_prime = h1_prime + h2_prime
            elif abs(h1_prime - h2_prime) <= 180:
                h_avg_prime = (h1_prime + h2_prime) / 2.0
            elif abs(h1_prime - h2_prime) > 180 and h1_prime + h2_prime < 360:
                h_avg_prime = (h1_prime + h2_prime + 360) / 2.0
            else:
                h_avg_prime = (h1_prime + h2_prime - 360) / 2.0

            # Step 8: Calculate T
            T = (1 - 0.17 * math.cos(math.radians(h_avg_prime - 30)) +
                 0.24 * math.cos(math.radians(2 * h_avg_prime)) +
                 0.32 * math.cos(math.radians(3 * h_avg_prime + 6)) -
                 0.20 * math.cos(math.radians(4 * h_avg_prime - 63)))

            # Step 9: Calculate SL, SC, SH
            delta_theta = 30 * math.exp(-((h_avg_prime - 275) / 25)**2)
            RC = 2 * math.sqrt(C_avg_prime**7 / (C_avg_prime**7 + 25**7))
            SL = 1 + (0.015 * (L_avg_prime - 50)**2) / math.sqrt(20 + (L_avg_prime - 50)**2)
            SC = 1 + 0.045 * C_avg_prime
            SH = 1 + 0.015 * C_avg_prime * T
            RT = -math.sin(math.radians(2 * delta_theta)) * RC

            # Step 10: Calculate final Delta E
            term1 = (delta_L_prime / (kL * SL))**2
            term2 = (delta_C_prime / (kC * SC))**2
            term3 = (delta_H_prime / (kH * SH))**2
            term4 = RT * (delta_C_prime / (kC * SC)) * (delta_H_prime / (kH * SH))

            delta_e = math.sqrt(term1 + term2 + term3 + term4)
            return delta_e

        except Exception as e:
            print(f"WARNING: Delta E calculation failed: {e}")
            # Fallback to Euclidean distance
            return math.sqrt((L1 - L2)**2 + (a1 - a2)**2 + (b1 - b2)**2)

    def process_colour_entry(self, colour_id, colour_data):
        """
        Process a single color entry: convert LAB to CMYK and calculate Delta E

        Args:
            colour_id: Colour ID string
            colour_data: Colour data dictionary

        Returns:
            dict: Updated colour data with CMYK values
        """
        try:
            # Extract original LAB values
            original_data = colour_data.get('original_data', {})
            L = original_data.get('L', 0)
            a = original_data.get('a', 0)
            b = original_data.get('b', 0)

            # Skip if LAB values are all zero (likely missing data)
            if L == 0 and a == 0 and b == 0:
                log_msg = f"WARNING: Colour ID {colour_id} ({original_data.get('code', 'Unknown')}): All LAB values are zero, skipping CMYK conversion"
                print(log_msg)
                self.conversion_log.append(log_msg)
                return colour_data

            # Convert LAB to CMYK
            c, m, y, k = self.lab_to_cmyk(L, a, b)

            # Convert CMYK back to LAB for Delta E calculation
            lab_from_cmyk = self.cmyk_to_lab(c, m, y, k)

            # Calculate Delta E between original LAB and CMYK-converted LAB
            delta_e = self.calculate_delta_e_cie2000((L, a, b), lab_from_cmyk)

            # Update computed_data
            colour_data['computed_data']['C'] = round(c, 2)
            colour_data['computed_data']['M'] = round(m, 2)
            colour_data['computed_data']['Y'] = round(y, 2)
            colour_data['computed_data']['K'] = round(k, 2)
            colour_data['computed_data']['cmyk_delta_e00'] = round(delta_e, 3)

            # Log successful conversion
            chart_name = original_data.get('chart', 'Unknown')
            code_name = original_data.get('code', 'Unknown')
            log_msg = f"INFO: Colour ID {colour_id} ({chart_name}:{code_name}): LAB({L:.1f},{a:.1f},{b:.1f}) → CMYK({c:.1f},{m:.1f},{y:.1f},{k:.1f}), ΔE={delta_e:.3f}"
            self.conversion_log.append(log_msg)

            return colour_data

        except Exception as e:
            chart_name = colour_data.get('original_data', {}).get('chart', 'Unknown')
            code_name = colour_data.get('original_data', {}).get('code', 'Unknown')
            log_msg = f"ERROR: Colour ID {colour_id} ({chart_name}:{code_name}): CMYK conversion failed - {e}"
            print(log_msg)
            self.conversion_log.append(log_msg)
            return colour_data

    def add_cmyk_data(self, json_data, icc_profile_path=None):
        """
        Main function to add CMYK data to all Colours in JSON structure

        Args:
            json_data: Complete JSON structure from excel_parser
            icc_profile_path: Optional override for ICC profile path

        Returns:
            dict: Updated JSON structure with CMYK data
        """
        try:
            print(f"INFO: Starting CMYK conversion process")

            # Update ICC profile if provided
            if icc_profile_path and icc_profile_path != self.icc_profile_path:
                self.icc_profile_path = icc_profile_path
                self._initialize_colour_transform()

            # Reset conversion log
            self.conversion_log = []

            # Process each Colour entry
            processed_count = 0
            failed_count = 0

            for colour_id, colour_data in json_data.items():
                # Skip metadata entry
                if colour_id == 'metadata':
                    continue

                try:
                    json_data[colour_id] = self.process_colour_entry(colour_id, colour_data)
                    processed_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"ERROR: Failed to process Colour ID {colour_id}: {e}")

            # Update metadata
            if 'metadata' in json_data:
                json_data['metadata']['icc_profile'] = str(Path(self.icc_profile_path).name)
                json_data['metadata']['cmyk_conversion_date'] = datetime.now().isoformat()
                json_data['metadata']['cmyk_processed'] = processed_count
                json_data['metadata']['cmyk_failed'] = failed_count
                json_data['metadata']['processing_status'] = 'cmyk_processed'

            print(f"INFO: CMYK conversion complete")
            print(f"INFO: Colours processed: {processed_count}")
            print(f"INFO: Colours failed: {failed_count}")
            print(f"INFO: ICC Profile used: {Path(self.icc_profile_path).name}")

            return json_data

        except Exception as e:
            print(f"ERROR: CMYK conversion process failed: {e}")
            raise


def main():
    """Test function for standalone usage"""
    # Example usage
    processor = ColourProcessor("PSOcoated_v3.icc")

    # Load test data
    test_json_file = "Colours_base.json"

    try:
        with open(test_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Process CMYK conversions
        updated_data = processor.add_cmyk_data(json_data)

        # Save updated data
        output_file = "Colours_with_cmyk.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)

        print(f"\nINFO: Test output saved to: {output_file}")

    except Exception as e:
        print(f"ERROR: Test failed: {e}")


if __name__ == "__main__":
    main()
