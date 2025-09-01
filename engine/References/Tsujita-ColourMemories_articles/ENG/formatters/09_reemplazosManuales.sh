#!/bin/sh

for f in *.md; do
    changed=0

    # Reemplazos manuales exactos
    if grep -q '\*Space Battleship Yamato\*' "$f"; then
        sed -i 's/\*Space Battleship Yamato\*/"Space Battleship Yamato"/g' "$f"
        changed=1
    fi

    if grep -q '\*Robotex\*' "$f"; then
        sed -i 's/\*Robotex\*/"Robotex"/g' "$f"
        changed=1
    fi

    # <<< # Espacio para futuras adiciones manuales >>>

    if [ $changed -eq 1 ]; then
        echo "Reemplazos aplicados en: $f"
    fi
done
