#!/bin/sh

# kicadCommand.sh index.md

CMDFILE=$1

KIPRJ_DIR_ARRAY=${KIPRJ_DIR_ARRAY:-"hardware*"}
KIPRJ_NAME=${KIPRJ_NAME:-"main"}

for KIPRJ_DIR in $KIPRJ_DIR_ARRAY; do
  TARGET_DIR=`realpath ${KIPRJ_DIR}`
  if [ ! -f "${TARGET_DIR}/${KIPRJ_NAME}.kicad_pro" ]; then
    echo "WARN: Skip folder ${TARGET_DIR}";
    continue;
  fi;
  cat $CMDFILE | sed -i 's/\r//g' | grep "^/" | while read line || [[ -n $line ]];
  do
    set -- $line; 
    case $1 in
      "/CHG")
        if [[ -n "$2" && -n "$3" && -z "$4" ]]; then
          echo "CHG $2 -> $3";
          sed -i -z "s@\"$3\"@\"$2\"@g" ${TARGET_DIR}/*.kicad_*
        else
          echo "Incorrect number of arguments: $1"
        fi
        ;;
      *)
        echo "Unknown operation: $1"
        ;;
    esac
  done
done;