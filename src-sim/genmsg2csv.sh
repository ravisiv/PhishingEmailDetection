#!/bin/bash

conf_file="conf/phishing.yaml"

ROOT_DIR=$(grep 'rootdir' ${conf_file} | sed 's/^.*: //')
MSG_DIR=$(grep 'msgdir' ${conf_file} | sed 's/^.*: //')

MSG_PATH=${ROOT_DIR}/${MSG_DIR}
echo $MSG_PATH

echo "Extracting CSVs"
for f in ${MSG_PATH}/*; do
    if [ -d "$f" ]; then
      python3 msg2csv.py $f
    fi
done
