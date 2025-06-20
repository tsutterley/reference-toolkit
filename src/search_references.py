#!/usr/bin/env python
u"""
search_references.py (11/2024)
Reads bibtex files for each article in a given set of years to search for
    keywords, authors, journal, etc using regular expressions

CALLING SEQUENCE:
    python search_references.py -A Rignot -F -Y 2008 -J "Nature Geoscience"
        will return the bibtex entry for this publication

COMMAND LINE OPTIONS:
    -A X, --author X: last name of author of publications to search
    -F, --first: Search only first authors
    -Y X, --year X: years of publication to search (can be regular expression)
    -K X, --keyword X: keywords to search
    -J X, --journal X: publication journals to search
    -D X, --doi X: search for a specific set of DOIs
    -O, --open: open publication directory with found matches
    -W, --webpage: open publication webpage with found matches
    -E X, --export X: export all found matches to a single bibtex file
    -R, --reverse: reverse the search returns

PROGRAM DEPENDENCIES:
    utilities.py: Sets default file path and file format for output files
    language_conversion.py: mapping to convert symbols between languages

UPDATE HISTORY:
    Updated 06/2025: can reverse the order of the search results
    Updated 11/2024: use f-strings for print statements
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2019: modifications for python3 string compatibility
    Updated 06/2018: added DOI search using the -D or --doi options
    Updated 11/2017: added export command to print matches to a single file
    Updated 10/2017: use data path and data file format from referencerc file
    Updated 07/2017: print number of matching articles in search query
    Updated 06/2017: added webbrowser to open the webpage of found articles
    Written 06/2017
"""
from __future__ import print_function

import sys
import re
import os
import pathlib
import argparse
import posixpath
import subprocess
import webbrowser
import reference_toolkit

# Reads bibtex files for each article stored in the working directory for
# keywords, authors, journal, etc
def search_references(AUTHOR, JOURNAL, YEAR, KEYWORDS, DOI, FIRST=False,
    OPEN=False, WEBPAGE=False, EXPORT=None, REVERSE=False):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # bibtex fields to be printed in the output file
    bibtex_field_types = ['address','affiliation','annote','author',
        'booktitle','chapter','crossref','doi','edition','editor',
        'howpublished','institution','isbn','issn','journal','key',
        'keywords','month','note','number','organization','pages',
        'publisher','school','series','title','type','url','volume','year']
    field_regex = r'[\s]?(' + '|'.join(bibtex_field_types) + \
        r')[\s]?\=[\s]?[\{]?[\{]?(.*?)[\}]?[\}]?[\,]?[\s]?\n'
    R1 = re.compile(field_regex, flags=re.IGNORECASE)

    # compile regular expression operators for input search terms
    if AUTHOR and FIRST:
        R2 = re.compile(r'^'+'|'.join(AUTHOR), flags=re.IGNORECASE)
    elif AUTHOR:
        R2 = re.compile(r'|'.join(AUTHOR), flags=re.IGNORECASE)
    if JOURNAL:
        R3 = re.compile(r'|'.join(JOURNAL), flags=re.IGNORECASE)
    if KEYWORDS:
        R4 = re.compile(r'|'.join(KEYWORDS), flags=re.IGNORECASE)

    # if exporting matches to a single file or standard output (to terminal)
    if EXPORT:
        EXPORT = pathlib.Path(EXPORT).expanduser().absolute()
        fid = EXPORT.open(mode="w", encoding="utf8")
    else:
        fid = sys.stdout

    # find directories of years
    regex_years = r'|'.join(YEAR) if YEAR else r'\d+'
    years = sorted([sd for sd in datapath.iterdir() if
        re.match(regex_years, sd.name) and sd.is_dir()])
    # reverse the order of the years
    if REVERSE:
        years = reversed(years)
    # number of matches
    match_count = 0
    query_count = 0
    for Y in years:
        # find author directories in year
        authors = [sd for sd in Y.iterdir() if sd.is_dir()]
        for A in sorted(authors):
            # find bibtex files
            bibtex_files = [fi for fi in A.iterdir()
                if re.match(r'(.*?)-(.*?).bib$',fi.name)]
            # read each bibtex file
            for bibtex_file in bibtex_files:
                with bibtex_file.open(mode="r", encoding="utf-8") as f:
                    bibtex_entry = f.read()
                # extract bibtex fields
                bibtex_field_entries = R1.findall(bibtex_entry)
                entry = {}
                for key,val in bibtex_field_entries:
                    # replace latex symbols with unicode characters
                    # 1: latex, 2: combining unicode, 3: unicode, 4: plain
                    for LV, CV, UV, PV in reference_toolkit.language_conversion():
                        val = val.replace(LV,CV)
                    # add to current entry dictionary
                    entry[key.lower()] = val
                # use search terms to find journals
                # Search bibtex author entries for AUTHOR
                F1 = R2.search(entry['author']) if AUTHOR else True
                # Search bibtex journal entries for JOURNAL
                F2 = False if JOURNAL else True
                if ('journal' in entry.keys() and JOURNAL):
                    F2 = R3.search(entry['journal'])
                # Search bibtex title entries for KEYWORDS
                F3 = R4.search(entry['title']) if KEYWORDS else True
                # Search bibtex keyword entries for KEYWORDS
                F4 = False if KEYWORDS else True
                if ('keywords' in entry.keys() and KEYWORDS):
                    F4 = R4.search(entry['keywords'])
                # Search bibtex DOI entries for a specific set of DOI's
                F5 = False if DOI else True
                if ('doi' in entry.keys() and DOI):
                    F5 = entry['doi'] in DOI
                # print the complete bibtex entry if search was found
                if bool(F1) & bool(F2) & (bool(F3) | bool(F4)) & bool(F5):
                    print(bibtex_entry, file=fid)
                    file_opener(bibtex_file) if OPEN else None
                    # URL to open if WEBPAGE (from url or using doi)
                    if 'url' in entry.keys():
                        URL = entry['url']
                    elif 'doi' in entry.keys():
                        URL = posixpath.join('https://doi.org',entry['doi'])
                    # Open URL in a new tab, if browser window is already open
                    webbrowser.open_new_tab(URL) if (WEBPAGE and URL) else None
                    # add to total match count
                    match_count += 1
                # add to total query count
                query_count += 1
    # print the number of matching and number of queried references
    print(f'Matching references = {match_count:d} out of {query_count:d} queried')
    # close the exported bibtex file
    fid.close() if EXPORT else None

