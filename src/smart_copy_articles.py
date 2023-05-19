#!/usr/bin/env python
u"""
smart_copy_articles.py (05/2023)
Copies journal articles and supplements from a website to a local directory
     using information from crossref.org

Enter DOI's of journals to copy a file from a URL to the reference path

CALLING SEQUENCE:
    python smart_copy_articles.py --doi 10.1038/ngeo102 \
        https://www.nature.com/ngeo/journal/v1/n2/pdf/ngeo102.pdf

    will download the copy to 2008/Rignot/Rignot_Nat._Geosci.-1_2008.pdf

INPUTS:
    url to file to be copied into the reference path

COMMAND LINE OPTIONS:
    -D X, --doi X: DOI of the publication
    -S, --supplement: file is a supplemental file

PROGRAM DEPENDENCIES:
    read_referencerc.py: Sets default file path and file format for output files
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
    Updated 07/2018: using urllib.request for python3
    Updated 10/2017: use data path and data file format from referencerc file
    Updated 09/2017: use timeout of 20 to prevent socket.timeout
    Updated 06/2017: use language_conversion for journal name
    Forked 05/2017 from copy_journal_articles.py to use info from crossref.org
    Updated 05/2017: Convert special characters with language_conversion program
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
import urllib.parse
import urllib.request
import reference_toolkit

# PURPOSE: check internet connection and URL
def check_connection(remote_url, timeout=20):
    # attempt to connect to remote url
    try:
        urllib.request.urlopen(remote_url,
            timeout=timeout,
            context=ssl.SSLContext()
        )
    except urllib.request.HTTPError:
        raise RuntimeError(f'Check URL: {remote_url}')
    except urllib.request.URLError:
        raise RuntimeError('Check internet connection')
    else:
        return True

# PURPOSE: create directories and copy a reference file after formatting
def smart_copy_articles(remote_file,doi,SUPPLEMENT):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # input remote file scrubbed of any additional html information
    fi = pathlib.Path(re.sub(r'\?[\_a-z]{1,4}\=(.*?)$','',remote_file))
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
    author = re.sub('\s','_',author); author = re.sub(r'\-|\'','',author)

    # get publication date (prefer date when in print)
    if 'published-print' in resp['message'].keys():
        date_parts, = resp['message']['published-print']['date-parts']
    elif 'published-online' in resp['message'].keys():
        date_parts, = resp['message']['published-online']['date-parts']
    # extract year from date parts and convert to string
    year = '{0:4d}'.format(date_parts[0])

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

    # chunked transfer encoding size
    CHUNK = 16 * 1024
    # open url and copy contents to local file using chunked transfer encoding
    # transfer should work properly with ascii and binary data formats
    headers = {'User-Agent':"Magic Browser"}
    request = urllib.request.Request(remote_file, headers=headers)
    f_in = urllib.request.urlopen(request, timeout=20, context=context)
    with create_unique_filename(local_file) as f_out:
        shutil.copyfileobj(f_in, f_out, CHUNK)
    f_in.close()

# PURPOSE: open a unique filename adding a numerical instance if existing
def create_unique_filename(filename):
    # create counter to add to the end of the filename if existing
    counter = 1
    while counter:
        try:
            # open file descriptor only if the file doesn't exist
            fd = filename.open(mode='xb')
        except OSError:
            pass
        else:
            print(str(compressuser(filename)))
            return fd
        # new filename adds counter the between fileBasename and fileExtension
        filename = f'{filename.stem}-{counter:d}{filename.suffix}'
        counter += 1

def compressuser(filename):
    """
    Tilde-compresses a file to be relative to the home directory

    Parameters
    ----------
    filename: str
        outptu filename
    """
    filename = pathlib.Path(filename).expanduser().absolute()
    try:
        relative_to = filename.relative_to(pathlib.Path().home())
    except ValueError as exc:
        return filename
    else:
        return pathlib.Path('~').joinpath(relative_to)

# main program that calls smart_copy_articles()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Copies a journal article from a website to the reference
            local directory using information from crossref.org
            """
    )
    # command line parameters
    parser.add_argument('url',
        type=str, help='url to article to be copied into the reference path')
    parser.add_argument('--doi','-D',
        type=str, help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--supplement','-S',
        default=False, action='store_true',
        help='File is an article supplement')
    args = parser.parse_args()

    # check connection to url and then download article
    if check_connection(args.url):
        smart_copy_articles(args.url,args.doi,args.supplement)

# run main program
if __name__ == '__main__':
    main()
