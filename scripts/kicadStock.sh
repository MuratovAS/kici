#!/bin/sh

# BOMVERIFIERARG="-qty=1 -lcsc=sku -lcscRW=pn -promelec -elitan" PREVCOLUMN="qty,pn,lcsc,lcsc_sku,lcsc_consistent,lcsc_stock,promelec_consistent,promelec_stock,elitan_consistent,elitan_enough" ./kicadStock.sh

PRJ_VERSION=${PRJ_VERSION:-"v0.0.0-def"}
PRJ_REPO=${PRJ_REPO:-"repo"}
KIPRJ_DIR_ARRAY=${KIPRJ_DIR_ARRAY:-"hardware*"}

KIPRJ_NAME=${KIPRJ_NAME:-"main"}
OUTPUT_DIR=${OUTPUT_DIR:-"build"}

BOMVERIFIERARG=${BOMVERIFIERARG:-"-lcsc=sku -lcscRW=pn"}
PREVCOLUMN=${PREVCOLUMN:-"qty,pn,lcsc,lcsc_sku,lcsc_consistent,lcsc_stock"}

# USERAGENTURL=

if [ -n "$USERAGENTURL" ]; then
  export USERAGENT=`wget -q -O - ${USERAGENTURL}`
  echo "INFO: User-Agent:$USERAGENT"
fi

mkdir -p $OUTPUT_DIR
OUTPUT_DIR=`realpath $OUTPUT_DIR`

for KIPRJ_DIR in $KIPRJ_DIR_ARRAY; do

  NAME=${PRJ_REPO}_${KIPRJ_DIR}_${PRJ_VERSION}
  TARGET_DIR=`realpath ${KIPRJ_DIR}`
  if [ ! -f "${TARGET_DIR}/${KIPRJ_NAME}.kicad_pro" ]; then
    echo "WARN: Skip folder ${TARGET_DIR}";
    continue;
  fi;
  
  ## BOM
  kicad-cli sch export bom ${TARGET_DIR}/${KIPRJ_NAME}.kicad_sch -o ${OUTPUT_DIR}/${NAME}_bom.csv \
   						 --preset general --format-preset CSV
  sed -i 's/"Value"/Comment/'         ${OUTPUT_DIR}/${NAME}_bom.csv
  sed -i 's/"Reference"/Designator/'  ${OUTPUT_DIR}/${NAME}_bom.csv
  # sed -i 's/"lcsc"/LCSC/'             ${OUTPUT_DIR}/${NAME}_bom.csv
  ## CPL
  kicad-cli pcb export pos   ${TARGET_DIR}/${KIPRJ_NAME}.kicad_pcb -o ${OUTPUT_DIR}/${NAME}_cpl.csv \
  						   --side both --format csv --units mm --use-drill-file-origin
  sed -i 's/Ref/Designator/' ${OUTPUT_DIR}/${NAME}_cpl.csv
  sed -i 's/PosX/Mid X/'     ${OUTPUT_DIR}/${NAME}_cpl.csv
  sed -i 's/PosY/Mid Y/'     ${OUTPUT_DIR}/${NAME}_cpl.csv
  sed -i 's/Rot,/Rotation,/' ${OUTPUT_DIR}/${NAME}_cpl.csv
  sed -i 's/Side/Layer/'     ${OUTPUT_DIR}/${NAME}_cpl.csv

  python3 /tools/bomVerifier.py ${OUTPUT_DIR}/${NAME}_bom.csv -o ${OUTPUT_DIR}/${NAME}_bom_stock.csv ${BOMVERIFIERARG}

  if [ -n "$PREVCOLUMN" ]; then
    python3 /tools/csvExtractor.py ${OUTPUT_DIR}/${NAME}_bom_stock.csv \
    $PREVCOLUMN  \
    | sed "s/\",\"/;/g" | sed 's/^"//' | sed 's/"$//' | sed "s/_consistent/_ok/g"| LANG=C sed "s/[\x80-\xFF]/#/g" | column -t -s ";" -R 2 -o ' | ' \
    | sed "s/True/✅  /g" | sed "s/False/❌   /g";
  fi
done
