from bs4 import BeautifulSoup
from bs4.element import Comment
from email.parser import HeaderParser
from scipy.stats import entropy
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
import ipaddress
import urllib.parse
import phdcommon as conf


def get_msg_type(msgdir):
    #This will read .msgtype file in the directory
    filename = f"{msgdir}/.msgtype"
    promotion = 0
    target = 0
    spam = 0
    with open(filename) as f:
        line = f.readlines()[0]
        line = line.strip()
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
    global td_ind
    global sd_ind
    global suffix_ind
    global urls_ind
    global headers_ind
    ret_val = 0
    param = param.strip(",")
    param = param.strip("'")
    param = param.strip('"')
    param = param.strip(' ')
    if not param or param == "":
        return 0
    try:
        if itype == "url":
            ret_val = urls_ind.get_loc(param)
        if itype == "topdomain":
            ret_val = td_ind.get_loc(param)
        if itype == "subdomain":
            ret_val = sd_ind.get_loc(param)
        if itype == "suffix":
            ret_val = suffix_ind.get_loc(param)
        if itype == "header":
            ret_val = headers_ind.get_loc(param)
        return ret_val
    except Exception as e:
        print("cannot find: type:",itype,"value:",param,"error:",str(e)) 
        return ret_val


def get_email_as_dict(msg):
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())

    emaildata = {}
    all_urls_vectors = []
    all_headers_vectors = []
    all_topdomains_vectors = []
    all_subdomains_vectors = []
    all_suffix_vectors = []
    headers = conf.get_headers(msg)
    for header in headers:
        header_index = get_index("header", header)
        all_headers_vectors.append(header_index)

    body, anchor_urls = parse_body(msg)
    safeurls = set()
    for eachurl in anchor_urls:
        safeurl = conf.get_urls(eachurl)
        if len(safeurl)> 0:
            for eachset in safeurl:
                if len(eachset) > 0:
                    saniurl = conf.sanitize_url(eachset.pop())
                    if len(saniurl) > 4:
                        safeurls.update(saniurl)
                    safeurls.update(saniurl)
    attchments = get_attachments(msg)
    str_body = str(body)
    str_body = str_body.replace("\n", " ")
    f.seek(0)
    urls,td,sd,suffix = conf.get_urls(msg.as_string())
    for each_url in urls:
        url_index = get_index("url", each_url)
        all_urls_vectors.append(url_index)
    
    for each_td in td:
        topdomain_index = get_index("topdomain", each_td)
        all_topdomains_vectors.append(topdomain_index)
    

    for each_sd in sd:
        subdomain_index = get_index("subdomain", each_sd)
        all_subdomains_vectors.append(subdomain_index)
        

    for each_suffix in suffix: 
        suffix_index = get_index("suffix", each_suffix)
        all_suffix_vectors.append(suffix_index)

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
        subdomain = ""
        topdomain = res[1] + "." + res[2]
        suffix = res[2]
        return subdomain, topdomain, suffix
    else:
        subdomain = res[0] + "." + res[1] + "." + res[2]
        topdomain = res[1] + "." + res[2]
        suffix = res[2]
        return subdomain, topdomain, suffix

def get_as_row(metatype, list_data, max_cols=12):
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

master_urls = conf.get_target("masterurls")
master_headers = conf.get_target("masterheaders")
master_topdomains = conf.get_target("mastertopdomains")
master_subdomains = conf.get_target("mastersubdomains")
master_suffix = conf.get_target("mastersuffix")

td_ind = pd.Index(pd.read_csv(master_topdomains, header=None).squeeze("columns"))
sd_ind = pd.Index(pd.read_csv(master_subdomains, header=None).squeeze("columns"))
suffix_ind = pd.Index(pd.read_csv(master_suffix, header=None).squeeze("columns"))
urls_ind = pd.Index(pd.read_csv(master_urls,header=None).squeeze("columns"))
headers_ind = pd.Index(pd.read_csv(master_headers, header=None).squeeze("columns"))

if sys.argv[1] == None or sys.argv[1] == "":
    print("Argument mbox folder required!")
    exit(0)

data_path = sys.argv[1]
target, spam, promotion = get_msg_type(data_path)

cur_files = next(os.walk(data_path))[2]

all_email_data =[] 
all_cols = []
for file in cur_files:
    with open(f"{data_path}/{file}") as f:
        f_realpath = os.path.realpath(f.name)
        if not ".msgtype" in f.name:
            try:
                msg = email.message_from_file(f)
                attachments = get_attachments(msg)
                emaildata = get_email_as_dict(msg)
                emaildata["attachment_count"] = attachments['attachment_count']
                emaildata["spam"] = spam
                emaildata["target"] = target
                emaildata["promotion"] = promotion
                all_email_data.append(emaildata.values())
                if (len(all_cols) == 0):
                    all_cols = emaildata.keys()
                print("CSV generated:",f_realpath)
            except Exception as e:
                print(traceback.format_exc())
                print("#Skipped:", f_realpath, "due to ", str(e))

email_df = pd.DataFrame.from_dict(all_email_data)

filename_digest = conf.get_sha1_hash("".join(cur_files))

data_root_dir = conf.get_target("datadir")
columns_file = conf.get_target("columnsfile")

datadir = f"{data_root_dir}/digest"
target_dir = f"{datadir}/{filename_digest}"
Path(target_dir).mkdir(parents=True, exist_ok=True)
emaildata_file = f"{datadir}/{filename_digest}/emails.csv"
print("Saving to ", emaildata_file)
email_df.to_csv(emaildata_file, index=False, columns=None)

with open(columns_file, 'w') as f:
    f.write(",".join(all_cols))
    f.close()
