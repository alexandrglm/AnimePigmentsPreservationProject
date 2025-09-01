#!/bin/sh

for f in *.md; do
    if grep -q '# \*\*Color Design Notes \[Tsujita Kunio\]\*\*' "$f"; then

        sed -i 's/# \*\*Color Design Notes \[Tsujita Kunio\]\*\*/# Color Design Notes [Tsujita Kunio]/g' "$f"

        echo "Article-Title FIXED: $f"

    fi

done

echo ""
echo "D0NE!"
