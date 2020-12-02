#!/usr/bin/env python
u"""
smart_citekeys.py (12/2020)
Generates Papers2-like cite keys for BibTeX using information from crossref.org

Enter DOI's of journals to generate "universal" keys

CALLING SEQUENCE:
    python smart_citekeys.py "10.1038/ngeo102"
    will result in Rignot:2008ct as the citekey

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        http://python-future.org/

PROGRAM DEPENDENCIES:
    language_conversion.py: Outputs map for converting symbols between languages

NOTES:
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js
    Check unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
    Updated 12/2020: using argparse to set command line options
    Updated 07/2019: modifications for python3 string compatibility
    Updated 07/2018: using python3 urllib.request with future library
    Updated 10/2017: use modulus of 0xffffffff (4294967295)
    Updated 09/2017: use timeout of 20 to prevent socket.timeout
    Forked 05/2017 from gen_citekeys.py to use information from crossref.org
    Updated 05/2017: removing whitespace from authors.
        Converting special characters with language_conversion program
    Updated 02/2017: universal citekeys from DOI or title hashes
        (will create the same citekeys as the Papers2 application)
    Written 02/2017
"""
from __future__ import print_function
import future.standard_library

import sys
import os
import re
import ssl
import math
import json
import binascii
import argparse
import posixpath
from language_conversion import language_conversion
with future.standard_library.hooks():
    import urllib.request
    import urllib.parse

#-- PURPOSE: check internet connection and URL
def check_connection(doi):
    #-- attempt to connect to remote url
    remote_url = posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    try:
        urllib.request.urlopen(remote_url,timeout=20,context=ssl.SSLContext())
    except urllib.request.HTTPError:
        raise RuntimeError('Check URL: {0}'.format(remote_url))
    except urllib.request.URLError:
        raise RuntimeError('Check internet connection')
    else:
        return True

#-- PURPOSE: create a Papers2-like cite key using the DOI
def smart_citekey(doi):
    #-- open connection with crossref.org for DOI
    crossref=posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    request=urllib.request.Request(url=crossref)
    response=urllib.request.urlopen(request,timeout=60,context=ssl.SSLContext())
    resp=json.loads(response.read())

    #-- get author and replace unicode characters in author with plain text
    author = resp['message']['author'][0]['family']
    if sys.version_info[0] == 2:
        author = author.decode('unicode-escape')
    #-- check if author fields are initially uppercase: change to title
    author = author.title() if author.isupper() else author
    #-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in language_conversion():
        author = author.replace(UV, PV)
    #-- replace symbols
    author = re.sub(b'\s|\-|\'',b'',author.encode('utf-8')).decode('utf-8')

    #-- get publication date (prefer date when in print)
    if 'published-print' in resp['message'].keys():
        date_parts, = resp['message']['published-print']['date-parts']
    elif 'published-online' in resp['message'].keys():
        date_parts, = resp['message']['published-online']['date-parts']
    #-- extract year from date parts
    year = date_parts[0]

    #-- create citekey suffix using a DOI-based universal citekey
    #-- convert to unsigned 32-bit int if needed
    crc = binascii.crc32(doi.encode('utf-8')) & 0xffffffff
    #-- generate individual hashes
    hash1 = chr(int(ord('b') + math.floor((crc % (10*26))/26)))
    hash2 = chr(int(ord('a') + (crc % 26)))
    #-- concatenate to form DOI-based universal citekey suffix
    key = hash1 + hash2
    #-- return the final citekey from the function
    return '{0}:{1:4d}{2}'.format(author,year,key)

#-- main program that calls smart_citekey()
def main():
    #-- Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Generates Papers2-like cite keys for BibTeX using
            information from crossref.org
            """
    )
    #-- command line parameters
    parser.add_argument('doi',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    args = parser.parse_args()

    #-- run for each DOI entered after the program
    for doi in args.doi:
        if check_connection(doi):
            citekey = smart_citekey(doi)
            print(citekey)

#-- run main program
if __name__ == '__main__':
    main()
