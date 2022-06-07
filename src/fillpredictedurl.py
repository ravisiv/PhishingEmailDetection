import os
import sys
import pandas as pd

#Main Method
datafile = sys.argv[1]
masteremailurl = sys.argv[2]
url_df = pd.read_csv(datafile)
url_columns = list(url_df.columns)

#Load Master URL
masteremail_df = pd.read_csv(masteremailurl)
masteremail_cols = list(masteremail_df.columns)
predict_column = masteremail_cols.index("url_predicted")
predict_max_for_one = 0.6

predict_row = []
index = 0
for row in url_df.iterrows():
    predict_count = 0
    for key in row[1].keys():
        if "url" in key:
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
    predict_row.append(predict_count)
    print(index,end="\r")
    index +=1

url_df["urlpredict"] = predict_row
dir_name = os.path.dirname(datafile)
outfile = f"{dir_name}/allemail_p.csv"

url_df.to_csv(outfile)
