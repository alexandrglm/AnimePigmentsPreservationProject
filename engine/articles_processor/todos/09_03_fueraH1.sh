#!/bin/sh
for f in ./*.md; do
  [ -f "$f" ] || continue
  sed -i '1{s/\r$//; /^# Colour Design Memories, by Kunio Tsujita$/d}' "$f"
done
