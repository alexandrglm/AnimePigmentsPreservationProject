#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
page_count_verifier.py
Verifies page counts in JSON against actual PDF files
"""

import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Install with: pip install pypdf")
    sys.exit(1)


class PageCountVerifier:
    """Verifies page counts between JSON data and actual PDF files"""

    def __init__(self):
        self.json_file = Path("./articles_page_counts.json")
        self.pdfs_dir = Path("./00_single_articles/")
        self.discrepancies = []

    def count_pdf_pages(self, pdf_path):
        """Count pages in a PDF file using same method as Finals.py"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"ERROR: Could not count pages in {pdf_path}: {e}")
            return None

    def load_json_data(self):
        """Load page counts from JSON file"""
        try:
            if not self.json_file.exists():
                print(f"ERROR: JSON file not found: {self.json_file}")
                return None

            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"INFO: Loaded JSON with {len(data)} articles")
            return data

        except Exception as e:
            print(f"ERROR: Failed to load JSON: {e}")
            return None

    def verify_all_page_counts(self):
        """Verify page counts for all articles"""
        print("PAGE COUNT VERIFICATION")
        print("=" * 60)

        # Load JSON data
        json_data = self.load_json_data()
        if json_data is None:
            return False

        print(f"JSON file: {self.json_file}")
        print(f"PDFs directory: {self.pdfs_dir}")
        print(f"Total articles to verify: {len(json_data)}")
        print()

        # Verify each article
        total_articles = len(json_data)
        perfect_matches = 0
        discrepancies_found = 0
        missing_pdfs = 0

        for article in json_data:
            article_num = article['article_number']
            json_pages = article['pages']
            title = article['title']

            # Find corresponding PDF
            pdf_path = self.pdfs_dir / f"article_{article_num:03d}.pdf"

            if not pdf_path.exists():
                print(f"❌ Article {article_num:03d}: PDF missing - {pdf_path.name}")
                missing_pdfs += 1
                continue

            # Count actual PDF pages
            actual_pages = self.count_pdf_pages(pdf_path)

            if actual_pages is None:
                print(f"❌ Article {article_num:03d}: Could not read PDF - {pdf_path.name}")
                continue

            # Compare
            if json_pages == actual_pages:
                print(f"✅ Article {article_num:03d}: {json_pages} pages MATCH - {title[:40]}...")
                perfect_matches += 1
            else:
                difference = actual_pages - json_pages
                print(f"⚠️  Article {article_num:03d}: JSON={json_pages}, PDF={actual_pages} (diff: {difference:+d}) - {title[:40]}...")
                discrepancies_found += 1

                self.discrepancies.append({
                    'article_number': article_num,
                    'title': title,
                    'json_pages': json_pages,
                    'pdf_pages': actual_pages,
                    'difference': difference,
                    'pdf_path': str(pdf_path)
                })

        # Summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total articles: {total_articles}")
        print(f"Perfect matches: {perfect_matches}")
        print(f"Discrepancies: {discrepancies_found}")
        print(f"Missing PDFs: {missing_pdfs}")
        print()

        if discrepancies_found == 0 and missing_pdfs == 0:
            print("🎉 ALL PAGE COUNTS ARE PERFECT!")
        else:
            success_rate = (perfect_matches / total_articles) * 100
            print(f"📊 Success rate: {success_rate:.1f}%")

        # Detailed discrepancy report
        if self.discrepancies:
            print("\nDETAILED DISCREPANCIES:")
            print("-" * 40)
            for disc in self.discrepancies:
                print(f"Article {disc['article_number']:03d}: {disc['json_pages']} → {disc['pdf_pages']} ({disc['difference']:+d})")
                print(f"  Title: {disc['title']}")
                print(f"  PDF: {disc['pdf_path']}")
                print()

        return discrepancies_found == 0 and missing_pdfs == 0

    def save_discrepancies_report(self, output_file="page_count_discrepancies.json"):
        """Save detailed discrepancies report to JSON"""
        if not self.discrepancies:
            print("INFO: No discrepancies to save")
            return

        try:
            output_path = self.pdfs_dir.parent / output_file

            report = {
                'verification_date': json.dumps(datetime.now().isoformat()),
                'total_discrepancies': len(self.discrepancies),
                'discrepancies': self.discrepancies
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"INFO: Discrepancies report saved: {output_path}")

        except Exception as e:
            print(f"ERROR: Could not save discrepancies report: {e}")

    def check_specific_article(self, article_number):
        """Check a specific article in detail"""
        json_data = self.load_json_data()
        if json_data is None:
            return False

        # Find the article
        article = None
        for art in json_data:
            if art['article_number'] == article_number:
                article = art
                break

        if article is None:
            print(f"ERROR: Article {article_number} not found in JSON")
            return False

        print(f"DETAILED CHECK - ARTICLE {article_number:03d}")
        print("=" * 50)
        print(f"Title: {article['title']}")
        print(f"JSON pages: {article['pages']}")
        print(f"File path: {article['file_path']}")
        print()

        # Check PDF
        pdf_path = self.pdfs_dir / f"article_{article_number:03d}.pdf"
        docx_path = self.pdfs_dir / f"article_{article_number:03d}.docx"

        print(f"Expected PDF: {pdf_path}")
        print(f"Expected DOCX: {docx_path}")
        print(f"PDF exists: {pdf_path.exists()}")
        print(f"DOCX exists: {docx_path.exists()}")

        if pdf_path.exists():
            actual_pages = self.count_pdf_pages(pdf_path)
            print(f"Actual PDF pages: {actual_pages}")

            if actual_pages != article['pages']:
                difference = actual_pages - article['pages']
                print(f"❌ DISCREPANCY: {difference:+d} pages")
            else:
                print("✅ PERFECT MATCH")
        else:
            print("❌ PDF file missing")

        return True


def main():
    """Main verification function"""
    if len(sys.argv) > 1:
        try:
            # Check specific article
            article_num = int(sys.argv[1])
            verifier = PageCountVerifier()
            verifier.check_specific_article(article_num)
        except ValueError:
            print("ERROR: Article number must be an integer")
            print("Usage: python page_count_verifier.py [article_number]")
            return 1
    else:
        # Verify all articles
        verifier = PageCountVerifier()
        success = verifier.verify_all_page_counts()

        # Save discrepancies report if any found
        verifier.save_discrepancies_report()

        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
