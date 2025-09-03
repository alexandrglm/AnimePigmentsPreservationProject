#!/bin/sh

# las fechas, juan, las fechas

for f in *.md; do
    lastline=$(tail -n 1 "$f")

    # if end = (x)
    if printf "%s" "$lastline" | grep -Eq '\([^)]*\)$'; then

        # las italicas no van a entrar asi
        if printf "%s" "$lastline" | grep -Eq '^\*.*\)$'; then

            :

        else

            # se le italiza
            new="*${lastline}*"
            sed -i "\$s|.*|$new|" "$f"
        fi
    else
        echo "[WARN] $f has DIFFERENT ENDING!!!"
    fi
done
