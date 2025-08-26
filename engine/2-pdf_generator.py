#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_generator.py
Generates PDF color cards from processed JSON data with embedded ICC profile
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PrimaryStyles:

    def __init__(self, 
                customTTF1=pdfmetrics.registerFont(TTFont("Title", "./1.ttf")),
                customTTF2=pdfmetrics.registerFont(TTFont("P1", "./2.ttf")),
                customTTF3=pdfmetrics.registerFont(TTFont("Table1", "./3.ttf"))
                ):
        self.customTTF1 = customTTF1
        self.customTTF2 = customTTF2
        self.customTTF3 = customTTF3



class ColoursVisor(Flowable):

    """Custom flowable for displaying colour swatches including custom fonts"""

    def __init__(self, srgb_colour, prophoto_colour, size=5*cm):

        Flowable.__init__(self)
        self.srgb_colour = srgb_colour
        self.prophoto_colour = prophoto_colour
        self.size = size
        self.width = size * 2 + 0.5*cm  # Two squares plus gap
        self.height = size


    def draw(self):
        """Draw the dual colour swatch"""
        # Draw sRGB swatch (left square)
        self.canv.setFillColor(self.srgb_colour)
        self.canv.rect(0, 0, self.size, self.size, fill=1, stroke=0)

        # Draw ProPhoto swatch (right square)
        self.canv.setFillColor(self.prophoto_colour)
        self.canv.rect(self.size + 0.5*cm, 0, self.size, self.size, fill=1, stroke=0)

        # Draw borders
        self.canv.setStrokeColor(Color(0, 0, 0))  # Black as RGB
        self.canv.setLineWidth(0.5)
        self.canv.rect(0, 0, self.size, self.size, fill=0, stroke=1)
        self.canv.rect(self.size + 0.5*cm, 0, self.size, self.size, fill=0, stroke=1)

        # Add labels
        self.canv.setFont('Helvetica-Bold', 12)

        # sRGB label (with shadow for visibility)
        self.canv.setFillColor(Color(0, 0, 0))  # Black
        self.canv.drawString(self.size/2 - 15, self.size - 20 - 1, "sRGB")
        self.canv.setFillColor(Color(1, 1, 1))  # White
        self.canv.drawString(self.size/2 - 15 - 1, self.size - 20, "sRGB")

        # ProPhoto label
        self.canv.setFillColor(Color(0, 0, 0))  # Black
        self.canv.drawString(self.size + 0.5*cm + self.size/2 - 20, self.size - 20 - 1, "ProPhoto")
        self.canv.setFillColor(Color(1, 1, 1))  # White
        self.canv.drawString(self.size + 0.5*cm + self.size/2 - 20 - 1, self.size - 20, "ProPhoto")


