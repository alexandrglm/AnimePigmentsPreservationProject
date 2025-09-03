#!/bin/sh
for f in ./*.md; do
  [ -f "$f" ] || continue
  matches=$(grep -oE '\w*(ize|izing)\w*' "$f" | sort -u)
  if [ -n "$matches" ]; then
    echo "Archivo: $f"
    echo "$matches" | sed 's/^/  /'
  fi
done
