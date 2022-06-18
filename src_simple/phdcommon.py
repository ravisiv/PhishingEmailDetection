import yaml
import hashlib
import csv
import tldextract
import ipaddress
import email
from email.parser import HeaderParser
from urlextract import URLExtract
import urllib

conf_file = "conf/phishing.yaml"
def get_domain(urldata: str):
    urlwithdomain = urldata.lower()
    res = tldextract.extract(urlwithdomain)
    if res[2] == '':
        subdomain = ""
        topdomain = res[1] + "." + res[2]
        suffix = res[2]
        return  subdomain, topdomain, suffix
    else:
        subdomain = res[0] + "." + res[1] + "." + res[2]
        topdomain = res[1] + "." + res[2]
        suffix = res[2]
        return  subdomain, topdomain, suffix


def sanitize_url(surl: str):
    if surl.startswith("@"):
        surl = surl[1:]

    try:
        ip_add = ipaddress.ip_address(surl)
        surl = f"http://{surl}"
    except:
        pass

    if surl.startswith("mailto"):
        return None
    if surl.startswith("file://"):
        return None

    surl = surl.strip("\n")
    surl = surl.strip("\t")
    surl = surl.strip("\r")
    surl = surl.strip("\\t")
    surl = surl.strip("\\n")
    surl = surl.strip("\\r")

    if surl.startswith("tel:"):
        return None

    if surl.startswith("\\thttp"):
        surl = surl[2:]

    if surl.startswith("\\nhttp"):
        surl = surl[2:]

    if surl.startswith("nhttps://"):
        surl = surl[1:]

    if surl.startswith("nhttp://"):
        surl = surl[1:]

    if not surl.startswith("http"):
        surl = f"http://{surl}"

    return surl

def get_sha1_hash(data):
    BUF_SIZE = 67108864  
    sha1 = hashlib.sha1()
    sha1.update(data.encode())
    return sha1.hexdigest()

def save_to_file(data,filename):
    with open(filename, 'w', newline='') as myfile:
        (csv.writer(myfile, csv.QUOTE_NONE)
         ).writerows([[i] for i in data])

def get_target(target_type):
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data[target_type]
		except yaml.YAMLError as exc:
			return "errordir"
	return "errordir"

def get_headers(msg):
    parser = email.parser.HeaderParser()
    headers = parser.parsestr(msg.as_string())
    all_headers = set()
    for h in headers.items():
        headerval = h[0]
        if headerval:
            headerval = ''.join(e for e in headerval if e.isalnum())
            all_headers.add(headerval.lower())
    return all_headers

def get_urls(msgstr: str):
    extractor = URLExtract()
    all_safe_urls = set()
    all_topdomains = set()
    all_subdomains = set()
    all_suffix = set()
    lines = set(msgstr.splitlines())
    for line in lines:
        words = set(line.split(" "))
        for chunks in words:
            if "." in chunks:
                urls = extractor.find_urls(chunks)
                for each_url in urls:
                    if len(each_url) > 4:
                        strip_url = each_url.lower().strip().replace(
                            "\\\\n", "").replace("\\\\t", "").replace("nhttp", "http")
                        sdomain, tdomain, suffix = get_domain(
                            strip_url)
                        safe_url = sanitize_url(strip_url)
                        if safe_url:
                            all_safe_urls.add(safe_url)
                        all_topdomains.add(tdomain)
                        all_subdomains.add(sdomain)
                        all_suffix.add(suffix)
    return all_safe_urls, all_topdomains, all_subdomains,all_suffix
