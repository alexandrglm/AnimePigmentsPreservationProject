#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quality_analyzer.py
Analyzes Delta E values in processed Colour JSON to assess conversion quality
"""

import json
import sys
from pathlib import Path
import statistics


class ColourQualityAnalyzer:
    """Analyzes colour conversion quality based on Delta E values"""

    def __init__(self):
        self.delta_e_thresholds = {
            'imperceptible': 1.0,
            'barely_perceptible': 3.0,
            'perceptible': 6.0,
            'clearly_visible': 10.0
        }

        self.quality_levels = {
            'excellent': 'imperceptible',
            'good': 'barely_perceptible',
            'acceptable': 'perceptible',
            'problematic': 'clearly_visible',
            'unacceptable': float('inf')
        }

    def categorize_delta_e(self, delta_e):
        """Categorize a Delta E value into quality levels"""
        if delta_e is None:
            return 'no_data'

        delta_e = float(delta_e)

        if delta_e < self.delta_e_thresholds['imperceptible']:
            return 'excellent'
        elif delta_e < self.delta_e_thresholds['barely_perceptible']:
            return 'good'
        elif delta_e < self.delta_e_thresholds['perceptible']:
            return 'acceptable'
        elif delta_e < self.delta_e_thresholds['clearly_visible']:
            return 'problematic'
        else:
            return 'unacceptable'

    def analyze_cmyk_quality(self, json_data):
        """Analyze CMYK conversion quality"""
        cmyk_analysis = {
            'total_colours': 0,
            'analyzed': 0,
            'no_data': 0,
            'categories': {
                'excellent': [],       # ΔE < 1.0
                'good': [],           # 1.0 ≤ ΔE < 3.0
                'acceptable': [],     # 3.0 ≤ ΔE < 6.0
                'problematic': [],    # 6.0 ≤ ΔE < 10.0
                'unacceptable': []    # ΔE ≥ 10.0
            },
            'statistics': {},
            'worst_performers': []
        }

        delta_e_values = []

        for colour_id, colour_data in json_data.items():
            if colour_id == 'metadata':
                continue

            cmyk_analysis['total_colours'] += 1

            computed_data = colour_data.get('computed_data', {})
            delta_e = computed_data.get('cmyk_delta_e00')

            original_data = colour_data.get('original_data', {})
            chart = original_data.get('chart', 'Unknown')
            code = original_data.get('code', 'Unknown')

            colour_info = {
                'id': colour_id,
                'chart': chart,
                'code': code,
                'delta_e': delta_e,
                'lab': (original_data.get('L', 0), original_data.get('a', 0), original_data.get('b', 0)),
                'cmyk': (computed_data.get('C', 0), computed_data.get('M', 0),
                        computed_data.get('Y', 0), computed_data.get('K', 0))
            }

            if delta_e is None:
                cmyk_analysis['no_data'] += 1
                continue

            cmyk_analysis['analyzed'] += 1
            delta_e_values.append(delta_e)

            category = self.categorize_delta_e(delta_e)
            cmyk_analysis['categories'][category].append(colour_info)

        # Calculate statistics
        if delta_e_values:
            cmyk_analysis['statistics'] = {
                'min': min(delta_e_values),
                'max': max(delta_e_values),
                'mean': statistics.mean(delta_e_values),
                'median': statistics.median(delta_e_values),
                'stdev': statistics.stdev(delta_e_values) if len(delta_e_values) > 1 else 0
            }

            # Find worst performers (top 10 highest Delta E)
            all_colours_with_delta = []
            for category_colours in cmyk_analysis['categories'].values():
                all_colours_with_delta.extend(category_colours)

            cmyk_analysis['worst_performers'] = sorted(
                all_colours_with_delta,
                key=lambda x: x['delta_e'],
                reverse=True
            )[:10]

        return cmyk_analysis

    def analyze_pantone_quality(self, json_data):
        """Analyze Pantone matching quality"""
        pantone_analysis = {
            'total_colours': 0,
            'analyzed': 0,
            'no_match': 0,
            'categories': {
                'excellent': [],
                'good': [],
                'acceptable': [],
                'problematic': [],
                'unacceptable': []
            },
            'statistics': {},
            'worst_performers': []
        }

        delta_e_values = []

        for colour_id, colour_data in json_data.items():
            if colour_id == 'metadata':
                continue

            pantone_analysis['total_colours'] += 1

            computed_data = colour_data.get('computed_data', {})
            delta_e = computed_data.get('pantone_delta_e00')
            pantone_name = computed_data.get('pantone_name', '')
            pantone_code = computed_data.get('pantone_code', '')

            original_data = colour_data.get('original_data', {})
            chart = original_data.get('chart', 'Unknown')
            code = original_data.get('code', 'Unknown')

            colour_info = {
                'id': colour_id,
                'chart': chart,
                'code': code,
                'delta_e': delta_e,
                'pantone_name': pantone_name,
                'pantone_code': pantone_code,
                'lab': (original_data.get('L', 0), original_data.get('a', 0), original_data.get('b', 0))
            }

            if delta_e is None or pantone_name == 'N/A':
                pantone_analysis['no_match'] += 1
                continue

            pantone_analysis['analyzed'] += 1
            delta_e_values.append(delta_e)

            category = self.categorize_delta_e(delta_e)
            pantone_analysis['categories'][category].append(colour_info)

        # Calculate statistics
        if delta_e_values:
            pantone_analysis['statistics'] = {
                'min': min(delta_e_values),
                'max': max(delta_e_values),
                'mean': statistics.mean(delta_e_values),
                'median': statistics.median(delta_e_values),
                'stdev': statistics.stdev(delta_e_values) if len(delta_e_values) > 1 else 0
            }

            # Find worst performers
            all_colours_with_delta = []
            for category_colours in pantone_analysis['categories'].values():
                all_colours_with_delta.extend(category_colours)

            pantone_analysis['worst_performers'] = sorted(
                all_colours_with_delta,
                key=lambda x: x['delta_e'],
                reverse=True
            )[:10]

        return pantone_analysis

    def print_cmyk_report(self, analysis):
        """Print detailed CMYK quality report"""
        print("CMYK CONVERSION QUALITY ANALYSIS")
        print("=" * 50)

        total = analysis['total_colours']
        analyzed = analysis['analyzed']
        no_data = analysis['no_data']

        print(f"Total colours: {total}")
        print(f"Analyzed: {analyzed} ({(analyzed/total)*100:.1f}%)")
        print(f"No Data: {no_data} ({(no_data/total)*100:.1f}%)")

        if analyzed == 0:
            print("No CMYK data to analyze!")
            return False

        # Category breakdown
        print(f"\nQUALITY BREAKDOWN:")
        categories = analysis['categories']

        for category, colours in categories.items():
            count = len(colours)
            percentage = (count / analyzed) * 100

            status = "✅" if category in ['excellent', 'good'] else \
                    "⚠️" if category == 'acceptable' else \
                    "❌"

            print(f"{status} {category.upper()}: {count} colours ({percentage:.1f}%)")

        # Statistics
        stats = analysis['statistics']
        if stats:
            print(f"\nSTATISTICS:")
            print(f"  Mean ΔE: {stats['mean']:.2f}")
            print(f"  Median ΔE: {stats['median']:.2f}")
            print(f"  Min ΔE: {stats['min']:.2f}")
            print(f"  Max ΔE: {stats['max']:.2f}")
            print(f"  Std Dev: {stats['stdev']:.2f}")

        # Quality assessment
        excellent_good = len(categories['excellent']) + len(categories['good'])
        acceptable = len(categories['acceptable'])
        problematic_unacceptable = len(categories['problematic']) + len(categories['unacceptable'])

        print(f"\nOVERALL ASSESSMENT:")
        if (excellent_good / analyzed) > 0.8:
            print("✅ CMYK QUALITY: EXCELLENT - Most colours convert with high fidelity")
        elif (excellent_good / analyzed) > 0.6:
            print("⚠️ CMYK QUALITY: GOOD - Most colours acceptable, some issues")
        elif (acceptable / analyzed) > 0.5:
            print("⚠️ CMYK QUALITY: ACCEPTABLE - Noticeable differences but usable")
        else:
            print("❌ CMYK QUALITY: PROBLEMATIC - Many colours have significant differences")

        # Worst performers
        if analysis['worst_performers']:
            print(f"\nWORST PERFORMERS (Highest ΔE):")
            for i, color in enumerate(analysis['worst_performers'][:5], 1):
                lab = color['lab']
                cmyk = color['cmyk']
                print(f"  {i}. {color['chart']}:{color['code']} - ΔE={color['delta_e']:.2f}")
                print(f"     LAB({lab[0]:.1f},{lab[1]:.1f},{lab[2]:.1f}) → CMYK({cmyk[0]:.1f},{cmyk[1]:.1f},{cmyk[2]:.1f},{cmyk[3]:.1f})")

        return problematic_unacceptable < (analyzed * 0.1)  # Less than 10% problematic

    def print_pantone_report(self, analysis):
        """Print detailed Pantone quality report"""
        print("\nPANTONE MATCHING QUALITY ANALYSIS")
        print("=" * 50)

        total = analysis['total_colours']
        analyzed = analysis['analyzed']
        no_match = analysis['no_match']

        print(f"Total colours: {total}")
        print(f"Matched: {analyzed} ({(analyzed/total)*100:.1f}%)")
        print(f"No Match: {no_match} ({(no_match/total)*100:.1f}%)")

        if analyzed == 0:
            print("No Pantone matches to analyze!")
            return False

        # Category breakdown
        print(f"\nMATCH QUALITY BREAKDOWN:")
        categories = analysis['categories']

        for category, colours in categories.items():
            count = len(colours)
            percentage = (count / analyzed) * 100

            status = "✅" if category in ['excellent', 'good'] else \
                    "⚠️" if category == 'acceptable' else \
                    "❌"

            print(f"{status} {category.upper()}: {count} matches ({percentage:.1f}%)")

        # Statistics
        stats = analysis['statistics']
        if stats:
            print(f"\nSTATISTICS:")
            print(f"  Mean ΔE: {stats['mean']:.2f}")
            print(f"  Median ΔE: {stats['median']:.2f}")
            print(f"  Min ΔE: {stats['min']:.2f}")
            print(f"  Max ΔE: {stats['max']:.2f}")
            print(f"  Std Dev: {stats['stdev']:.2f}")

        # Quality assessment
        excellent_good = len(categories['excellent']) + len(categories['good'])
        problematic_unacceptable = len(categories['problematic']) + len(categories['unacceptable'])

        print(f"\nOVERALL ASSESSMENT:")
        if stats['mean'] < 3.0 and (excellent_good / analyzed) > 0.7:
            print("✅ PANTONE QUALITY: EXCELLENT - Most matches are close")
        elif stats['mean'] < 6.0 and (excellent_good / analyzed) > 0.5:
            print("⚠️ PANTONE QUALITY: GOOD - Reasonable matches, some differences")
        elif stats['mean'] < 10.0:
            print("⚠️ PANTONE QUALITY: ACCEPTABLE - Matches found but with noticeable differences")
        else:
            print("❌ PANTONE QUALITY: POOR - Matches are distant, may not be useful")

        # Worst performers
        if analysis['worst_performers']:
            print(f"\nWORST MATCHES (Highest ΔE):")
            for i, color in enumerate(analysis['worst_performers'][:5], 1):
                lab = color['lab']
                print(f"  {i}. {color['chart']}:{color['code']} → {color['pantone_name']} - ΔE={color['delta_e']:.2f}")
                print(f"     LAB({lab[0]:.1f},{lab[1]:.1f},{lab[2]:.1f})")

        return stats['mean'] < 6.0  # Mean Delta E less than 6.0 is acceptable

    def analyze_json_quality(self, json_file_path):
        """Main function to analyze quality of processed JSON"""
        print("COLOR CONVERSION QUALITY ANALYZER")
        print("=" * 80)

        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            print(f"Analyzing: {json_file_path}")

            # Get metadata
            metadata = json_data.get('metadata', {})
            total_colours = len([k for k in json_data.keys() if k != 'metadata'])
            print(f"Total colours in dataset: {total_colours}")

            # Analyze CMYK quality
            cmyk_analysis = self.analyze_cmyk_quality(json_data)
            cmyk_quality_ok = self.print_cmyk_report(cmyk_analysis)

            # Analyze Pantone quality
            pantone_analysis = self.analyze_pantone_quality(json_data)
            pantone_quality_ok = self.print_pantone_report(pantone_analysis)

            # Final verdict
            print("\n" + "=" * 80)
            print("FINAL VERDICT:")

            if cmyk_quality_ok and pantone_quality_ok:
                print("✅ ME LO CREO - Color conversion quality is excellent")
                verdict = "EXCELLENT"
            elif cmyk_quality_ok or pantone_quality_ok:
                print("⚠️ PARCIALMENTE CREÍBLE - Some quality issues detected")
                verdict = "ACCEPTABLE"
            else:
                print("❌ NO ME LO CREO - Significant quality problems detected")
                verdict = "PROBLEMATIC"

            print("=" * 80)

            return verdict, cmyk_analysis, pantone_analysis

        except Exception as e:
            print(f"ERROR: Failed to analyze JSON file: {e}")
            return None, None, None


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python quality_analyzer.py <colours_complete.json>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not Path(json_file).exists():
        print(f"ERROR: File not found: {json_file}")
        sys.exit(1)

    analyzer = ColourQualityAnalyzer()
    verdict, cmyk_analysis, pantone_analysis = analyzer.analyze_json_quality(json_file)

    if verdict is None:
        sys.exit(1)

    # Exit codes for automation
    if verdict == "EXCELLENT":
        sys.exit(0)
    elif verdict == "ACCEPTABLE":
        sys.exit(1)
    else:  # PROBLEMATIC
        sys.exit(2)


if __name__ == "__main__":
    main()
