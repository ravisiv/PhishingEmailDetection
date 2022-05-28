import bs4
import mailbox
import traceback
import os
from scipy.stats import entropy
import pickle
from bs4 import BeautifulSoup
from bs4.element import Comment
import tldextract
import pandas as pd
import email
from email.parser import HeaderParser
from urlextract import URLExtract
import base64
import sys

scratch_dir = "/scratch/users/rsivaraman/"
#scratch_dir = "/Users/ravis/Downloads/phishingdata/"
master_urls = scratch_dir + "masterdata/urlsinmails.csv"
master_headers = scratch_dir + "masterdata/headersinmails.csv"
master_topdomains = scratch_dir + "masterdata/topdomainsinmails.csv"
master_subdomains = scratch_dir + "masterdata/subdomainsinmails.csv"
master_suffix = scratch_dir + "masterdata/suffixinmails.csv"

headers_df = pd.read_csv(master_headers)

#domain and subdomain must be a complex number

topdomains_df = pd.read_csv(master_topdomains)
subdomains_df = pd.read_csv(master_subdomains)
suffix_df = pd.read_csv(master_suffix)
urls_df = pd.read_csv(master_urls)
headers_df = pd.read_csv(master_headers)
print(sys.argv[1])

eta_urls = {}
meta_headers = {}

#TODO: This method need lots of tuning


def get_email_as_dict(msg):

    global urls_df
    global topdomains_df
    global subdomains_df
    global suffix_df
    global headers_df
    #untuned code

    extractor = URLExtract()
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())

    metadata = {}
    all_urls = []
    all_headers = []
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
        all_headers.append(h[0])

    body = parse_body(msg)
    attchments = get_attachments(msg)
    str_body = str(body)
    str_body = str_body.replace("\n", " ")
    urls = extractor.find_urls(str_body)

    all_urls = all_urls + urls
    all_urls_vectors = []
    all_topdomains_vectors = []
    all_subdomains_vectors = []
    all_suffix_vectors = []

    all_headers_vectors = []
    for each_url in all_urls:
        strip_url = each_url.lower().strip().replace(
            "\\n", "").replace("\\t", "").replace("nhttp", "http")
        sdomain, tdomain, suffix = get_domain(strip_url)

        try:
            url_index = urls_df["url"].to_list().index(strip_url) + 1
            all_urls_vectors.append(url_index)

        except ValueError as e:
            urls_df = pd.concat([urls_df, pd.DataFrame(
                {"url": [strip_url]})], ignore_index=True)
            urls_df.reset_index()
            url_index = urls_df["url"].shape[0]
            all_urls_vectors.append(url_index)

        if sdomain != '':
            try:
                subdomain_index = subdomains_df["subdomain"].to_list().index(
                    sdomain) + 1
                all_subdomains_vectors.append(subdomain_index)
            except ValueError as e:
                subdomains_df = pd.concat([subdomains_df, pd.DataFrame(
                    {"subdomain": [sdomain]})], ignore_index=True)
                subdomains_df.reset_index()
                subdomain_index = subdomains_df["subdomain"].shape[0]
                all_subdomains_vectors.append(subdomain_index)
        else:
            all_subdomains_vectors.append(0)

        try:
            topdomain_index = topdomains_df["topdomain"].to_list().index(
                tdomain) + 1
            all_topdomains_vectors.append(topdomain_index)
        except ValueError as e:
            topdomains_df = pd.concat([topdomains_df, pd.DataFrame(
                {"topdomain": [tdomain]})], ignore_index=True,sort=True)
            topdomains_df.reset_index()
            topdomain_index = topdomains_df["topdomain"].shape[0]
            all_topdomains_vectors.append(topdomain_index)

        if suffix != '':
            try:
                suffix_index = suffix_df["suffix"].to_list().index(suffix) + 1
                all_suffix_vectors.append(suffix_index)
            except ValueError as e:
                suffix_df = pd.concat([suffix_df, pd.DataFrame(
                    {"suffix": [suffix]})], ignore_index=True, sort=True)
                suffix_df.reset_index()
                suffix_index = suffix_df["suffix"].shape[0]
                all_suffix_vectors.append(suffix_index)
        else:
            all_suffix_vectors.append(0)

    for each_header in all_headers:
        strip_header = each_header.lower().strip()
        try:
            header_index = headers_df["header"].to_list().index(
                strip_header) + 1
            all_headers_vectors.append(header_index)

        except ValueError as e:
            headers_df = pd.concat([headers_df, pd.DataFrame(
                {"header": [strip_header]})], ignore_index=True,sort=True)
            headers_df.reset_index()
            header_index = headers_df["header"].shape[0]
            all_headers_vectors.append(header_index)

    dict_row_urls = get_as_row(metatype="url", list_data=all_urls_vectors)
    dict_row_header = get_as_row(
        metatype="header", list_data=all_headers_vectors)
    dict_row_topdomain = get_as_row(
        metatype="topdomain", list_data=all_topdomains_vectors)
    dict_row_subdomain = get_as_row(
        metatype="subdomain", list_data=all_subdomains_vectors)
    dict_row_suffix = get_as_row(
        metatype="suffix", list_data=all_suffix_vectors)

    metadata.update(dict_row_urls)
    metadata.update(dict_row_header)
    metadata.update(dict_row_topdomain)
    metadata.update(dict_row_subdomain)
    metadata.update(dict_row_suffix)
    metadata.update(attchments)
    metadata["bodytext"] = str_body

    #print("metadata", metadata)
    return metadata


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

data_path =  sys.argv[1]
f_realpath = f"{data_path}"
mbox_obj = mailbox.mbox(f"{data_path}")
is_spam = "Spam" in f_realpath
is_promotion = "Promotion" in f_realpath
is_phishing = "Phishing" in f_realpath
metadata_mbox_all = []

for idx, email_obj in enumerate(mbox_obj):
    try:
        metadata = get_email_as_dict(email_obj)
        attachments = get_attachments(email_obj)
        #body_list.append([body, attachments['attachment_count'],1 if is_spam is True else 0])
        metadata["attachment_count"] = attachments['attachment_count']
        metadata["is_spam"] = 1 if is_spam is True else 0
        metadata_mbox_all.append(metadata)
        print(idx, end=" ")
    except Exception as e:
        print("--------------------------------starting------------")
        print(traceback.format_exc())
        print("--------------------------------ending------------")
        continue

urls_df.to_csv(sys.argv[1] + "_url.csv")
topdomains_df.to_csv(sys.argv[1] + "_td.csv")
subdomains_df.to_csv(sys.argv[1] + "_sd.csv")
suffix_df.to_csv(sys.argv[1] + "_sf.csv")
headers_df.to_csv(sys.argv[1] + "_head.csv")


metadata_mbox_df = pd.DataFrame.from_dict(metadata_mbox_all)
metadata_mbox_df.to_csv(sys.argv[1] + ".csv")
