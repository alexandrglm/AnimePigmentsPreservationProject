#!/bin/sh

for f in *.md; do
    # Comprobamos que haya al menos 2 líneas
    line_count=$(wc -l < "$f")
    if [ "$line_count" -lt 2 ]; then
        continue
    fi

    # Obtenemos la segunda línea
    second_line=$(sed -n '2p' "$f")

    # Verificamos que empiece con ##
    if echo "$second_line" | grep -q '^##'; then
        # Eliminamos ** al inicio y al final, si existen
        cleaned_line=$(echo "$second_line" | sed -E 's/^##\s*\*\*/## /; s/\*\*\s*$//')

        # Reemplazamos la segunda línea en el archivo
        sed -i "2s|.*|$cleaned_line|" "$f"
        echo "Limpieza de ** en segunda línea: $f"
    fi
done
