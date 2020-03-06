#!/usr/bin/env python
u"""
export_library.py (02/2018)
Exports library of individual BibTeX files into a single sorted BibTeX file

CALLING SEQUENCE:
    python export_library.py --sort=author --export=bibtex_library.bib

COMMAND LINE OPTIONS:
    -S X, --sort=X: sort output entries by
        year: Year of publication
        author: First Author Lastname (default)
        type: BibTeX Entry Types (article, book, etc)
    -E X, --export=X: output BibTeX filename (default: standard output)

PROGRAM DEPENDENCIES:
    read_referencerc.py: Sets default file path and file format for output files

UPDATE HISTORY:
    Written 02/2018
"""
from __future__ import print_function

import sys
import re
import os
import time
import getopt
import inspect
from read_referencerc import read_referencerc

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- PURPOSE: create a named list with named attributes for each BibTeX entry
class BibTeX:
    def __init__(self, citekey, year, type, entry):
        self.citekey = citekey
        self.year = year
        self.type = type
        self.entry = entry
    def __repr__(self):
        return repr((self.citekey, self.year, self.type, self.entry))

#-- Reads BibTeX files for each article stored in the working directory
#-- exports as a single file sorted by BibTeX key
def export_library(SORT=None, EXPORT=None):
    #-- get reference filepath and reference format from referencerc file
    datapath,dataformat=read_referencerc(os.path.join(filepath,'.referencerc'))
    #-- valid BibTeX entry types
    bibtex_entry_types = ['article','book','booklet','conference','inbook',
        'incollection','inproceedings','manual','mastersthesis','phdthesis',
        'proceedings','techreport','unpublished','webpage']
    entry_regex = '[?<=\@](' + '|'.join([i for i in bibtex_entry_types]) + \
        ')\{(.*?),'
    R1 = re.compile(entry_regex, flags=re.IGNORECASE)

    #-- if exporting to a single file or standard output
    fid = open(os.path.expanduser(EXPORT), 'w') if EXPORT else sys.stdout

    #-- sorting operators
    if (SORT == 'author'):
        sorting_operator = 'lambda self: self.citekey'
    elif (SORT == 'year'):
        sorting_operator = 'lambda self: self.year'
    elif (SORT == 'type'):
        sorting_operator = 'lambda self: self.type'

    #-- Python list with all BibTeX entries
    bibtex_entries = []
    #-- iterate over yearly directories
    years = [sd for sd in os.listdir(datapath) if re.match('\d+',sd) and
        os.path.isdir(os.path.join(datapath,sd))]
    for Y in sorted(years):
        #-- find author directories in year
        authors = [sd for sd in os.listdir(os.path.join(datapath,Y)) if
            os.path.isdir(os.path.join(datapath,Y,sd))]
        for A in sorted(authors):
            #-- find BibTeX files within author directory
            bibtex_files = [fi for fi in os.listdir(os.path.join(datapath,Y,A))
                if re.match('(.*?)-(.*?).bib$',fi)]
            #-- read each BibTeX file
            for fi in bibtex_files:
                with open(os.path.join(datapath,Y,A,fi), 'r') as f:
                    bibtex_entry = f.read()
                #-- extract BibTeX citekeys
                bibtype,bibkey = R1.findall(bibtex_entry.lower()).pop()
                #-- add BibTeX entry to list with named attributes
                bibtex_entries.append(BibTeX(bibkey,Y,bibtype,bibtex_entry))

    #-- print header with date created and total number of BibTeX entries
    print(time.strftime('%%%% BibTeX File Created on %Y-%m-%d',
        time.localtime()), file=fid)
    print('%% Number of Entries: {0:d}\n'.format(len(bibtex_entries)), file=fid)
    #-- sort by the chosen operator and print to file
    for key in sorted(bibtex_entries, key=eval(sorting_operator)):
        print(key.entry, file=fid)

    #-- close the exported BibTeX file
    fid.close() if EXPORT else None

#-- PURPOSE: help module to describe the optional input parameters
def usage():
    print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
    print(' -S X, --sort=X\t\tSort output entries by:')
    print('\tyear: Year of publication')
    print('\tauthor: First Author Lastname (default)')
    print('\ttype: BibTeX Entry Type (article, book, etc)')
    print(' -E X, --export=X\tOutput BibTeX filename\n')

#-- main program that calls export_library()
def main():
    long_options = ['help','sort=','export=']
    optlist,arglist = getopt.getopt(sys.argv[1:],'hS:E:',long_options)

    #-- default: sort by author and print to standard output
    SORT = 'author'
    EXPORT = None
    #-- for each input argument
    for opt, arg in optlist:
        if opt in ('-h','--help'):
            usage()
            sys.exit()
        elif opt in ('-S','--sort'):
            SORT = arg
        elif opt in ('-E','--export'):
            EXPORT = arg

    #-- export references to a single file
    export_library(SORT=SORT, EXPORT=EXPORT)

#-- run main program
if __name__ == '__main__':
    main()
