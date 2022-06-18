import yaml
import sys
import shutil
import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import phdcommon as conf


#Main Method
datafile = sys.argv[1]
if datafile == None:
    exit(0)
modeldir = conf.get_target("modeldir")

url_df = pd.read_csv(datafile)
urls = url_df["url"]
print("columns", len(url_df.columns))

bert_model = tf.keras.models.load_model(f"{modeldir}/bert/bert_model")
if bert_model == None:
	exit(0)

predicted_val = []
columns = url_df.columns.tolist()

url_df = url_df.drop(columns[columns.index("url")], axis=1)
#url_df = url_df.drop(columns[columns.index("status")], axis=1)

X = url_df['bodytext']

#Scale the data using standard scalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

 #Predict using urlmodel
y_pred = bert_model.predict(X_scaled)
url_df["url_predicted"] = y_pred
url_df["url"] = urls
dir_name = os.path.dirname(datafile)
bname = os.path.basename(datafile)
outfile = f"{dir_name}/predicted_{bname}"
#Save
url_df.drop(columns=url_df.columns[0],
        axis=1,
        inplace=True)
url_df.to_csv(outfile,index=False)
print("Email url features with predicted phishing using external data model")
print("Saved the predicted email url data:",outfile)