class PDFColourChartsGenerator:
    """Generator for PDF colour cards from JSON data"""

    def __init__(self, icc_profile_path="PSOcoated_v3.icc"):
        self.icc_profile_path = icc_profile_path
        self.styles = getSampleStyleSheet()
        self.current_page = 1
        self.page_offset = 0  # Configurable offset for page numbering when usin shellcmd
        self._setup_custom_styles()
        self.primary_styles = PrimaryStyles()

    def _setup_custom_styles(self):
        """Setup custom PDF styles matching original design"""

        primary_colour = Color(0.2, 0.2, 0.4)
        secondary_colour = Color(0.4, 0.2, 0.2)
        accent_colour = Color(0.3, 0.3, 0.3)


        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName='Title',
            fontSize=24,
            spaceAfter=25,
            spaceBefore=30,
            alignment=1,  # Centered
            textColour=primary_colour,
            leading=28
        )

        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName='P1',
            fontSize=22,
            spaceAfter=18,
            spaceBefore=20,
            alignment=1,
            textColour=secondary_colour,
            leading=22
        )

        # Section title style
        self.section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontName='P1',
            fontSize=16,
            spaceAfter=12,
            spaceBefore=15,
            alignment=0,
            textColour=primary_colour
        )

        # Colour info style
        self.colour_info_style = ParagraphStyle(
            'ColorInfo',
            parent=self.styles['Normal'],
            fontName='P1',
            fontSize=11,
            textColour=accent_colour,
            leading=15
        )

        # Crear un estilo específico para valores con negrita
        self.value_style = ParagraphStyle(
            'ValueStyle',
            parent=self.colour_info_style,
            fontName='Helvetica',  # Base font
            fontSize=11,
            textColour=Color(0.2, 0.2, 0.3),
            leading=15
        )
        

        # Notes style
        self.notes_style = ParagraphStyle(
            'Notes',
            parent=self.styles['Normal'],
            fontName='P1',
            fontSize=11,
            spaceAfter=10,
            spaceBefore=8,
            alignment=4,  # Justified
            textColour=accent_colour,
            leading=15,
            backColour=Color(0.95, 0.95, 0.95),
            borderPadding=5
        )

    def rgb_to_colour(self, r, g, b):
        """Convert RGB values to ReportLab Color"""
        try:
            r = max(0, min(255, int(float(r))))
            g = max(0, min(255, int(float(g))))
            b = max(0, min(255, int(float(b))))
            return Color(r/255.0, g/255.0, b/255.0)
        except:
            return Color(0.8, 0.8, 0.8)  # Light gray as RGB

    def hex_to_colour(self, hex_value):
        """Convert hex value to ReportLab Color object"""
        try:
            if not hex_value or hex_value == "N/A":
                return Color(0.8, 0.8, 0.8)  # Light gray default

            hex_str = str(hex_value).replace('#', '').strip().upper()

            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16) / 255.0
                g = int(hex_str[2:4], 16) / 255.0
                b = int(hex_str[4:6], 16) / 255.0
                return Color(r, g, b)
            elif len(hex_str) == 3:
                r = int(hex_str[0]*2, 16) / 255.0
                g = int(hex_str[1]*2, 16) / 255.0
                b = int(hex_str[2]*2, 16) / 255.0
                return Color(r, g, b)
            else:
                return Color(0.8, 0.8, 0.8)
        except:
            return Color(0.8, 0.8, 0.8)

    def calculate_page_numbers(self, charts):
        """Calculate exact page numbers for each color based on PDF structure"""
        page_mapping = {}
        current_page = 1 + self.page_offset

        # Account for initial pages
        # 1 page: Title page
        # 1 page: Summary
        current_page += 1

        # Calculate pages for visual index
        colours_per_index_page = 48  # 8x6 grid

        for chart_name, colors in charts.items():
            colour_count = len(colors)

            # Pages needed for visual index of this chart
            index_pages_needed = math.ceil(colour_count / colours_per_index_page)
            current_page += index_pages_needed

        # Now calculate individual colour pages
        for chart_name, colors in charts.items():
            # Chart title page
            current_page += 1

            # Individual colour pages
            for colour_id, colour_data in colors:
                page_mapping[colour_id] = current_page
                current_page += 1

        return page_mapping

    def create_visual_index_page(self, chart_name, colors, page_mapping):
        """Create visual index page with 8x6 color grid"""
        story = []

        colours_per_row = 8
        rows_per_page = 6
        colours_per_page = colours_per_row * rows_per_page
        total_colours = len(colors)

        for page_start in range(0, total_colours, colours_per_page):
            # Add PageBreak before new page (except first)
            if page_start > 0:
                story.append(PageBreak())
                story.append(Paragraph(f"{chart_name} (continued)", self.title_style))
                story.append(Spacer(1, 0.3*inch))
            else:
                # First page of this chart
                story.append(Paragraph(f" {chart_name}", self.title_style))
                colour_count = len(colors)
                story.append(Paragraph(f"{colour_count} colors", self.subtitle_style))
                story.append(Spacer(1, 0.3*inch))

            page_end = min(page_start + colours_per_page, total_colours)
            page_colors = colors[page_start:page_end]

            # Create color grid
            table_data = []
            current_row = []

            for colour_id, colour_data in page_colors:
                original_data = colour_data.get('original_data', {})
                code = original_data.get('code', 'Unknown')

                # Get color for swatch
                srgb_colour = self.rgb_to_colour(
                    original_data.get('R', 0),
                    original_data.get('G', 0),
                    original_data.get('B', 0)
                )

                # Get page number for this color
                colour_page = page_mapping.get(colour_id, 0)

                # Create compact color cell
                colour_cell = Table([
                    [''],  # Color swatch space
                    [code],
                    [f"(Page {colour_page})"]
                ], colWidths=[2.2*cm], rowHeights=[1.8*cm, 0.4*cm, 0.3*cm])

                colour_cell.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), srgb_colour),
                    ('GRID', (0, 0), (0, 0), 1, Color(0, 0, 0)),  # Black border
                    ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 1), (0, 1), 8),
                    ('FONTSIZE', (0, 2), (0, 2), 7),
                    ('ALIGN', (0, 1), (0, 2), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 1), (0, 1), 2),
                    ('BOTTOMPADDING', (0, 1), (0, 1), 1),
                ]))

                current_row.append(colour_cell)

                # Complete row or end of colors
                if len(current_row) == colours_per_row or colour_id == colors[-1][0]:
                    # Pad row if necessary
                    while len(current_row) < colours_per_row:
                        current_row.append("")

                    table_data.append(current_row)
                    current_row = []



            # Create main table
            if table_data:
                col_widths = [2.2*cm] * colours_per_row
                main_table = Table(table_data, colWidths=col_widths)
                main_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))

                # Center the table
                centered_table = Table([[main_table]], colWidths=[A4[0] - 4*cm])
                centered_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ]))

                story.append(centered_table)
                story.append(Spacer(1, 0.3*inch))

        return story

    def create_complete_index_pages(self, json_data):
        """Create title page, summary, and visual indices for all charts"""
        story = []

        # Group colors by chart
        charts = {}
        for colour_id, colour_data in json_data.items():
            if colour_id == 'metadata':
                continue

            chart_name = colour_data.get('original_data', {}).get('chart', 'Unknown')
            if chart_name not in charts:
                charts[chart_name] = []
            charts[chart_name].append((colour_id, colour_data))

        # Calculate all page numbers first
        page_mapping = self.calculate_page_numbers(charts)

