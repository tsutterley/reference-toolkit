#!/usr/bin/env python
u"""
open_doi.py (12/2020)
Opens the webpages and crossref.org API webpages associated with a Digital
    Object Identifier (DOI)

CALLING SEQUENCE:
    python open_doi.py 10.1038/ngeo102

COMMAND LINE OPTIONS:
    -C, --crossref: Open crossref.org API associated with a DOI
    -V, --verbose: Verbose output of webpages opened

UPDATE HISTORY:
    Updated 12/2020: using argparse to set command line options
    Written 10/2017
"""
from __future__ import print_function
import future.standard_library

import sys
import os
import argparse
import posixpath
import webbrowser
with future.standard_library.hooks():
    import urllib.parse

#-- PURPOSE: open webpage associated with a Digital Object Identifier (DOI)
def doiopen(DOI, VERBOSE=False):
    #-- Open URL for DOI in a new tab, if browser window is already open
    URL = posixpath.join('https://doi.org',DOI)
    print(URL) if VERBOSE else None
    webbrowser.open_new_tab(URL)

#-- PURPOSE: open crossref.org API associated with a DOI
def crossrefopen(DOI, VERBOSE=False):
    #-- Open URL for DOI in a new tab, if browser window is already open
    URL = posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    print(URL) if VERBOSE else None
    webbrowser.open_new_tab(URL)

#-- main program that calls doiopen() and crossrefopen()
def main():
    #-- Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Opens the webpages and crossref.org API webpages
            associated with a Digital Object Identifier (DOI)
            """
    )
    #-- command line parameters
    parser.add_argument('doi',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--crossref','-C',
        default=False, action='store_true',
        help='Open crossref.org API associated with a DOI')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Verbose output of webpages opened')
    args = parser.parse_args()

    #-- run for each DOI entered after the program
    for DOI in args.doi:
        doiopen(DOI, VERBOSE=args.verbose)
        crossrefopen(DOI, VERBOSE=args.verbose) if args.crossref else None

#-- run main program
if __name__ == '__main__':
    main()
