#!/bin/sh

REPORT="reporte_estilos.md"
echo "# Reporte de estilos Markdown" > "$REPORT"
echo "" >> "$REPORT"

for f in *.md; do
    echo "## Archivo: $f" >> "$REPORT"

    # Líneas con bold + italic juntos (**_..._** o _**...**_)
    grep -En '(\*\*\*.+\*\*\*|_\*\*.+\*\*_|_\*\*.+\*\*_)' "$f" >> "$REPORT"

    # Líneas con doble asterisco y un asterisco adyacente (ej. **bold* o *italic**)
    grep -En '(\*\*.*\*|\*.*\*\*)' "$f" >> "$REPORT"

    # Líneas con guiones, más de 3 consecutivos (posible separador confuso)
    grep -En '^---{2,}$' "$f" >> "$REPORT"

    # Líneas con comillas y asteriscos mezclados de forma sospechosa
    grep -En '["].*[*_].*["]' "$f" >> "$REPORT"

    # Si no hay coincidencias, avisar
    if ! grep -Eq '(\*\*\*.+\*\*\*|_\*\*.+\*\*_|_\*\*.+\*\*_)|(\*\*.*\*|\*.*\*\*)|^---{2,}$|["].*[*_].*["]' "$f"; then
        echo "Sin incidencias detectadas" >> "$REPORT"
    fi

    echo "" >> "$REPORT"
done

echo "Reporte generado en $REPORT"