###################################### FIRST TITLE PAGE

        story.append(Paragraph("COLOUR CHARTS DATABASE", self.title_style))
        # story.append(Paragraph("Complete Colorimetric Database", self.subtitle_style))
        story.append(Spacer(1, 0.5*inch))

        # Summary paGE
        total_colours = len([k for k in json_data.keys() if k != 'metadata'])
        metadata = json_data.get('metadata', {})


        def timedata_guay(iso):
            try:

                from datetime import datetime

                dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
                return dt.strftime("%B %d, %Y")

            except Exception as e:
                print('[ERROR] Time datastamps error, check time func: {e}')
                return "Unknown"
            

        processed_date = timedata_guay(metadata.get('processing_end_time', ''))
        
        summary_text = f"""
        <b>• SUMMARY •</b><br/><br/>
        • Total Colours Processed: <b>{total_colours}</b><br/>
        • Total Charts Processed: <b>{len(charts)}</b><br/><br/>
        • ICC Profile Used: {metadata.get('icc_profile', 'Unknown')}<br/>
        • Pantone Database: {metadata.get('pantone_database', 'Unknown')}<br/>
        • Source File: {metadata.get('source_file', 'Unknown')}<br/><br/>   
        • Processing Date: {processed_date}<br/>
        """
        ###################################### OLD DATA STORE

        # summary_text = f"""
        # <b>Collection Summary:</b><br/><br/>
        # • Total Colours: {total_colours}<br/><br/>
        # • Colour Charts: {len(charts)}<br/>
        # • Source: {metadata.get('source_file', 'Unknown')}<br/>
        # • Processing Date: {metadata.get('processing_end_time', 'Unknown')}<br/>
        # • ICC Profile: {metadata.get('icc_profile', 'Unknown')}<br/>
        # • Pantone Database: {metadata.get('pantone_database', 'Unknown')}
        # """



        story.append(Paragraph(summary_text, self.colour_info_style))
        story.append(PageBreak())



######################################  CHARTS INDEX PAGES
        for chart_name, colors in charts.items():
            visual_index = self.create_visual_index_page(chart_name, colors, page_mapping)
            story.extend(visual_index)
            story.append(PageBreak())

        return story

    def create_colour_info_table(self, colour_data):
        """Create table with complete colorimetric information"""
        original_data = colour_data.get('original_data', {})
        computed_data = colour_data.get('computed_data', {})

        # Extract values with safe defaults
        def safe_float(value, default=0.0, decimals=1):
            try:
                return f"{float(value):.{decimals}f}"
            except:
                return f"{default:.{decimals}f}"

        def safe_int(value, default=0):
            try:
                return str(int(float(value)))
            except:
                return str(default)

        def safe_string(value, default="N/A"):
            return str(value) if value and str(value) != "None" else default

