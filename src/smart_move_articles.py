#!/usr/bin/env python
u"""
smart_move_articles.py (05/2023)
Moves journal articles and supplements to the reference local directory
    using information from crossref.org

Enter DOI's of journals to move a file to the reference path

CALLING SEQUENCE:
    python smart_move_articles.py --doi 10.1038/ngeo102 ~/Downloads/ngeo102.pdf

    will move the file to 2008/Rignot/Rignot_Nat._Geosci.-1_2008.pdf

INPUTS:
    file to be moved into the reference path

COMMAND LINE OPTIONS:
    -D X, --doi X: DOI of the publication
    -S, --supplement: file is a supplemental file
    -C, --cleanup: Remove the input file after moving

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        http://python-future.org/

PROGRAM DEPENDENCIES:
    utilities.py: Sets default file path and file format for output files
    language_conversion.py: mapping to convert symbols between languages

NOTES:
    Lists of journal abbreviations
        https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
    If using author name with unicode characters: put in quotes and check
        unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2018: using python3 urllib.request with future library
        tilde-expansion of input journal file
    Updated 10/2017: use data path and data file format from referencerc file
    Updated 09/2017: use timeout of 20 to prevent socket.timeout
    Updated 06/2017: use language_conversion for journal name
    Forked 05/2017 from move_journal_articles.py to use info from crossref.org
    Written 05/2017
"""
from __future__ import print_function

import re
import ssl
import json
import shutil
import pathlib
import argparse
import posixpath
import urllib.request
import urllib.parse
import reference_toolkit

# PURPOSE: create directories and move a reference file after formatting
def smart_move_articles(fi,doi,SUPPLEMENT,CLEANUP):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # get extension from file (assume pdf if extension cannot be extracted)
    fileExtension = fi.suffix if fi.suffix else '.pdf'

    # ssl context
    context = ssl.SSLContext()
    # open connection with crossref.org for DOI
    crossref = posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    request = urllib.request.Request(url=crossref)
    response = urllib.request.urlopen(request,timeout=60,context=context)
    resp = json.loads(response.read())

    # get author and replace unicode characters in author with plain text
    author = resp['message']['author'][0]['family']
    # check if author fields are initially uppercase: change to title
    author = author.title() if author.isupper() else author
    # get journal name
    journal, = resp['message']['container-title']
    # 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        author = author.replace(UV, CV)
        journal = journal.replace(UV, PV)
    # remove spaces, dashes and apostrophes
    author = re.sub(r'\s','_',author); author = re.sub('\-|\'','',author)

    # get publication date (prefer date when in print)
    if 'published-print' in resp['message'].keys():
        date_parts, = resp['message']['published-print']['date-parts']
    elif 'published-online' in resp['message'].keys():
        date_parts, = resp['message']['published-online']['date-parts']
    # extract year from date parts and convert to string
    year = f'{date_parts[0]:4d}'

    # get publication volume and number
    vol = resp['message']['volume'] if 'volume' in resp['message'].keys() else ''
    num = resp['message']['issue'] if 'issue' in resp['message'].keys() else ''

    # file listing journal abbreviations modified from
    # https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
    abbreviation_file = reference_toolkit.get_data_path(['assets',
        'journal_abbreviations_webofscience-ts.txt'])
    # create regular expression pattern for extracting abbreviations
    arg = journal.replace(' ',r'\s+')
    rx = re.compile(rf'\n{arg}[\s+]?\=[\s+]?(.*?)\n', flags=re.IGNORECASE)
    # try to find journal article within filename from webofscience file
    with abbreviation_file.open(mode="r", encoding="utf8") as f:
        abbreviation_contents = f.read()

    # if abbreviation not found: just use the whole journal name
    # else use the found journal abbreviation
    if not bool(rx.search(abbreviation_contents)):
        print(f'Abbreviation for {journal} not found')
        abbreviation = journal
    else:
        abbreviation = rx.findall(abbreviation_contents)[0]

    # directory path for local file
    if SUPPLEMENT:
        directory = datapath.joinpath(year,author,'Supplemental')
    else:
        directory = datapath.joinpath(year,author)
    # check if output directory currently exist and recursively create if not
    directory.mkdir(parents=True, exist_ok=True)

    # format used for saving articles using string formatter
    # 0) Author Last Name
    # 1) Journal Name
    # 2) Journal Abbreviation
    # 3) Publication Volume
    # 4) Publication Number
    # 5) Publication Year
    # 6) File Extension (will include period)
    # initial test case for output file (will add numbers if not unique in fs)
    args = (author, journal.replace(' ','_'), abbreviation.replace(' ','_'),
        vol, num, year, fileExtension)
    local_file = directory.joinpath(dataformat.format(*args))

    # open input file and copy contents to local file
    with open(fi, 'rb') as f_in, \
        reference_toolkit.create_unique_filename(local_file) as f_out:
            shutil.copyfileobj(f_in, f_out)
    # remove the input file
    fi.unlink() if CLEANUP else None

# main program that calls smart_move_articles()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Moves a journal article to the reference local directory
            using information from crossref.org
            """
    )
    # command line parameters
    parser.add_argument('infile',
        type=pathlib.Path,
        help='article file to be copied into the reference path')
    parser.add_argument('--doi','-D',
        type=str, help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--supplement','-S',
        default=False, action='store_true',
        help='File is an article supplement')
    parser.add_argument('--cleanup','-C',
        default=False, action='store_true',
        help='Remove input file after moving')
    args = parser.parse_args()

    # move article file to reference directory
    smart_move_articles(args.infile, args.doi, args.supplement, args.cleanup)

# run main program
if __name__ == '__main__':
    main()
