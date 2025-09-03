#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
Main orchestrator for the colour processing pipeline
Coordinates all processing modules to create complete colour database
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
import sys
import traceback

# Import processing modules
try:

    from excel_parser import ExcelColorParser
    from colour_processor import ColourProcessor
    from pantone_matcher import PantoneMatcher
    from equivalences import EquivalencesProcessor

except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Ensure all module files are in the same directory:")
    print("  - excel_parser.py")
    print("  - colour_processor.py")
    print("  - pantone_matcher.py")
    print("  - equivalences.py")
    sys.exit(1)


class ColourProcessingPipeline:
    """Main pipeline orchestrator for color processing"""

    def __init__(self, config=None):
        self.config = config or {}
        self.processing_log = []
        self.start_time = datetime.now()

    def log_step(self, step_name, status, details=""):
        """Log processing step with timestamp"""
        timestamp = datetime.now()
        duration = (timestamp - self.start_time).total_seconds()

        log_entry = {
            'step': step_name,
            'status': status,
            'timestamp': timestamp.isoformat(),
            'duration_seconds': duration,
            'details': details
        }

        self.processing_log.append(log_entry)

        status_symbol = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⏳"
        print(f"{status_symbol} [{duration:6.1f}s] {step_name}: {status}")
        if details:
            print(f"    {details}")

    def validate_inputs(self, excel_path, icc_profile_path, pantone_csv_path):
        """Validate all input files exist"""
        self.log_step("Input Validation", "RUNNING")

        missing_files = []

        if not Path(excel_path).exists():
            missing_files.append(f"Excel file: {excel_path}")

        if not Path(icc_profile_path).exists():
            missing_files.append(f"ICC profile: {icc_profile_path}")

        if not Path(pantone_csv_path).exists():
            missing_files.append(f"Pantone CSV: {pantone_csv_path}")

        if missing_files:
            error_msg = f"Missing files: {', '.join(missing_files)}"
            self.log_step("Input Validation", "FAILED", error_msg)
            raise FileNotFoundError(error_msg)

        self.log_step("Input Validation", "SUCCESS", f"All input files found")


    def step_1_parse_excel(self, excel_path):
        """Step 1: Parse Excel and create base JSON structure"""
        self.log_step("Excel Parsing", "RUNNING")

        try:
            parser = ExcelColorParser()
            json_data = parser.process_excel(excel_path)

            total_colors = len([k for k in json_data.keys() if k != 'metadata'])
            details = f"Extracted {total_colors} colors from {json_data.get('metadata', {}).get('sheets_processed', 0)} sheets"
            self.log_step("Excel Parsing", "SUCCESS", details)

            return json_data

        except Exception as e:
            self.log_step("Excel Parsing", "FAILED", str(e))
            raise

    def step_2_process_cmyk(self, json_data, icc_profile_path):
        """Step 2: Add CMYK conversion data"""
        self.log_step("CMYK Processing", "RUNNING")

        try:
            processor = ColourProcessor(icc_profile_path)
            json_data = processor.add_cmyk_data(json_data, icc_profile_path)

            metadata = json_data.get('metadata', {})
            processed = metadata.get('cmyk_processed', 0)
            failed = metadata.get('cmyk_failed', 0)
            details = f"Processed {processed} colors, {failed} failed"
            self.log_step("CMYK Processing", "SUCCESS", details)

            return json_data

        except Exception as e:
            self.log_step("CMYK Processing", "FAILED", str(e))
            raise

    def step_3_match_pantone(self, json_data, pantone_csv_path):
        """Step 3: Add Pantone matching data"""
        self.log_step("Pantone Matching", "RUNNING")

        try:
            matcher = PantoneMatcher(pantone_csv_path)
            json_data = matcher.add_pantone_data(json_data, pantone_csv_path)

            metadata = json_data.get('metadata', {})
            processed = metadata.get('pantone_processed', 0)
            matched = metadata.get('pantone_matched', 0)
            failed = metadata.get('pantone_failed', 0)
            details = f"Processed {processed} colors, {matched} matched, {failed} failed"
            self.log_step("Pantone Matching", "SUCCESS", details)

            return json_data

        except Exception as e:
            self.log_step("Pantone Matching", "FAILED", str(e))
            raise

    def step_4_process_equivalences(self, json_data, excel_path):
        """Step 4: Add equivalences data"""
        self.log_step("Equivalences Processing", "RUNNING")

        try:
            processor = EquivalencesProcessor()
            json_data = processor.add_equivalences_data(json_data, excel_path)

            metadata = json_data.get('metadata', {})
            processed = metadata.get('equivalences_processed', 0)
            found = metadata.get('equivalences_found', 0)
            failed = metadata.get('equivalences_failed', 0)
            details = f"Processed {processed} colors, {found} with equivalences, {failed} failed"
            self.log_step("Equivalences Processing", "SUCCESS", details)

            return json_data

        except Exception as e:
            self.log_step("Equivalences Processing", "FAILED", str(e))
            raise

    def finalize_metadata(self, json_data):
        """Add final metadata to JSON structure"""
        self.log_step("Metadata Finalization", "RUNNING")

        try:
            end_time = datetime.now()
            total_duration = (end_time - self.start_time).total_seconds()

            if 'metadata' not in json_data:
                json_data['metadata'] = {}

            # Add pipeline metadata
            json_data['metadata'].update({
                'pipeline_version': '1.0.0',
                'processing_complete': True,
                'processing_start_time': self.start_time.isoformat(),
                'processing_end_time': end_time.isoformat(),
                'total_processing_time_seconds': total_duration,
                'processing_log': self.processing_log,
                'final_status': 'COMPLETE'
            })

            # Calculate final statistics
            total_colors = len([k for k in json_data.keys() if k != 'metadata'])

            stats = {
                'colors_processed': total_colors,
                'cmyk_success_rate': 0,
                'pantone_match_rate': 0,
                'equivalences_rate': 0
            }

            if total_colors > 0:
                cmyk_processed = json_data['metadata'].get('cmyk_processed', 0)
                pantone_matched = json_data['metadata'].get('pantone_matched', 0)
                equivalences_found = json_data['metadata'].get('equivalences_found', 0)

                stats.update({
                    'cmyk_success_rate': (cmyk_processed / total_colors) * 100,
                    'pantone_match_rate': (pantone_matched / total_colors) * 100,
                    'equivalences_rate': (equivalences_found / total_colors) * 100
                })

            json_data['metadata']['final_statistics'] = stats

            details = f"Total duration: {total_duration:.1f}s, {total_colors} colors processed"
            self.log_step("Metadata Finalization", "SUCCESS", details)

            return json_data

        except Exception as e:
            self.log_step("Metadata Finalization", "FAILED", str(e))
            raise

    def save_output(self, json_data, output_path, backup=True):
        """Save final JSON output with optional backup"""
        self.log_step("Output Generation", "RUNNING")

        try:
            output_path = Path(output_path)

            # Create backup if file exists
            if backup and output_path.exists():
                backup_path = output_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                output_path.rename(backup_path)
                print(f"    Existing file backed up to: {backup_path}")

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save JSON with pretty formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, sort_keys=False)

            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            details = f"Saved to {output_path} ({file_size:.1f} MB)"
            self.log_step("Output Generation", "SUCCESS", details)

            return str(output_path.absolute())

        except Exception as e:
            self.log_step("Output Generation", "FAILED", str(e))
            raise

    def print_final_summary(self, json_data, output_path):
        """Print comprehensive processing summary"""
        print("\n" + "="*80)
        print("COLOR PROCESSING PIPELINE - FINAL SUMMARY")
        print("="*80)

        # Basic statistics
        metadata = json_data.get('metadata', {})
        total_colors = len([k for k in json_data.keys() if k != 'metadata'])

        print(f"📊 PROCESSING RESULTS:")
        print(f"   Total Colors Processed: {total_colors}")
        print(f"   Source File: {metadata.get('source_file', 'Unknown')}")
        print(f"   Output File: {output_path}")
        print(f"   Total Processing Time: {metadata.get('total_processing_time_seconds', 0):.1f} seconds")

        # Success rates
        final_stats = metadata.get('final_statistics', {})
        print(f"\n📈 SUCCESS RATES:")
        print(f"   CMYK Conversion: {final_stats.get('cmyk_success_rate', 0):.1f}%")
        print(f"   Pantone Matching: {final_stats.get('pantone_match_rate', 0):.1f}%")
        print(f"   Equivalences Found: {final_stats.get('equivalences_rate', 0):.1f}%")

        # Processing details
        print(f"\n🔧 PROCESSING DETAILS:")
        print(f"   ICC Profile: {metadata.get('icc_profile', 'Unknown')}")
        print(f"   Pantone Database: {metadata.get('pantone_database', 'Unknown')}")
        print(f"   Correspondence Entries: {metadata.get('correspondence_entries', 0)}")

        # Step summary
        print(f"\n⚙️  PROCESSING STEPS:")
        for log_entry in self.processing_log:
            status_symbol = "✅" if log_entry['status'] == "SUCCESS" else "❌"
            print(f"   {status_symbol} {log_entry['step']}: {log_entry['status']} ({log_entry['duration_seconds']:.1f}s)")

        print("\n" + "="*80)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80)

    def run_pipeline(self, excel_path, output_path, icc_profile_path, pantone_csv_path):
        """Run complete processing pipeline"""
        print("🚀 STARTING COLOR PROCESSING PIPELINE")
        print("="*80)
        print(f"Excel Source: {excel_path}")
        print(f"Output Target: {output_path}")
        print(f"ICC Profile: {icc_profile_path}")
        print(f"Pantone Database: {pantone_csv_path}")
        print("="*80)

        try:
            # Validate inputs
            self.validate_inputs(excel_path, icc_profile_path, pantone_csv_path)

            # Step 1: Parse Excel
            json_data = self.step_1_parse_excel(excel_path)

            # Step 2: Process CMYK
            json_data = self.step_2_process_cmyk(json_data, icc_profile_path)

            # Step 3: Match Pantone
            json_data = self.step_3_match_pantone(json_data, pantone_csv_path)

            # Step 4: Process Equivalences
            json_data = self.step_4_process_equivalences(json_data, excel_path)

            # Finalize metadata
            json_data = self.finalize_metadata(json_data)

            # Save output
            final_output_path = self.save_output(json_data, output_path)

            # Print summary
            self.print_final_summary(json_data, final_output_path)

            return json_data, final_output_path

        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            print(f"Error details: {traceback.format_exc()}")

            # Try to save partial results if any processing was completed
            if 'json_data' in locals():
                try:
                    error_output = Path(output_path).with_suffix('.error.json')
                    self.save_output(json_data, error_output, backup=False)
                    print(f"Partial results saved to: {error_output}")
                except:
                    pass

            raise


