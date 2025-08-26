#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
excel_parser.py
Module for parsing Excel files and extracting color data into JSON structure
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)


class ExcelColorParser:
    """Parser for Excel color chart files"""

    def __init__(self):
        self.colour_id_counter = 1
        self.substitution_log = []

    def clean_and_validate_value(self, value, expected_type, field_name, sheet_name, row_idx, code_name):
        """
        Clean and validate values, assign defaults if missing
        Log all substitutions for debugging

        Args:
            value: Raw value from Excel
            expected_type: 'float', 'int', or 'string'
            field_name: Name of the field being processed
            sheet_name: Excel sheet name
            row_idx: Row index (0-based)
            code_name: Color code name for identification

        Returns:
            Cleaned value or default
        """
        try:
            # Handle NaN, None, empty strings
            if pd.isna(value) or value == '' or value is None:
                if expected_type == 'string':
                    default_value = "N/A"
                else:
                    default_value = 0.0

                log_msg = f"WARNING: Sheet '{sheet_name}', Row {row_idx + 2}, Code Name '{code_name}', Field '{field_name}': Missing value, using {default_value}"
                print(log_msg)
                self.substitution_log.append(log_msg)
                return default_value

            # Convert to expected type
            if expected_type == 'float':
                return float(value)
            elif expected_type == 'int':
                return int(float(value))  # Convert via float first to handle decimal strings
            elif expected_type == 'string':
                return str(value).strip()
            else:
                return value

        except (ValueError, TypeError) as e:
            # If conversion fails, use default
            if expected_type == 'string':
                default_value = "N/A"
            else:
                default_value = 0.0

            log_msg = f"WARNING: Sheet '{sheet_name}', Row {row_idx + 2}, Code Name '{code_name}', Field '{field_name}': Invalid value '{value}' ({e}), using {default_value}"
            print(log_msg)
            self.substitution_log.append(log_msg)
            return default_value

    def is_valid_color_sheet(self, df, sheet_name):
        """
        Determine if a sheet contains valid color data

        Args:
            df: pandas DataFrame
            sheet_name: Name of the sheet

        Returns:
            bool: True if sheet contains color data
        """
        try:
            if df.empty:
                print(f"INFO: Sheet '{sheet_name}': Empty sheet, skipping")
                return False

            # Clean column names
            df.columns = df.columns.str.strip()

            # Required columns for color cards
            required_columns = ['Code', 'L', 'a', 'b', 'R', 'G', 'B']
            columns_present = df.columns.tolist()
            required_present = sum(1 for col in required_columns if col in columns_present)

            if required_present < len(required_columns):
                missing_cols = [col for col in required_columns if col not in columns_present]
                print(f"INFO: Sheet '{sheet_name}': Missing required columns {missing_cols}, skipping")
                return False

            # Check if there's at least some numeric data
            numeric_cols = ['L', 'a', 'b', 'R', 'G', 'B']
            has_numeric_data = False

            for col in numeric_cols:
                if col in df.columns:
                    numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_values) > 0:
                        has_numeric_data = True
                        break

            if not has_numeric_data:
                print(f"INFO: Sheet '{sheet_name}': No valid numeric data found, skipping")
                return False

            print(f"INFO: Sheet '{sheet_name}': Valid color sheet with {len(df)} rows")
            return True

        except Exception as e:
            print(f"ERROR: Sheet '{sheet_name}': Error during validation - {e}")
            return False

    def extract_colour_data(self, sheet_name, df):
        """
        Extract color data from a sheet and build JSON structure

        Args:
            sheet_name: Name of the Excel sheet
            df: pandas DataFrame containing color data

        Returns:
            dict: Dictionary with color data keyed by ID
        """
        colors_data = {}

        # Clean column names
        df.columns = df.columns.str.strip()

        # Map common column name variations
        column_mapping = {
            'Hex (sRGB)': ['hex_srgb', 'Hex sRGB', 'HEX_SRGB'],
            'Hex (ProPhoto RGB)': ['hex_prophoto', 'Hex ProPhoto', 'HEX_PROPHOTO'],
            'L (%)': ['L_hsl', 'L%', 'L_percent']
        }

        for idx, row in df.iterrows():
            try:
                # Get color code - this is mandatory
                code_raw = row.get('Code', None)
                if pd.isna(code_raw) or str(code_raw).strip() == '':
                    print(f"ERROR: Sheet '{sheet_name}', Row {idx + 2}: No valid Code found, skipping row")
                    continue

                code = str(code_raw).strip()

                # Extract original data with validation
                original_data = {
                    'chart': sheet_name,
                    'code': code,
                    # LAB values
                    'L': self.clean_and_validate_value(row.get('L'), 'float', 'L', sheet_name, idx, code),
                    'a': self.clean_and_validate_value(row.get('a'), 'float', 'a', sheet_name, idx, code),
                    'b': self.clean_and_validate_value(row.get('b'), 'float', 'b', sheet_name, idx, code),
                    # RGB values
                    'R': self.clean_and_validate_value(row.get('R'), 'int', 'R', sheet_name, idx, code),
                    'G': self.clean_and_validate_value(row.get('G'), 'int', 'G', sheet_name, idx, code),
                    'B': self.clean_and_validate_value(row.get('B'), 'int', 'B', sheet_name, idx, code),
                    # Hex values
                    'hex_srgb': self.clean_and_validate_value(row.get('Hex (sRGB)'), 'string', 'Hex (sRGB)', sheet_name, idx, code),
                    'hex_prophoto': self.clean_and_validate_value(row.get('Hex (ProPhoto RGB)'), 'string', 'Hex (ProPhoto RGB)', sheet_name, idx, code),
                    # HSL values
                    'H': self.clean_and_validate_value(row.get('H'), 'float', 'H', sheet_name, idx, code),
                    'S': self.clean_and_validate_value(row.get('S (%)'), 'float', 'S (%)', sheet_name, idx, code),
                    'L_hsl': self.clean_and_validate_value(row.get('L (%)'), 'float', 'L (%)', sheet_name, idx, code)
                }

                # Build complete color entry
                color_entry = {
                    'original_data': original_data,
                    'computed_data': {
                        'C': None,
                        'M': None,
                        'Y': None,
                        'K': None,
                        'cmyk_delta_e00': None,
                        'pantone_name': None,
                        'pantone_code': None,
                        'pantone_delta_e00': None
                    },
                    'correspondences': {
                        'has_equivalences': False,
                        'equivalences': {}
                    }
                }

                # Add to colors data with auto-incremented ID
                colors_data[str(self.colour_id_counter)] = color_entry
                self.colour_id_counter += 1

            except Exception as e:
                print(f"ERROR: Sheet '{sheet_name}', Row {idx + 2}, Code '{code if 'code' in locals() else 'Unknown'}': Error processing row - {e}")
                continue

        return colors_data

    def process_excel(self, file_path):
        """
        Main function to process Excel file and return complete JSON structure

        Args:
            file_path: Path to Excel file

        Returns:
            dict: Complete JSON structure with all color data
        """
        try:
            print(f"INFO: Starting Excel processing: {file_path}")

            # Reset counters for fresh processing
            self.colour_id_counter = 1
            self.substitution_log = []

            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Excel file not found: {file_path}")

            # Read all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            total_sheets = len(excel_data)
            print(f"INFO: Found {total_sheets} sheets in Excel file")

            # Process each sheet
            all_colors = {}
            processed_sheets = 0
            skipped_sheets = 0

            for sheet_name, df in excel_data.items():
                print(f"\nINFO: Analyzing sheet: '{sheet_name}'")

                if self.is_valid_color_sheet(df, sheet_name):
                    colors_data = self.extract_colour_data(sheet_name, df)
                    all_colors.update(colors_data)
                    processed_sheets += 1
                    print(f"INFO: Sheet '{sheet_name}': Processed {len(colors_data)} colors")
                else:
                    skipped_sheets += 1
                    print(f"INFO: Sheet '{sheet_name}': Skipped (not a color sheet)")

            # Build final JSON structure
            json_output = {
                **all_colors,  # All color entries with numeric IDs
                'metadata': {
                    'source_file': str(Path(file_path).name),
                    'source_path': str(Path(file_path).absolute()),
                    'generation_date': datetime.now().isoformat(),
                    'total_colors': len(all_colors),
                    'sheets_processed': processed_sheets,
                    'sheets_skipped': skipped_sheets,
                    'substitutions_made': len(self.substitution_log),
                    'icc_profile': None,  # Will be filled by colour_processor
                    'processing_status': 'excel_parsed'
                }
            }

            print(f"\nINFO: Excel processing complete")
            print(f"INFO: Total colors extracted: {len(all_colors)}")
            print(f"INFO: Sheets processed: {processed_sheets}")
            print(f"INFO: Sheets skipped: {skipped_sheets}")
            print(f"INFO: Value substitutions made: {len(self.substitution_log)}")

            return json_output

        except Exception as e:
            print(f"ERROR: Failed to process Excel file: {e}")
            raise


def main():
    """Test function for standalone usage"""
    # Example usage
    parser = ExcelColorParser()

    # Test file path - adjust as needed
    test_file = "ORIGINAL_Cel_Animation_Color_Charts.xlsx"

    try:
        json_data = parser.process_excel(test_file)

        # Save test output
        output_file = "colors_base.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\nINFO: Test output saved to: {output_file}")

    except Exception as e:
        print(f"ERROR: Test failed: {e}")


if __name__ == "__main__":
    main()
