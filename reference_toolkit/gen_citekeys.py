#!/usr/bin/env python
u"""
gen_citekeys.py (09/2022)
Generates Papers2-like cite keys for BibTeX

Enter Author names and publication years
Uses DOI's or titles to generate "universal" keys
Alternatively can generate a random suffix

CALLING SEQUENCE:
    python gen_citekeys.py --author=Rignot --year=2008 \
        --doi="10.1038/ngeo102"

    will result in Rignot:2008ct as the citekey

    python gen_citekeys.py --author=RIgnot --year=2008 \
        --title="Direct Evidence Of Flying Birds Found In Sky Pictures"

    will result in Rignot:2008vv as the citekey

COMMAND LINE OPTIONS:
    -A X, --author X: authors of publications
    -Y X, --year X: corresponding publication years
    -D X, --doi X: corresponding DOI of the publication
    -T X, --title X: corresponding title of the publication
        if the DOI is not available

PROGRAM DEPENDENCIES:
    language_conversion.py: Outputs map for converting symbols between languages

NOTES:
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js
    Check unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 10/2019: strip title of leading and trailing whitespace before hash
    Updated 07/2019: modifications for python3 string compatibility
    Updated 10/2017: use modulus of 0xffffffff (4294967295)
    Updated 05/2017: removing whitespace from authors.
        Converting special characters with language_conversion program
    Updated 02/2017: universal citekeys from DOI or title hashes
        (will create the same citekeys as the Papers2 application)
    Written 02/2017
"""
from __future__ import print_function

import re
import math
import string
import random
import argparse
import binascii
from reference_toolkit.language_conversion import language_conversion

#-- PURPOSE: create a Papers2-like cite key using the DOI
def gen_citekey(author,year,doi,title):
    #-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in language_conversion():
        author = author.replace(UV, PV)
    #-- replace symbols
    author = re.sub(b'\s|\-|\'',b'',author.encode('utf-8')).decode('utf-8')

    #-- create citekey suffix first attempting:
    #-- a DOI-based universal citekey
    #-- then attempting a title-based universal citekey
    #-- finally generating a random citekey (non-universal)
    if doi:
        #-- convert to unsigned 32-bit int if needed
        crc = binascii.crc32(doi.encode('utf-8')) & 0xffffffff
        #-- generate individual hashes
        hash1 = chr(int(ord('b') + math.floor((crc % (10*26))/26)))
        hash2 = chr(int(ord('a') + (crc % 26)))
        #-- concatenate to form DOI-based universal citekey suffix
        key = hash1 + hash2
    elif title:
        #-- scrub special characters from title and set as lowercase
        title = re.sub(r'[\_\-\=\/\|\.\{\}]',' ',title.lower())
        title = ''.join(re.findall(r'[a-zA-Z0-9\s]',title))
        #-- convert to unsigned 32-bit int if needed
        crc = binascii.crc32(title.strip().encode('utf-8')) & 0xffffffff
        #-- generate individual hashes
        hash1 = chr(int(ord('t') + math.floor((crc % (4*26))/26)))
        hash2 = chr(int(ord('a') + (crc % 26)))
        #-- concatenate to form title-based universal citekey suffix
        key = hash1 + hash2
    else:
        key = ''.join(random.sample(string.ascii_lowercase,2))
    #-- return the final citekey from the function
    return '{0}:{1}{2}'.format(author,year,key)

#-- main program that calls gen_citekey()
def main():
    #-- Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Copies a journal article from a website to the reference
            local directory
            """
    )
    #-- command line parameters
    parser.add_argument('--author','-A',
        type=str, nargs='+',
        help='Lead author of publication')
    parser.add_argument('--year','-Y',
        type=str, nargs='+',
        help='Corresponding publication year')
    parser.add_argument('--doi','-D',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--title','-T',
        type=str, nargs='+',
        help='Corresponding publication title')
    args = parser.parse_args()

    #-- if not using DOIs to set citekeys
    if args.doi is None:
        args.doi = [None]*len(args.author)
    #-- if not using titles to set citekeys
    if args.title is None:
        args.title = [None]*len(args.author)

    #-- run for each author-year pair
    for A,Y,D,T in zip(args.author,args.year,args.doi,args.title):
        citekey = gen_citekey(A,Y,D,T)
        print(citekey)

#-- run main program
if __name__ == '__main__':
    main()
