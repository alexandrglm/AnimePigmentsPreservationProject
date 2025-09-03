#!/bin/sh
# md_search_replace.sh
# Busca en ./*.md y opcionalmente reemplaza palabras exactas (coincidencia por palabra).

printf "Elige opción:\n 1) Buscar\n 2) Buscar y reemplazar\n> "
read opt

if [ "$opt" != "1" ] && [ "$opt" != "2" ]; then
  printf "Opción inválida\n" >&2
  exit 1
fi

printf "Escribe la palabra exacta a buscar:\n> "
read search

if [ -z "$search" ]; then
  printf "Cadena de búsqueda vacía\n" >&2
  exit 1
fi

# Opción 2 pide la palabra de reemplazo
if [ "$opt" = "2" ]; then
  printf "Escribe la palabra exacta de reemplazo:\n> "
  read replace
  if [ -z "$replace" ]; then
    printf "Reemplazo vacío\n" >&2
    exit 1
  fi
fi

# Buscar (palabra exacta). mostramos nombre de fichero y línea.
printf "\nResultados de la búsqueda (palabra completa):\n\n"
# grep con -w para palabra completa, -n para línea y -H para fichero
grep -Rnw --include="*.md" -e "$search" . || printf "No se encontraron coincidencias.\n"

# Si es opción 2, confirmamos y reemplazamos usando perl (in-place, portable)
if [ "$opt" = "2" ]; then
  printf "\n¿Confirmas reemplazar todas las coincidencias exactas de '%s' por '%s' en todos los .md? (y/n)\n> " "$search" "$replace"
  read conf
  case "$conf" in
    y|Y)
      # Reemplazo en todos los .md, usando límites de palabra (\b) y escaping seguro.
      find . -type f -name '*.md' -print0 | xargs -0 perl -pi -e "s/\\b\\Q$search\\E\\b/$replace/g"
      printf "Reemplazo completado.\n"
      ;;
    *) printf "Operación cancelada.\n" ;;
  esac
fi
