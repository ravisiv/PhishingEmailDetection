import traceback
import os
import base64
import sys
import yaml
from pathlib import Path
import email
import phdcommon as conf
from bs4 import BeautifulSoup
from bs4.element import Comment
import tldextract

def parse_body(email_msg):
    bodies = []
    body_texts = []
    for part in email_msg.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get('Content-Disposition'))
        if ctype == 'text/plain' and 'attachment' not in cdispo:
            body = part.get_payload(decode=True)
            if body:
                body_texts.append(str(body))
        else:
            body = email_msg.get_payload(decode=True)
            if body:
                body_texts.append(str(body))

    ret_val = ""
    if len(body_texts) > 0:
        ret_val = "\n".join(body_texts)
    body_text_conv = text_from_html(ret_val)
    urls = urls_from_html(ret_val)


    #Check if it is not html
    if len(body_text_conv) == 0:
        return ret_val.strip(), urls
    else:

        return body_text_conv.strip(), urls
#Reference https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def urls_from_html(body):
    if body == "":
        return []
    soup = BeautifulSoup(body, 'html.parser')
    if soup:
        urls = set()
        for a in soup.find_all('a', href=True):
            url = a['href']
            if len(url) > 4:
                if url.startswith("http:"):
                    urls.add(url)
        return list(set(urls))
    else:
        return []


def text_from_html(body):
    if body == "":
        return ""
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)



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
                    _, anchor_urls = parse_body(msg)
                    safeurls = set()
                    for eachurl in anchor_urls:
                        safeurl = conf.get_urls(eachurl)
                        if len(safeurl) > 0:
                            for eachset in safeurl:
                                if len(eachset) > 0:
                                    saniurl = conf.sanitize_url(eachset.pop())
                                    if len(saniurl) > 4:
                                        safeurls.update(saniurl)
                    f.seek(0)
                    urls,td,sd,suffix = conf.get_urls(msg.as_string())
                    all_urls.update(urls)
                    all_urls.update(safeurls)
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