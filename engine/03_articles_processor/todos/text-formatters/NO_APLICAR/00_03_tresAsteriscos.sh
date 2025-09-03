#!/bin/sh

for f in *.md; do
    if grep -q '\*\*\*.*\*\*\*' "$f"; then
        sed -i -E 's/\*\*\*(.+?)\*\*\*/"\1"/g' "$f"
        echo "Reemplazado ***...*** por \"...\" en: $f"
    fi
done
