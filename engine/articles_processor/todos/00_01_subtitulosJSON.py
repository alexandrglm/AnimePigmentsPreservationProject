#!/usr/bin/env python3
import os
import json

MD_FOLDER = '.'
OUTPUT_JSON = 'second_lines.json'

result = {}

for fname in os.listdir(MD_FOLDER):
    if fname.endswith('.md'):
        path = os.path.join(MD_FOLDER, fname)
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                second_line = lines[1].strip()
                if second_line.startswith('##'):
                    result[fname] = second_line

with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"JSON generado: {OUTPUT_JSON}")