###################################### COLOURIMETRIC INFO YTABLES
        # LAB values
        l_val = safe_float(original_data.get('L'), decimals=1)
        a_val = safe_float(original_data.get('a'), decimals=1)
        b_val = safe_float(original_data.get('b'), decimals=1)

        # RGB values
        r_val = safe_int(original_data.get('R'))
        g_val = safe_int(original_data.get('G'))
        b_val = safe_int(original_data.get('B'))

        # CMYK values
        c_val = safe_float(computed_data.get('C'), decimals=2)
        m_val = safe_float(computed_data.get('M'), decimals=2)
        y_val = safe_float(computed_data.get('Y'), decimals=2)
        k_val = safe_float(computed_data.get('K'), decimals=2)

        # Hex values
        hex_srgb = safe_string(original_data.get('hex_srgb'))
        hex_prophoto = safe_string(original_data.get('hex_prophoto'))

        # HSL values
        h_val = safe_float(original_data.get('H'), decimals=1)
        s_val = safe_float(original_data.get('S'), decimals=1)
        l_hsl_val = safe_float(original_data.get('L_hsl'), decimals=1)

        # Pantone information
        pantone_name = safe_string(computed_data.get('pantone_name'))
        pantone_code = safe_string(computed_data.get('pantone_code'))
        pantone_delta = safe_float(computed_data.get('pantone_delta_e00'), decimals=3)

        # CMYK Delta E
        cmyk_delta = safe_float(computed_data.get('cmyk_delta_e00'), decimals=3)



        # Crear datos con Paragraphs
        table_data = []
        for row_data in [
            ['LAB', f"L: <b>{l_val}</b> • a: <b>{a_val}</b> • b: <b>{b_val}</b>"],
            ['RGB', f"R: <b>{r_val}</b> • G: <b>{g_val}</b> • B: <b>{b_val}</b>"],
            ['CMYK', f"C: <b>{c_val}%</b> • M: <b>{m_val}%</b> • Y: <b>{y_val}%</b> • K: <b>{k_val}%</b>"],
            ['CMYK ΔE00', f"{cmyk_delta}"],
            ['Hex sRGB', f"<b>{hex_srgb}</b>"],
            ['Hex ProPhoto', f"<b>{hex_prophoto}</b>"],
            ['HSL', f"H: <b>{h_val}°</b> • S: <b>{s_val}%</b> • L: <b>{l_hsl_val}%</b>"],
            ['PANTONE', f"{pantone_name} ({pantone_code})"],
            ['Pantone ΔE00', f"{pantone_delta}"]
        ]:
            label = row_data[0]
            content = Paragraph(row_data[1], self.value_style)
            table_data.append([label, content])

        table = Table(table_data, colWidths=[3.5*cm, 10.5*cm])
        table.setStyle(TableStyle([
            # Header cells styling
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('textColour', (0, 0), (-1, -1), Color(0.2, 0.2, 0.3)),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.96, 0.96, 0.96)),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            
            # Value cells styling
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (1, 0), (1, -1), Color(1, 1, 1)),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        return table


    def create_equivalences_note(self, colour_data):
        """Create equivalences note text if available"""
        correspondences = colour_data.get('correspondences', {})
        if not correspondences.get('has_equivalences', False):
            return ""

        equivalences = correspondences.get('equivalences', {})
        if not equivalences:
            return ""

        note_parts = []
        for chart_name, codes in equivalences.items():
            if codes:
                codes_str = ', '.join(codes)
                note_parts.append(f"• Equivalent to {chart_name} : {codes_str}")

        if not note_parts:
            return ""

        return "\n".join(note_parts)

    def create_colour_pages(self, json_data):
        """Create individual pages for each color"""
        story = []

        # Group colors by chart
        charts = {}
        for colour_id, colour_data in json_data.items():
            if colour_id == 'metadata':
                continue

            chart_name = colour_data.get('original_data', {}).get('chart', 'Unknown')
            if chart_name not in charts:
                charts[chart_name] = []
            charts[chart_name].append((colour_id, colour_data))

        # Process each chart
        for chart_name, colors in charts.items():
            # Chart title page
            story.append(Spacer(2, 2*cm))
            story.append(Paragraph(f"{chart_name.upper()}", self.title_style))
            story.append(Paragraph(f"{len(colors)} colours", self.subtitle_style))
            story.append(PageBreak())

            # Individual colour pages
            for colour_id, colour_data in colors:
                original_data = colour_data.get('original_data', {})
                computed_data = colour_data.get('computed_data', {})

                colour_code = original_data.get('code', f'Color {colour_id}')

                # Color title
                story.append(Paragraph(f" {colour_code} • ({chart_name})", self.subtitle_style))
                story.append(Spacer(1, 0.2*inch))

                # Create color swatches (centered)
                srgb_colour = self.rgb_to_colour(
                    original_data.get('R', 0),
                    original_data.get('G', 0),
                    original_data.get('B', 0)
                )

                prophoto_colour = self.hex_to_colour(
                    original_data.get('hex_prophoto', 'N/A')
                )

                colour_swatch = ColoursVisor(srgb_colour, prophoto_colour)

                # Center the swatch using table
                swatch_table = Table([[colour_swatch]], colWidths=[A4[0] - 4*cm])
                swatch_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ]))

                story.append(swatch_table)
                story.append(Spacer(1, 0.3*inch))

                # Colorimetric information
                story.append(Paragraph("COLORIMETRIC INFORMATION", self.section_title_style))
                story.append(Spacer(1, 0.15*inch))

                colour_table = self.create_colour_info_table(colour_data)
                story.append(colour_table)
                story.append(Spacer(1, 0.3*inch))

                # Notes section with equivalences
                story.append(Paragraph("NOTES", self.section_title_style))
                story.append(Spacer(1, 0.15*inch))

                # Get equivalences text
                equivalences_text = self.create_equivalences_note(colour_data)
                if equivalences_text:
                    story.append(Paragraph(equivalences_text, self.notes_style))
                    story.append(Spacer(1, 0.2*inch))
                else:
                    story.append(Spacer(1, 0.1*inch))

                story.append(Spacer(1, 0.3*inch))

                # Page break for next color
                story.append(PageBreak())

        return story


