#!/bin/sh

# buscasimbolos extraños

for f in *.md; do

    if grep -q '■' "$f"; then

        echo "Found: $f"
    fi


done
