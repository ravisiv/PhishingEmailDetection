import yaml
import sys
import shutil
import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import phdcommon as conf
from sklearn.metrics import classification_report
import numpy as np

#Main Method
datafile = sys.argv[1]
if datafile == None:
    exit(0)
#modeldir = conf.get_target("modeldir")
modeldir = "/Users/ravis/Library/CloudStorage/OneDrive-SouthernMethodistUniversity/CapstoneA/Data/FINALDATA/models"

header_df = pd.read_csv(datafile)
headers = header_df["header"]
print("columns", len(header_df.columns))

ext_header_model = tf.keras.models.load_model(f"{modeldir}/header_NN")
if ext_header_model == None:
	exit(0)

predicted_val = []
columns = header_df.columns.tolist()

header_df = header_df.drop(columns[columns.index("header")], axis=1)
#header_df = header_df.drop(columns[columns.index("status")], axis=1)

X = header_df

#Scale the data using standard scalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

 #Predict using headermodel
y_pred = ext_header_model.predict(X_scaled)
header_df["header_predicted"] = y_pred
#header_df["header"] = headers
dir_name = os.path.dirname(datafile)
bname = os.path.basename(datafile)
outfile = f"{dir_name}/predicted_{bname}"
#Save
header_df.drop(columns=header_df.columns[0],
        axis=1,
        inplace=True)
header_df.to_csv(outfile,index=False)
print("Email header features with predicted phishing using external data model")
print("Saved the predicted email header data:",outfile)