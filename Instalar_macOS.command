#!/bin/bash
# Instalar el español y activar las actualizaciones compatibles al abrir.
cd "$(dirname "$0")" || exit 1
./pvz-fusion instalar
RESULT=$?
if [ "$RESULT" -eq 0 ]; then
    printf '\nInstalado. Usa pvz-fusion en la terminal o abre PvZ Fusion desde Aplicaciones.\n'
fi
printf '\nPulsa Intro para cerrar.'
read -r
exit "$RESULT"
