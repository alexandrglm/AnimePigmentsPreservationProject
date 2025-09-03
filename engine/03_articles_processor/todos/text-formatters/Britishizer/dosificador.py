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

@dataclass
class ConversionResult:
    original_word: str
    suggested_word: str
    line_number: int
    context: str
    confidence: str  # 'high', 'medium', 'low'

class MarkdownBritishizer:
    def __init__(self, database_file: str = "unified_american_to_british.json"):
        self.database = self.load_database(database_file)
        self.conversions = self.database.get("conversions", {})
        self.british_only = set(self.database.get("british_only", []))
        self.american_only = set(self.database.get("american_only", []))
        self.different_meanings = self.database.get("different_meanings", {})
        self.ignore_words = set(self.database.get("ignore_words", []))

        # Compilar patrones regex para eficiencia
        self.word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        self.setup_intelligent_patterns()

    def load_database(self, filename: str) -> Dict:
        """Carga la base de datos unificada"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: No se encuentra {filename}")
            print("   Ejecuta primero el script unificador")
            exit(1)

    def setup_intelligent_patterns(self):
        """Configura patrones inteligentes para detección automática"""
        # Patrones para terminaciones comunes
        self.auto_patterns = [
            # -ize/-ise patterns
            (re.compile(r'\b(\w+)ize\b'), r'\1ise'),
            (re.compile(r'\b(\w+)ized\b'), r'\1ised'),
            (re.compile(r'\b(\w+)izing\b'), r'\1ising'),
            (re.compile(r'\b(\w+)ization\b'), r'\1isation'),

            # -yze/-yse patterns
            (re.compile(r'\b(\w+)yze\b'), r'\1yse'),
            (re.compile(r'\b(\w+)yzed\b'), r'\1ysed'),
            (re.compile(r'\b(\w+)yzing\b'), r'\1ysing'),

            # -or/-our patterns
            (re.compile(r'\b(\w+)or\b'), r'\1our'),

            # -er/-re patterns
            (re.compile(r'\b(\w+)er\b'), r'\1re'),

            # -ense/-ence patterns
            (re.compile(r'\b(\w+)ense\b'), r'\1ence'),
        ]

    def find_americanisms_in_text(self, text: str, filename: str) -> List[ConversionResult]:
        """Encuentra todas las palabras americanas en el texto"""
        results = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Buscar palabras individuales
            words = self.word_pattern.findall(line.lower())

            for word in words:
                # Ignorar palabras en ignore list
                if word in self.ignore_words:
                    continue

                # Buscar en diccionario directo
                if word in self.conversions:
                    british_word = self.conversions[word]
                    confidence = 'high'

                    result = ConversionResult(
                        original_word=word,
                        suggested_word=british_word,
                        line_number=line_num,
                        context=line.strip()[:100] + "..." if len(line) > 100 else line.strip(),
                        confidence=confidence
                    )
                    results.append(result)

                # Buscar patrones automáticos
                else:
                    for pattern, replacement in self.auto_patterns:
                        if pattern.match(word):
                            potential_british = pattern.sub(replacement, word)

                            # Verificar que la conversión sea válida
                            if self.is_valid_conversion(word, potential_british):
                                result = ConversionResult(
                                    original_word=word,
                                    suggested_word=potential_british,
                                    line_number=line_num,
                                    context=line.strip()[:100] + "..." if len(line) > 100 else line.strip(),
                                    confidence='medium'
                                )
                                results.append(result)
                            break

        return results

    def is_valid_conversion(self, american: str, british: str) -> bool:
        """Verifica si una conversión automática es válida"""
        # Evitar conversiones obvias incorrectas
        invalid_patterns = [
            r'^(the|and|or|for|in|on|at|to).*',  # Palabras funcionales
            r'^[a-z]{1,2}$',  # Palabras muy cortas
            r'^\d',  # Que empiecen con número
        ]

        for pattern in invalid_patterns:
            if re.match(pattern, american):
                return False

        # Verificar que no esté en ignore list
        if american in self.ignore_words or british in self.ignore_words:
            return False

        return True

    def process_file_mode_1(self, filepath: str) -> List[ConversionResult]:
        """Modo 1: Solo buscar y mostrar"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        results = self.find_americanisms_in_text(text, filepath)

        if results:
            print(f"\n📄 Archivo: {filepath}")
            print(f"🔍 Encontradas {len(results)} posibles conversiones:")

            for result in results:
                confidence_icon = "🟢" if result.confidence == 'high' else "🟡"
                print(f"  {confidence_icon} Línea {result.line_number}: '{result.original_word}' → '{result.suggested_word}'")
                print(f"     Contexto: {result.context}")
        else:
            print(f"✅ {filepath}: No se encontraron americanismos")

        return results

    def process_file_mode_2(self, filepath: str) -> int:
        """Modo 2: Cambiar automáticamente"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        original_text = text
        changes_made = 0

        # Aplicar conversiones de alta confianza
        for american, british in self.conversions.items():
            # Usar word boundaries para evitar cambios en medio de palabras
            pattern = rf'\b{re.escape(american)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                # Preservar capitalización original
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
                    changes_made += text.count(american.lower()) + text.count(american.capitalize()) + text.count(american.upper())
                    text = new_text

        # Guardar solo si hubo cambios
        if changes_made > 0:
            # Backup del original
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_text)

            # Guardar versión británica
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)

            print(f"✅ {filepath}: {changes_made} cambios realizados (backup: {backup_path})")
        else:
            print(f"ℹ️  {filepath}: No requiere cambios")

        return changes_made

    def process_file_mode_3(self, filepath: str) -> int:
        """Modo 3: Preguntar uno por uno"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        results = self.find_americanisms_in_text(text, filepath)

        if not results:
            print(f"✅ {filepath}: No se encontraron americanismos")
            return 0

        print(f"\n📄 Procesando: {filepath}")
        print(f"🔍 Encontradas {len(results)} posibles conversiones")

        changes_made = 0
        approved_changes = {}

        for result in results:
            confidence_icon = "🟢" if result.confidence == 'high' else "🟡"
            print(f"\n{confidence_icon} Línea {result.line_number}:")
            print(f"   Contexto: {result.context}")
            print(f"   Cambio: '{result.original_word}' → '{result.suggested_word}'")

            while True:
                choice = input("   ¿Cambiar? (s/n/q para salir): ").lower().strip()
                if choice in ['s', 'y', 'yes', 'sí']:
                    approved_changes[result.original_word] = result.suggested_word
                    changes_made += 1
                    break
                elif choice in ['n', 'no']:
                    break
                elif choice in ['q', 'quit', 'salir']:
                    if changes_made > 0:
                        self.apply_manual_changes(filepath, text, approved_changes)
                    return changes_made
                else:
                    print("   Opción inválida. Use s/n/q")

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
            pattern = rf'\b{re.escape(american)}\b'

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

        print(f"✅ {len(changes)} cambios aplicados (backup: {backup_path})")

    def process_directory(self, directory: str, mode: int):
        """Procesa todos los archivos .md en un directorio"""
        md_files = list(Path(directory).rglob("*.md"))

        if not md_files:
            print(f"❌ No se encontraron archivos .md en {directory}")
            return

        print(f"📁 Encontrados {len(md_files)} archivos .md")

        total_changes = 0
        for md_file in md_files:
            if mode == 1:
                self.process_file_mode_1(str(md_file))
            elif mode == 2:
                total_changes += self.process_file_mode_2(str(md_file))
            elif mode == 3:
                total_changes += self.process_file_mode_3(str(md_file))

        if mode in [2, 3]:
            print(f"\n🎯 Resumen: {total_changes} cambios totales en {len(md_files)} archivos")

