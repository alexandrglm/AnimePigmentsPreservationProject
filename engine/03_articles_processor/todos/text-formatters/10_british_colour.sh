#!/bin/sh
for f in ./*.md; do
  [ -f "$f" ] || continue
  if grep -q '\bCOLOR\b' "$f"; then
    sed -i 's/\bCOLOR\b/COLOUR/g' "$f"
    echo "Modificado: $f"
  fi
done
