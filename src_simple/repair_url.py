import pandas as pd
import sys
import os

datafile = sys.argv[1]

url_df = pd.read_csv(datafile)


def sanitize_url(surl: str):
    if surl.startswith("@"):
        surl = surl[1:]

    try:
        ip_add = ipaddress.ip_address(surl)
        surl = f"http://{surl}"
    except:
        pass

    if surl.startswith("nhttps://"):
        surl = surl[1:]

    if surl.startswith("nhttp://"):
        surl = surl[1:]

    if not surl.startswith("http"):
        surl = f"http://{surl}"

    return surl


all_urls = []
index= 1
for row in url_df.iterrows():
    trow = row[1]
    url = trow['url']
    url = sanitize_url(url)
    all_urls.append(url)
    print(index, end="\r")
    index += 1

url_df['url'] = all_urls

dir_name = os.path.dirname(datafile)
b_name = os.path.basename(datafile)
fname = os.path.splitext(b_name)[0]
target_file = f"{dir_name}/{fname}_repaired.csv"
url_df.to_csv(target_file)
