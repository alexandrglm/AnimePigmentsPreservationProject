#!/bin/sh

for f in *.md; do

    if tail -n +3 "$f" | grep -q '^#'; then

        echo "TITLES FOUND: $f"
    fi
done
