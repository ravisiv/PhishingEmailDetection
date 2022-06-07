#!/bin/bash

conf_file="conf/phishing.yaml"

#Predict for Email URLS from above model
EXT_URLSTATS_FILE=$(grep 'extmasterurl-stats' ${conf_file} | sed 's/^.*: //')
#Train URL NN with external known data
python3 URL_NN.py $EXT_URLSTATS_FILE


EMAIL_STATS_FILE=$(grep 'masteremailurlstats' ${conf_file} | sed 's/^.*: //')
echo "Predicting for email URLS from pretrained model"
python3 predictemailurls.py $EMAIL_STATS_FILE

MASTER_EMAIL_DATA=$(grep 'masteremails' ${conf_file} | sed 's/^.*: //')
PREDICTED_URL_STATS=$(grep 'p_emailurlstats' ${conf_file} | sed 's/^.*: //')

echo "Populating with predicted valuesl of email URLS from pretrained model"
python3 fillpredictedurl.py $MASTER_EMAIL_DATA $PREDICTED_URL_STATS
