#!/bin/bash

conf_file="conf/phishing.yaml"
MASTER_URLS_FILE=$(grep 'masterurls' ${conf_file} | sed 's/^.*: //')
EMAIL_STATS_FILE=$(grep 'masteremailurlstats' ${conf_file} | sed 's/^.*: //')

EXT_PHISHURLS_FILE=$(grep 'extphishurls' ${conf_file} | sed 's/^.*: //')
EXT_PHISHSTATS_FILE=$(grep 'extphishurl-stats' ${conf_file} | sed 's/^.*: //')


EXT_LEGIURLS_FILE=$(grep 'extlegiurls' ${conf_file} | sed 's/^.*: //')
EXT_LEGISTATS_FILE=$(grep 'extlegiurl-stats' ${conf_file} | sed 's/^.*: //')

EXT_MASTER_STATS_FILE=$(grep 'extmasterurl-stats' ${conf_file} | sed 's/^.*: //')

#echo "Generating URL features for email URLS"
#echo python3 feature_extractor.py $MASTER_URLS_FILE $EMAIL_STATS_FILE

#echo "Generating URL features for external URLs"
#python3 feature_extractor.py $EXT_PHISHURLS_FILE $EXT_PHISHSTATS_FILE  1

#python3 feature_extractor.py $EXT_LEGIURLS_FILE $EXT_LEGISTATS_FILE 0

#Create a master extdata
cp $EXT_PHISHSTATS_FILE $EXT_MASTER_STATS_FILE  
tail +2 $EXT_LEGISTATS_FILE >> $EXT_MASTER_STATS_FILE 
echo "Master external URL data generated: " $EXT_MASTER_STATS_FILE