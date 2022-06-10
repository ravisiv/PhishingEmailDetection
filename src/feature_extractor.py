#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 13:23:31 2020

@author: hannousse
"""

#Modified by Ravi

import time
import url_features as urlfe
import pandas as pd 
import urllib.parse
import tldextract
import json
import csv
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import unquote


def get_domain(url):
    o = urllib.parse.urlsplit(url)
    return o.hostname, tldextract.extract(url).domain, o.path

#################################################################################################################################
#              Calculate features from extracted data
#################################################################################################################################

def extract_features(url):
    
    def words_raw_extraction(domain, subdomain, path):
        w_domain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", domain.lower())
        w_subdomain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", subdomain.lower())   
        w_path = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", path.lower())
        raw_words = w_domain + w_path + w_subdomain
        w_host = w_domain + w_subdomain
        raw_words = list(filter(None,raw_words))
        return raw_words, list(filter(None,w_host)), list(filter(None,w_path))

    
    hostname, domain, path = get_domain(url)
    extracted_domain = tldextract.extract(url)
    domain = extracted_domain.domain+'.'+extracted_domain.suffix
    subdomain = extracted_domain.subdomain
    tmp = url[url.find(extracted_domain.suffix):len(url)]
    pth = tmp.partition("/")
    path = pth[1] + pth[2]
    words_raw, words_raw_host, words_raw_path= words_raw_extraction(extracted_domain.domain, subdomain, pth[2])
    tld = extracted_domain.suffix
    parsed = urlparse(url)
    scheme = parsed.scheme

    Title =''
    Text= ''
    urlfe_statistical_report = urlfe.statistical_report(url, domain)
    row = [url,
            # url-based features
            urlfe.url_length(url),
            urlfe.url_length(hostname),
            urlfe.having_ip_address(url),
            urlfe.count_dots(url),
            urlfe.count_hyphens(url),
            urlfe.count_at(url),
            urlfe.count_exclamation(url),
            urlfe.count_and(url),
            urlfe.count_or(url),
            urlfe.count_equal(url),
            urlfe.count_underscore(url),
            urlfe.count_tilde(url),
            urlfe.count_percentage(url),
            urlfe.count_slash(url),
            urlfe.count_star(url),
            urlfe.count_colon(url),
            urlfe.count_comma(url),
            urlfe.count_semicolumn(url),
            urlfe.count_dollar(url),
            urlfe.count_space(url),
            
            urlfe.check_www(words_raw),
            urlfe.check_com(words_raw),
            urlfe.count_double_slash(url),
            urlfe.count_http_token(path),
            urlfe.https_token(scheme),
            
            urlfe.ratio_digits(url),
            urlfe.ratio_digits(hostname),
            urlfe.punycode(url),
            urlfe.port(url),
            urlfe.tld_in_path(tld, path),
            urlfe.tld_in_subdomain(tld, subdomain),
            urlfe.abnormal_subdomain(url),
            urlfe.count_subdomain(url),
            urlfe.prefix_suffix(url),
            urlfe.shortening_service(url),
            
            urlfe.path_extension(path),
            urlfe.length_word_raw(words_raw),
            urlfe.char_repeat(words_raw),
            urlfe.shortest_word_length(words_raw),
            urlfe.shortest_word_length(words_raw_host),
            urlfe.shortest_word_length(words_raw_path),
            urlfe.longest_word_length(words_raw),
            urlfe.longest_word_length(words_raw_host),
            urlfe.longest_word_length(words_raw_path),
            urlfe.average_word_length(words_raw),
            urlfe.average_word_length(words_raw_host),
            urlfe.average_word_length(words_raw_path),
            
            urlfe.phish_hints(url),  
            urlfe.domain_in_brand(extracted_domain.domain),
            urlfe.brand_in_path(extracted_domain.domain,subdomain),
            urlfe.brand_in_path(extracted_domain.domain,path),
            urlfe.suspecious_tld(tld),
            urlfe_statistical_report
            ]
        #print(row)
    return row

    
#################################################################################################################################
#             Intialization
#################################################################################################################################

url_headers = [ 'url',
                'length_url',                                  
                   'length_hostname',
                   'ip',
                   'nb_dots',
                   'nb_hyphens',
                   'nb_at',
                   'nb_qm',
                   'nb_and',
                   'nb_or',
                   'nb_eq',                  
                   'nb_underscore',
                   'nb_tilde',
                   'nb_percent',
                   'nb_slash',
                   'nb_star',
                   'nb_colon',
                   'nb_comma',
                   'nb_semicolumn',
                   'nb_dollar',
                   'nb_space',
                   'nb_www',
                   'nb_com',
                   'nb_dslash',
                   'http_in_path',
                   'https_token',
                   'ratio_digits_url',
                   'ratio_digits_host',
                   'punycode',
                   'port',
                   'tld_in_path',
                   'tld_in_subdomain',
                   'abnormal_subdomain',
                   'nb_subdomains',
                   'prefix_suffix',
                   'shortening_service',
                   'path_extension',
                   
                   'length_words_raw',
                   'char_repeat',
                   'shortest_words_raw',
                   'shortest_word_host',
                   'shortest_word_path',
                   'longest_words_raw',
                   'longest_word_host',
                   'longest_word_path',
                   'avg_words_raw',
                   'avg_word_host',
                   'avg_word_path',
                   'phish_hints',
                   'domain_in_brand',
                   'brand_in_subdomain',
                   'brand_in_path',
                   'suspecious_tld',
                   'statistical_report'
                ]

url_struct_headers = [    
                   'ip',
                   'https_token',
                   'punycode',
                   'port',
                   'tld_in_path',
                   'tld_in_subdomain',
                   'abnormal_subdomain',
                   'prefix_suffix',
                   'shortening_service',
                   'path_extension',
                   
                   'domain_in_brand',
                   'brand_in_subdomain',
                   'brand_in_path',
                   'suspecious_tld',
                   'statistical_report'
                ]


url_stat_headers = [    
                    'length_url',                                  
                   'length_hostname',
                   'nb_dots',
                   'nb_hyphens',
                   'nb_at',
                   'nb_qm',
                   'nb_and',
                   'nb_or',
                   'nb_eq',                  
                   'nb_underscore',
                   'nb_tilde',
                   'nb_percent',
                   'nb_slash',
                   'nb_star',
                   'nb_colon',
                   'nb_comma',
                   'nb_semicolumn',
                   'nb_dollar',
                   'nb_space',
                   'nb_www',
                   'nb_com',
                   'nb_dslash',
                   'http_in_path',
                   'ratio_digits_url',
                   'ratio_digits_host',
                   'nb_subdomains',
                   
                   
                   'length_words_raw',
                   'char_repeat',
                   'shortest_words_raw',
                   'shortest_word_host',
                   'shortest_word_path',
                   'longest_words_raw',
                   'longest_word_host',
                   'longest_word_path',
                   'avg_words_raw',
                   'avg_word_host',
                   'avg_word_path',
                   'phish_hints',
                ]


datafile = sys.argv[1]
outfile = sys.argv[2]

status = 10
if len(sys.argv) > 3:
    status = int(sys.argv[3])
    url_headers = url_headers + ["status"]


url_df = pd.read_csv(datafile, header=None)
url_list = []
for index, row in url_df.iterrows():
    rawurl = row[0] 
    if rawurl:
        if rawurl:
            try:
                checklen = len(rawurl)
                if checklen < 4:
                    continue
            except:
                continue
            print(rawurl)
            try:
                feat = extract_features(rawurl)
                if status < 10:
                    feat = feat + [status]
                url_list.append(feat)
            except:
                print("Skipping", rawurl)
                continue

email_url_stats_df = pd.DataFrame(url_list, columns=url_headers)

dname = os.path.dirname(outfile)
Path(dname).mkdir(parents=True, exist_ok=True)
email_url_stats_df.to_csv(outfile, index=False)
print("Saved in",outfile)