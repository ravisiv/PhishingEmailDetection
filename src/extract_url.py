import traceback
import os
import base64
import sys
import yaml
from pathlib import Path
import email
import phdcommon as conf

#Main method
data_path = sys.argv[1]

#get msg type
all_headers = set()
all_urls = set()
all_topdomains = set()
all_subdomains = set()
all_suffix = set()
filecount = 0
all_names = ""
for subdir, dirs, files in os.walk(data_path):
    cur_files =  next(os.walk(subdir))[2]
    for file in cur_files:
        with open(f"{subdir}/{file}") as f:
            f_realpath = os.path.realpath(f.name)
            basename = os.path.basename(f_realpath)
            all_names = basename + all_names
            is_error = False
            if not basename.startswith("."):
                try:
                    msg = email.message_from_file(f)
                    headers = conf.get_headers(msg)
                    all_headers.update(headers)
                    f.seek(0)
                    urls,td,sd,suffix = conf.get_urls(msg.as_string())
                    all_urls.update(urls)
                    all_topdomains.update(td)
                    all_subdomains.update(sd)
                    all_suffix.update(suffix)
                except Exception as e:
                    print(str(e))
                    is_error = True

            else:
                is_error = True
            if is_error:
                print("Error-Skipped:", f_realpath)
            else:
                print("URL extracted:", f_realpath)

            f.close()
            filecount += 1

data_root_dir = conf.get_target("datadir")
data_dir = f"{data_root_dir}/digest"

digest = conf.get_sha1_hash(all_names)
target_dir = f"{data_dir}/{digest}"
Path(target_dir).mkdir(parents=True, exist_ok=True)

header_target = f"{target_dir}/headers.csv"
conf.save_to_file(list(all_headers),header_target)
print("Saved", header_target)

urls_target = f"{target_dir}/urls.csv"
conf.save_to_file(list(all_urls), urls_target)
print("Saved", urls_target)

topdomains_target = f"{target_dir}/topdomains.csv"
conf.save_to_file(list(all_topdomains),topdomains_target)
print("Saved", topdomains_target)

subdomains_target = f"{target_dir}/subdomains.csv"
conf.save_to_file(list(all_subdomains),subdomains_target)
print("Saved", subdomains_target)

suffix_target = f"{target_dir}/suffix.csv"
conf.save_to_file(list(all_suffix),suffix_target)
print("Saved", suffix_target)