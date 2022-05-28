import traceback
import os
from bs4 import BeautifulSoup
from bs4.element import Comment
import email
from email.parser import HeaderParser
from urlextract import URLExtract
import base64
import sys
import csv
import tldextract
import hashlib

conf_file = "conf/phishing.yaml"


def get_unicode(string):
    return string.encode()

def get_domain(urlwithdomain):
    res = tldextract.extract(urlwithdomain)
    if res[2] == '':
        return res[0], res[1], res[2]
    else:
        return res[0], res[1] + "." + res[2], res[2]


def get_sha1_hash(data):
    BUF_SIZE = 67108864  
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()

def save_to_file(data,filename):
    with open(filename, 'w', newline='') as myfile:
        (csv.writer(myfile, quoting=csv.QUOTE_ALL)).writerow(data)

def get_target_dir(dirtype):
	default_dir = "messages"
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data[dirtype]
		except yaml.YAMLError as exc:
			return default_dir
	return default_dir

# Reference:
# https://stackoverflow.com/questions/17874360/python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not
#body = ""
def parse_body(email_msg):
    bodies = []
    for part in email_msg.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get('Content-Disposition'))
        if ctype == 'text/plain' and 'attachment' not in cdispo:
            bodies.append(part.get_payload(decode=True))
        else:
            bodies.append(email_msg.get_payload(decode=True))

    body_texts = []
    for body in bodies:
        if body is None:
            body_text = ""
        else:
            body_text = str(body)
        body_texts.append(body_text)

    ret_val = ""
    if len(body_texts) > 0:
        ret_val = "\n".join(body_texts)
    body_text_conv = text_from_html(ret_val)

    #Check if it is not html
    if len(body_text_conv) == 0:
        return ret_val.strip()
    else:
        return body_text_conv.strip()


#Reference https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)



#TODO: This method need lots of tuning
def get_urls_headers(msg):
    extractor = URLExtract()
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())
    all_urls = []
    all_strip_urls = []
    all_headers = []
    all_subdomains = []
    all_topdomains = []
    all_suffix = []
    for h in headers.items():
        urls = extractor.find_urls(h[1])
        all_urls = all_urls + urls
        #base64 decode
        if isBase64(h[1]):
            try:
                b64_h1 = base64.b64decode(h[1]).decode("utf-8")
                urls = extractor.find_urls(str(b64_h1))
                all_urls = all_urls + urls

            except Exception as e:
                b64_h1 = ""

        all_headers.append(h[0])

    body = parse_body(msg)
    str_body = str(body)
    if str_body:
        str_body = str_body.replace("\n", " ")
        urls = extractor.find_urls(str_body)
        all_urls = all_urls + urls
    for each_url in all_urls:
        strip_url = each_url.lower().strip().replace(
            "\\n", "").replace("\\t", "").replace("nhttp", "http")
        sdomain, tdomain, suffix = get_domain(strip_url)
        if sdomain:
            all_subdomains.append(sdomain)
        if tdomain:
            all_topdomains.append(tdomain)
        if suffix:
            all_suffix.append(suffix)
        if each_url:
            all_strip_urls.append(strip_url)

    all_headers = list(set(all_headers))
    all_strip_urls = list(set(all_strip_urls))
    all_topdomains = list(set(all_topdomains))
    all_subdomains = list(set(all_subdomains))
    all_suffix = list(set(all_suffix))

    return all_headers,all_strip_urls, all_topdomains,all_subdomains, all_suffix


def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


#Main method
data_path = sys.argv[1]
cur_files =  next(os.walk(data_path))[2]

#get msg type
all_headers = set()
all_urls = set()
all_topdomains = set()
all_subdomains = set()
all_suffix = set()
for file in cur_files:
    with open(f"{data_path}/{file}") as f:
        f_realpath = os.path.realpath(f.name)
        if f.name.startswith("."):
            try:
                print(f.name)
                headers,urls,topdomains,subdomains,suffix = get_urls_headers(email.message_from_file(f))
                all_headers.add(headers)
                all_urls.add(urls)
                all_topdomains.add(topdomains)
                all_subdomains.add(subdomains)
                all_suffix.add(suffix)
            except Exception as e:
                print("--------------------------------starting------------")
                print(traceback.format_exc())
                print("--------------------------------ending------------")
                continue

u_curfiles = map(get_unicode, cur_files)
filename_digest = get_sha1_hash(' '.join(unicode.decode() for unicode in u_curfiles))
conf_dir = get_target_dir("url")
target_dir = f"{conf_dir}/{filename_digest}"

save_to_file(list(all_headers),f"{target_dir}/headers.csv")
save_to_file(list(all_urls),f"{target_dir}/urls.csv")
save_to_file(list(all_topdomains),f"{target_dir}/topdomains.csv")
save_to_file(list(all_subdomains),f"{target_dir}/subdomains.csv")
save_to_file(list(all_suffix),f"{target_dir}/suffix.csv")
