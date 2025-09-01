#!/bin/sh
# double emptyline remover

for f in *.md; do

    sed -i '/^$/N;/^\n$/D' "$f"

    echo "FIXED at: $f"
    
done
