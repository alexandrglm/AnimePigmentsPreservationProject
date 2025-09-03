#!/bin/sh
# reemplaza simbolos extraños por lo más idoneo, estilos heaidng 4

for f in *.md; do

    if grep -q '■' "$f"; then

        sed -i 's/■/#### /g' "$f"
        echo "FIXES APPLIED at: $f"

    fi
done
