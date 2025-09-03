#!/bin/sh

for f in *.md; do
    # Verificar si hay líneas que empiecen con # desde la línea 3 en adelante
    if tail -n +3 "$f" | grep -q '^#'; then
        echo "Título encontrado después de línea 2 en: $f"
    fi
done
