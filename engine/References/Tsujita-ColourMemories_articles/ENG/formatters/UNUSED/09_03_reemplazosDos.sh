#!/bin/sh

for f in *.md; do
    changed=0

    # Reemplazos manuales exactos

    sed -i -e 's/\*Taichi Senjimon\*/"Taichi Senjimon"/g' \
           -e 's/\*Haikara-san ga Touru\*/"Haikara-san ga Touru"/g' \
           -e 's/\*Maison Ikkoku\*/"Maison Ikkoku"/g' \
           -e 's/\*Muppet Babies\*/"Muppet Babies"/g' \
           -e 's/\*Transformers\*/"Transformers"/g' \
           -e 's/\*GeGeGe no Kitaro: Yokai Daisenso\*/"GeGeGe no Kitaro: Yokai Daisenso"/g' \
           -e 's/\*\*Itasaka-san\*\*/"Itasaka-san"/g' \
           -e 's/\*Kitaro\*/"Kitaro"/g' \
           -e 's/\*Hokuto no Ken\*/"Hokuto no Ken"/g' \
           -e 's/\*Theatrical Hokuto no Ken Film Book\*/"Theatrical Hokuto no Ken Film Book"/g' \
           -e 's/\*Saint Seiya\*/"Saint Seiya"/g' "$f" && changed=1

    # <<< # Espacio para futuras adiciones manuales >>>

    if [ $changed -eq 1 ]; then
        echo "Reemplazos aplicados en: $f"
    fi
done