# PURPOSE: platform independent file opener
def file_opener(filename):
    if (sys.platform == "win32"):
        os.startfile(filename, "explore")
    elif (sys.platform == "darwin"):
        subprocess.call(["open", "-R", filename])
    else:
        subprocess.call(["xdg-open", filename])

# main program that calls search_references()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Reads BibTeX files for each article in a given set of
            years to search for keywords, authors, journal, etc using regular
            expressions
            """
    )
    # command line parameters
    parser.add_argument('--author','-A',
        type=str, nargs='+',
        help='Author of publications to search')
    parser.add_argument('--first','-F',
        default=False, action='store_true',
        help='Search only lead authors')
    parser.add_argument('--journal','-J',
        type=str, nargs='+',
        help='Publication journals to search')
    parser.add_argument('--year','-Y',
        type=str, nargs='+',
        help='Years of publication to search')
    parser.add_argument('--keyword','-K',
        type=str, nargs='+',
        help='Keywords to search')
    parser.add_argument('--doi','-D',
        type=str, nargs='+',
        help='Search for specific Digital Object Identifiers (DOIs)')
    parser.add_argument('--open','-O',
        default=False, action='store_true',
        help='Open publication directory with found matches')
    parser.add_argument('--webpage','-W',
        default=False, action='store_true',
        help='Open publication webpage with found matches')
    parser.add_argument('--export','-E',
        type=pathlib.Path,
        help='Export found matches to a single BibTeX file')
    parser.add_argument('--reverse','-R',
        default=False, action='store_true',
        help='Open publication webpage with found matches')
    args = parser.parse_args()

    # search references for requested fields
    search_references(args.author, args.journal, args.year, args.keyword,
        args.doi, FIRST=args.first, OPEN=args.open, WEBPAGE=args.webpage,
        EXPORT=args.export, REVERSE=args.reverse)

# run main program
if __name__ == '__main__':
    main()
