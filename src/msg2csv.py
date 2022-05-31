from bs4 import BeautifulSoup
from bs4.element import Comment
from email.parser import HeaderParser
from scipy.stats import entropy
from urlextract import URLExtract
import base64
import bs4
import email
import hashlib
import mailbox
import os
import pandas as pd
import pickle
import sys
import tldextract
import traceback
from sys import exit
import yaml
from pathlib import Path

conf_file = "conf/phishing.yaml"


def get_sha1_hash(data):
    BUF_SIZE = 67108864
    sha1 = hashlib.sha1()
    sha1.update(data.encode())
    return sha1.hexdigest()


def get_target_dir(dirtype):
	default_dir = "messages"
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data[dirtype]
		except yaml.YAMLError as exc:
			return default_dir
	return default_dir


def get_msg_type(msgdir):
    #This will read .msgtype file in the directory
    filename = f"{msgdir}/.msgtype"
    promotion = 0
    target = 0
    spam = 0
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            keyval = line.split("=")
            if keyval[0] == "msgtype":
                if keyval[1] == "spam":
                    spam = 1
                if keyval[1] == "phishing":
                    target = 1
                if keyval[1] == "promotions":
                    promotion = 1
    return target, spam, promotion


def get_index(itype, param):
    global topdomains_s
    global subdomains_s
    global suffix_s
    global urls_s
    global headers_s

    try:
        if itype == "url":
            urls_s.get_loc(param)
        if itype == "topdomain":
            topdomains_s.get_loc(param)
        if itype == "subdomain":
            subdomains_s.get_loc(param)
        if itype == "suffix":
            suffix_s.get_loc(param)
        if itype == "header":
            headers_s.get_loc(param)

    except:
        return 0


def get_email_as_dict(msg):
    extractor = URLExtract()
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())

    emaildata = {}
    all_urls = []
    all_urls_vectors = []
    all_headers_vectors = []
    all_topdomains_vectors = []
    all_subdomains_vectors = []
    all_suffix_vectors = []
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
        # email_headers[h[0]] = [h[1]]
        each_header = h[0]
        strip_header = each_header.lower().strip()
        header_index = get_index("header", strip_header)
        all_headers_vectors.append(header_index)

    body, anchor_urls = parse_body(msg)
    attchments = get_attachments(msg)
    str_body = str(body)
    str_body = str_body.replace("\n", " ")

    for chunk in str_body.split(" "):
        urls = extractor.find_urls(chunk)
        all_urls = all_urls + urls

    all_urls = all_urls + anchor_urls

    for each_url in all_urls:
        try:
            if each_url != None or each_url != "":
                strip_url = each_url.lower().strip().replace(
                    "\\n", "").replace("\\t", "").replace("nhttp", "http")
                sdomain, tdomain, suffix = get_domain(strip_url)

                url_index = get_index("url", strip_url)
                all_urls_vectors.append(url_index)

                subdomain_index = get_index("subdomain", sdomain)
                all_subdomains_vectors.append(subdomain_index)

                topdomain_index = get_index("topdomain", tdomain)
                all_topdomains_vectors.append(topdomain_index)

                suffix_index = get_index("suffix", tdomain)
                all_suffix_vectors.append(suffix_index)
        except:
            continue

    dict_row_urls = get_as_row(metatype="url", list_data=all_urls_vectors)
    dict_row_header = get_as_row(
        metatype="header", list_data=all_headers_vectors)
    dict_row_topdomain = get_as_row(
        metatype="topdomain", list_data=all_topdomains_vectors)
    dict_row_subdomain = get_as_row(
        metatype="subdomain", list_data=all_subdomains_vectors)
    dict_row_suffix = get_as_row(
        metatype="suffix", list_data=all_suffix_vectors)

    emaildata.update(dict_row_urls)
    emaildata.update(dict_row_header)
    emaildata.update(dict_row_topdomain)
    emaildata.update(dict_row_subdomain)
    emaildata.update(dict_row_suffix)
    emaildata.update(attchments)
    emaildata["bodytext"] = str_body

    return emaildata


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


