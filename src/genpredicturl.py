import yaml
import sys
import shutil
import os
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
conf_file = "conf/phishing.yaml"

def get_target_dir(dirtype):
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data[dirtype]
		except yaml.YAMLError as exc:
			return default_dir
		if stream:
			stream.close()
	return default_dir

#Main Method
datafile = sys.argv[1]
if datafile == None:
    exit(0)
modeldir = get_target_dir(dirtype="modeldir")

#Copy file to mem
bname = os.path.basename(datafile)
memname = f"/Users/ravis/Downloads/tmp/shm/{bname}"
shutil.copyfile(datafile, memname )
url_df = pd.read_csv(memname)
urls = url_df["url"]
print("columns", len(url_df.columns))

#Load Model
modeldir="/Users/ravis/Downloads/tmp"

modeldir = "/Users/ravis/Library/CloudStorage/OneDrive-SouthernMethodistUniversity/CapstoneA/Code/Models/URL_NN_Modeljune2"
ext_url_model = tf.keras.models.load_model(f"{modeldir}")
if ext_url_model == None:
	exit(0)

predicted_val = []
columns = url_df.columns.tolist()

url_df = url_df.drop(columns[columns.index("url")], axis=1)
url_df = url_df.drop(columns[columns.index("status")], axis=1)

X = url_df

#Scale the data using standard scalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

 #Predict using urlmodel
y_pred = ext_url_model.predict(X_scaled)
url_df["url_predicted"] = y_pred
url_df["url"] = urls
print(url_df["url_predicted"])
dir_name = os.path.dirname(datafile)
bname = os.path.basename(datafile)
outfile = f"{dir_name}/predicted_{bname}"
#Save
url_df.drop(columns=url_df.columns[0],
        axis=1,
        inplace=True)
url_df.to_csv(outfile,index=False)