#!/usr/bin/env python
u"""
move_journal_articles.py (09/2022)
Moves journal articles and supplements to the reference local directory

Enter Author names, journal name, publication year and volume will copy a pdf
    file (or any other file if supplement) to the reference path

CALLING SEQUENCE:
    python move_journal_articles.py --author Rignot --year 2008 \
        --journal "Nature Geoscience" --volume 1 ~/Downloads/ngeo102.pdf

    will move the file to 2008/Rignot/Rignot_Nat._Geosci.-1_2008.pdf

INPUTS:
    file to be moved into the reference path

COMMAND LINE OPTIONS:
    -A X, --author X: lead author of publication
    -J X, --journal X: corresponding publication journal
    -Y X, --year X: corresponding publication year
    -V X, --volume X: corresponding publication volume
    -N X, --number X: Corresponding publication number
    -S, --supplement: file is a supplemental file
    -C, --cleanup: Remove input file after moving

PROGRAM DEPENDENCIES:
    read_referencerc.py: Sets default file path and file format for output files
    language_conversion.py: Outputs map for converting symbols between languages

NOTES:
    Lists of journal abbreviations
        https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
    If using author name with unicode characters: put in quotes and check
        unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2019: modifications for python3 string compatibility
    Updated 07/2018: tilde-expansion of input journal file
    Updated 10/2017: use data path and data file format from referencerc file
    Written 05/2017
"""
from __future__ import print_function

import sys
import os
import re
import shutil
import argparse
import reference_toolkit

#-- PURPOSE: create directories and move a reference file after formatting
def move_journal_articles(fi,author,journal,year,volume,number,SUPPLEMENT,CLEANUP):
    #-- get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    #-- get extension from file (assume pdf if extension cannot be extracted)
    fileExtension=os.path.splitext(fi)[1] if os.path.splitext(fi)[1] else '.pdf'

    #-- file listing journal abbreviations modified from
    #-- https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
    abbreviation_file = reference_toolkit.get_data_path(['assets',
        'journal_abbreviations_webofscience-ts.txt'])
    #-- create regular expression pattern for extracting abbreviations
    arg = journal.replace(' ',r'\s+')
    rx=re.compile(r'\n{0}[\s+]?\=[\s+]?(.*?)\n'.format(arg),flags=re.IGNORECASE)
    #-- try to find journal article within filename from webofscience file
    with open(abbreviation_file, mode="r", encoding="utf8") as f:
        abbreviation_contents = f.read()

    #-- if abbreviation not found: just use the whole journal name
    #-- else use the found journal abbreviation
    if not bool(rx.search(abbreviation_contents)):
        print('Abbreviation for {0} not found'.format(journal))
        abbreviation = journal
    else:
        abbreviation = rx.findall(abbreviation_contents)[0]

    #-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        author = author.replace(UV, CV)

    #-- directory path for local file
    if SUPPLEMENT:
        directory = os.path.join(datapath,year,author,'Supplemental')
    else:
        directory = os.path.join(datapath,year,author)
    #-- check if output directory currently exist and recursively create if not
    os.makedirs(directory) if not os.path.exists(directory) else None

    #-- format used for saving articles using string formatter
    #-- 0) Author Last Name
    #-- 1) Journal Name
    #-- 2) Journal Abbreviation
    #-- 3) Publication Volume
    #-- 4) Publication Number
    #-- 5) Publication Year
    #-- 6) File Extension (will include period)
    #-- initial test case for output file (will add numbers if not unique in fs)
    args = (author, journal.replace(' ','_'), abbreviation.replace(' ','_'),
        volume, number, year, fileExtension)
    local_file = os.path.join(directory, dataformat.format(*args))
    #-- open input file and copy contents to local file
    with open(fi, 'rb') as f_in, create_unique_filename(local_file) as f_out:
        shutil.copyfileobj(f_in, f_out)
    #-- remove the input file
    os.remove(fi) if CLEANUP else None

#-- PURPOSE: open a unique filename adding a numerical instance if existing
def create_unique_filename(filename):
    #-- split filename into fileBasename and fileExtension
    fileBasename, fileExtension = os.path.splitext(filename)
    #-- create counter to add to the end of the filename if existing
    counter = 1
    while counter:
        try:
            #-- open file descriptor only if the file doesn't exist
            fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except OSError:
            pass
        else:
            print(filename.replace(os.path.expanduser('~'),'~'))
            return os.fdopen(fd, 'wb+')
        #-- new filename adds counter the between fileBasename and fileExtension
        filename = u'{0}-{1:d}{2}'.format(fileBasename, counter, fileExtension)
        counter += 1

#-- main program that calls move_journal_articles()
def main():
    #-- Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Moves a journal article to the reference local directory
            """
    )
    #-- command line parameters
    parser.add_argument('infile',
        type=lambda p: os.path.abspath(os.path.expanduser(p)),
        help='article file to be copied into the reference path')
    parser.add_argument('--author','-A',
        type=str, help='Lead author of publication')
    parser.add_argument('--journal','-J',
        type=str, help='Corresponding publication journal')
    parser.add_argument('--year','-Y',
        type=str, help='Corresponding publication year')
    parser.add_argument('--volume','-V',
        type=str, default='', help='Corresponding publication volume')
    parser.add_argument('--number','-N',
        type=str, default='', help='Corresponding publication number')
    parser.add_argument('--supplement','-S',
        default=False, action='store_true',
        help='File is an article supplement')
    parser.add_argument('--cleanup','-C',
        default=False, action='store_true',
        help='Remove input file after moving')
    args = parser.parse_args()

    #-- move article file to reference directory
    move_journal_articles(args.infile, args.author, args.journal, args.year,
        args.volume, args.number, args.supplement, args.cleanup)

#-- run main program
if __name__ == '__main__':
    main()
