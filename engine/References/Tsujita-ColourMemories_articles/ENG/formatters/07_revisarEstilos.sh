#!/bin/sh

REPORT="POSSIBLE-ISSUE-report.md"

echo "# POSSIBLE ISSUES TO FIX" > "$REPORT"
echo "" >> "$REPORT"

for f in *.md; do

    echo "## FILE: $f" >> "$REPORT"

    # **bold with *italics* in the same place**
    grep -En '(\*\*\*.+\*\*\*|_\*\*.+\*\*_|_\*\*.+\*\*_)' "$f" >> "$REPORT"

    # **example* or *example**
    grep -En '(\*\*.*\*|\*.*\*\*)' "$f" >> "$REPORT"

    # more than THREE ---
    grep -En '^---{2,}$' "$f" >> "$REPORT"

    # problem "* *"
    grep -En '["].*[*_].*["]' "$f" >> "$REPORT"

    # else No Concide ninguna
    if ! grep -Eq '(\*\*\*.+\*\*\*|_\*\*.+\*\*_|_\*\*.+\*\*_)|(\*\*.*\*|\*.*\*\*)|^---{2,}$|["].*[*_].*["]' "$f"; then
        echo "No problems found" >> "$REPORT"
    fi

    echo "" >> "$REPORT"
done
echo ""
echo "REPORT SAVED -> $REPORT"
echo "D0NE!"
