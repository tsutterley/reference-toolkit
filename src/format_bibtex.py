#!/usr/bin/env python
u"""
format_bibtex.py (05/2023)
Reformats journal bibtex files into a standard form with Universal citekeys

COMMAND LINE OPTIONS:
    -O, --output: Output to new bibtex file
    -C, --cleanup: Remove the input file after formatting
    -V, --verbose: Verbose output of input files and entries

PROGRAM DEPENDENCIES:
    gen_citekeys.py: Generates Papers2-like cite keys for BibTeX
    utilities.py: Sets default file path and file format for output files
    language_conversion.py: mapping to convert symbols between languages

NOTES:
    May get capitalization incorrect for authors with lowercase first letters
        possible for cases when author fields are initially fully capitalized
    Check unicode characters with http://www.fileformat.info/
        can add more entries to the language_conversion matrix
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2019: modifications for python3 string compatibility
    Updated 07/2018: format editor fields to be "family name, given name"
    Updated 04/2018: use regular expression for splitting between authors
    Updated 02/2018: changed variable name of bibentry to bibtype
    Updated 11/2017: remove line skips and series of whitespace from title
    Updated 10/2017: if --output place file in reference directory
        use data path and data file format from referencerc file
    Updated 06/2017: Separate initials of authors if listed as singular variable
        format author names even if in family name, given name format
        added option --cleanup to remove the input RIS file after formatting
    Written 05/2017
"""
from __future__ import print_function

import sys
import re
import pathlib
import argparse
import reference_toolkit

