#!/bin/sh

for f in *.md; do
    if grep -q '\bSTAC\b' "$f"; then
        echo "Encontrado en: $f"
    fi
done
