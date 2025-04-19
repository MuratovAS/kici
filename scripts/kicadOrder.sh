#!/bin/sh

# PRJ_REPO="repo" kicadOrder.sh index.md

ISSUEPATH=$1

export PRJ_REPO=${PRJ_REPO:-"repo"}
export OUTPUT_DIR=${OUTPUT_DIR:-"build"}
export BOMVERIFIERARG=${BOMVERIFIERARG:-"-lcsc=sku -lcscRW=pn"}
export PREVCOLUMN=${PREVCOLUMN:-"qty,pn,lcsc,lcsc_sku,lcsc_consistent,lcsc_stock"}

# github for some reason pushes the \r character in the text
sed -i 's/\r//g' $ISSUEPATH

PRJ_VERSION_CUR=`sed -n '7p' $ISSUEPATH`
KIPRJ_DIR_CUR=`sed -n '11p' $ISSUEPATH`

SMTTYPE=`sed -n '15p' $ISSUEPATH`
BOMAUTO=`sed -n '19p' $ISSUEPATH`
SMTQTY=`sed -n '23p' $ISSUEPATH`
BOMLIST=`cat $ISSUEPATH | sed 's/\`\`\`/@@@/g' | sed -n '/@@@extendedBom/,/@@@/p' | sed '/^@/d' | tr -s '\r\n' ' ' | sed 's/ //g'`

PRJ_VERSION_CUR=$(echo ${PRJ_VERSION_CUR} | sed 's/ //g');
KIPRJ_DIR_CUR=$(echo ${KIPRJ_DIR_CUR} | sed 's/ //g');

echo "INFO: PRJ_VERSION_CUR=$PRJ_VERSION_CUR"
echo "INFO: KIPRJ_DIR_CUR=$KIPRJ_DIR_CUR"
echo "INFO: SMTTYPE=$SMTTYPE"
echo "INFO: BOMAUTO=$BOMAUTO"
echo "INFO: SMTQTY=$SMTQTY"
echo "INFO: BOMLIST=$BOMLIST"

NAME=${PRJ_REPO}_${KIPRJ_DIR_CUR}_${PRJ_VERSION_CUR}

git config --global --add safe.directory '*'
git config --global advice.detachedHead false
git fetch --prune --unshallow --tags
git checkout $PRJ_VERSION_CUR

BOMVERIFIERARG="$BOMVERIFIERARG -qty=$SMTQTY" PRJ_VERSION=$PRJ_VERSION_CUR KIPRJ_DIR_ARRAY=$KIPRJ_DIR_CUR ./kicadStock.sh

SMTTYPENEG="both"
if [ "$SMTTYPE" = "top" ]; then SMTTYPENEG="bottom"; elif [ "$SMTTYPE" = "bottom" ]; then SMTTYPENEG="top"; elif [ "$SMTTYPE" = "both" ]; then SMTTYPENEG="no"; elif [ "$SMTTYPE" = "no" ]; then SMTTYPENEG="both"; fi
echo "INFO: Update SMTTYPENEG=$SMTTYPENEG"
        
if [ "$SMTTYPENEG" != "both" ]; then \
  BOMLIST=`cat ${OUTPUT_DIR}/${NAME}_cpl.csv | grep ",${SMTTYPENEG}$" | awk -F, '{print $1}' | tr -s '\r\n' ',' | sed 's/"//g'`${BOMLIST}; \
  echo "INFO: SMTTYPE: BOMLIST=$BOMLIST"; \
fi

if [ "$BOMAUTO" = "yes" ] && [ "$SMTTYPENEG" != "both" ]; then \
  BOMLIST=`python3 /tools/csvExtractor.py "${OUTPUT_DIR}/${NAME}_bom_stock.csv" "designator,lcsc_enough" | sed 's/,""$/,"False"/g' | grep "False" | sed "s/\",\"/\"@\"/g" | awk -F@ '{print $1}' | tr -s '\r\n' ',' | sed 's/"//g'`${BOMLIST}; \
  echo "INFO: BOMAUTO: BOMLIST=$BOMLIST"; \
fi

if [ "$BOMLIST" != "" ] && [ "$SMTTYPENEG" != "both" ]; then \
  BOMLIST=$(echo ${BOMLIST} | tr a-z A-Z); \
  echo "INFO: run bomExtractor.py"; \
  python3 /tools/bomExtractor.py "${OUTPUT_DIR}/${NAME}_bom_stock.csv" $BOMLIST \
  -o "${OUTPUT_DIR}/${NAME}_bom_stock_extract.csv"; \
fi