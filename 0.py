import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageCms
import csv
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
import math


class AnimeColourCardsPDF:

    def __init__(self, excel_file_path, output_pdf_path="anime_colour_cards.pdf", pantone_csv_path="pantone_lab.csv"):
        self.excel_file_path = excel_file_path
        self.output_pdf_path = output_pdf_path
        self.pantone_csv_path = pantone_csv_path
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.current_page = 1
        self.sheet_name = ""
        self.page_offset = 0  # Para llevar cuenta de páginas de título
        self.sheet_page_starts = {}  # Para almacenar dónde empieza cada carta
        self.pantone_list = self.load_pantone_data()

    def load_pantone_data(self):
        """Load Pantone color data from CSV file"""
        pantone_list = []
        try:
            if os.path.exists(self.pantone_csv_path):
                print(f"📖 Loading Pantone data from: {self.pantone_csv_path}")
                with open(self.pantone_csv_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            pantone_list.append({
                                'name': row['PANTONENAME'],
                                'code': row['UNIQUECODE'],
                                'lab': LabColor(float(row['L']), float(row['a']), float(row['b']))
                            })
                        except (ValueError, KeyError) as e:
                            print(f"  ⚠️ Skipping invalid Pantone row: {e}")
                print(f"  ✅ Loaded {len(pantone_list)} Pantone colors")
            else:
                print(f"  ⚠️ Pantone CSV file not found: {self.pantone_csv_path}")
                print("  ℹ️ Pantone matching will be disabled")
        except Exception as e:
            print(f"  ❌ Error loading Pantone data: {e}")
        return pantone_list



############### BE CAREFUL

    def find_closest_pantone(self, L, a, b):
        """Find the closest Pantone color using CIE2000 delta E"""
        if not self.pantone_list or pd.isna(L) or pd.isna(a) or pd.isna(b):
            return "N/A", "N/A", "N/A"

        try:
            # Create LabColor object from input values
            input_lab = LabColor(float(L), float(a), float(b))

            best_match = None
            min_delta = float('inf')

            for pantone in self.pantone_list:
                # Usar nuestra propia implementación de delta E CIE2000
                de = self.delta_e_cie2000_custom(input_lab, pantone['lab'])
                if de < min_delta:
                    min_delta = de
                    best_match = pantone

            if best_match:
                return best_match['name'], best_match['code'], f"{min_delta:.2f}"
            else:
                return "N/A", "N/A", "N/A"

        except Exception as e:
            print(f"Error finding Pantone match: {e}")
            return "N/A", "N/A", "N/A"


## !
    def delta_e_cie2000_custom(self, lab1, lab2):
        """
        Delta E CIE2000 pura en Python moderno.
        lab1, lab2: LabColor
        """
        try:
            L1, a1, b1 = lab1.lab_l, lab1.lab_a, lab1.lab_b
            L2, a2, b2 = lab2.lab_l, lab2.lab_a, lab2.lab_b

            kL = kC = kH = 1.0

            # Step 1: C1, C2
            C1 = math.hypot(a1, b1)
            C2 = math.hypot(a2, b2)
            C_avg = (C1 + C2) / 2.0

            # Step 2: G
            G = 0.5 * (1 - math.sqrt((C_avg**7) / (C_avg**7 + 25**7)))

            # Step 3: a'
            a1_prime = a1 * (1 + G)
            a2_prime = a2 * (1 + G)

            # Step 4: C'
            C1_prime = math.hypot(a1_prime, b1)
            C2_prime = math.hypot(a2_prime, b2)

            # Step 5: h'
            h1_prime = math.degrees(math.atan2(b1, a1_prime)) % 360 if C1_prime != 0 else 0
            h2_prime = math.degrees(math.atan2(b2, a2_prime)) % 360 if C2_prime != 0 else 0

            # Step 6: ΔL', ΔC', ΔH'
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

            # Step 7: L', C', h' promedio
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

            # Step 8: T
            h_rad = math.radians(h_avg_prime)
            T = (1
                - 0.17 * math.cos(h_rad - math.radians(30))
                + 0.24 * math.cos(2 * h_rad)
                + 0.32 * math.cos(3 * h_rad + math.radians(6))
                - 0.20 * math.cos(4 * h_rad - math.radians(63)))

            # Step 9: S_L, S_C, S_H
            S_L = 1 + ((0.015 * (L_avg_prime - 50) ** 2) / math.sqrt(20 + (L_avg_prime - 50) ** 2))
            S_C = 1 + 0.045 * C_avg_prime
            S_H = 1 + 0.015 * C_avg_prime * T

            # Step 10: R_T
            R_T = -2 * math.sqrt(C_avg_prime ** 7 / (C_avg_prime ** 7 + 25 ** 7)) * \
                math.sin(math.radians(30) * math.exp(-((h_avg_prime - 275)/25)**2))

            # Step 11: ΔE00
            term1 = (delta_L_prime / (kL * S_L))**2
            term2 = (delta_C_prime / (kC * S_C))**2
            term3 = (delta_H_prime / (kH * S_H))**2
            term4 = R_T * (delta_C_prime / (kC * S_C)) * (delta_H_prime / (kH * S_H))

            delta_e = math.sqrt(term1 + term2 + term3 + term4)
            return delta_e

        except Exception as e:
            print(f"Error in custom delta E calculation: {e}")
            # Fallback Euclidiano
            return math.sqrt((L1 - L2)**2 + (a1 - a2)**2 + (b1 - b2)**2)


############### BE CAREFUL



    def setup_custom_styles(self):
        """Configure custom styles for the PDF with a more professional look"""
        # Base font configuration - using more professional fonts
        primary_font = 'Helvetica'
        secondary_font = 'Helvetica-Bold'

        # Color scheme - more professional palette
        primary_color = Color(0.2, 0.2, 0.4)  # Dark blue-navy
        secondary_color = Color(0.4, 0.2, 0.2)  # Burgundy
        accent_color = Color(0.3, 0.3, 0.3)    # Dark gray
        light_accent = Color(0.9, 0.9, 0.92)   # Very light blue-gray

        # Main title style - more elegant
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=secondary_font,
            fontSize=24,
            spaceAfter=25,
            spaceBefore=30,
            alignment=1,  # Centered
            textColor=primary_color,
            leading=28
        )

        # Subtitle style - refined
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName=secondary_font,
            fontSize=18,
            spaceAfter=18,
            spaceBefore=20,
            alignment=1,
            textColor=secondary_color,
            leading=22
        )

        # Section title style - cleaner
        self.section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontName=secondary_font,
            fontSize=16,
            spaceAfter=12,
            spaceBefore=15,
            alignment=0,  # Left aligned
            textColor=primary_color,
            borderPadding=(0, 0, 0, 5),
            borderColor=secondary_color,
            borderWidth=(0, 0, 2, 0)  # Bottom border only
        )

        # Index style - more readable
        self.index_style = ParagraphStyle(
            'IndexStyle',
            parent=self.styles['Normal'],
            fontName=primary_font,
            fontSize=12,
            leftIndent=20,
            spaceAfter=8,
            spaceBefore=5,
            textColor=accent_color,
            leading=16
        )

        # Notes style - improved readability
        self.notes_style = ParagraphStyle(
            'NotesStyle',
            parent=self.styles['Normal'],
            fontName=primary_font,
            fontSize=11,
            spaceAfter=10,
            spaceBefore=8,
            alignment=4,  # Justified
            textColor=accent_color,
            leading=15,
            backColor=light_accent,
            borderColor=colors.lightgrey,
            borderWidth=1,
            borderPadding=5
        )

        # Footer style - more subtle
        self.footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontName=primary_font,
            fontSize=10,
            alignment=1,
            textColor=colors.darkgray,
            spaceBefore=15
        )

        # New: Table header style
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName=secondary_font,
            fontSize=12,
            textColor=colors.white,
            alignment=1,
            backColor=primary_color
        )

        # New: Table cell style
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName=primary_font,
            fontSize=11,
            textColor=accent_color,
            alignment=0,
            leading=13
        )

        # New: Color code style
        self.color_code_style = ParagraphStyle(
            'ColorCode',
            parent=self.styles['Normal'],
            fontName='Helvetica-BoldOblique',
            fontSize=10,
            textColor=accent_color,
            alignment=1
        )

    def lab_to_cmyk(self, L, a, b):
        """Convert LAB values to CMYK using specific ICC profiles"""
        try:
            # Normalizar valores LAB para Pillow
            # Pillow LAB: L=0-100, a=-128..127, b=-128..127
            L_val = float(L)
            a_val = float(a)
            b_val = float(b)

            # Ajustar a y b para el rango de Pillow (0-255)
            a_adj = max(-128, min(127, a_val))
            b_adj = max(-128, min(127, b_val))

            # Crear imagen 1x1 en modo LAB
            lab_image = Image.new("LAB", (1, 1))
            lab_image.putpixel((0, 0), (
                int(L_val * 2.55),  # L* 0-100 -> 0-255
                int(a_adj + 128),   # a* -128..127 -> 0-255
                int(b_adj + 128)    # b* -128..127 -> 0-255
            ))

            # Ruta a perfiles ICC reales
            icc_cmyk = "PSOcoated_v3.icc"  # Perfil ICC CMYK real (archivo .icc)

            # Crear transformador LAB -> CMYK
            transform = ImageCms.buildTransformFromOpenProfiles(
                ImageCms.createProfile("LAB"),
                ImageCms.getOpenProfile(icc_cmyk),
                "LAB",
                "CMYK"
            )

            # Convertir
            cmyk_image = ImageCms.applyTransform(lab_image, transform)

            # Extraer valores CMYK (0-255)
            c, m, y, k = cmyk_image.getpixel((0, 0))

            # Convertir a valores 0-100%
            c_percent = c / 2.55
            m_percent = m / 2.55
            y_percent = y / 2.55
            k_percent = k / 2.55

            return c_percent, m_percent, y_percent, k_percent

        except Exception as e:
            print(f"Error converting LAB to CMYK: {e}")
            return 0, 0, 0, 0  # Negro por defecto en caso de error

    def cmyk_to_rgb(self, c, m, y, k):
        """Convert CMYK percentages to RGB for display"""
        try:
            # Convert CMYK percentages (0-100) to 0-1 range
            c_norm = max(0, min(100, float(c))) / 100.0
            m_norm = max(0, min(100, float(m))) / 100.0
            y_norm = max(0, min(100, float(y))) / 100.0
            k_norm = max(0, min(100, float(k))) / 100.0

            # Convert CMYK to RGB
            r = 255 * (1 - c_norm) * (1 - k_norm)
            g = 255 * (1 - m_norm) * (1 - k_norm)
            b = 255 * (1 - y_norm) * (1 - k_norm)

            # Clamp values
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))

            return Color(r/255.0, g/255.0, b/255.0)

        except Exception as e:
            print(f"Error converting CMYK to RGB: {e}")
            return colors.black

    def is_colour_card_sheet(self, df, sheet_name):
        """Determine if a sheet is a valid colour card"""
        try:
            if df.empty:
                return False

            df.columns = df.columns.str.strip()

            # Required columns for colour cards
            required_columns = ['Code', 'L', 'a', 'b', 'R', 'G', 'B']

            columns_present = df.columns.tolist()
            required_present = sum(1 for col in required_columns if col in columns_present)

            if required_present < 5:
                print(f"  ❌ '{sheet_name}': Only {required_present}/7 required columns found")
                return False

            # Verify numeric data
            numeric_cols = ['L', 'a', 'b', 'R', 'G', 'B']
            numeric_data_found = False

            for col in numeric_cols:
                if col in df.columns:
                    numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_values) > 0:
                        numeric_data_found = True
                        break

            if not numeric_data_found:
                print(f"  ❌ '{sheet_name}': No valid numeric data found")
                return False

            print(f"  ✅ '{sheet_name}': Identified as valid colour card")
            return True

        except Exception as e:
            print(f"  ❌ '{sheet_name}': Error validating - {e}")
            return False

    def read_excel_data(self):
        """Read all sheets from Excel file and separate colour cards from other content"""
        try:
            excel_data = pd.read_excel(self.excel_file_path, sheet_name=None)
            total_sheets = len(excel_data)
            print(f"Found {total_sheets} sheets in Excel file")
            print("\nAnalysing sheets...")

            colour_card_data = {}
            other_sheets_data = {}

            for sheet_name, df in excel_data.items():
                print(f"\nAnalysing: '{sheet_name}'")

                if self.is_colour_card_sheet(df, sheet_name):
                    df.columns = df.columns.str.strip()
                    colour_card_data[sheet_name] = df
                else:
                    other_sheets_data[sheet_name] = df

            print(f"\n📊 SUMMARY:")
            print(f"  - Colour cards found: {len(colour_card_data)}")
            print(f"  - Other sheets (notes/conversions): {len(other_sheets_data)}")

            return colour_card_data, other_sheets_data

        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None, None

    def calculate_hex_srgb(self, r, g, b):
        """Calculate Hex sRGB from R, G, B values like Excel formula does"""
        try:
            if pd.isna(r) or pd.isna(g) or pd.isna(b):
                return 'N/A'

            # Convert to integers
            r_int = int(float(r))
            g_int = int(float(g))
            b_int = int(float(b))

            # Clamp values between 0-255
            r_int = max(0, min(255, r_int))
            g_int = max(0, min(255, g_int))
            b_int = max(0, min(255, b_int))

            # Convert to hex (like Excel's DEC2HEX function)
            hex_r = format(r_int, '02x').upper()
            hex_g = format(g_int, '02x').upper()
            hex_b = format(b_int, '02x').upper()

            return f"#{hex_r}{hex_g}{hex_b}"

        except:
            return 'N/A'

    def get_colour_from_row(self, row):
        """Get colour from row data, trying multiple methods"""
        try:
            # Method 1: Try Hex sRGB (calculated)
            r = row.get('R', None)
            g = row.get('G', None)
            b = row.get('B', None)
            if all(x is not None and not pd.isna(x) for x in [r, g, b]):
                return self.rgb_to_colour(r, g, b)

            # Method 2: Try Hex ProPhoto
            hex_pro = row.get('Hex (ProPhoto RGB)', None)
            if hex_pro and not pd.isna(hex_pro):
                colour = self.hex_to_colour(hex_pro)
                if colour != colors.white:
                    return colour

            return colors.lightgrey
        except:
            return colors.lightgrey

    def hex_to_colour(self, hex_value):
        """Convert hex value to ReportLab Colour object"""
        try:
            if pd.isna(hex_value) or not hex_value:
                return colors.white

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
                return colors.white
        except:
            return colors.white

    def rgb_to_colour(self, r, g, b):
        """Convert RGB values to ReportLab Colour object"""
        try:
            if pd.isna(r) or pd.isna(g) or pd.isna(b):
                return colors.white

            r = max(0, min(255, int(float(r))))
            g = max(0, min(255, int(float(g))))
            b = max(0, min(255, int(float(b))))

            return Color(r/255.0, g/255.0, b/255.0)
        except:
            return colors.white

    def format_value(self, value, value_type):
        """Format values properly without HTML tags"""
        if pd.isna(value):
            return 'N/A'

        if value_type == 'lab':
            return f"{float(value):.1f}"
        elif value_type == 'rgb':
            return f"{int(float(value))}"
        elif value_type == 'hue':
            return f"{float(value):.1f}°"
        elif value_type == 'percent':
            return f"{float(value):.1f}%"
        else:
            return str(value)

    def create_colour_table(self, colour_data):
        """Create compact table with colorimetric information including Pantone"""
        # LAB Values
        l_val = self.format_value(colour_data.get('L'), 'lab')
        a_val = self.format_value(colour_data.get('a'), 'lab')
        b_val = self.format_value(colour_data.get('b'), 'lab')

        # CMYK Values
        L_val = colour_data.get('L')
        a_val_cmyk = colour_data.get('a')
        b_val_cmyk = colour_data.get('b')
        cmyk_values = "N/A"

        if not pd.isna(L_val) and not pd.isna(a_val_cmyk) and not pd.isna(b_val_cmyk):
            try:
                c, m, y, k = self.lab_to_cmyk(L_val, a_val_cmyk, b_val_cmyk)
                cmyk_values = f"C: {c:.1f}% M: {m:.1f}% Y: {y:.1f}% K: {k:.1f}%"
            except Exception as e:
                print(f"Error processing CMYK for table: {e}")
                cmyk_values = "N/A"

        # RGB Values
        r_val = self.format_value(colour_data.get('R'), 'rgb')
        g_val = self.format_value(colour_data.get('G'), 'rgb')
        b_val = self.format_value(colour_data.get('B'), 'rgb')

        # Calculate Hex sRGB (like Excel formula)
        hex_srgb = self.calculate_hex_srgb(
            colour_data.get('R'),
            colour_data.get('G'),
            colour_data.get('B')
        )

        # Hex ProPhoto
        hex_pro = colour_data.get('Hex (ProPhoto RGB)', 'N/A')
        if pd.isna(hex_pro):
            hex_pro = 'N/A'

        # HSL Values
        h_val = self.format_value(colour_data.get('H'), 'hue')
        s_val = self.format_value(colour_data.get('S (%)'), 'percent')
        l_hsl_val = self.format_value(colour_data.get('L (%)'), 'percent')

        # Find closest Pantone
        pantone_name, pantone_code, delta_e = self.find_closest_pantone(
            colour_data.get('L'),
            colour_data.get('a'),
            colour_data.get('b')
        )

        # Create compact table with better styling
        table_data = [
            ['LAB', f"L*: {l_val}  a*: {a_val}  b*: {b_val}"],
            ['CMYK', cmyk_values],
            ['RGB', f"R: {r_val}  G: {g_val}  B: {b_val}"],
            ['Hex sRGB', hex_srgb],
            ['Hex ProPhoto', hex_pro],
            ['HSL', f"H: {h_val}  S: {s_val}%  L: {l_hsl_val}%"],
            ['PANTONE', f"{pantone_name} ({pantone_code})"],
            ['Delta E00', f"{delta_e} (CIE2000)"]
        ]

        table = Table(table_data, colWidths=[3.5*cm, 8.5*cm])
        table.setStyle(TableStyle([
            # Background colors
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),

            # Fonts
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),

            # Special styling for Pantone row
            ('BACKGROUND', (0, 6), (1, 6), Color(0.95, 0.95, 1.0)),  # Light blue background
            ('FONTNAME', (0, 6), (1, 6), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 6), (1, 6), Color(0.1, 0.1, 0.5)),  # Dark blue text

            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Grid - thinner lines for better aesthetics
            ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        return table

    def create_visual_index_page(self, sheet_name, df, start_page):
        """Create visual index page with colour squares"""
        story = []

        # Card title
        story.append(Paragraph(f"VISUAL INDEX: {sheet_name}", self.title_style))
        story.append(Paragraph(f"Detailed pages start: Page {start_page + 23}", self.index_style))
        story.append(Spacer(1, 0.2*inch))

        # 6x8 grid = 48 colours per page
        colours_per_row = 6
        rows_per_page = 8
        colours_per_page = colours_per_row * rows_per_page
        total_colours = len(df)

        for page_start in range(0, total_colours, colours_per_page):
            # Añadir PageBreak ANTES de comenzar una nueva página (excepto la primera)
            if page_start > 0:
                story.append(PageBreak())
                story.append(Paragraph(f"VISUAL INDEX: {sheet_name} (continued)", self.title_style))
                story.append(Spacer(1, 0.2*inch))

            page_end = min(page_start + colours_per_page, total_colours)
            page_colours = df.iloc[page_start:page_end]

            # Create colour grid
            table_data = []
            current_row = []

            for idx, (_, row) in enumerate(page_colours.iterrows()):
                code = row.get('Code', f'Colour {idx+1}')
                colour_obj = self.get_colour_from_row(row)

                # Calculate the actual page number for this color
                # Each sheet has a title page, then individual color pages
                actual_page = start_page + idx

                # Create compact colour cell with more space
                colour_cell = Table([
                    [''],  # Colour space
                    [f"{code}"],
                    [f"(Page {actual_page + 23})"]
                ], colWidths=[2.8*cm], rowHeights=[1.2*cm, 0.4*cm, 0.3*cm])

                colour_cell.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colour_obj),
                    ('GRID', (0, 0), (0, 0), 1, colors.black),
                    ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 1), (0, 1), 9),
                    ('FONTSIZE', (0, 2), (0, 2), 8),
                    ('ALIGN', (0, 1), (0, 2), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 1), (0, 1), 4),
                    ('BOTTOMPADDING', (0, 1), (0, 1), 2),
                ]))

                current_row.append(colour_cell)

                # Complete row
                if len(current_row) == colours_per_row or idx == len(page_colours) - 1:
                    while len(current_row) < colours_per_row:
                        current_row.append("")

                    table_data.append(current_row)
                    current_row = []

            # Create main table
            if table_data:
                col_widths = [2.8*cm] * colours_per_row
                main_table = Table(table_data, colWidths=col_widths)
                main_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(main_table)
                story.append(Spacer(1, 0.3*inch))

        return story

    def create_other_content_pages(self, other_sheets_data):
        """Create readable pages for non-colour-card content"""
        story = []

        if not other_sheets_data:
            return story

        # Section separator
        story.append(PageBreak())
        story.append(Paragraph("ADDITIONAL REFERENCE MATERIAL", self.title_style))
        story.append(Spacer(1, 0.3*inch))

        for sheet_name, df in other_sheets_data.items():
            story.append(PageBreak())
            story.append(Paragraph(f"{sheet_name.upper()}", self.subtitle_style))
            story.append(Spacer(1, 0.2*inch))

            if not df.empty:
                # Convert dataframe to readable text
                for idx, row in df.iterrows():
                    row_text = []
                    for col_name, value in row.items():
                        if pd.notna(value) and str(value).strip():
                            row_text.append(f"{col_name}: {value}")

                    if row_text:
                        paragraph_text = " | ".join(row_text)
                        story.append(Paragraph(paragraph_text, self.notes_style))
                        story.append(Spacer(1, 0.1*inch))

            else:
                story.append(Paragraph("No data available in this sheet.", self.notes_style))

            story.append(Spacer(1, 0.3*inch))

        return story

    def create_index_page(self, colour_data):
        """Create visual index pages for all colour cards"""
        story = []

        # General title page
        story.append(Paragraph("ANIME COLOUR CARDS COLLECTION", self.title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Visual Indices", self.subtitle_style))
        story.append(Spacer(1, 0.3*inch))

        # Summary of cards with page numbers
        # Start counting from page 3 (title page + this page + next page)
        current_page = 3

        for sheet_name, df in colour_data.items():
            colour_count = len(df)
            # Store where each sheet starts (title page + 1 for first color)
            self.sheet_page_starts[sheet_name] = current_page + 1
            story.append(Paragraph(f"• {sheet_name}: {colour_count} colours (Page {current_page + 1})", self.index_style))
            # Add pages for this sheet: 1 title page + colour pages
            current_page += 1 + len(df)

        # Añadir PageBreak ANTES de comenzar con los índices visuales
        story.append(PageBreak())

        # Create visual index for each card
        colours_per_page = 48

        # Calculate starting pages considering title pages
        current_sheet_start = 3  # After title and summary pages

        for i, (sheet_name, df) in enumerate(colour_data.items()):
            # Añadir PageBreak ANTES de comenzar con una nueva hoja (excepto la primera)
            if i > 0:
                story.append(PageBreak())

            # Calculate detailed pages start (after title page for this sheet)
            detailed_start = current_sheet_start + 1

            # Create visual index
            index_content = self.create_visual_index_page(sheet_name, df, detailed_start)
            story.extend(index_content)

            # Update for next sheet: title page + colour pages
            current_sheet_start += 1 + len(df)

        return story

    def add_page_number(self, canvas, doc):
        """Add page number to footer"""
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.gray)
        canvas.drawCentredString(A4[0]/2, 1*cm, f"Page {self.current_page}")
        canvas.restoreState()
        self.current_page += 1

    def create_colour_pages(self, colour_data):
        """Create individual pages for each colour with CMYK conversion"""
        story = []

        for sheet_name, df in colour_data.items():
            self.sheet_name = sheet_name

            # Card title page
            story.append(PageBreak())
            story.append(Paragraph(f"COLOUR CARD: {sheet_name.upper()}", self.title_style))
            story.append(Spacer(1, 0.5*inch))

            # Add sheet info
            colour_count = len(df)
            story.append(Paragraph(f"Total colours: {colour_count}", self.subtitle_style))
            story.append(PageBreak())

            for idx, row in df.iterrows():
                # New page for each colour
                if idx > 0:
                    story.append(PageBreak())

                # Get colour data
                code = row.get('Code', f'Colour {idx+1}')
                hex_pro = row.get('Hex (ProPhoto RGB)', 'N/A')
                if pd.isna(hex_pro):
                    hex_pro = 'N/A'

                # Title with colour code and sheet name
                story.append(Paragraph(f"Colour: {code} ({sheet_name})", self.subtitle_style))
                story.append(Spacer(1, 0.15*inch))

                # Get colour object for sRGB display
                srgb_colour = self.get_colour_from_row(row)

                # Convert LAB to CMYK for print display
                L_val = row.get('L')
                a_val = row.get('a')
                b_val = row.get('b')

                cmyk_colour = colors.white
                cmyk_values = "N/A"

                if not pd.isna(L_val) and not pd.isna(a_val) and not pd.isna(b_val):
                    try:
                        c, m, y, k = self.lab_to_cmyk(L_val, a_val, b_val)
                        cmyk_colour = self.cmyk_to_rgb(c, m, y, k)
                        cmyk_values = f"C: {c:.1f}% M: {m:.1f}% Y: {y:.1f}% K: {k:.1f}%"
                    except Exception as e:
                        print(f"Error processing CMYK for {code}: {e}")
                        cmyk_colour = colors.lightgrey

                # Create colour display with two samples
                colour_display_data = [
                    ['sRGB SAMPLE', 'CMYK SAMPLE'],
                    ['', '']  # Color boxes
                ]

                colour_display = Table(colour_display_data, colWidths=[6*cm, 6*cm], rowHeights=[0.6*cm, 4*cm])

                colour_display.setStyle(TableStyle([
                    # Headers
                    ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (1, 0), 12),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('GRID', (0, 0), (1, 0), 0.25, colors.darkgrey),

                    # sRGB sample
                    ('BACKGROUND', (0, 1), (0, 1), srgb_colour),
                    ('GRID', (0, 1), (0, 1), 0.5, colors.black),

                    # CMYK sample
                    ('BACKGROUND', (1, 1), (1, 1), cmyk_colour),
                    ('GRID', (1, 1), (1, 1), 0.5, colors.black),
                ]))

                story.append(colour_display)
                story.append(Spacer(1, 0.15*inch))

                # Colorimetric information
                story.append(Paragraph("Colorimetric Information", self.section_title_style))
                story.append(Spacer(1, 0.1*inch))

                colour_table = self.create_colour_table(row)
                story.append(colour_table)

                story.append(Spacer(1, 0.15*inch))

                # Notes section
                notes_style = ParagraphStyle(
                    'NotesTitle',
                    parent=self.styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=12,
                    textColor=colors.darkblue,
                    spaceAfter=6
                )

                story.append(Paragraph("NOTES", notes_style))

                # Add a line separator
                line = Table([['']], colWidths=[19*cm], rowHeights=[0.05*cm])
                line.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
                    ('GRID', (0, 0), (0, 0), 0, colors.white),
                ]))
                story.append(line)

                # Add space for notes
                story.append(Spacer(1, 4*cm))

        return story

    def generate_pdf(self):
        """Generate the complete PDF"""
        print("🎨 ANIME COLOUR CARDS PDF GENERATOR")
        print("=" * 50)

        # Read Excel data
        colour_data, other_sheets_data = self.read_excel_data()
        if not colour_data:
            print("❌ No valid colour cards found!")
            return

        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_pdf_path,
            pagesize=A4,
            topMargin=2*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )

        story = []

        # Add index pages
        print("\n📑 Creating index pages...")
        index_content = self.create_index_page(colour_data)
        story.extend(index_content)

        # Add colour pages
        print("🎨 Creating colour pages...")
        colour_pages = self.create_colour_pages(colour_data)
        story.extend(colour_pages)

        # Add other content pages
        if other_sheets_data:
            print("📝 Creating additional content pages...")
            other_content = self.create_other_content_pages(other_sheets_data)
            story.extend(other_content)

        # Build PDF
        print(f"\n📄 Building PDF: {self.output_pdf_path}")
        doc.build(story, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)

        print(f"✅ PDF generated successfully!")
        print(f"📊 Total pages: {self.current_page - 1}")
        print(f"🎨 Colour cards processed: {sum(len(df) for df in colour_data.values())}")

        # Open the PDF
        try:
            os.startfile(self.output_pdf_path)
            print("📂 Opening PDF...")
        except:
            print(f"📂 PDF saved at: {os.path.abspath(self.output_pdf_path)}")


# Usage
if __name__ == "__main__":
    excel_file = "anime_colors.xlsx"  # Your Excel file
    pantone_csv = "pantone_lab.csv"  # Pantone reference CSV

    generator = AnimeColourCardsPDF(excel_file, "anime_colour_cards.pdf", pantone_csv)
    generator.generate_pdf()
