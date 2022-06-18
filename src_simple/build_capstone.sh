#!/bin/bash

#Build All

#Split mbox files as msg files
./genmbox2msg.sh

#Extract URLs  and other metadata from msgs
./genextracturl.sh

#Generate CSV files from msg files
./genmsg2csv.sh

#Build Exernal URL data
./genurlfeatures.sh

#Train Neural Network from External data and fill the predicted values for email URLs
./exturlNN.sh

#./genbertmodels.sh

#./genimagemodels.sh


#./genurltrustnetmodels.sh

#Do the final ensemble
./buildfinalensemble.sh