################################### FOOTER

    def add_page_footer(self, canvas, doc):
        """Add page footer with metadata"""
        canvas.saveState()
        canvas.setFont('P1', 10)
        canvas.setFillColor(Color(0.5, 0.5, 0.5))  # Gray color

        # Left: Document title
        canvas.drawString(1*cm, 1*cm, "Anime Cel Pigments Reference")

        # Center: Page number with offset
        page_number = self.current_page + self.page_offset
        page_text = f"{page_number}"
        text_width = canvas.stringWidth(page_text, 'Helvetica', 10)
        canvas.drawString((A4[0] - text_width)/2, 1*cm, page_text)

        # Right: Version info
        version_text = "Version 1.1 • ICC PSO Coated V3"
        version_width = canvas.stringWidth(version_text, 'Helvetica', 10)
        canvas.drawString(A4[0] - version_width - 1*cm, 1*cm, version_text)

        canvas.restoreState()
        self.current_page += 1



######################### PIKEPDF METADATA INTEGRATION
    def load_metadata_file(self, metadata_file):
        """Load metadata from text file"""
        metadata = {}

        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            metadata[key.strip()] = value.strip()

                print(f"INFO: Loaded {len(metadata)} metadata entries from {metadata_file}")
            else:
                print(f"WARNING: Metadata file not found: {metadata_file}")

        except Exception as e:
            print(f"WARNING: Failed to load metadata file: {e}")

        return metadata



