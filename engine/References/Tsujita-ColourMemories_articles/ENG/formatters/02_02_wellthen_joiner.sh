#!/bin/sh
for f in ./*.md; do
  [ -f "$f" ] || continue
  awk '
  {
    if (($0=="Well then." || $0=="Now then." || $0=="Anyway.") && prev=="") {
      # Línea anterior vacía: imprimir solo la frase
      print $0
      prev=""  # reset
    } else {
      if (NR>1) print prev
      prev=$0
    }
  }
  END { if (prev!="") print prev }
  ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
