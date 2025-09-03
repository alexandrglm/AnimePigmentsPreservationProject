#!/usr/bin/env python3
"""
Script para unificar todas las fuentes de conversión American → British English
"""

import json
import re
import os
from typing import Dict, Set, List, Tuple

class DictionaryUnifier:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.unified_dict = {}
        self.british_only_words = set()
        self.american_only_words = set()
        self.different_meanings = {}
        self.ignore_words = set()

    def load_json_file(self, filename: str) -> Dict:
        """Carga archivo JSON de manera segura"""
        try:
            with open(os.path.join(self.base_path, filename), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Archivo no encontrado: {filename}")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️  Error JSON en: {filename}")
            return {}

    def load_text_file(self, filename: str) -> List[str]:
        """Carga archivo de texto línea por línea"""
        try:
            with open(os.path.join(self.base_path, filename), 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"⚠️  Archivo no encontrado: {filename}")
            return []

    def parse_wikipedia_variants(self, lines: List[str]) -> Dict[str, str]:
        """Parsea el formato de Wikipedia: 'british, american'"""
        variants = {}
        for line in lines:
            if ',' in line and not line.startswith('#'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    british = parts[0].strip()
                    american = parts[1].strip()
                    if british and american and british != american:
                        variants[american] = british
        return variants

    def generate_verb_variants(self, base_american: str, base_british: str) -> Dict[str, str]:
        """Genera variantes automáticas de verbos (ed, ing, s, etc.)"""
        variants = {}

        # Casos especiales para -ize/-ise
        if base_american.endswith('ize') and base_british.endswith('ise'):
            root_am = base_american[:-3]
            root_br = base_british[:-3]

            variants.update({
                f"{root_am}ized": f"{root_br}ised",
                f"{root_am}izing": f"{root_br}ising",
                f"{root_am}ization": f"{root_br}isation",
                f"{root_am}izes": f"{root_br}ises"
            })

        # Casos especiales para -yze/-yse
        elif base_american.endswith('yze') and base_british.endswith('yse'):
            root_am = base_american[:-3]
            root_br = base_british[:-3]

            variants.update({
                f"{root_am}yzed": f"{root_br}ysed",
                f"{root_am}yzing": f"{root_br}ysing",
                f"{root_am}yzes": f"{root_br}yses"
            })

        # Casos generales para otros verbos
        else:
            # Formas -ed
            if not base_american.endswith('e'):
                variants[f"{base_american}ed"] = f"{base_british}ed"
            else:
                variants[f"{base_american}d"] = f"{base_british}d"

            # Formas -ing
            variants[f"{base_american}ing"] = f"{base_british}ing"

            # Formas -s
            if base_american.endswith(('s', 'sh', 'ch', 'x', 'z')):
                variants[f"{base_american}es"] = f"{base_british}es"
            else:
                variants[f"{base_american}s"] = f"{base_british}s"

        return variants

    def generate_pattern_words(self) -> Dict[str, str]:
        """Genera patrones automáticos basados en terminaciones comunes"""
        patterns = {}

        # Patrones -our/-or
        our_words = ['colour', 'honour', 'favour', 'flavour', 'labour', 'neighbour',
                     'harbour', 'rumour', 'humour', 'vigour', 'odour', 'splendour']
        for word in our_words:
            american = word.replace('our', 'or')
            patterns[american] = word
            # Agregar derivados
            patterns[f"{american}ed"] = f"{word}ed"
            patterns[f"{american}ing"] = f"{word}ing"
            patterns[f"{american}s"] = f"{word}s"

        # Patrones -re/-er
        re_words = ['centre', 'theatre', 'metre', 'litre', 'fibre', 'calibre']
        for word in re_words:
            american = word.replace('re', 'er')
            patterns[american] = word

        # Patrones -ence/-ense
        ence_words = ['defence', 'offence', 'licence', 'pretence']
        for word in ence_words:
            american = word.replace('ence', 'ense')
            patterns[american] = word

        # Patrones -ae/-e
        ae_words = ['anaemia', 'paediatric', 'leukaemia', 'diarrhoea']
        for word in ae_words:
            american = word.replace('ae', 'e')
            patterns[american] = word

        return patterns

    def unify_all_sources(self):
        """Unifica todas las fuentes en un diccionario maestro"""
        print("🔄 Unificando fuentes...")

        # 1. Cargar archivos principales
        british_spellings = self.load_json_file("british_spellings.json")
        american_spellings = self.load_json_file("american_spellings.json")
        different_meanings = self.load_json_file("different_meanings.json")
        british_only = self.load_json_file("british_only.json")
        american_only = self.load_json_file("american_only.json")
        ignore_list = self.load_json_file("ignore_list.json")

        # 2. Procesar ignore list
        if isinstance(ignore_list, list):
            self.ignore_words = set(ignore_list)

        # 3. Combinar spellings (american → british)
        self.unified_dict.update(american_spellings)

        # Invertir british_spellings (british → american → british)
        for brit, amer in british_spellings.items():
            self.unified_dict[amer] = brit

        # 4. Agregar palabras exclusivas
        self.british_only_words = set(british_only.keys())
        self.american_only_words = set(american_only.keys())
        self.different_meanings = different_meanings

        # 5. Cargar variantes de Wikipedia
        wiki_lines = self.load_text_file("wki_list_spell_variants.txt")
        wiki_variants = self.parse_wikipedia_variants(wiki_lines)
        self.unified_dict.update(wiki_variants)

        # 6. Generar patrones automáticos
        pattern_words = self.generate_pattern_words()
        self.unified_dict.update(pattern_words)

        # 7. Generar variantes de verbos
        verb_variants = {}
        for american, british in list(self.unified_dict.items()):
            if len(american) > 3:  # Evitar palabras muy cortas
                variants = self.generate_verb_variants(american, british)
                verb_variants.update(variants)

        self.unified_dict.update(verb_variants)

        # 8. Limpiar ignore words
        for word in self.ignore_words:
            self.unified_dict.pop(word, None)

        print(f"✅ Unificación completa: {len(self.unified_dict)} conversiones")

    def save_unified_database(self, output_file: str = "unified_american_to_british.json"):
        """Guarda la base de datos unificada"""
        database = {
            "conversions": self.unified_dict,
            "british_only": list(self.british_only_words),
            "american_only": list(self.american_only_words),
            "different_meanings": self.different_meanings,
            "ignore_words": list(self.ignore_words),
            "metadata": {
                "total_conversions": len(self.unified_dict),
                "description": "American to British English conversion database"
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)

        print(f"💾 Base de datos guardada en: {output_file}")

        # Estadísticas
        print(f"📊 Estadísticas:")
        print(f"   - Conversiones: {len(self.unified_dict)}")
        print(f"   - Británicas exclusivas: {len(self.british_only_words)}")
        print(f"   - Americanas exclusivas: {len(self.american_only_words)}")
        print(f"   - Significados diferentes: {len(self.different_meanings)}")

def main():
    unifier = DictionaryUnifier()
    unifier.unify_all_sources()
    unifier.save_unified_database()

if __name__ == "__main__":
    main()