######################### PIKEPDF ICC PROFILE INTEGRATION
    def embed_icc_profile_and_metadata(self, pdf_path, metadata_file="./pdf_metadata/metadata.txt"):
        """Embed ICC profile and metadata in the PDF using pikepdf"""
        try:
            # Import pikepdf here to avoid variable errors, there's no other way to 
            
            try:
                import pikepdf
                from pikepdf import Pdf, Dictionary, Array, Stream
            
            except ImportError:
                print("WARNING: pikepdf not installed. Install with: pip install pikepdf")
                return False

            if not os.path.exists(self.icc_profile_path):
                print(f"WARNING: ICC profile not found: {self.icc_profile_path}")
                return False

            print(f"INFO: Embedding ICC profile and metadata...")



            # Open PDF for editing
            pdf = Pdf.open(pdf_path, allow_overwriting_input=True)

            # 1. Embed ICC profile
            with open(self.icc_profile_path, 'rb') as f:
                icc_data = f.read()

            print(f"INFO: ICC profile loaded: {len(icc_data)} bytes")

            # Create ICC stream
            icc_stream = Stream(pdf, icc_data)
            icc_stream.N = 4  # CMYK = 4 components
            icc_stream.Filter = ["/FlateDecode"]
            icc_stream.Alternate = "/DeviceCMYK"



            # Add ICC profile to PDF structure
            if not hasattr(pdf.Root, 'OutputIntents'):
                pdf.Root.OutputIntents = Array()


            output_intent = Dictionary({
                "/Type": "/OutputIntent",
                "/S": "/GTS_PDFA1",
                "/OutputConditionIdentifier": f"({Path(self.icc_profile_path).stem})",
                "/DestOutputProfile": icc_stream
            })

            pdf.Root.OutputIntents.append(output_intent)

            # 2. Load and embed metadata
            metadata_dict = self.load_metadata_file(metadata_file)

            # SSi no hay metadata.txt, para evitar fallos, usar default vaules
            pdf.docinfo["/Title"] = metadata_dict.get("title", "Title")
            pdf.docinfo["/Author"] = metadata_dict.get("author", "Author")
            pdf.docinfo["/Subject"] = metadata_dict.get("subject", "Subject")
            pdf.docinfo["/Keywords"] = metadata_dict.get("keywords", "keywords")
            pdf.docinfo["/Creator"] = metadata_dict.get("creator", "creator")
            pdf.docinfo["/Producer"] = metadata_dict.get("producer", "Producer")

            # Custom metadata fields

            for key, value in metadata_dict.items():

                try:

                    if key.startswith("custom_"):
                
                        pdf_key = f"/{key.replace('custom_', '').title()}"
                        pdf.docinfo[pdf_key] = str(value)
                
                except Exception as e:

                    print(f"ERROR: metadata.txt file errors: {e}")

            # Save modified PDF
            pdf.save(pdf_path)
            pdf.close()

            print(f"INFO: ICC profile and metadata embedded successfully")
            return True

        
        except Exception as e:
            print(f"ERROR: Failed to embed ICC profile and metadata: {e}")
            return False


######################################## El verdadero momento donde generamos el PDF con los sets dados en shell

    def generate_pdf(self, json_data, output_path="colour_cards.pdf", prepend_pdf=None, page_offset=0):
        """Generate complete PDF from JSON data and optionally prepend another PDF"""
        
        try:
            output_dir = Path("./output/")
            output_dir.mkdir(exist_ok=True)
            
            if not str(output_path).startswith("./output/"):
                output_path = output_dir / Path(output_path).name
            
            output_path_str = str(output_path)

            print(f"INFO: Starting PDF generation: {output_path_str}")
            
            # Set page offset
            self.page_offset = page_offset
            print(f"INFO: Page numbering offset: {page_offset}")

            story = []

            # Create complete index pages (title, summary, visual indices)
            print("INFO: Creating index pages and visual colour charts...")
            index_pages = self.create_complete_index_pages(json_data)
            story.extend(index_pages)

            # Create individual colour pages
            print("INFO: Creating individual colour pages...")
            colour_pages = self.create_colour_pages(json_data)
            story.extend(colour_pages)

            if prepend_pdf and Path(prepend_pdf).exists():
                print(f"INFO: Prepending PDF: {prepend_pdf}")
                
                # Generate temporary PDF first
                temp_path = str(Path(output_path_str).with_suffix('.temp.pdf'))
                doc = SimpleDocTemplate(
                    temp_path,
                    pagesize=A4,
                    topMargin=1*cm,
                    bottomMargin=2*cm,
                    leftMargin=2*cm,
                    rightMargin=2*cm
                )
                
                print("INFO: Building temporary PDF document...")
                doc.build(story, onFirstPage=self.add_page_footer, onLaterPages=self.add_page_footer)
                
                # Merge PDFs: existing + generated
                print("INFO: Merging PDFs...")
                import pikepdf
                existing = pikepdf.Pdf.open(prepend_pdf)
                generated = pikepdf.Pdf.open(temp_path)
                
                # Copy pages: first existing, then generated
                for page in generated.pages:
                    existing.pages.append(page)
                    
                existing.save(output_path_str)
                existing.close()
                generated.close()
                Path(temp_path).unlink()  # Clean up temporary file
                
            else:
                # Normal process without merging
                print("INFO: Building PDF document...")
                doc = SimpleDocTemplate(
                    output_path_str,
                    pagesize=A4,
                    topMargin=1*cm,
                    bottomMargin=2*cm,
                    leftMargin=2*cm,
                    rightMargin=2*cm
                )
                doc.build(story, onFirstPage=self.add_page_footer, onLaterPages=self.add_page_footer)

            # Embed ICC profile and metadata
            self.embed_icc_profile_and_metadata(output_path_str)

            print(f"INFO: PDF generated successfully: {output_path_str}")
            print(f"INFO: Total pages: {self.current_page + self.page_offset - 1}")

            return output_path_str

        except Exception as e:
            print(f"ERROR: PDF generation failed: {e}")
            raise


