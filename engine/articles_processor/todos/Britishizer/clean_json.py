#!/usr/bin/env python3
import json
import re
import sys

def extract_first_word(text):
    """Extrae la primera palabra de un texto"""
    if not isinstance(text, str):
        return None
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return words[0].lower() if words else None

def clean_json_file(filename):
    """Limpia un archivo JSON dejando solo primeras palabras"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error leyendo {filename}: {e}")
        return

    # Si el JSON tiene estructura anidada, usar solo "conversions"
    if isinstance(data, dict) and "conversions" in data:
        data = data["conversions"]

    cleaned = {}

    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, str):
            clean_key = extract_first_word(key)
            clean_value = extract_first_word(value)

            if clean_key and clean_value and clean_key != clean_value:
                cleaned[clean_key] = clean_value

    output_file = filename.replace('.json', '_cleaned.json')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        print(f"✅ {filename}: {len(data)} → {len(cleaned)} entries → {output_file}")

    except Exception as e:
        print(f"Error escribiendo {output_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 clean_json.py archivo.json")
        sys.exit(1)

    clean_json_file(sys.argv[1])
