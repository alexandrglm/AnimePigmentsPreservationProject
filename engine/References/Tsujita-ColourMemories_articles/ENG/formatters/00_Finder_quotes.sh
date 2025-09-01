#!/bin/sh

for f in *.md; do
    if grep -q '^>' "$f"; then
        echo "QUOTES FOUND: $f"
    fi
done

