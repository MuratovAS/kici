#!/bin/sh

KIPRJ_DIR=${KIPRJ_DIR:-"hardware*"}
KIPRJ_NAME=${KIPRJ_NAME:-"main"}
RETURNCODE=0

while getopts 'ed' OPTION; do  
  for arg in $KIPRJ_DIR; do
    case "$OPTION" in
      e)
        echo "Checking (ERC): ${arg}"; \
        kicad-cli sch erc --severity-error --exit-code-violations ${arg}/${KIPRJ_NAME}.kicad_sch -o ${arg}/${KIPRJ_NAME}-erc.rpt || RETURNCODE=1
        cat ${arg}/${KIPRJ_NAME}-erc.rpt
        rm ${arg}/${KIPRJ_NAME}-erc.rpt
        ;;
      d)
        echo "Checking (DRC): ${arg}"; \
        kicad-cli pcb drc --schematic-parity --severity-error --exit-code-violations ${arg}/${KIPRJ_NAME}.kicad_pcb -o ${arg}/${KIPRJ_NAME}-drc.rpt || RETURNCODE=1
        cat ${arg}/${KIPRJ_NAME}-drc.rpt
        rm ${arg}/${KIPRJ_NAME}-drc.rpt
        ;;
    esac
  done
done
shift "$(($OPTIND -1))"

exit $RETURNCODE