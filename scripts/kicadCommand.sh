#!/bin/bash

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
  cat $CMDFILE | sed 's/\r//g' | grep "^/" | while read line || [[ -n $line ]];
  do
    set -- $line; 
    case $1 in
      "/CHG")
        if [[ -n "$2" && -n "$3" && -z "$4" ]]; then
          echo "CHG $2 -> $3 in '${TARGET_DIR}/*.kicad_*'";
          sed -i -z "s@\"$2\"@\"$3\"@g" ${TARGET_DIR}/*.kicad_*
        else
          echo "Incorrect number of arguments: $1"
        fi
        ;;
      "/PROPHIDE")
        if [[ -n "$2" && -z "$3" ]]; then
          echo "PROPHIDE $2 in '${TARGET_DIR}/*.kicad_sch'";
          for SCH_FILE in ${TARGET_DIR}/*.kicad_sch; do
            python3 /tools/schPropHide.py ${SCH_FILE} $2 yes
          done
        else
          echo "Incorrect number of arguments: $1"
        fi
        ;;
      "/PROPEDIT")
        if [[ -n "$2" && -n "$3" && -n "$4" && -n "$5" && -z "$6"  ]]; then
          echo "PROPEDIT $2 in '${TARGET_DIR}/*.kicad_sch'";
          for SCH_FILE in ${TARGET_DIR}/*.kicad_sch; do
            python3 /tools/schPropEdit.py ${SCH_FILE} --search_name $2 --search_value $3 --change_name $4 --change_value $5
          done
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