def get_domain(urlwithdomain):
    res = tldextract.extract(urlwithdomain)
    if res[2] == '':
        return res[0], res[1], res[2]
    else:
        return res[0], res[1] + "." + res[2], res[2]


def get_as_row(metatype, list_data, max_cols=20):
    row = {}
    for index, eachitem in enumerate(list_data):
        row[metatype + str(index+1)] = eachitem
        if index > 9:
            break
    index = len(row.keys())
    if index < max_cols:
        for idx in range(max_cols-index-1):
            row[metatype + str(index+1)] = 0
            index += 1
    return row

# Reference:
# https://stackoverflow.com/questions/17874360/python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not
#body = ""


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
        href_tags = soup.find_all(href=True)
        return href_tags
    else:
        return []


def text_from_html(body):
    if body == "":
        return ""
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def get_attachments(email_msg):
    attachments = {}
    if email_msg == None:
        return {}
    attachment_count = 0
    for part in email_msg.walk():
        content_dis = part.get_content_disposition()
        if content_dis == "attachment":
            att_filename = part.get_filename()
            payload = bytearray(part.get_payload(decode=True))
            att_entropy = entropy(payload, base=2)
            att_size = len(payload)
            prefix = "attachment" + str(attachment_count)
            attachment = {}
            attachment[prefix + "_filename"] = att_filename
            attachment[prefix + "_entropy"] = att_entropy
            attachment[prefix + "_size"] = att_size
            #attachments.update(attachment)
            attachment_count += 1
    attachment_count = {}
    attachment_count["attachment_count"] = len(attachments)//3
    attachments.update(attachment_count)
    return attachments


#Main method

conf_dir = get_target_dir("urldir")
master_urls = f"{conf_dir}/masterurls.csv"
master_headers = f"{conf_dir}/masterheaders.csv"
master_topdomains = f"{conf_dir}/mastertopdomains.csv"
master_subdomains = f"{conf_dir}/mastersubdomains.csv"
master_suffix = f"{conf_dir}/mastersuffix.csv"

topdomains_s = pd.read_csv(master_topdomains, squeeze=True)
subdomains_s = pd.read_csv(master_subdomains, squeeze=True)
suffix_s = pd.read_csv(master_suffix, squeeze=True)
urls_s = pd.read_csv(master_urls, squeeze=True)
headers_s = pd.read_csv(master_headers, squeeze=True)

if sys.argv[1] == None or sys.argv[1] == "":
    print("Argument mbox folder required!")
    exit(0)

data_path = sys.argv[1]
target, spam, promotion = get_msg_type(data_path)

cur_files = next(os.walk(data_path))[2]

all_email_data = []
for file in cur_files:
    with open(f"{data_path}/{file}") as f:
        f_realpath = os.path.realpath(f.name)
        if not ".msgtype" in f.name:
            try:
                msg = email.message_from_file(f)
                emaildata = get_email_as_dict(msg)
                attachments = get_attachments(msg)
                emaildata["attachment_count"] = attachments['attachment_count']
                emaildata["spam"] = spam
                emaildata["target"] = target
                emaildata["promotion"] = promotion
                all_email_data.append(emaildata)
                print(".", end=" ")
            except Exception as e:
                print("--------------------------------starting------------")
                print(traceback.format_exc())
                print("--------------------------------ending------------")
                continue

email_df = pd.DataFrame.from_dict(all_email_data)

filename_digest = get_sha1_hash("".join(cur_files))

datadir = get_target_dir("datadir")
target_dir = f"{datadir}/{filename_digest}"
Path(target_dir).mkdir(parents=True, exist_ok=True)
emaildata_file = f"{datadir}/{filename_digest}/emails.csv"
email_df.to_csv(emaildata_file)
