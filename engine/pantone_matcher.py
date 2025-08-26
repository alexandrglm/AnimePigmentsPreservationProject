#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pantone_matcher.py
Module for finding closest Pantone color matches using Delta E CIE2000
"""

import json
import csv
import math
from datetime import datetime
from pathlib import Path
import pandas as pd


class PantoneMatcher:
    """Matcher for finding closest Pantone colours using Delta E CIE2000"""

    def __init__(self, pantone_csv_path="pantone_lab_2024.csv"):
        self.pantone_csv_path = pantone_csv_path
        self.pantone_database = []
        self.matching_log = []
        self._load_pantone_database()

    def _load_pantone_database(self):
        """Load Pantone color database from CSV file"""
        try:
            if not Path(self.pantone_csv_path).exists():
                raise FileNotFoundError(f"Pantone CSV file not found: {self.pantone_csv_path}")

            print(f"INFO: Loading Pantone database from: {self.pantone_csv_path}")

            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(self.pantone_csv_path, encoding=encoding)
                    print(f"INFO: Successfully loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise ValueError("Failed to load CSV with any supported encoding")

            # Clean column names
            df.columns = df.columns.str.strip()

            # Expected column mappings (handle variations)
            column_mappings = {
                'name': ['PANTONENAME', 'PANTONE_NAME', 'Name', 'COLOR_NAME', 'Pantone Name'],
                'code': ['UNIQUECODE', 'UNIQUE_CODE', 'Code', 'COLOR_CODE', 'Pantone Code'],
                'L': ['L', 'L*', 'LAB_L', 'Lightness'],
                'a': ['a', 'a*', 'LAB_A'],
                'b': ['b', 'b*', 'LAB_B']
            }

            # Find actual column names
            actual_columns = {}
            for key, possible_names in column_mappings.items():
                found_col = None
                for possible_name in possible_names:
                    if possible_name in df.columns:
                        found_col = possible_name
                        break
                if found_col:
                    actual_columns[key] = found_col
                else:
                    available_cols = ', '.join(df.columns.tolist())
                    raise ValueError(f"Required column '{key}' not found. Available columns: {available_cols}")

            print(f"INFO: Using columns - Name: {actual_columns['name']}, Code: {actual_columns['code']}, L: {actual_columns['L']}, a: {actual_columns['a']}, b: {actual_columns['b']}")

            # Process each row
            loaded_count = 0
            skipped_count = 0

            for idx, row in df.iterrows():
                try:
                    name = str(row[actual_columns['name']]).strip()
                    code = str(row[actual_columns['code']]).strip()
                    L = float(row[actual_columns['L']])
                    a = float(row[actual_columns['a']])
                    b = float(row[actual_columns['b']])

                    # Validate values
                    if name and code and not pd.isna(L) and not pd.isna(a) and not pd.isna(b):
                        self.pantone_database.append({
                            'name': name,
                            'code': code,
                            'L': L,
                            'a': a,
                            'b': b
                        })
                        loaded_count += 1
                    else:
                        skipped_count += 1

                except (ValueError, KeyError) as e:
                    skipped_count += 1
                    print(f"WARNING: Skipping invalid Pantone row {idx + 1}: {e}")

            print(f"INFO: Pantone database loaded - {loaded_count} colours loaded, {skipped_count} rows skipped")

            if loaded_count == 0:
                raise ValueError("No valid Pantone colours loaded from database")

        except Exception as e:
            print(f"ERROR: Failed to load Pantone database: {e}")
            self.pantone_database = []
            raise

    def calculate_delta_e_cie2000(self, lab1, lab2):
        """
        Calculate Delta E CIE2000 between two LAB colours
        Same implementation as colour_processor for consistency

        Args:
            lab1: tuple (L, a, b) - reference color
            lab2: tuple (L, a, b) - comparison color

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

    def find_closest_pantone(self, L, a, b, max_delta_e=None):
        """
        Find the closest Pantone color using CIE2000 Delta E

        Args:
            L, a, b: LAB color values
            max_delta_e: Optional maximum Delta E threshold

        Returns:
            tuple: (pantone_name, pantone_code, delta_e) or (None, None, None) if not found
        """
        if not self.pantone_database:
            return None, None, None

        try:
            # Validate input LAB values
            if any(x is None or pd.isna(x) for x in [L, a, b]):
                return None, None, None

            L_val = float(L)
            a_val = float(a)
            b_val = float(b)

            # Skip if all values are zero (missing data)
            if L_val == 0 and a_val == 0 and b_val == 0:
                return None, None, None

            # Find best match
            best_match = None
            min_delta = float('inf')

            input_lab = (L_val, a_val, b_val)

            for pantone in self.pantone_database:
                pantone_lab = (pantone['L'], pantone['a'], pantone['b'])
                delta_e = self.calculate_delta_e_cie2000(input_lab, pantone_lab)

                if delta_e < min_delta:
                    min_delta = delta_e
                    best_match = pantone

            # Check threshold if specified
            if max_delta_e and min_delta > max_delta_e:
                return None, None, None

            if best_match:
                return best_match['name'], best_match['code'], min_delta
            else:
                return None, None, None

        except Exception as e:
            print(f"WARNING: Pantone matching failed for LAB({L}, {a}, {b}): {e}")
            return None, None, None

    def process_colour_entry(self, colour_id, colour_data):
        """
        Process a single color entry: find closest Pantone match

        Args:
            colour_id: Color ID string
            colour_data: Color data dictionary

        Returns:
            dict: Updated color data with Pantone information
        """
        try:
            # Extract original LAB values
            original_data = colour_data.get('original_data', {})
            L = original_data.get('L', 0)
            a = original_data.get('a', 0)
            b = original_data.get('b', 0)

            # Find closest Pantone
            pantone_name, pantone_code, delta_e = self.find_closest_pantone(L, a, b)

            # Update computed_data
            if pantone_name and pantone_code and delta_e is not None:
                colour_data['computed_data']['pantone_name'] = pantone_name
                colour_data['computed_data']['pantone_code'] = pantone_code
                colour_data['computed_data']['pantone_delta_e00'] = round(delta_e, 3)

                # Log successful match
                chart_name = original_data.get('chart', 'Unknown')
                code_name = original_data.get('code', 'Unknown')
                log_msg = f"INFO: Color ID {colour_id} ({chart_name}:{code_name}): LAB({L:.1f},{a:.1f},{b:.1f}) → PANTONE {pantone_name} ({pantone_code}), ΔE={delta_e:.3f}"
                self.matching_log.append(log_msg)
            else:
                # No match found
                colour_data['computed_data']['pantone_name'] = "N/A"
                colour_data['computed_data']['pantone_code'] = "N/A"
                colour_data['computed_data']['pantone_delta_e00'] = None

                chart_name = original_data.get('chart', 'Unknown')
                code_name = original_data.get('code', 'Unknown')
                log_msg = f"WARNING: Color ID {colour_id} ({chart_name}:{code_name}): No suitable Pantone match found for LAB({L:.1f},{a:.1f},{b:.1f})"
                print(log_msg)
                self.matching_log.append(log_msg)

            return colour_data

        except Exception as e:
            chart_name = colour_data.get('original_data', {}).get('chart', 'Unknown')
            code_name = colour_data.get('original_data', {}).get('code', 'Unknown')
            log_msg = f"ERROR: Color ID {colour_id} ({chart_name}:{code_name}): Pantone matching failed - {e}"
            print(log_msg)
            self.matching_log.append(log_msg)

            # Set N/A values on error
            colour_data['computed_data']['pantone_name'] = "N/A"
            colour_data['computed_data']['pantone_code'] = "N/A"
            colour_data['computed_data']['pantone_delta_e00'] = None

            return colour_data

    def add_pantone_data(self, json_data, pantone_csv_path=None):
        """
        Main function to add Pantone data to all colours in JSON structure

        Args:
            json_data: Complete JSON structure with color data
            pantone_csv_path: Optional override for Pantone CSV path

        Returns:
            dict: Updated JSON structure with Pantone data
        """
        try:
            print(f"INFO: Starting Pantone matching process")

            # Update Pantone database if new path provided
            if pantone_csv_path and pantone_csv_path != self.pantone_csv_path:
                self.pantone_csv_path = pantone_csv_path
                self._load_pantone_database()

            # Reset matching log
            self.matching_log = []

            # Check if database is loaded
            if not self.pantone_database:
                raise ValueError("Pantone database not loaded or empty")

            # Process each color entry
            processed_count = 0
            matched_count = 0
            failed_count = 0

            for colour_id, colour_data in json_data.items():
                # Skip metadata entry
                if colour_id == 'metadata':
                    continue

                try:
                    original_pantone_name = colour_data.get('computed_data', {}).get('pantone_name')
                    json_data[colour_id] = self.process_colour_entry(colour_id, colour_data)

                    processed_count += 1

                    # Check if match was found
                    new_pantone_name = json_data[colour_id].get('computed_data', {}).get('pantone_name')
                    if new_pantone_name and new_pantone_name != "N/A":
                        matched_count += 1

                except Exception as e:
                    failed_count += 1
                    print(f"ERROR: Failed to process color ID {colour_id}: {e}")

            # Update metadata
            if 'metadata' in json_data:
                json_data['metadata']['pantone_database'] = str(Path(self.pantone_csv_path).name)
                json_data['metadata']['pantone_colours_available'] = len(self.pantone_database)
                json_data['metadata']['pantone_matching_date'] = datetime.now().isoformat()
                json_data['metadata']['pantone_processed'] = processed_count
                json_data['metadata']['pantone_matched'] = matched_count
                json_data['metadata']['pantone_failed'] = failed_count
                json_data['metadata']['processing_status'] = 'pantone_processed'

            print(f"INFO: Pantone matching complete")
            print(f"INFO: Colours processed: {processed_count}")
            print(f"INFO: Colours matched: {matched_count}")
            print(f"INFO: Colours failed: {failed_count}")
            print(f"INFO: Match rate: {(matched_count/processed_count)*100:.1f}%" if processed_count > 0 else "INFO: Match rate: 0%")
            print(f"INFO: Pantone database: {len(self.pantone_database)} colours available")

            return json_data

        except Exception as e:
            print(f"ERROR: Pantone matching process failed: {e}")
            raise

    def get_matching_statistics(self, json_data):
        """
        Generate statistics about Pantone matching results

        Args:
            json_data: Processed JSON data with Pantone matches

        Returns:
            dict: Statistics about matching results
        """
        try:
            delta_e_ranges = {
                'excellent': 0,      # ΔE < 1.0
                'good': 0,          # 1.0 ≤ ΔE < 3.0
                'acceptable': 0,    # 3.0 ≤ ΔE < 6.0
                'poor': 0,          # 6.0 ≤ ΔE < 10.0
                'very_poor': 0,     # ΔE ≥ 10.0
                'no_match': 0       # N/A
            }

            delta_e_values = []
            total_colours = 0

            for colour_id, colour_data in json_data.items():
                if colour_id == 'metadata':
                    continue

                total_colours += 1
                computed_data = colour_data.get('computed_data', {})
                delta_e = computed_data.get('pantone_delta_e00')

                if delta_e is None or computed_data.get('pantone_name') == "N/A":
                    delta_e_ranges['no_match'] += 1
                else:
                    delta_e_values.append(delta_e)

                    if delta_e < 1.0:
                        delta_e_ranges['excellent'] += 1
                    elif delta_e < 3.0:
                        delta_e_ranges['good'] += 1
                    elif delta_e < 6.0:
                        delta_e_ranges['acceptable'] += 1
                    elif delta_e < 10.0:
                        delta_e_ranges['poor'] += 1
                    else:
                        delta_e_ranges['very_poor'] += 1

            # Calculate statistics
            stats = {
                'total_colours': total_colours,
                'matched_colours': len(delta_e_values),
                'match_rate': (len(delta_e_values) / total_colours) * 100 if total_colours > 0 else 0,
                'delta_e_ranges': delta_e_ranges,
                'delta_e_statistics': {}
            }

            if delta_e_values:
                stats['delta_e_statistics'] = {
                    'min': min(delta_e_values),
                    'max': max(delta_e_values),
                    'mean': sum(delta_e_values) / len(delta_e_values),
                    'median': sorted(delta_e_values)[len(delta_e_values) // 2]
                }

            return stats

        except Exception as e:
            print(f"ERROR: Failed to generate matching statistics: {e}")
            return {}


def main():
    """Test function for standalone usage"""
    # Example usage
    matcher = PantoneMatcher("pantone_lab_2024.csv")

    # Load test data (should have CMYK data from previous step)
    test_json_file = "colours_with_cmyk.json"

    try:
        with open(test_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Process Pantone matching
        updated_data = matcher.add_pantone_data(json_data)

        # Generate statistics
        stats = matcher.get_matching_statistics(updated_data)
        print(f"\nINFO: Matching Statistics:")
        print(f"  Total colours: {stats.get('total_colours', 0)}")
        print(f"  Matched colours: {stats.get('matched_colours', 0)}")
        print(f"  Match rate: {stats.get('match_rate', 0):.1f}%")

        # Save updated data
        output_file = "colours_with_pantone.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)

        print(f"\nINFO: Test output saved to: {output_file}")

    except Exception as e:
        print(f"ERROR: Test failed: {e}")


if __name__ == "__main__":
    main()
