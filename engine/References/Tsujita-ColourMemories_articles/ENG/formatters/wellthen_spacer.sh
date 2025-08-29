#!/bin/sh
set -eu

for f in ./*.md; do
  awk '{
    sub(/\r$/,"")
    if ($0 ~ /^(Well then\.|Now then\.)$/) {
      print
      print ""
      print "---"
      print ""
      drop=1
      next
    }
    if (drop && $0=="") { drop=0; next }
    drop=0
    print
  }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
