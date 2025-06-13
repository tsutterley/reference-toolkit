#!/usr/bin/env python
u"""
smart_citekeys.py (06/2025)
Generates Papers2-like cite keys for BibTeX using information
from crossref.org or datacite.org

Enter DOI's of journals to generate "universal" keys

CALLING SEQUENCE:
    python smart_citekeys.py "10.1038/ngeo102"
    will result in Rignot:2008ct as the citekey
  
COMMAND LINE OPTIONS:
    -A X, --author-field X: Author field in JSON response

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        http://python-future.org/

PROGRAM DEPENDENCIES:
    gen_citekeys.py: Generates Papers2-like cite keys for BibTeX
    language_conversion.py: mapping to convert symbols between languages

NOTES:
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js
    Check unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
    Updated 06/2025: can try fetching JSON data from datacite.org
        added option to choose the author field from the JSON response
    Updated 11/2023: updated ssl context to fix deprecation errors
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
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

import re
import argparse
import reference_toolkit

# PURPOSE: create a Papers2-like cite key using the DOI
def smart_citekey(doi, AUTHOR_FIELD='author'):

    # fetch json data for the given doi
    resp = reference_toolkit.utilities.citeproc_json(doi)

    # get author and replace unicode characters in author with plain text
    try:
        author = resp[AUTHOR_FIELD][0]['family']
        # check if author fields are initially uppercase: change to title
        author = author.title() if author.isupper() else author
    except KeyError:
        # check if author is a literal and do not modify case
        author = resp[AUTHOR_FIELD][0]['literal']

    # 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        author = author.replace(UV, PV)
    # replace symbols
    author = re.sub(rb'\s|\-|\'',rb'',author.encode('utf-8')).decode('utf-8')

    # get publication date (prefer date when in print)
    for P in ['published-print','published-online','issued']:
        try:
            date_parts, = resp[P]['date-parts']
            # extract year from date parts
            year = date_parts[0]
        except:
            pass
        else:
            break

    # create citekey suffix using a DOI-based universal citekey
    return reference_toolkit.gen_citekey(author, year, doi, None)

# main program that calls smart_citekey()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Generates Papers2-like cite keys for BibTeX using
            information from crossref.org
            """
    )
    # command line parameters
    parser.add_argument('doi',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--author-field','-A',
        default='author', type=str, 
        help='Author field in JSON response')
    args = parser.parse_args()

    # run for each DOI entered after the program
    for doi in args.doi:
        citekey = smart_citekey(doi, AUTHOR_FIELD=args.author_field)
        print(citekey)

# run main program
if __name__ == '__main__':
    main()
