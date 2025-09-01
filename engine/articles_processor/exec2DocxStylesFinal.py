#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocxStyles.py
Complete styles configuration module for DOCX generation
Centralizes all typography, colors, fonts, and layout settings
"""

from pathlib import Path
from datetime import datetime
import json

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


class StylesConfig:
    """
    UNIFIED CONFIGURATION - Edit all styles here
    Change any value and call refresh_styles() to apply changes
    """

    def __init__(self):
        # === COLORS ===
        self.colors = {
            'primary': RGBColor(51, 51, 102),        # Dark blue
            'secondary': RGBColor(102, 51, 51),      # Dark red
            'accent': RGBColor(77, 77, 77),          # Dark gray
            'text': RGBColor(26, 26, 26),            # Almost black
            'light_text': RGBColor(180, 180, 180),   # Light gray
            'japanese': RGBColor(0, 0, 0),           # Pure black for Japanese
            'light_bg': RGBColor(245, 245, 245),     # Light background
            'quote_bg': RGBColor(250, 250, 250),     # Quote background
            'quote_border': RGBColor(200, 200, 200), # Quote border
            'code_bg': RGBColor(240, 240, 240),      # Code background
            'code_text': RGBColor(50, 50, 50),       # Code text
            'code_border': RGBColor(200, 200, 200),  # Code border
            'white': RGBColor(255, 255, 255)         # Pure white
        }

        # === FONTS ===
        self.fonts = {
            'title': 'BPG Serif GPL&GNU',           # For H1, cover titles
            'header': 'BPG Gorda GPL&GNU',          # For H2, H3
            'body': 'Amiri',                        # For normal text
            'japanese': 'Noto Sans CJK JP',         # For Japanese characters
            'monospace': 'Courier New',             # For code blocks
            'code': 'Courier New'                   # For inline code
        }

        # Font fallbacks (when custom fonts not available)
        self.font_fallbacks = {
            'title': 'Times New Roman',
            'header': 'Arial',
            'body': 'Times New Roman',
            'japanese': 'Arial Unicode MS',
            'monospace': 'Courier New',
            'code': 'Courier New'
        }

        # === FONT SIZES (as numbers, not Pt objects) ===
        self.font_sizes = {
            'cover_title': 28,
            'cover_subtitle': 18,
            'h1': 20,
            'h2': 16,
            'h3': 15,
            'h4': 14,
            'h5': 13,
            'h6': 12,
            'normal': 14,
            'quote': 12,
            'code_inline': 10,
            'code_block': 10,
            'toc': 12,
            'profile': 10,
            'small': 9
        }

        # === PAGE LAYOUT (as numbers for inches) ===
        self.margins = {
            'top': 0.8,
            'bottom': 1.0,
            'left': 0.8,
            'right': 0.8
        }

        # === UNIFIED SPACING SYSTEM (as numbers for points) ===
        self.spacing = {
            # HEADERS - BEFORE spacing
            'h1_before': 0,
            'h2_before': 0,
            'h3_before': 0,
            'h4_before': 0,
            'h5_before': 0,
            'h6_before': 0,

            # HEADERS - AFTER spacing
            'h1_after': 1,
            'h2_after': 1,
            'h3_after': 1,
            'h4_after': 1,
            'h5_after': 1,
            'h6_after': 1,

            # PARAGRAPHS - general spacing
            'paragraph_before': 3,
            'paragraph_after': 0,

            # QUOTES - spacing and indentation
            'quote_before': 1,
            'quote_after': 1,
            'quote_indent_left': 30,
            'quote_indent_right': 30,

            # CODE - spacing and indentation
            'code_block_before': 1,
            'code_block_after': 1,
            'code_block_indent_left': 20,
            'code_block_indent_right': 20,

            # LISTS - spacing and indentation
            'list_before': 1,
            'list_after': 1,
            'list_indent': 20,
            'list_item_spacing': 4,

            # COVER PAGE - special spacing
            'cover_title_before': 30,
            'cover_title_after': 20,
            'cover_subtitle_before': 0,
            'cover_subtitle_after': 15,

            # TOC - table of contents spacing
            'toc_before': 3,
            'toc_after': 8,
            'toc_indent': 20,

            # PROFILE - special sections
            'profile_before': 15,
            'profile_after': 8,

            # SPECIAL ELEMENTS
            'blank_page_before': 0,
            'blank_page_after': 0,
            'horizontal_rule_before': 10,
            'horizontal_rule_after': 10
        }

        # === LINE SPACING (as floats, no conversion needed) ===
        self.line_spacing = {
            'cover': 1.2,
            'header': 1.1,
            'normal': 0.80,
            'quote': 1.2,
            'code': 1.0,
            'toc': 1.0
        }

        # === DOCUMENT METADATA ===
        self.document_info = {
            'title': "COLOR DESIGN NOTES",
            'subtitle': "Complete Article Collection",
            'author': "Tsujita Kunio",
            'author_japanese': "辻田邦夫"
        }

        # === PROCESSING SETTINGS ===
        self.processing = {
            'verbose': False,
            'cleanup_temp_files': False,
            'estimated_lines_per_page': 45,
            'toc_entries_per_page': 35,
            'header_line_multiplier': 2,
            'default_index_offset': 13,
            'default_title_offset': 2,
            'output_dir': Path("./output/"),
            'temp_dir_name': "00_single_articles"
        }

    def get_generation_date(self):
        """Get formatted generation date"""
        return datetime.now().strftime('%B %d, %Y')


class FontManager:
    """Manages font availability and fallbacks"""

    def __init__(self, config, fonts_dir="./fonts/"):
        self.config = config
        self.fonts_dir = Path(fonts_dir)
        self.available_fonts = self._check_available_fonts()

    def _check_available_fonts(self):
        """Check which custom fonts are available"""
        available = {}

        # Updated font file mappings to match your actual files
        font_files = {
            'title': 'bpg_serif.ttf',               # BPG Serif
            'header': 'bpg_gorda.ttf',              # BPG Gorda
            'body': 'amiri.ttf',                    # Amiri
            'japanese': 'NotoSansJP-SemiBold.ttf',
            'monospace': 'courier.ttf',             # Courier for monospace
            'code': 'courier.ttf'                   # Same as monospace for code
        }

        for font_type, font_name in self.config.fonts.items():
            if font_type in font_files:
                font_file = self.fonts_dir / font_files[font_type]
                if font_file.exists():
                    available[font_type] = font_name
                    print(f"INFO: Found custom font {font_type}: {font_name} ({font_files[font_type]})")
                else:
                    available[font_type] = self.config.font_fallbacks[font_type]
                    print(f"WARNING: Custom font {font_type} not found at {font_file}, using fallback: {available[font_type]}")
            else:
                available[font_type] = font_name

        return available

    def get_font(self, font_type):
        """Get font name for a specific type"""
        return self.available_fonts.get(font_type, self.config.font_fallbacks.get(font_type, 'Times New Roman'))


class DocumentStyles:
    """Document styles manager that applies configuration"""

    def __init__(self, document, config):
        self.document = document
        self.config = config
        self.font_manager = FontManager(config)
        self.styles_created = False

    def setup_page_settings(self):
        """Configure document page settings"""
        section = self.document.sections[0]
        section.top_margin = Inches(self.config.margins['top'])
        section.bottom_margin = Inches(self.config.margins['bottom'])
        section.left_margin = Inches(self.config.margins['left'])
        section.right_margin = Inches(self.config.margins['right'])

    def modify_default_normal_style(self):
        """Modify Word's default Normal style"""
        try:
            normal_style = self.document.styles['Normal']
            normal_style.font.name = self.font_manager.get_font('body')
            normal_style.font.size = Pt(self.config.font_sizes['normal'])
            normal_style.paragraph_format.space_after = Pt(self.config.spacing['paragraph_after'])
            normal_style.paragraph_format.space_before = Pt(self.config.spacing['paragraph_before'])
            normal_style.paragraph_format.line_spacing = self.config.line_spacing['normal']
            print(f"INFO: Modified Normal style - Font: {self.font_manager.get_font('body')}, Size: {self.config.font_sizes['normal']}pt")
        except Exception as e:
            print(f"WARNING: Could not modify Normal style: {e}")

    def create_cover_styles(self):
        """Create cover page styles"""
        styles = self.document.styles

        # Cover title
        if 'CoverTitle' not in [s.name for s in styles]:
            cover_title = styles.add_style('CoverTitle', WD_STYLE_TYPE.PARAGRAPH)
        else:
            cover_title = styles['CoverTitle']

        cover_title.font.name = self.font_manager.get_font('title')
        cover_title.font.size = Pt(self.config.font_sizes['cover_title'])
        cover_title.font.color.rgb = self.config.colors['primary']
        cover_title.font.bold = True
        cover_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cover_title.paragraph_format.space_after = Pt(self.config.spacing['cover_title_after'])
        cover_title.paragraph_format.space_before = Pt(self.config.spacing['cover_title_before'])

        # Cover subtitle
        if 'CoverSubtitle' not in [s.name for s in styles]:
            cover_subtitle = styles.add_style('CoverSubtitle', WD_STYLE_TYPE.PARAGRAPH)
        else:
            cover_subtitle = styles['CoverSubtitle']

        cover_subtitle.font.name = self.font_manager.get_font('body')
        cover_subtitle.font.size = Pt(self.config.font_sizes['cover_subtitle'])
        cover_subtitle.font.color.rgb = self.config.colors['secondary']
        cover_subtitle.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cover_subtitle.paragraph_format.space_after = Pt(self.config.spacing['cover_subtitle_after'])
        cover_subtitle.paragraph_format.space_before = Pt(self.config.spacing['cover_subtitle_before'])

    def create_header_styles(self):
        """Create header styles (H1-H6) with unified spacing system"""
        styles = self.document.styles

        # H1 - Article title
        if 'ArticleH1' not in [s.name for s in styles]:
            h1_style = styles.add_style('ArticleH1', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h1_style = styles['ArticleH1']

        h1_style.font.name = self.font_manager.get_font('title')
        h1_style.font.size = Pt(self.config.font_sizes['h1'])
        h1_style.font.color.rgb = self.config.colors['primary']
        h1_style.font.bold = True
        h1_style.paragraph_format.space_after = Pt(self.config.spacing['h1_after'])
        h1_style.paragraph_format.space_before = Pt(self.config.spacing['h1_before'])

        # H2 - Article subtitle
        if 'ArticleH2' not in [s.name for s in styles]:
            h2_style = styles.add_style('ArticleH2', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h2_style = styles['ArticleH2']

        h2_style.font.name = self.font_manager.get_font('header')
        h2_style.font.size = Pt(self.config.font_sizes['h2'])
        h2_style.font.color.rgb = self.config.colors['secondary']
        h2_style.font.bold = True
        h2_style.paragraph_format.space_after = Pt(self.config.spacing['h2_after'])
        h2_style.paragraph_format.space_before = Pt(self.config.spacing['h2_before'])

        # H3 - Section subtitle
        if 'ArticleH3' not in [s.name for s in styles]:
            h3_style = styles.add_style('ArticleH3', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h3_style = styles['ArticleH3']

        h3_style.font.name = self.font_manager.get_font('header')
        h3_style.font.size = Pt(self.config.font_sizes['h3'])
        h3_style.font.color.rgb = self.config.colors['accent']
        h3_style.font.bold = True
        h3_style.paragraph_format.space_after = Pt(self.config.spacing['h3_after'])
        h3_style.paragraph_format.space_before = Pt(self.config.spacing['h3_before'])

        # H4 - Smaller section subtitle
        if 'ArticleH4' not in [s.name for s in styles]:
            h4_style = styles.add_style('ArticleH4', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h4_style = styles['ArticleH4']

        h4_style.font.name = self.font_manager.get_font('header')
        h4_style.font.size = Pt(self.config.font_sizes['h4'])
        h4_style.font.color.rgb = self.config.colors['accent']
        h4_style.font.bold = True
        h4_style.paragraph_format.space_after = Pt(self.config.spacing['h4_after'])
        h4_style.paragraph_format.space_before = Pt(self.config.spacing['h4_before'])

        # H5 - Minor subheading
        if 'ArticleH5' not in [s.name for s in styles]:
            h5_style = styles.add_style('ArticleH5', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h5_style = styles['ArticleH5']

        h5_style.font.name = self.font_manager.get_font('body')
        h5_style.font.size = Pt(self.config.font_sizes['h5'])
        h5_style.font.color.rgb = self.config.colors['accent']
        h5_style.font.bold = True
        h5_style.paragraph_format.space_after = Pt(self.config.spacing['h5_after'])
        h5_style.paragraph_format.space_before = Pt(self.config.spacing['h5_before'])

        # H6 - Smallest subheading
        if 'ArticleH6' not in [s.name for s in styles]:
            h6_style = styles.add_style('ArticleH6', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h6_style = styles['ArticleH6']

        h6_style.font.name = self.font_manager.get_font('body')
        h6_style.font.size = Pt(self.config.font_sizes['h6'])
        h6_style.font.color.rgb = self.config.colors['accent']
        h6_style.font.bold = True
        h6_style.paragraph_format.space_after = Pt(self.config.spacing['h6_after'])
        h6_style.paragraph_format.space_before = Pt(self.config.spacing['h6_before'])

    def create_content_styles(self):
        """Create content and text styles with unified spacing"""
        styles = self.document.styles

        # Normal text
        if 'NormalText' not in [s.name for s in styles]:
            normal_style = styles.add_style('NormalText', WD_STYLE_TYPE.PARAGRAPH)
        else:
            normal_style = styles['NormalText']

        normal_style.font.name = self.font_manager.get_font('body')
        normal_style.font.size = Pt(self.config.font_sizes['normal'])
        normal_style.font.color.rgb = self.config.colors['text']
        normal_style.paragraph_format.space_after = Pt(self.config.spacing['paragraph_after'])
        normal_style.paragraph_format.space_before = Pt(self.config.spacing['paragraph_before'])
        normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal_style.paragraph_format.line_spacing = self.config.line_spacing['normal']

        # Blockquote style
        if 'BlockQuote' not in [s.name for s in styles]:
            quote_style = styles.add_style('BlockQuote', WD_STYLE_TYPE.PARAGRAPH)
        else:
            quote_style = styles['BlockQuote']

        quote_style.font.name = self.font_manager.get_font('body')
        quote_style.font.size = Pt(self.config.font_sizes['quote'])
        quote_style.font.color.rgb = self.config.colors['accent']
        quote_style.font.italic = True
        quote_style.paragraph_format.space_after = Pt(self.config.spacing['quote_after'])
        quote_style.paragraph_format.space_before = Pt(self.config.spacing['quote_before'])
        quote_style.paragraph_format.left_indent = Pt(self.config.spacing['quote_indent_left'])
        quote_style.paragraph_format.right_indent = Pt(self.config.spacing['quote_indent_right'])
        quote_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        quote_style.paragraph_format.line_spacing = self.config.line_spacing['quote']

        # Code block style
        if 'CodeBlock' not in [s.name for s in styles]:
            code_block_style = styles.add_style('CodeBlock', WD_STYLE_TYPE.PARAGRAPH)
        else:
            code_block_style = styles['CodeBlock']

        code_block_style.font.name = self.font_manager.get_font('code')
        code_block_style.font.size = Pt(self.config.font_sizes['code_block'])
        code_block_style.font.color.rgb = self.config.colors['code_text']
        code_block_style.paragraph_format.space_after = Pt(self.config.spacing['code_block_after'])
        code_block_style.paragraph_format.space_before = Pt(self.config.spacing['code_block_before'])
        code_block_style.paragraph_format.left_indent = Pt(self.config.spacing['code_block_indent_left'])
        code_block_style.paragraph_format.right_indent = Pt(self.config.spacing['code_block_indent_right'])
        code_block_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        code_block_style.paragraph_format.line_spacing = self.config.line_spacing['code']

        # Table of contents
        if 'TOCEntry' not in [s.name for s in styles]:
            toc_style = styles.add_style('TOCEntry', WD_STYLE_TYPE.PARAGRAPH)
        else:
            toc_style = styles['TOCEntry']

        toc_style.font.name = self.font_manager.get_font('body')
        toc_style.font.size = Pt(self.config.font_sizes['toc'])
        toc_style.font.color.rgb = self.config.colors['text']
        toc_style.paragraph_format.space_after = Pt(self.config.spacing['toc_after'])
        toc_style.paragraph_format.space_before = Pt(self.config.spacing['toc_before'])
        toc_style.paragraph_format.left_indent = Pt(self.config.spacing['toc_indent'])
        toc_style.paragraph_format.line_spacing = self.config.line_spacing['toc']

        # Profile text
        if 'ProfileText' not in [s.name for s in styles]:
            profile_style = styles.add_style('ProfileText', WD_STYLE_TYPE.PARAGRAPH)
        else:
            profile_style = styles['ProfileText']

        profile_style.font.name = self.font_manager.get_font('body')
        profile_style.font.size = Pt(self.config.font_sizes['profile'])
        profile_style.font.color.rgb = self.config.colors['accent']
        profile_style.paragraph_format.space_after = Pt(self.config.spacing['profile_after'])
        profile_style.paragraph_format.space_before = Pt(self.config.spacing['profile_before'])
        profile_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def create_special_styles(self):
        """Create special purpose styles with unified spacing"""
        styles = self.document.styles

        # Blank page style
        if 'BlankPage' not in [s.name for s in styles]:
            blank_style = styles.add_style('BlankPage', WD_STYLE_TYPE.PARAGRAPH)
        else:
            blank_style = styles['BlankPage']

        blank_style.font.name = self.font_manager.get_font('body')
        blank_style.font.size = Pt(self.config.font_sizes['small'])
        blank_style.font.color.rgb = self.config.colors['light_text']
        blank_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        blank_style.paragraph_format.space_after = Pt(self.config.spacing['blank_page_after'])
        blank_style.paragraph_format.space_before = Pt(self.config.spacing['blank_page_before'])

        # Japanese character style
        if 'JapaneseText' not in [s.name for s in styles]:
            japanese_style = styles.add_style('JapaneseText', WD_STYLE_TYPE.CHARACTER)
        else:
            japanese_style = styles['JapaneseText']

        japanese_style.font.name = self.font_manager.get_font('japanese')
        japanese_style.font.color.rgb = self.config.colors['japanese']

        # Inline code character style
        if 'InlineCode' not in [s.name for s in styles]:
            inline_code_style = styles.add_style('InlineCode', WD_STYLE_TYPE.CHARACTER)
        else:
            inline_code_style = styles['InlineCode']

        inline_code_style.font.name = self.font_manager.get_font('code')
        inline_code_style.font.size = Pt(self.config.font_sizes['code_inline'])
        inline_code_style.font.color.rgb = self.config.colors['code_text']

        # List style with unified spacing
        if 'ListItem' not in [s.name for s in styles]:
            list_style = styles.add_style('ListItem', WD_STYLE_TYPE.PARAGRAPH)
        else:
            list_style = styles['ListItem']

        list_style.font.name = self.font_manager.get_font('body')
        list_style.font.size = Pt(self.config.font_sizes['normal'])
        list_style.font.color.rgb = self.config.colors['text']
        list_style.paragraph_format.space_after = Pt(self.config.spacing['list_after'])
        list_style.paragraph_format.space_before = Pt(self.config.spacing['list_before'])
        list_style.paragraph_format.left_indent = Pt(self.config.spacing['list_indent'])
        list_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        list_style.paragraph_format.line_spacing = self.config.line_spacing['normal']

        # Horizontal rule style
        if 'HorizontalRule' not in [s.name for s in styles]:
            hr_style = styles.add_style('HorizontalRule', WD_STYLE_TYPE.PARAGRAPH)
        else:
            hr_style = styles['HorizontalRule']

        hr_style.font.name = self.font_manager.get_font('body')
        hr_style.font.size = Pt(self.config.font_sizes['normal'])
        hr_style.font.color.rgb = self.config.colors['accent']
        hr_style.paragraph_format.space_after = Pt(self.config.spacing['horizontal_rule_after'])
        hr_style.paragraph_format.space_before = Pt(self.config.spacing['horizontal_rule_before'])
        hr_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def refresh_all_styles(self):
        """Refresh all styles with current configuration values"""
        print("INFO: Refreshing all styles with unified spacing system...")

        # Setup page layout
        self.setup_page_settings()

        # Modify default styles
        self.modify_default_normal_style()

        # Recreate all custom styles
        self.create_cover_styles()
        self.create_header_styles()
        self.create_content_styles()
        self.create_special_styles()

        self.styles_created = True
        print(f"INFO: All styles refreshed with unified spacing - Normal font: {self.font_manager.get_font('body')}, Size: {self.config.font_sizes['normal']}pt")

    def get_style_names(self):
        """Get dictionary of all style names for easy reference"""
        return {
            'cover_title': 'CoverTitle',
            'cover_subtitle': 'CoverSubtitle',
            'h1': 'ArticleH1',
            'h2': 'ArticleH2',
            'h3': 'ArticleH3',
            'h4': 'ArticleH4',
            'h5': 'ArticleH5',
            'h6': 'ArticleH6',
            'normal': 'NormalText',
            'quote': 'BlockQuote',
            'code_block': 'CodeBlock',
            'list': 'ListItem',
            'horizontal_rule': 'HorizontalRule',
            'toc': 'TOCEntry',
            'profile': 'ProfileText',
            'blank': 'BlankPage',
            'japanese': 'JapaneseText',
            'inline_code': 'InlineCode'
        }


class StylesManager:
    """Main styles manager that coordinates all style components"""

    def __init__(self, document):
        self.document = document
        self.config = StylesConfig()
        self.document_styles = DocumentStyles(document, self.config)

        # Initialize styles
        self.refresh_styles()

        print(f"INFO: StylesManager initialized with unified spacing")

    def refresh_styles(self):
        """Refresh all document styles"""
        self.document_styles.refresh_all_styles()

    def get_style(self, style_name):
        """Get a specific style by name"""
        style_names = self.document_styles.get_style_names()
        docx_style_name = style_names.get(style_name)

        if docx_style_name and docx_style_name in [s.name for s in self.document.styles]:
            return self.document.styles[docx_style_name]
        else:
            print(f"WARNING: Style '{style_name}' not found, using Normal")
            return self.document.styles['Normal']

    def update_config(self, **kwargs):
        """Update configuration and refresh styles"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"INFO: Updated {key} = {value}")

        self.refresh_styles()

    def print_configuration_summary(self):
        """Print summary of current configuration"""
        print("\n" + "="*80)
        print("UNIFIED DOCUMENT STYLES CONFIGURATION SUMMARY")
        print("="*80)

        print(f"Document: {self.config.document_info['title']}")
        print(f"Author: {self.config.document_info['author']} ({self.config.document_info['author_japanese']})")
        print(f"Date: {datetime.now().strftime('%B %d, %Y')}")

        print(f"\nColors:")
        print(f"   Primary: {self.config.colors['primary']}")
        print(f"   Secondary: {self.config.colors['secondary']}")
        print(f"   Text: {self.config.colors['text']}")
        print(f"   Code: {self.config.colors['code_text']}")

        print(f"\nFonts:")
        for font_type, font_name in self.document_styles.font_manager.available_fonts.items():
            print(f"   {font_type.title()}: {font_name}")

        print(f"\nLayout:")
        print(f"   Margins: {self.config.margins['top']}\" top, {self.config.margins['bottom']}\" bottom")
        print(f"   Line spacing: {self.config.line_spacing['normal']}")

        print(f"\nTypography:")
        print(f"   H1: {self.config.font_sizes['h1']}pt (before: {self.config.spacing['h1_before']}pt, after: {self.config.spacing['h1_after']}pt)")
        print(f"   H2: {self.config.font_sizes['h2']}pt (before: {self.config.spacing['h2_before']}pt, after: {self.config.spacing['h2_after']}pt)")
        print(f"   H3: {self.config.font_sizes['h3']}pt (before: {self.config.spacing['h3_before']}pt, after: {self.config.spacing['h3_after']}pt)")
        print(f"   H4: {self.config.font_sizes['h4']}pt (before: {self.config.spacing['h4_before']}pt, after: {self.config.spacing['h4_after']}pt)")
        print(f"   H5: {self.config.font_sizes['h5']}pt (before: {self.config.spacing['h5_before']}pt, after: {self.config.spacing['h5_after']}pt)")
        print(f"   H6: {self.config.font_sizes['h6']}pt (before: {self.config.spacing['h6_before']}pt, after: {self.config.spacing['h6_after']}pt)")
        print(f"   Normal: {self.config.font_sizes['normal']}pt (before: {self.config.spacing['paragraph_before']}pt, after: {self.config.spacing['paragraph_after']}pt)")
        print(f"   Quote: {self.config.font_sizes['quote']}pt (before: {self.config.spacing['quote_before']}pt, after: {self.config.spacing['quote_after']}pt)")
        print(f"   Code inline: {self.config.font_sizes['code_inline']}pt")
        print(f"   Code block: {self.config.font_sizes['code_block']}pt (before: {self.config.spacing['code_block_before']}pt, after: {self.config.spacing['code_block_after']}pt)")

        print("="*80)


def create_styles_for_document(document, verbose=False):
    """
    Main function to create and configure all styles for a document

    Args:
        document: python-docx Document object
        verbose: Enable verbose output

    Returns:
        StylesManager: Configured styles manager
    """
    styles_manager = StylesManager(document)

    if verbose:
        styles_manager.config.processing['verbose'] = True
        styles_manager.print_configuration_summary()

    return styles_manager


def modify_styles(document, **style_changes):
    """
    Convenient function to modify specific styles

    Usage examples:
    modify_styles(doc, normal_size=14, primary_color=RGBColor(100, 50, 50))
    modify_styles(doc, h1_size=24, h1_before=30, h1_after=20)
    modify_styles(doc, quote_size=13, h4_size=13, code_inline_size=9)
    modify_styles(doc, h3_before=1, h4_before=1, h5_before=1, h6_before=1)
    """
    styles_manager = StylesManager(document)

    # Apply font size changes
    font_size_mapping = {
        'normal_size': 'normal',
        'h1_size': 'h1', 'h2_size': 'h2', 'h3_size': 'h3',
        'h4_size': 'h4', 'h5_size': 'h5', 'h6_size': 'h6',
        'cover_title_size': 'cover_title', 'cover_subtitle_size': 'cover_subtitle',
        'toc_size': 'toc', 'profile_size': 'profile',
        'quote_size': 'quote', 'code_inline_size': 'code_inline', 'code_block_size': 'code_block'
    }

    # Apply spacing changes - UNIFIED SYSTEM
    spacing_mapping = {
        # Headers before
        'h1_before': 'h1_before', 'h2_before': 'h2_before', 'h3_before': 'h3_before',
        'h4_before': 'h4_before', 'h5_before': 'h5_before', 'h6_before': 'h6_before',
        # Headers after
        'h1_after': 'h1_after', 'h2_after': 'h2_after', 'h3_after': 'h3_after',
        'h4_after': 'h4_after', 'h5_after': 'h5_after', 'h6_after': 'h6_after',
        # Paragraphs
        'paragraph_before': 'paragraph_before', 'paragraph_after': 'paragraph_after',
        # Quotes
        'quote_before': 'quote_before', 'quote_after': 'quote_after',
        'quote_indent_left': 'quote_indent_left', 'quote_indent_right': 'quote_indent_right',
        # Code
        'code_block_before': 'code_block_before', 'code_block_after': 'code_block_after',
        'code_block_indent_left': 'code_block_indent_left', 'code_block_indent_right': 'code_block_indent_right',
        # Lists
        'list_before': 'list_before', 'list_after': 'list_after', 'list_indent': 'list_indent',
        # Others
        'toc_before': 'toc_before', 'toc_after': 'toc_after',
        'profile_before': 'profile_before', 'profile_after': 'profile_after'
    }

    # Apply font size changes
    for change_key, value in style_changes.items():
        if change_key in font_size_mapping:
            font_key = font_size_mapping[change_key]
            styles_manager.config.font_sizes[font_key] = value
            print(f"INFO: Modified {change_key} -> {value}pt")

    # Apply spacing changes
    for change_key, value in style_changes.items():
        if change_key in spacing_mapping:
            spacing_key = spacing_mapping[change_key]
            styles_manager.config.spacing[spacing_key] = value
            print(f"INFO: Modified {change_key} -> {value}pt")

    # Apply color changes
    color_mapping = {
        'primary_color': 'primary', 'secondary_color': 'secondary', 'accent_color': 'accent',
        'text_color': 'text', 'quote_color': 'accent', 'japanese_color': 'japanese',
        'code_text_color': 'code_text', 'code_bg_color': 'code_bg'
    }

    for change_key, value in style_changes.items():
        if change_key in color_mapping:
            color_key = color_mapping[change_key]
            styles_manager.config.colors[color_key] = value
            print(f"INFO: Modified {change_key} -> {value}")

    # Apply font changes
    font_mapping = {
        'title_font': 'title', 'header_font': 'header', 'body_font': 'body',
        'japanese_font': 'japanese', 'code_font': 'code', 'monospace_font': 'monospace'
    }

    for change_key, value in style_changes.items():
        if change_key in font_mapping:
            font_key = font_mapping[change_key]
            styles_manager.config.fonts[font_key] = value
            print(f"INFO: Modified {change_key} -> {value}")

    # Refresh styles to apply changes
    styles_manager.refresh_styles()

    return styles_manager


# Quick access functions for common operations
def get_default_config():
    """Get default configuration for easy editing"""
    return StylesConfig()

def quick_spacing_change(document, **spacing_changes):
    """Quick way to change spacing values"""
    return modify_styles(document, **spacing_changes)

def quick_font_size_change(document, **font_changes):
    """Quick way to change font sizes"""
    return modify_styles(document, **font_changes)


# Example usage and testing
if __name__ == "__main__":
    print("DOCX Styles Configuration Module - UNIFIED SPACING SYSTEM")
    print("="*60)

    # Test configuration
    config = get_default_config()
    print(f"Default spacing values:")
    print(f"   H1: before={config.spacing['h1_before']}pt, after={config.spacing['h1_after']}pt")
    print(f"   H2: before={config.spacing['h2_before']}pt, after={config.spacing['h2_after']}pt")
    print(f"   H3: before={config.spacing['h3_before']}pt, after={config.spacing['h3_after']}pt")
    print(f"   H4: before={config.spacing['h4_before']}pt, after={config.spacing['h4_after']}pt")
    print(f"   H5: before={config.spacing['h5_before']}pt, after={config.spacing['h5_after']}pt")
    print(f"   H6: before={config.spacing['h6_before']}pt, after={config.spacing['h6_after']}pt")
    print(f"   Paragraph: before={config.spacing['paragraph_before']}pt, after={config.spacing['paragraph_after']}pt")
    print(f"   Quote: before={config.spacing['quote_before']}pt, after={config.spacing['quote_after']}pt")
    print(f"   Code block: before={config.spacing['code_block_before']}pt, after={config.spacing['code_block_after']}pt")

    print(f"\nQuick modifications examples:")
    print("modify_styles(doc, h3_before=1, h4_before=1, h5_before=1, h6_before=1)")
    print("quick_spacing_change(doc, paragraph_after=3, h4_before=2)")
    print("quick_font_size_change(doc, h4_size=13, quote_size=11)")

    print("\nUnified spacing system ready!")
    print("All elements now have before/after spacing controlled from StylesConfig")
