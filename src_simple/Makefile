#!/bin/bash

#Build All

#Split mbox files as msg files
all: final_ensemble
	echo "Completed"

mbox_msg: greet
	echo ./genmbox2msg.sh

#Extract URLs  and other metadata from msgs
extract_urls: msg_csv
	echo ./genextracturl.sh

#Generate CSV files from msg files
msg_csv: mbox_msg
	echo ./genmsg2csv.sh

#Build Exernal URL data
url_features: msg_csv
	echo ./genurlfeatures.sh

#Train Neural Network from External data and fill the predicted values for email URLs
ext_url_nn: url_features extract_urls
	echo ./exturlNN.sh

bert_models:
	#./genbertmodels.sh

image_models:
	#./genimagemodels.sh

#./genurltrustnetmodels.sh

#Do the final ensemble
final_ensemble: ext_url_nn
	echo ./buildfinalensemble.sh

greet: 
	echo "Building Darth..."
