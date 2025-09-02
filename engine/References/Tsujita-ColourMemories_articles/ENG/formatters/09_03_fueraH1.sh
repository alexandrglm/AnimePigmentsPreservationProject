#!/bin/sh
for f in ./*.md; do
  [ -f "$f" ] || continue
  sed -i '1{s/\r$//; /^# Color Design Notes \[Tsujita Kunio\]$/d}' "$f"
done