def main():
    """Main function with command line argument support"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF Colour Charts Generator\n\n'
                    'Generates professional PDF colour cards from processed JSON data.\n'
                    'Features:\n'
                    '  • Visual index pages with colour swatches\n'
                    '  • Individual colour pages with complete colorimetric data\n'
                    '  • ICC profile embedding for print accuracy\n'
                    '  • Pantone matching and CMYK conversion data\n'
                    '  • Optional PDF merging for custom covers/introductions\n\n'
                    'Example: python pdf_generator.py colours.json -j intro.pdf --offset 10',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='For more information about the colour processing pipeline, see main.py --help'
    )

    # Required argument
    parser.add_argument(
        'json_file',
        help='Input JSON file with processed colour data (from processing pipeline)'
    )

    # Optional arguments
    parser.add_argument(
        'output_pdf',
        nargs='?',
        default='colour_cards.pdf',
        help='Output PDF filename (default: colour_cards.pdf)'
    )

    parser.add_argument(
        '-j', '--join',
        dest='prepend_pdf',
        help='PDF file to prepend before colour cards (e.g., cover, introduction)'
    )

    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Page numbering offset for merged documents (default: 0)'
    )

    parser.add_argument(
        '-i', '--icc-profile',
        default='PSOcoated_v3.icc',
        help='ICC profile for CMYK embedding (default: PSOcoated_v3.icc)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Validate input file
        if not Path(args.json_file).exists():
            print(f"ERROR: JSON file not found: {args.json_file}")
            return 1

        # Load JSON data
        print(f"Loading JSON data: {args.json_file}")
        with open(args.json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Validate prepend PDF if specified
        if args.prepend_pdf and not Path(args.prepend_pdf).exists():
            print(f"WARNING: Prepend PDF not found: {args.prepend_pdf}")
            print("Continuing without PDF merging...")
            args.prepend_pdf = None

        # Generate PDF
        generator = PDFColourChartsGenerator(args.icc_profile)
        
        if args.verbose:
            print(f"Configuration:")
            print(f"  JSON input: {args.json_file}")
            print(f"  PDF output: {args.output_pdf}")
            print(f"  Prepend PDF: {args.prepend_pdf or 'None'}")
            print(f"  Page offset: {args.offset}")
            print(f"  ICC profile: {args.icc_profile}")
            print()

        output_path = generator.generate_pdf(
            json_data=json_data,
            output_path=args.output_pdf,
            prepend_pdf=args.prepend_pdf,
            page_offset=args.offset
        )

        print(f"SUCCESS: PDF generated at {output_path}")
        
        # Summary
        total_colors = len([k for k in json_data.keys() if k != 'metadata'])
        print(f"Summary: {total_colors} colours processed")
        
        if args.prepend_pdf:
            print(f"Merged with: {args.prepend_pdf}")

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130

    except Exception as e:
        print(f"ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())