#!/bin/bash

conf_file="conf/phishing.yaml"

MSG_DIR=$(grep 'msgdir' ${conf_file} | sed 's/^.*: //')
DATA_DIR=$(grep 'datadir' ${conf_file} | sed 's/^.*: //')
MASTER_HEADER_FILE=$(grep 'masterheaders' ${conf_file} | sed 's/^.*: //')
MASTER_URL_FILE=$(grep 'masterurls' ${conf_file} | sed 's/^.*: //')
MASTER_TD_FILE=$(grep 'mastertopdomains' ${conf_file} | sed 's/^.*: //')
MASTER_SD_FILE=$(grep 'mastersubdomains' ${conf_file} | sed 's/^.*: //')
MASTER_SUFFIX_FILE=$(grep 'mastersuffix' ${conf_file} | sed 's/^.*: //')

echo "Extracting URLs, topdomains, subdomains, suffix"
for f in ${MSG_DIR}/*; do
    if [ -d "$f" ]; then
      python3 extract_url.py $f
    fi
done

#Sorting and Create Master data
echo "Creating master headers"
find $DATA_DIR/digest -name headers.csv -exec cat {} + | sort -u > $MASTER_HEADER_FILE

echo "Creating master urls"
find $DATA_DIR/digest -name urls.csv -exec cat {} + | sort -u > $MASTER_URL_FILE

echo "Creating master topdomains"
find $DATA_DIR/digest -name topdomains.csv -exec cat {} + | sort -u > $MASTER_TD_FILE

echo "Creating master subdomains"
find $DATA_DIR/digest -name subdomains.csv -exec cat {} + | sort -u > $MASTER_SD_FILE

echo "Creating master suffix"
find $DATA_DIR/digest -name suffix.csv -exec cat {} + | sort -u > $MASTER_SUFFIX_FILE
