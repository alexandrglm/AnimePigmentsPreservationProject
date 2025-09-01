#!/bin/bash
# Only remove line 2 if it's empty, preserves all other content

echo "Processing articles start..."

for file in *.md; do

if [[ -f "$file" ]]; then

        echo "Checking: $file"
        second_line=$(sed -n '2p' "$file")

        if [[ -z "$(echo "$second_line" | tr -d '[:space:]')" ]]; then

            echo "   ... Removing empty second line..."
            sed -i '2d' "$file"


        else
            echo "  [WARN] 2nd line has content!"
        fi

    fi
done

echo "D0NE!"
