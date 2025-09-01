#!/bin/sh
# En teoria ya no hace falta, el motor ya aplica bien italics+bolds


for f in *.md; do

    line_count=$(wc -l < "$f")

    if [ "$line_count" -lt 2 ]; then

        continue
    fi


    second_line=$(sed -n '2p' "$f")

    if echo "$second_line" | grep -q '^##'; then

        cleaned_line=$(echo "$second_line" | sed -E 's/^##\s*\*\*/## /; s/\*\*\s*$//')


        sed -i "2s|.*|$cleaned_line|" "$f"
        echo "FIXED ** here: $f"
    fi
done
