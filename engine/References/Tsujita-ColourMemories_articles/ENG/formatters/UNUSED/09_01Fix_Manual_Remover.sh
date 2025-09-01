#!/bin/sh
# NO continuara


for f in *.md; do

    if grep -Eq '^#### Continues to Episode [0-9]+$|^To be continued in Episode [0-9]+$|^Continued in Episode [0-9]+$|^## \*\*#### Continues to Episode [0-9]+\*\*$|^####  Continued in Episode [0-9]+$' "$f"; then

        sed -i -E \
            -e '/^#### Continues to Episode [0-9]+$/d' \
            -e '/^To be continued in Episode [0-9]+$/d' \
            -e '/^Continued in Episode [0-9]+$/d' \
            -e '/^## \*\*#### Continues to Episode [0-9]+\*\*$/d' \
            -e '/^####  Continued in Episode [0-9]+$/d' \
            "$f"

        echo "FIXES APPLIED at: $f"
    fi
done