# PURPOSE: formats an input bibtex file
def format_bibtex(file_contents, OUTPUT=False, VERBOSE=False):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # valid bibtex entry types
    bibtex_entry_types = ['article','book','booklet','conference','inbook',
        'incollection','inproceedings','manual','mastersthesis','phdthesis',
        'proceedings','techreport','unpublished','webpage']
    entry_regex = r'[?<=\@](' + '|'.join(bibtex_entry_types) + r')[\s]?\{(.*?)[\s]?,[\s]?'
    R1 = re.compile(entry_regex, flags=re.IGNORECASE)
    # bibtex fields to be printed in the output file
    bibtex_field_types = ['address','affiliation','annote','author','booktitle',
        'chapter','crossref','doi','edition','editor','howpublished','institution',
        'isbn','issn','journal','key','keywords','month','note','number','organization',
        'pages','publisher','school','series','title','type','url','volume','year']
    field_regex = r'[\s]?(' + r'|'.join(bibtex_field_types) + \
        r')[\s]?\=[\s]?[\"|\']?[\{]?[\{]?[\s]?(.*?)[\s+]?[\}]?[\}]?[\"|\']?[\s]?[\,]?[\s]?\n'
    R2 = re.compile(field_regex, flags=re.IGNORECASE)
    # sort bibtex fields in output files
    bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
        'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
        'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
        'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
        'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
        'volume':5,'year':3}
    # regular expression pattern to extract doi from webpages or "doi:"
    doi_regex = r'(doi\:[\s]?|http[s]?\:\/\/(dx\.)?doi\.org\/)?(10\.(.*?))$'
    R3 = re.compile(doi_regex, flags=re.IGNORECASE)

    # list of known compound surnames to search for
    compound_surname_regex = []
    compound_surname_regex.append(r'(?<=\s)van\s[de|den]?[\s]?(.*?)')
    compound_surname_regex.append(r'(?<=\s)von\s[de|den]?[\s]?(.*?)')
    compound_surname_regex.append(r'(?<![van|von])(?<=\s)de\s(.*?)')
    compound_surname_regex.append(r'(?<!de)(?<=\s)(la|los)\s?(.*?)')

    # create python dictionary with entry
    bibtex_entry = {}
    bibtex_key = {}
    # extract bibtex entry type and bibtex cite key
    bibtype,bibkey = R1.findall(file_contents).pop()
    bibtex_key['entrytype'] = bibtype.lower()
    bibtex_key['citekey'] = bibkey
    bibtex_field_entries = R2.findall(file_contents)
    bibtex_keywords = []
    for key,val in bibtex_field_entries:
        if (key.lower() == 'title'):
            # format titles in double curly brackets
            bibtex_entry[key.lower()] = '{{{0}}}'.format(val)
        elif (key.lower() in ('author','editor')) and (',' not in val):
            # format authors in surname, given name(s)
            current_authors = []
            for A in re.split(' and ', val, flags=re.IGNORECASE):
                # flip given name(s) and lastname
                i = None; j = 0
                # check if lastname is in list of known compound surnames
                while (i is None) and (j < len(compound_surname_regex)):
                    R = re.compile(compound_surname_regex[j],flags=re.IGNORECASE)
                    i = R.search(A).start() if R.search(A) else None
                    j += 1
                # if the lastname was compound
                if i is not None:
                    ALN,AGN = A[i:],A[:i].rstrip()
                else:
                    # flip given name(s) and lastname
                    author_fields = A.split(' ')
                    ALN = author_fields[-1]
                    AGN = ' '.join(author_fields[:-1])
                # split initials if as a single variable
                if re.match(r'([A-Z])\.([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Za-z]+)\s([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Za-z]+)\s([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.',AGN))
                # add to current authors list
                current_authors.append('{0}, {1}'.format(ALN,AGN))
            # merge authors list
            bibtex_entry[key.lower()] = ' and '.join(current_authors)
        elif (key.lower() in ('author','editor')):
            current_authors = []
            for A in re.split(' and ', val, flags=re.IGNORECASE):
                ALN,AGN = A.split(', ')
                # split initials if as a single variable
                if re.match(r'([A-Z])\.([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Za-z]+)\s([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Za-z]+)\s([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.',AGN))
                # add to current authors list
                current_authors.append('{0}, {1}'.format(ALN,AGN))
            # merge authors list
            bibtex_entry[key.lower()] = ' and '.join(current_authors)
        elif (key.lower() == 'doi') and bool(R3.match(val)):
            bibtex_entry[key.lower()] = R3.match(val).group(3)
        elif (key.lower() == 'pages') and re.match(r'(.*?)\s\-\s(.*?)$',val):
            pages, = re.findall(r'(.*?)\s\-\s(.*?)$',val)
            bibtex_entry[key.lower()] = '{0}--{1}'.format(pages[0],pages[1])
        elif (key.lower() == 'keywords'):
            bibtex_keywords.append(val)
        else:
            bibtex_entry[key.lower()] = val

    # if author fields are initially completely uppercase: change to title()
    if bibtex_entry['author'].isupper():
        bibtex_entry['author'] = bibtex_entry['author'].title()
    # extract surname of first author
    firstauthor = bibtex_entry['author'].split(',')[0]
    author_directory = bibtex_entry['author'].split(',')[0]

    # firstauthor: replace unicode characters with plain text
    # author_directory: replace unicode characters with combined unicode
    # bibtex entry for authors: replace unicode characters with latex symbols
    # bibtex entry for titles: replace unicode characters with latex symbols
    # 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        firstauthor = firstauthor.replace(LV, PV).replace(UV, PV)
        author_directory = author_directory.replace(LV, CV).replace(UV, CV)
        bibtex_entry['author'] = bibtex_entry['author'].replace(UV, LV)
        bibtex_entry['title'] = bibtex_entry['title'].replace(UV, LV)
    # encode as utf-8
    firstauthor = firstauthor.encode('utf-8')
    # remove line skips and series of whitespace from title
    bibtex_entry['title'] = re.sub(r'\s+',' ',bibtex_entry['title'])
    # remove spaces, dashes and apostrophes from author_directory
    author_directory = re.sub(r'\s','_',author_directory)
    author_directory = re.sub(r'\-|\'','',author_directory)
    year_directory, = re.findall(r'\d+',bibtex_entry['year'])

    # create list of article keywords if present in bibliography file
    if bibtex_keywords:
        bibtex_entry['keywords'] = ', '.join(bibtex_keywords)

    # extract DOI and title for generating universal citekeys
    doi = bibtex_entry['doi'] if 'doi' in bibtex_entry.keys() else None
    title = bibtex_entry['title'] if 'title' in bibtex_entry.keys() else None
    # calculate the universal citekey
    univ_key = reference_toolkit.gen_citekey(firstauthor.decode('utf-8'),
        bibtex_entry['year'], doi, title)

    # if printing to file: output bibtex file for author and year
    if OUTPUT:
        # parse universal citekey to generate output filename
        authkey,citekey,=re.findall(r'(\D+)\:(\d+\D+)',univ_key).pop()
        # output directory
        bibtex_dir = datapath.joinpath(year_directory,author_directory)
        bibtex_dir.mkdir(parents=True, exist_ok=True)
        # create file object for output file
        bibtex_file = bibtex_dir.joinpath(f'{authkey}-{citekey}.bib')
        fid = bibtex_file.open(mode='w', encoding='utf-8')
        print(f'  --> {str(compressuser(bibtex_file))}') if VERBOSE else None
    else:
        fid = sys.stdout

    # print the bibtex citation
    print('@{0}{{{1},'.format(bibtex_key['entrytype'],univ_key),file=fid)
    # sort output bibtex files as listed above
    field_indices = [bibtex_field_sort[b] for b in bibtex_entry.keys()]
    field_tuple = zip(field_indices,bibtex_entry.keys(),bibtex_entry.values())
    # for each field within the entry
    for s,k,v in sorted(field_tuple):
        # make sure ampersands are in latex format (marked with symbol)
        v = re.sub(r'(?<=\s)\&',r'\\\&',v) if re.search(r'(?<=\s)\&',v) else v
        # do not put the month field in brackets
        if (k == 'month'):
            print('{0} = {1},'.format(k,v.lower()),file=fid)
        else:
            print('{0} = {{{1}}},'.format(k,v),file=fid)
    print('}', file=fid)

    # close the output file
    if OUTPUT:
        fid.close()

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

# main program that calls format_bibtex()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Reformats journal BibTeX files into a standard form with
            Universal citekeys
            """
    )
    # command line parameters
    parser.add_argument('infile',
        type=pathlib.Path, nargs='+',
        help='BibTeX file to be copied into the reference path')
    parser.add_argument('--output','-O',
        default=False, action='store_true',
        help='Output to bibtex files')
    parser.add_argument('--cleanup','-C',
        default=False, action='store_true',
        help='Remove input BibTeX file after conversion')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Verbose output of input and output files')
    args = parser.parse_args()

    # for each file entered
    for FILE in args.infile:
        # run for the input file
        print(str(compressuser(FILE))) if args.verbose else None
        with FILE.open(mode='r', encoding='utf-8') as f:
            file_contents = f.read()
        try:
            format_bibtex(re.sub('(\s+)\n','\n',file_contents),
                OUTPUT=args.output, VERBOSE=args.verbose)
        except:
            pass
        else:
            # remove the input file
            FILE.unlink() if args.cleanup else None

# run main program
if __name__ == '__main__':
    main()
