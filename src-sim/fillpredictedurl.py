import os
import sys
import pandas as pd
import numpy 

#Main Method
datafile = sys.argv[1]
masteremailurl = sys.argv[2]
url_df = pd.read_csv(datafile)
url_columns = list(url_df.columns)

#Load Master URL
masteremail_df = pd.read_csv(masteremailurl)
masteremail_cols = list(masteremail_df.columns)
predict_column = masteremail_cols.index("url_predicted")
predict_max_for_one = 0.60

predict_row = []
actual_predict_row =[]
index = 0
how_many_flagged = 0
for row in url_df.iterrows():
    predict_count = 0
    actual_predict_val = []
    for key in row[1].keys():
        if "topdomain" in key:
            url_vector = 0
            try:
                url_vector = int(row[1][key])
            except:
                url_vector=0
            predicted_val = 0
            if url_vector > 0:
                predicted_val = 0
                try: 
                    predicted_val = masteremail_df.loc[url_vector].iat[predict_column]
                except:
                    predicted_val = 0
            if float(predicted_val) > predict_max_for_one:
                predict_count+=1
            actual_predict_val.append(float(predicted_val))
    predict_row.append(predict_count)
    if len(actual_predict_val) > 0:
        actual_predict_row.append(numpy.average(actual_predict_val))
    else:
        actual_predict_row.append(0)
    if predict_count > 1:
        how_many_flagged += 1
    print(index,end="\r")
    index +=1

url_df["urlpredict"] = predict_row
url_df["actualurlpredict"] = actual_predict_row
dir_name = os.path.dirname(datafile)
bname = os.path.basename(datafile)
outfile = f"{dir_name}/{bname}_p.csv"
url_df.to_csv(outfile, index=False)
print("Saved in ", outfile)
print("predicted value for 1", how_many_flagged)
