#!/bin/sh

for f in *.md; do
    if grep -q '^>' "$f"; then
        echo "Citas encontradas en: $f"
    fi
done
