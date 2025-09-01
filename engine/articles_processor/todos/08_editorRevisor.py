#!/usr/bin/env python3
import os
import re
from termcolor import colored
import pyfiglet

MD_FOLDER = '.'

patterns = [
    r'\*\*\*.+?\*\*\*',               # triple asterisco
    r'\*\*.*\*.+?\*.*\*\*',           # bold con italica dentro
    r'^(#+\s.*\*.*\*\*.*)$',          # títulos con mezcla
]

def prompt_fix(original, problem):
    print("\nFrase completa:")
    print(colored(original, 'white', attrs=['bold']))
    print("Problema detectado:")
    print(colored(problem, 'red', attrs=['bold']))
    print("Opciones:")
    print("1) Reemplazar *problem* por comillas")
    print("2) Quitar *problem* sin reemplazo")
    print("3) Editar manualmente la frase")
    print("4) Dejar como está")
    print("5) Saltar al siguiente archivo")

    choice = input("Elige opción (1/2/3/4/5): ").strip()
    return choice

def process_file(path):
    # Mostrar nombre de archivo gigante en cyan
    fig_text = pyfiglet.figlet_format(os.path.basename(path))
    print(colored(fig_text, 'cyan'))

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    skip_file = False

    for line in lines:
        if skip_file:
            new_lines.append(line)
            continue

        modified_line = line
        for pat in patterns:
            for m in re.finditer(pat, modified_line):
                choice = prompt_fix(modified_line, m.group(0))
                if choice == '1':
                    modified_line = modified_line.replace(m.group(0), f'"{m.group(0).strip("*")}"')
                    changed = True
                elif choice == '2':
                    modified_line = modified_line.replace(m.group(0), m.group(0).strip("*"))
                    changed = True
                elif choice == '3':
                    print("Introduce la frase corregida (Enter para mantener):")
                    new = input("> ")
                    modified_line = new if new else modified_line
                    changed = True
                elif choice == '4':
                    pass  # dejar como está
                elif choice == '5':
                    skip_file = True
                    print(colored(f"Saltando archivo: {path}", 'yellow'))
                    break
        new_lines.append(modified_line)

    if changed and not skip_file:
        print(f"\nGuardar cambios en {path}? (s/n)")
        save = input("> ").strip().lower()
        if save == 's':
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(colored(f"Archivo guardado: {path}", 'green'))
        else:
            print(colored(f"Cambios descartados: {path}", 'yellow'))

def main():
    # Listar archivos article_XXX_eng.md en orden numérico
    files = [f for f in os.listdir(MD_FOLDER) if re.match(r'article_(\d+)_eng\.md', f)]
    files.sort(key=lambda x: int(re.match(r'article_(\d+)_eng\.md', x).group(1)))

    for fname in files:
        process_file(os.path.join(MD_FOLDER, fname))

if __name__ == "__main__":
    main()