def main():
    parser = argparse.ArgumentParser(description="Convierte texto americano a británico en archivos Markdown")
    parser.add_argument("path", help="Archivo .md o directorio a procesar")
    parser.add_argument("-m", "--mode", type=int, choices=[1, 2, 3], default=1,
                       help="Modo: 1=buscar, 2=cambiar automático, 3=decidir uno por uno")
    parser.add_argument("-d", "--database", default="unified_american_to_british.json",
                       help="Archivo de base de datos (default: unified_american_to_british.json)")

    args = parser.parse_args()

    # Verificar que existe la base de datos
    if not os.path.exists(args.database):
        print(f"❌ Error: No se encuentra la base de datos {args.database}")
        print("   Ejecuta primero el script unificador")
        return

    # Inicializar procesador
    britishizer = MarkdownBritishizer(args.database)

    # Determinar si es archivo o directorio
    path = Path(args.path)

    if path.is_file() and path.suffix == '.md':
        print(f"📄 Procesando archivo: {path}")
        if args.mode == 1:
            britishizer.process_file_mode_1(str(path))
        elif args.mode == 2:
            changes = britishizer.process_file_mode_2(str(path))
            print(f"🎯 Total: {changes} cambios")
        elif args.mode == 3:
            changes = britishizer.process_file_mode_3(str(path))
            print(f"🎯 Total: {changes} cambios")

    elif path.is_dir():
        print(f"📁 Procesando directorio: {path}")
        britishizer.process_directory(str(path), args.mode)

    else:
        print(f"❌ Error: {path} no es un archivo .md válido o directorio")

if __name__ == "__main__":
    print("🇬🇧 Markdown Britishizer v1.0")
    print("=" * 50)

    # Mostrar ayuda si no hay argumentos
    import sys
    if len(sys.argv) == 1:
        print("Uso:")
        print("  python britishizer.py archivo.md -m 1    # Solo buscar")
        print("  python britishizer.py archivo.md -m 2    # Cambiar automático")
        print("  python britishizer.py directorio/ -m 3   # Decidir uno por uno")
        print("\nModos:")
        print("  1 = Solo buscar y mostrar americanismos")
        print("  2 = Cambiar automáticamente (crea backup)")
        print("  3 = Preguntar por cada cambio individualmente")
        print("\nEjecuta primero: python unify_dictionaries.py")
    else:
        main()
