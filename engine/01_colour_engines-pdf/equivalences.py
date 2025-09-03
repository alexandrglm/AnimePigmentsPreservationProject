#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
equivalences.py
Module for processing color equivalences between different charts from Excel correspondence sheet
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path


class EquivalencesProcessor:
    """Processor for color equivalences between different charts"""

    def __init__(self):
        self.equivalences_log = []
        self.correspondence_map = {}

    def clean_value(self, value):
        """Clean and normalize values for comparison"""
        if pd.isna(value) or value in ['', '-', '—', ' ', None]:
            return ''
        return str(value).strip().upper()

    def split_multiple_values(self, value):
        """Split multiple values separated by / or , or ;"""
        if not value:
            return []

        # Try different separators
        values = []
        for separator in ['/', ',', ';']:
            if separator in value:
                values = [v.strip().upper() for v in value.split(separator) if v.strip()]
                break

        # If no separator found, treat as single value
        if not values:
            values = [value.upper()] if value else []

        return values

    def find_correspondence_sheet(self, excel_data):
        """Find the correspondence/equivalences sheet in Excel data"""
        # Possible sheet names for correspondence data
        correspondence_sheet_names = [
            'CORRESPONDENCES', 'STAC', 'Correspondences',
            'STAC Correspondences', 'STAC-Taiyo', 'Equivalences',
            'EQUIVALENCES', 'Correspondence', 'Matches'
        ]

        for sheet_name in correspondence_sheet_names:
            # Case insensitive search
            for actual_sheet_name in excel_data.keys():
                if actual_sheet_name.upper() == sheet_name.upper():
                    print(f"INFO: Found correspondence sheet: '{actual_sheet_name}'")
                    return actual_sheet_name, excel_data[actual_sheet_name]

        print("WARNING: No correspondence sheet found")
        return None, None

    def identify_columns(self, df):
        """Identify correspondence columns in the dataframe"""
        df.columns = df.columns.str.strip()

        # Possible column name variations
        stac_columns = ['STAC', 'STAC COLOR', 'STAC_COLOR', 'NEW STAC', 'Current STAC']
        taiyo_columns = ['TAIYO', 'TAIYO COLOR', 'TAIYO_COLOR', 'TAIYO COLOUR']
        old_stac_columns = ['OLD STAC', 'OLD_STAC', 'OLDSTAC', 'PREVIOUS STAC', 'Original STAC']

        found_columns = {}

        # Find STAC column
        for col in df.columns:
            col_upper = col.upper()
            for stac_col in stac_columns:
                if stac_col in col_upper and 'OLD' not in col_upper:
                    found_columns['stac'] = col
                    break
            if 'stac' in found_columns:
                break

        # Find TAIYO column
        for col in df.columns:
            col_upper = col.upper()
            for taiyo_col in taiyo_columns:
                if taiyo_col in col_upper:
                    found_columns['taiyo'] = col
                    break
            if 'taiyo' in found_columns:
                break

        # Find OLD STAC column
        for col in df.columns:
            col_upper = col.upper()
            for old_stac_col in old_stac_columns:
                if old_stac_col in col_upper:
                    found_columns['old_stac'] = col
                    break
            if 'old_stac' in found_columns:
                break

        print(f"INFO: Identified columns - STAC: {found_columns.get('stac')}, TAIYO: {found_columns.get('taiyo')}, OLD STAC: {found_columns.get('old_stac')}")

        return found_columns

    def build_correspondence_map(self, excel_file_path):
        """Build correspondence map from Excel equivalences sheet"""
        try:
            # Load Excel data
            excel_data = pd.read_excel(excel_file_path, sheet_name=None)

            # Find correspondence sheet
            sheet_name, df = self.find_correspondence_sheet(excel_data)
            if sheet_name is None or df is None:
                print("WARNING: No correspondence data found")
                return {}

            # Identify columns
            columns = self.identify_columns(df)
            if not columns.get('stac'):
                print("ERROR: No STAC column found in correspondence sheet")
                return {}

            correspondence_map = {}
            processed_rows = 0
            skipped_rows = 0

            for idx, row in df.iterrows():
                try:
                    # Get and clean values
                    stac_val = self.clean_value(row.get(columns.get('stac', ''), ''))
                    taiyo_val = self.clean_value(row.get(columns.get('taiyo', ''), '')) if columns.get('taiyo') else ''
                    old_stac_val = self.clean_value(row.get(columns.get('old_stac', ''), '')) if columns.get('old_stac') else ''

                    # Skip header rows or empty rows
                    if not stac_val or stac_val in ['STAC', 'TAIYO', 'OLD STAC', 'OLD_STAC']:
                        skipped_rows += 1
                        continue

                    # Process multiple values (separated by /, ,, ;)
                    taiyo_values = self.split_multiple_values(taiyo_val)
                    old_stac_values = self.split_multiple_values(old_stac_val)

                    # Initialize correspondence entry for main STAC color
                    if stac_val not in correspondence_map:
                        correspondence_map[stac_val] = {
                            'stac': set(),
                            'taiyo': set(),
                            'old_stac': set()
                        }

                    # Add bidirectional correspondences
                    # STAC → TAIYO
                    for taiyo in taiyo_values:
                        if taiyo and taiyo != stac_val:  # Avoid self-references
                            correspondence_map[stac_val]['taiyo'].add(taiyo)

                            # Create reverse mapping: TAIYO → STAC
                            if taiyo not in correspondence_map:
                                correspondence_map[taiyo] = {
                                    'stac': set(),
                                    'taiyo': set(),
                                    'old_stac': set()
                                }
                            correspondence_map[taiyo]['stac'].add(stac_val)

                    # STAC → OLD STAC
                    for old_stac in old_stac_values:
                        if old_stac and old_stac != stac_val:  # Avoid self-references
                            correspondence_map[stac_val]['old_stac'].add(old_stac)

                            # Create reverse mapping: OLD STAC → STAC
                            if old_stac not in correspondence_map:
                                correspondence_map[old_stac] = {
                                    'stac': set(),
                                    'taiyo': set(),
                                    'old_stac': set()
                                }
                            correspondence_map[old_stac]['stac'].add(stac_val)

                    # TAIYO ↔ OLD STAC (if both exist and are different)
                    for taiyo in taiyo_values:
                        for old_stac in old_stac_values:
                            if taiyo and old_stac and taiyo != old_stac:
                                # TAIYO → OLD STAC
                                if taiyo not in correspondence_map:
                                    correspondence_map[taiyo] = {
                                        'stac': set(),
                                        'taiyo': set(),
                                        'old_stac': set()
                                    }
                                correspondence_map[taiyo]['old_stac'].add(old_stac)

                                # OLD STAC → TAIYO
                                if old_stac not in correspondence_map:
                                    correspondence_map[old_stac] = {
                                        'stac': set(),
                                        'taiyo': set(),
                                        'old_stac': set()
                                    }
                                correspondence_map[old_stac]['taiyo'].add(taiyo)

                    processed_rows += 1

                except Exception as e:
                    skipped_rows += 1
                    print(f"WARNING: Error processing correspondence row {idx + 1}: {e}")

            # Convert sets to lists for JSON serialization
            for color_code, correspondences in correspondence_map.items():
                for corr_type in correspondences:
                    correspondences[corr_type] = sorted(list(correspondences[corr_type]))

            print(f"INFO: Correspondence map built - {len(correspondence_map)} color codes, {processed_rows} rows processed, {skipped_rows} rows skipped")

            return correspondence_map

        except Exception as e:
            print(f"ERROR: Failed to build correspondence map: {e}")
            return {}

    def find_color_equivalences(self, color_code, chart_name):
        """Find equivalences for a specific color code"""
        if not self.correspondence_map:
            return False, {}

        # Clean and normalize the color code
        clean_code = self.clean_value(color_code)
        if not clean_code:
            return False, {}

        # Look for direct match
        if clean_code in self.correspondence_map:
            correspondences = self.correspondence_map[clean_code]

            # Filter out empty correspondences and convert to chart-specific format
            equivalences = {}

            # Map correspondence types to chart names
            type_to_chart = {
                'stac': 'STAC',
                'taiyo': 'TAIYO',
                'old_stac': 'OLD_STAC'
            }

            for corr_type, values in correspondences.items():
                if values:  # Only include non-empty lists
                    chart_name_mapped = type_to_chart.get(corr_type, corr_type.upper())
                    equivalences[chart_name_mapped] = values

            if equivalences:
                return True, equivalences

        return False, {}

    def process_colour_entry(self, colour_id, colour_data):
        """Process a single color entry to find equivalences"""
        try:
            # Extract color information
            original_data = colour_data.get('original_data', {})
            chart_name = original_data.get('chart', '')
            color_code = original_data.get('code', '')

            # Find equivalences
            has_equivalences, equivalences = self.find_color_equivalences(color_code, chart_name)

            # Update correspondences data
            colour_data['correspondences']['has_equivalences'] = has_equivalences
            colour_data['correspondences']['equivalences'] = equivalences

            # Log results
            if has_equivalences:
                equiv_summary = []
                for chart, codes in equivalences.items():
                    equiv_summary.append(f"{chart}({', '.join(codes)})")

                log_msg = f"INFO: Color ID {colour_id} ({chart_name}:{color_code}): Found equivalences - {', '.join(equiv_summary)}"
                self.equivalences_log.append(log_msg)
            else:
                log_msg = f"INFO: Color ID {colour_id} ({chart_name}:{color_code}): No equivalences found"
                self.equivalences_log.append(log_msg)

            return colour_data

        except Exception as e:
            chart_name = colour_data.get('original_data', {}).get('chart', 'Unknown')
            code_name = colour_data.get('original_data', {}).get('code', 'Unknown')
            log_msg = f"ERROR: Color ID {colour_id} ({chart_name}:{code_name}): Equivalences processing failed - {e}"
            print(log_msg)
            self.equivalences_log.append(log_msg)

            # Set no equivalences on error
            colour_data['correspondences']['has_equivalences'] = False
            colour_data['correspondences']['equivalences'] = {}

            return colour_data

    def add_equivalences_data(self, json_data, excel_file_path):
        """
        Main function to add equivalences data to all colours in JSON structure

        Args:
            json_data: Complete JSON structure with color data
            excel_file_path: Path to original Excel file with correspondence sheet

        Returns:
            dict: Updated JSON structure with equivalences data
        """
        try:
            print(f"INFO: Starting equivalences processing")

            # Build correspondence map from Excel
            self.correspondence_map = self.build_correspondence_map(excel_file_path)

            # Reset equivalences log
            self.equivalences_log = []

            # Process each color entry
            processed_count = 0
            equivalences_found_count = 0
            failed_count = 0

            for colour_id, colour_data in json_data.items():
                # Skip metadata entry
                if colour_id == 'metadata':
                    continue

                try:
                    json_data[colour_id] = self.process_colour_entry(colour_id, colour_data)
                    processed_count += 1

                    # Check if equivalences were found
                    if json_data[colour_id].get('correspondences', {}).get('has_equivalences', False):
                        equivalences_found_count += 1

                except Exception as e:
                    failed_count += 1
                    print(f"ERROR: Failed to process color ID {colour_id}: {e}")

            # Update metadata
            if 'metadata' in json_data:
                json_data['metadata']['equivalences_processing_date'] = datetime.now().isoformat()
                json_data['metadata']['equivalences_processed'] = processed_count
                json_data['metadata']['equivalences_found'] = equivalences_found_count
                json_data['metadata']['equivalences_failed'] = failed_count
                json_data['metadata']['correspondence_entries'] = len(self.correspondence_map)
                json_data['metadata']['processing_status'] = 'equivalences_processed'

            print(f"INFO: Equivalences processing complete")
            print(f"INFO: colours processed: {processed_count}")
            print(f"INFO: colours with equivalences: {equivalences_found_count}")
            print(f"INFO: colours failed: {failed_count}")
            print(f"INFO: Equivalence rate: {(equivalences_found_count/processed_count)*100:.1f}%" if processed_count > 0 else "INFO: Equivalence rate: 0%")
            print(f"INFO: Correspondence entries: {len(self.correspondence_map)}")

            return json_data

        except Exception as e:
            print(f"ERROR: Equivalences processing failed: {e}")
            raise

    def get_equivalences_statistics(self, json_data):
        """
        Generate statistics about equivalences processing results

        Args:
            json_data: Processed JSON data with equivalences

        Returns:
            dict: Statistics about equivalences results
        """
        try:
            chart_equivalences = {}
            total_colours = 0
            colours_with_equivalences = 0

            for colour_id, colour_data in json_data.items():
                if colour_id == 'metadata':
                    continue

                total_colours += 1
                original_data = colour_data.get('original_data', {})
                chart_name = original_data.get('chart', 'Unknown')

                if chart_name not in chart_equivalences:
                    chart_equivalences[chart_name] = {
                        'total': 0,
                        'with_equivalences': 0,
                        'equivalent_charts': set()
                    }

                chart_equivalences[chart_name]['total'] += 1

                correspondences = colour_data.get('correspondences', {})
                if correspondences.get('has_equivalences', False):
                    colours_with_equivalences += 1
                    chart_equivalences[chart_name]['with_equivalences'] += 1

                    # Track which charts this chart has equivalences with
                    equivalences = correspondences.get('equivalences', {})
                    for equiv_chart in equivalences.keys():
                        chart_equivalences[chart_name]['equivalent_charts'].add(equiv_chart)

            # Convert sets to lists
            for chart_data in chart_equivalences.values():
                chart_data['equivalent_charts'] = list(chart_data['equivalent_charts'])

            stats = {
                'total_colours': total_colours,
                'colours_with_equivalences': colours_with_equivalences,
                'equivalence_rate': (colours_with_equivalences / total_colours) * 100 if total_colours > 0 else 0,
                'chart_equivalences': chart_equivalences,
                'correspondence_entries': len(self.correspondence_map)
            }

            return stats

        except Exception as e:
            print(f"ERROR: Failed to generate equivalences statistics: {e}")
            return {}


def main():
    """Test function for standalone usage"""
    # Example usage
    processor = EquivalencesProcessor()

    # Test files
    test_json_file = "colours_with_pantone.json"
    excel_file = "ORIGINAL_Cel_Animation_Color_Charts.xlsx"

    try:
        with open(test_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Process equivalences
        updated_data = processor.add_equivalences_data(json_data, excel_file)

        # Generate statistics
        stats = processor.get_equivalences_statistics(updated_data)
        print(f"\nINFO: Equivalences Statistics:")
        print(f"  Total colours: {stats.get('total_colours', 0)}")
        print(f"  colours with equivalences: {stats.get('colours_with_equivalences', 0)}")
        print(f"  Equivalence rate: {stats.get('equivalence_rate', 0):.1f}%")
        print(f"  Correspondence entries: {stats.get('correspondence_entries', 0)}")

        # Save updated data
        output_file = "colours_complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)

        print(f"\nINFO: Test output saved to: {output_file}")

    except Exception as e:
        print(f"ERROR: Test failed: {e}")


if __name__ == "__main__":
    main()
