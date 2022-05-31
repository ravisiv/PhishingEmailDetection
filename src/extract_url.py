import traceback
import os
import email
from email.parser import HeaderParser
from urlextract import URLExtract
import base64
import sys
import csv
import tldextract
import hashlib
import yaml
from pathlib import Path

conf_file = "conf/phishing.yaml"

def get_domain(urlwithdomain):
    res = tldextract.extract(urlwithdomain)
    if res[2] == '':
        return res[0], res[1], res[2]
    else:
        return res[0], res[1] + "." + res[2], res[2]


def get_sha1_hash(data):
    BUF_SIZE = 67108864  
    sha1 = hashlib.sha1()
    sha1.update(data.encode())
    return sha1.hexdigest()

def save_to_file(data,filename):
    with open(filename, 'w', newline='') as myfile:
        (csv.writer(myfile, quoting=csv.QUOTE_ALL)
         ).writerows([[i] for i in data])

def get_target_dir(dirtype):
	default_dir = "messages"
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data[dirtype]
		except yaml.YAMLError as exc:
			return default_dir
	return default_dir

def get_headers(msg):
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())
    all_headers = set()
    for h in headers.items():
        all_headers.add(h[0])

    return all_headers


#Main method
data_path = sys.argv[1]
cur_files =  next(os.walk(data_path))[2]

#get msg type
all_headers = set()
all_urls = set()
all_strip_urls = set()
all_topdomains = set()
all_subdomains = set()
all_suffix = set()
for file in cur_files:
    with open(f"{data_path}/{file}") as f:
        f_realpath = os.path.realpath(f.name)
        if not ".msgtype" in f.name:
            try:
                print(f.name)
                msg = email.message_from_file(f)
                headers = get_headers(msg)
                all_headers.update(headers)
                f.seek(0)
                for line in f.readlines():
                    extractor = URLExtract()
                    for chunks in line.split(" "):
                        urls = extractor.find_urls(chunks)
                        all_urls.update(urls)
                for each_url in list(all_urls):
                    strip_url = each_url.lower().strip().replace(
                        "\\n", "").replace("\\t", "").replace("nhttp", "http")
                    sdomain, tdomain, suffix = get_domain(strip_url)

                    if not strip_url.startswith("http"):
                        strip_url = "http://" + strip_url
                    if strip_url.startswith("@"):
                        strip_url = "http://" + strip_url[1:]
                    if sdomain:
                        all_subdomains.add(sdomain)
                    if tdomain:
                        all_topdomains.add(tdomain)
                    if suffix:
                        all_suffix.add(suffix)
                    if each_url:
                        all_strip_urls.add(strip_url)

            except Exception as e:
                print("--------------------------------starting------------")
                print(traceback.format_exc())
                print("--------------------------------ending------------")
                continue

filename_digest = get_sha1_hash("".join(cur_files))
conf_dir = get_target_dir("urldir")
target_dir = f"{conf_dir}/{filename_digest}"
Path(target_dir).mkdir(parents=True, exist_ok=True)

save_to_file(list(all_headers),f"{target_dir}/headers.csv")
save_to_file(list(all_strip_urls),f"{target_dir}/urls.csv")
save_to_file(list(all_topdomains),f"{target_dir}/topdomains.csv")
save_to_file(list(all_subdomains),f"{target_dir}/subdomains.csv")
save_to_file(list(all_suffix),f"{target_dir}/suffix.csv")

