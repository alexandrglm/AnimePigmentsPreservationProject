#!/usr/bin/env python3
"""
Markdown Britishizer - Convierte texto americano a británico en archivos .md
"""

import json
import re
import os
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

# Colores ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class ConversionResult:
    original_word: str
    suggested_word: str
    line_number: int
    context: str
    confidence: str  # 'high' (json), 'medium' (pattern)
    source: str      # 'json' or 'pattern'

class MarkdownBritishizer:
    def __init__(self, database_file: str = "unified_american_to_british.json"):
        self.database = self.load_database(database_file)

        # PRIMERO asignar las conversiones
        self.conversions = self.database.get("conversions", {})
        self.british_only = set(self.database.get("british_only", []))
        self.american_only = set(self.database.get("american_only", []))
        self.different_meanings = self.database.get("different_meanings", {})
        self.ignore_words = set(self.database.get("ignore_words", []))

        # LUEGO hacer el debug
        print(f"DEBUG: Loaded database from {database_file}")
        print(f"DEBUG: Total conversions: {len(self.conversions)}")
        if self.conversions:
            sample = list(self.conversions.items())[:5]
            print(f"DEBUG: Sample conversions: {sample}")

        # Cargar/crear lista de palabras prohibidas
        self.prohibited_file = "prohibited_words.json"
        self.prohibited_words = self.load_prohibited_words()

        # Compilar patrones regex para eficiencia
        self.word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        self.setup_intelligent_patterns()

    def load_database(self, filename: str) -> Dict:
        """Carga la base de datos unificada"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Error: No se encuentra {filename}{Colors.END}")
            print("   Ejecuta primero el script unificador")
            exit(1)

    def load_prohibited_words(self) -> Set[str]:
        """Carga palabras prohibidas por el usuario"""
        try:
            with open(self.prohibited_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get("prohibited", []))
        except FileNotFoundError:
            return set()

    def save_prohibited_words(self):
        """Guarda palabras prohibidas"""
        data = {"prohibited": list(self.prohibited_words)}
        with open(self.prohibited_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def setup_intelligent_patterns(self):
        """Configura patrones inteligentes para detección automática"""
        # Solo patrones muy específicos y seguros
        self.auto_patterns = [
            # -ize/-ise patterns (solo para palabras conocidas)
            (re.compile(r'\b(organ|real|modern|legal|special|normal|local|social|national|international|personal|professional|global|digital|central|general|natural|cultural|traditional|regional|temporal|material|formal|moral|final|total|capital|hospital|criminal|original|individual|potential|essential)ize\b'), r'\1ise'),
            (re.compile(r'\b(organ|real|modern|legal|special|normal|local|social|national|international|personal|professional|global|digital|central|general|natural|cultural|traditional|regional|temporal|material|formal|moral|final|total|capital|hospital|criminal|original|individual|potential|essential)ized\b'), r'\1ised'),
            (re.compile(r'\b(organ|real|modern|legal|special|normal|local|social|national|international|personal|professional|global|digital|central|general|natural|cultural|traditional|regional|temporal|material|formal|moral|final|total|capital|hospital|criminal|original|individual|potential|essential)izing\b'), r'\1ising'),

            # -yze/-yse patterns (solo analyze/analyse y paralyze/paralyse)
            (re.compile(r'\b(anal|paral)yze\b'), r'\1yse'),
            (re.compile(r'\b(anal|paral)yzed\b'), r'\1ysed'),
            (re.compile(r'\b(anal|paral)yzing\b'), r'\1ysing'),
        ]

    def find_americanisms_in_text(self, text: str, filename: str, use_patterns: bool = True) -> List[ConversionResult]:
        """Encuentra todas las palabras americanas en el texto"""
        results = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            words = self.word_pattern.findall(line)

            for word in words:
                # Ignorar palabras prohibidas y en ignore list
                if word.lower() in self.ignore_words or word.lower() in self.prohibited_words:
                    continue

                # Buscar en diccionario JSON primero (alta confianza)
                # Buscar en diccionario JSON primero (alta confianza)
                if word.lower() in self.conversions:
                    british_word = self.conversions[word.lower()]  # ← ¡CORREGIR ESTA LÍNEA!

                    # DEBUG: Mostrar qué palabra se encontró
                    print(f"DEBUG: Found '{word.lower()}' -> '{british_word}' in JSON")
                    print(f"DEBUG: Original word: '{word}', Line: {line_num}")

                    result = ConversionResult(
                        original_word=word,  # Mantener capitalización original
                        suggested_word=british_word,
                        line_number=line_num,
                        context=line.strip(),
                        confidence='high',
                        source='json'
                    )
                    results.append(result)

                # Buscar patrones automáticos solo si se permite
                elif use_patterns:
                    for pattern, replacement in self.auto_patterns:
                        if pattern.match(word):
                            potential_british = pattern.sub(replacement, word)

                            if self.is_valid_conversion(word, potential_british):
                                result = ConversionResult(
                                    original_word=word,
                                    suggested_word=potential_british,
                                    line_number=line_num,
                                    context=line.strip(),
                                    confidence='medium',
                                    source='pattern'
                                )
                                results.append(result)
                            break

        return results

    def is_valid_conversion(self, american: str, british: str) -> bool:
        """Verifica si una conversión automática es válida"""
        # Evitar conversiones incorrectas
        invalid_patterns = [
            r'^(the|and|or|for|in|on|at|to|is|are|was|were|be|been|have|has|had|do|does|did|will|would|can|could|should|shall|may|might|must|a|an).*',
            r'^[a-z]{1,2}$',
            r'^\d',
        ]

        for pattern in invalid_patterns:
            if re.match(pattern, american):
                return False

        return True

    def highlight_word_in_context(self, context: str, word: str, suggestion: str) -> str:
        """Resalta la palabra en el contexto con colores"""
        # Resaltar palabra original en rojo y sugerencia en verde
        highlighted = re.sub(
            rf'\b{re.escape(word)}\b',
            f"{Colors.RED}{Colors.BOLD}{word}{Colors.END}",
            context,
            flags=re.IGNORECASE
        )
        return highlighted

    def process_file_mode_1(self, filepath: str) -> List[ConversionResult]:
        """Modo 1: Solo buscar y mostrar (con patrones)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        results = self.find_americanisms_in_text(text, filepath, use_patterns=True)

        if results:
            print(f"\n{Colors.BLUE}📄 Archivo: {filepath}{Colors.END}")
            print(f"{Colors.CYAN}🔍 Encontradas {len(results)} posibles conversiones:{Colors.END}")

            for result in results:
                confidence_icon = f"{Colors.GREEN}🟢" if result.confidence == 'high' else f"{Colors.YELLOW}🟡"
                source_label = f"{Colors.MAGENTA}[JSON]{Colors.END}" if result.source == 'json' else f"{Colors.YELLOW}[PATRÓN]{Colors.END}"

                print(f"  {confidence_icon} {source_label} Línea {result.line_number}: {Colors.RED}'{result.original_word}'{Colors.END} → {Colors.GREEN}'{result.suggested_word}'{Colors.END}")
                print(f"     {self.highlight_word_in_context(result.context, result.original_word, result.suggested_word)}")
        else:
            print(f"{Colors.GREEN}✅ {filepath}: No se encontraron americanismos{Colors.END}")

        return results

    def process_file_mode_2(self, filepath: str) -> int:
        """Modo 2: Cambiar automáticamente (con patrones)"""
        return self._auto_convert(filepath, use_patterns=True)

    def process_file_mode_3(self, filepath: str) -> int:
        """Modo 3: Preguntar uno por uno (con patrones)"""
        return self._interactive_convert(filepath, use_patterns=True)

    def process_file_mode_4(self, filepath: str) -> List[ConversionResult]:
        """Modo 4: Solo buscar en JSON (sin patrones)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        results = self.find_americanisms_in_text(text, filepath, use_patterns=False)

        if results:
            print(f"\n{Colors.BLUE}📄 Archivo: {filepath}{Colors.END}")
            print(f"{Colors.CYAN}🔍 Encontradas {len(results)} conversiones del diccionario:{Colors.END}")

            for result in results:
                print(f"  {Colors.GREEN}🟢 [JSON]{Colors.END} Línea {result.line_number}: {Colors.RED}'{result.original_word}'{Colors.END} → {Colors.GREEN}'{result.suggested_word}'{Colors.END}")
                print(f"     {self.highlight_word_in_context(result.context, result.original_word, result.suggested_word)}")
        else:
            print(f"{Colors.GREEN}✅ {filepath}: No se encontraron americanismos en el diccionario{Colors.END}")

        return results

    def process_file_mode_5(self, filepath: str) -> int:
        """Modo 5: Cambiar automáticamente solo JSON (sin patrones)"""
        return self._auto_convert(filepath, use_patterns=False)

    def process_file_mode_6(self, filepath: str) -> int:
        """Modo 6: Preguntar uno por uno solo JSON (sin patrones)"""
        return self._interactive_convert(filepath, use_patterns=False)

    def _auto_convert(self, filepath: str, use_patterns: bool) -> int:
        """Convierte automáticamente"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        original_text = text
        changes_made = 0

        # Solo usar conversiones del JSON si use_patterns=False
        conversions_to_use = self.conversions

        if use_patterns:
            # Agregar patrones automáticos
            pattern_conversions = {}
            for pattern, replacement in self.auto_patterns:
                matches = pattern.findall(text)
                for match in matches:
                    american_word = match + pattern.pattern.split('(')[1].split(')')[1].replace('\\b', '')
                    british_word = pattern.sub(replacement, american_word)
                    if self.is_valid_conversion(american_word, british_word):
                        pattern_conversions[american_word] = british_word

            conversions_to_use = {**self.conversions, **pattern_conversions}

        # Aplicar conversiones
        for american, british in conversions_to_use.items():
            if american not in self.prohibited_words:
                pattern = rf'{re.escape(american)}'
                if re.search(pattern, text, re.IGNORECASE):
                    def replace_preserve_case(match):
                        word = match.group()
                        if word.isupper():
                            return british.upper()
                        elif word.istitle():
                            return british.capitalize()
                        else:
                            return british.lower()

                    new_text = re.sub(pattern, replace_preserve_case, text, flags=re.IGNORECASE)
                    if new_text != text:
                        changes_made += len(re.findall(pattern, text, re.IGNORECASE))
                        text = new_text

        if changes_made > 0:
            # Backup
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_text)

            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)

            source_label = "JSON + PATRONES" if use_patterns else "SOLO JSON"
            print(f"{Colors.GREEN}✅ {filepath}: {changes_made} cambios ({source_label}) - backup: {backup_path}{Colors.END}")
        else:
            print(f"{Colors.BLUE}ℹ️  {filepath}: No requiere cambios{Colors.END}")

        return changes_made

    def _interactive_convert(self, filepath: str, use_patterns: bool) -> int:
        """Conversión interactiva"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        results = self.find_americanisms_in_text(text, filepath, use_patterns)

        if not results:
            source_label = "JSON + PATRONES" if use_patterns else "SOLO JSON"
            print(f"{Colors.GREEN}✅ {filepath}: No se encontraron americanismos ({source_label}){Colors.END}")
            return 0

        source_label = "JSON + PATRONES" if use_patterns else "SOLO JSON"
        print(f"\n{Colors.BLUE}📄 Procesando: {filepath} ({source_label}){Colors.END}")
        print(f"{Colors.CYAN}🔍 Encontradas {len(results)} posibles conversiones{Colors.END}")

        changes_made = 0
        approved_changes = {}

        for i, result in enumerate(results, 1):
            confidence_icon = f"{Colors.GREEN}🟢" if result.confidence == 'high' else f"{Colors.YELLOW}🟡"
            source_icon = f"{Colors.MAGENTA}[JSON]{Colors.END}" if result.source == 'json' else f"{Colors.YELLOW}[PATRÓN]{Colors.END}"

            print(f"\n{confidence_icon} {source_icon} {Colors.BOLD}({i}/{len(results)}){Colors.END} Línea {result.line_number}:")
            print(f"   Contexto: {self.highlight_word_in_context(result.context, result.original_word, result.suggested_word)}")
            print(f"   Cambio: {Colors.RED}'{result.original_word}'{Colors.END} → {Colors.GREEN}'{result.suggested_word}'{Colors.END}")

            while True:
                choice = input(f"   {Colors.BOLD}¿Cambiar? (Y/y/N/n/Q/q): {Colors.END}").strip()

                if choice.lower() in ['y', 'yes', 'sí', 's']:
                    approved_changes[result.original_word] = result.suggested_word
                    changes_made += 1
                    print(f"   {Colors.GREEN}✓ Aprobado{Colors.END}")
                    break

                elif choice.lower() in ['n', 'no']:
                    # Si es patrón, agregar a prohibidas
                    if result.source == 'pattern':
                        self.prohibited_words.add(result.original_word)
                        self.save_prohibited_words()
                        print(f"   {Colors.YELLOW}✗ Rechazado y agregado a prohibidas{Colors.END}")
                    else:
                        print(f"   {Colors.YELLOW}✗ Rechazado{Colors.END}")
                    break

                elif choice.lower() in ['q', 'quit', 'salir']:
                    if changes_made > 0:
                        self.apply_manual_changes(filepath, text, approved_changes)
                    return changes_made

                else:
                    print(f"   {Colors.RED}Opción inválida. Use Y/N/Q{Colors.END}")

        # Aplicar cambios aprobados
        if approved_changes:
            self.apply_manual_changes(filepath, text, approved_changes)

        return changes_made

    def apply_manual_changes(self, filepath: str, text: str, changes: Dict[str, str]):
        """Aplica los cambios manuales aprobados"""
        # Backup
        backup_path = filepath + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(text)

        # Aplicar cambios preservando capitalización
        for american, british in changes.items():
            pattern = rf'{re.escape(american)}'

            def replace_preserve_case(match):
                word = match.group()
                if word.isupper():
                    return british.upper()
                elif word.istitle():
                    return british.capitalize()
                else:
                    return british.lower()

            text = re.sub(pattern, replace_preserve_case, text, flags=re.IGNORECASE)

        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"{Colors.GREEN}✅ {len(changes)} cambios aplicados (backup: {backup_path}){Colors.END}")

    def process_directory(self, directory: str, mode: int):
        """Procesa todos los archivos .md en un directorio"""
        md_files = list(Path(directory).rglob("*.md"))

        if not md_files:
            print(f"{Colors.RED}❌ No se encontraron archivos .md en {directory}{Colors.END}")
            return

        print(f"{Colors.CYAN}📁 Encontrados {len(md_files)} archivos .md{Colors.END}")

        total_changes = 0
        for md_file in md_files:
            if mode == 1:
                self.process_file_mode_1(str(md_file))
            elif mode == 2:
                total_changes += self.process_file_mode_2(str(md_file))
            elif mode == 3:
                total_changes += self.process_file_mode_3(str(md_file))
            elif mode == 4:
                self.process_file_mode_4(str(md_file))
            elif mode == 5:
                total_changes += self.process_file_mode_5(str(md_file))
            elif mode == 6:
                total_changes += self.process_file_mode_6(str(md_file))

        if mode in [2, 3, 5, 6]:
            print(f"\n{Colors.BOLD}🎯 Resumen: {total_changes} cambios totales en {len(md_files)} archivos{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description="Convierte texto americano a británico en archivos Markdown")
    parser.add_argument("path", help="Archivo .md o directorio a procesar")
    parser.add_argument("-m", "--mode", type=int, choices=[1, 2, 3, 4, 5, 6], default=1,
                       help="Modo: 1=buscar+patrones, 2=auto+patrones, 3=interactivo+patrones, 4=buscar solo JSON, 5=auto solo JSON, 6=interactivo solo JSON")
    parser.add_argument("-d", "--database", default="unified_american_to_british.json",
                       help="Archivo de base de datos")

    args = parser.parse_args()

    # Verificar base de datos
    if not os.path.exists(args.database):
        print(f"{Colors.RED}❌ Error: No se encuentra la base de datos {args.database}{Colors.END}")
        print("   Ejecuta primero el script unificador")
        return

    # Inicializar procesador
    britishizer = MarkdownBritishizer(args.database)

    # Procesar
    path = Path(args.path)

    if path.is_file() and path.suffix == '.md':
        print(f"{Colors.BLUE}📄 Procesando archivo: {path}{Colors.END}")

        if args.mode == 1:
            britishizer.process_file_mode_1(str(path))
        elif args.mode == 2:
            changes = britishizer.process_file_mode_2(str(path))
            print(f"{Colors.BOLD}🎯 Total: {changes} cambios{Colors.END}")
        elif args.mode == 3:
            changes = britishizer.process_file_mode_3(str(path))
            print(f"{Colors.BOLD}🎯 Total: {changes} cambios{Colors.END}")
        elif args.mode == 4:
            britishizer.process_file_mode_4(str(path))
        elif args.mode == 5:
            changes = britishizer.process_file_mode_5(str(path))
            print(f"{Colors.BOLD}🎯 Total: {changes} cambios{Colors.END}")
        elif args.mode == 6:
            changes = britishizer.process_file_mode_6(str(path))
            print(f"{Colors.BOLD}🎯 Total: {changes} cambios{Colors.END}")

    elif path.is_dir():
        print(f"{Colors.CYAN}📁 Procesando directorio: {path}{Colors.END}")
        britishizer.process_directory(str(path), args.mode)

    else:
        print(f"{Colors.RED}❌ Error: {path} no es un archivo .md válido o directorio{Colors.END}")

if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.BLUE}🇬🇧 Markdown Britishizer v2.0{Colors.END}")
    print("=" * 50)

    import sys
    if len(sys.argv) == 1:
        print(f"{Colors.BOLD}Uso:{Colors.END}")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}1{Colors.END}    # Buscar (JSON + patrones)")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}2{Colors.END}    # Auto (JSON + patrones)")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}3{Colors.END}    # Interactivo (JSON + patrones)")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}4{Colors.END}    # Buscar (solo JSON)")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}5{Colors.END}    # Auto (solo JSON)")
        print(f"  python3 britishizer.py archivo.md -m {Colors.YELLOW}6{Colors.END}    # Interactivo (solo JSON)")
        print()
        print(f"{Colors.BOLD}Modos:{Colors.END}")
        print(f"  {Colors.GREEN}1-3{Colors.END} = Usa diccionario JSON + patrones predictivos")
        print(f"  {Colors.BLUE}4-6{Colors.END} = Usa solo diccionario JSON (sin predicciones)")
        print(f"  {Colors.YELLOW}3,6{Colors.END} = Los rechazos de patrones se guardan en prohibited_words.json")
        print()
        print(f"Para directorio: {Colors.CYAN}python3 britishizer.py . -m 6{Colors.END}")
    else:
        main()
