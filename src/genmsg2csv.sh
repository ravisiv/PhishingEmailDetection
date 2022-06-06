#!/bin/bash

conf_file="conf/phishing.yaml"

MSG_DIR=$(grep 'msgdir' ${conf_file} | sed 's/^.*: //')
DATA_DIR=$(grep 'datadir' ${conf_file} | sed 's/^.*: //')
MASTER_EMAIL_FILE=$(grep 'masteremails' ${conf_file} | sed 's/^.*: //')
COLUMNS_FILE=$(grep 'columnsfile' ${conf_file} | sed 's/^.*: //')

echo "Generating csv files from msg files"
for f in ${MSG_DIR}/*; do
    if [ -d "$f" ]; then
        python3 msg2csv.py $f
    fi
done

#Generating Master emails csv
find $DATA_DIR/digest -name emails.csv -exec cat {} + | sort -u > ${MASTER_EMAIL_FILE}.tmp
cat $COLUMNS_FILE ${MASTER_EMAIL_FILE}.tmp > ${MASTER_EMAIL_FILE} 
rm ${MASTER_EMAIL_FILE}.tmp
echo "Created master email csv: $MASTER_EMAIL_FILE"