def create_default_config():
    """Create a default configuration"""
    return {
        'excel_file': 'ORIGINAL_Cel_Animation_Color_Charts.xlsx',
        'output_file': 'colours_complete.json',
        'icc_profile': 'PSOcoated_v3.icc',
        'pantone_csv': 'pantone_lab_2024.csv',
        'backup_existing': True
    }


def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(
        description='Color Processing Pipeline - Convert Excel color charts to complete JSON database',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Define arguments
    parser.add_argument(
        'excel_file',
        nargs='?',
        default='ORIGINAL_Cel_Animation_Color_Charts.xlsx',
        help='Path to Excel file with color charts'
    )

    parser.add_argument(
        '-o', '--output',
        default='colours_complete.json',
        help='Output JSON file path'
    )

    parser.add_argument(
        '-i', '--icc-profile',
        default='PSOcoated_v3.icc',
        help='ICC profile for CMYK conversion'
    )

    parser.add_argument(
        '-p', '--pantone-csv',
        default='pantone_lab_2024.csv',
        help='Pantone color database CSV file'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not backup existing output file'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Parse arguments
    args = parser.parse_args()

    # Create and run pipeline
    try:
        config = {
            'backup_existing': not args.no_backup,
            'verbose': args.verbose
        }

        pipeline = ColourProcessingPipeline(config)

        json_data, output_path = pipeline.run_pipeline(
            excel_path=args.excel_file,
            output_path=args.output,
            icc_profile_path=args.icc_profile,
            pantone_csv_path=args.pantone_csv
        )

        return 0  # Success

    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        return 130

    except Exception as e:
        print(f"\n💥 Pipeline failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
