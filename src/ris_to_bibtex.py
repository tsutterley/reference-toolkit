#!/usr/bin/env python
u"""
ris_to_bibtex.py (05/2023)
Converts RIS bibliography files into bibtex files with Universal citekeys
    https://en.wikipedia.org/wiki/RIS_(file_format)

COMMAND LINE OPTIONS:
    -O, --output: Output to bibtex files (default to terminal)
    -C, --cleanup: Remove the input file after formatting
    -V, --verbose: Verbose output of input and output files

PROGRAM DEPENDENCIES:
    gen_citekey.py: Generates Papers2-like cite keys for BibTeX
    utilities.py: Sets default file path and file format for output files
    language_conversion.py: mapping to convert symbols between languages

NOTES:
    May get capitalization incorrect for authors with lowercase first letters
        possible for cases when author fields are initially fully capitalized
    Checked to be working with RIS files from Nature and Journal of Glaciology
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2019: modifications for python3 string compatibility
    Updated 07/2018: added editor fields as valid RIS entries with format FN,GN
    Updated 04/2018: don't use abbreviations for valid journal names
    Updated 11/2017: remove line skips and series of whitespace from title
    Updated 10/2017: if --output place file in reference directory
        use data path and data file format from referencerc file
    Updated 06/2017: added T2 for RIS entries with journal in T2 field
        some RIS files use LP for the end page (not just EP)
        separate initials of authors if listed as singular variable
        added option --cleanup to remove the input RIS file after conversion
    Updated 05/2017: Convert special characters with language_conversion program
    Written 05/2017
"""
from __future__ import print_function

import sys
import re
import pathlib
import argparse
import datetime
import reference_toolkit

def ris_to_bibtex(file_contents, OUTPUT=False, VERBOSE=False):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # easily mappable RIS and bibtex fields
    bibtex_field_map = {'JF':'journal','JO':'journal','T2':'journal','VL':'volume',
        'IS':'number','PB':'publisher','SN':'issn','UR':'url'}
    # map between RIS TY entries and bibtex entries
    bibtex_entry_map = {'JOUR':'article','EJOU':'article','BOOK':'book',
        'CHAP':'inbook','CONF':'proceedings','RPRT':'techreport',
        'THES':'phdthesis'}
    # fields of interest for parsing an RIS file
    RIS_fields = ['TY','AU','A1','A2','ED','TI','T1','T2','JA','JF','JO','PY','Y1',
        'VL','IS','SP','EP','LP','PB','SN','UR','L3','M3','ER','DO','DOI','N1',
        'KW','AB','KW']
    # regular expression for reading RIS files
    RIS_regex = r'({0})\s+\-\s+(.*?)[\s]?$'.format('|'.join(RIS_fields))
    R1 = re.compile(RIS_regex, flags=re.IGNORECASE)
    # regular expression pattern to extract doi from webpages or "doi:"
    doi_regex = r'(doi\:[\s]?|http[s]?\:\/\/(dx\.)?doi\.org\/)?(10\.(.*?))$'
    R2 = re.compile(doi_regex, flags=re.IGNORECASE)
    # sort bibtex fields in output
    bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
        'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
        'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
        'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
        'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
        'volume':5,'year':3}

    # list of known compound surnames to search for
    compound_surname_regex = []
    compound_surname_regex.append(r'(?<=\s)van\s[de|den]?[\s]?(.*?)')
    compound_surname_regex.append(r'(?<=\s)von\s[de|den]?[\s]?(.*?)')
    compound_surname_regex.append(r'(?<![van|von])(?<=\s)de\s(.*?)')
    compound_surname_regex.append(r'(?<!de)(?<=\s)(la|los)\s?(.*?)')

    # create python dictionaries with entries and citekey
    current_entry = {}
    current_key = {}
    # set initial setting for DOI to None
    current_entry['doi'] = ''
    # list of authors for current entry
    current_authors = []
    current_editors = []
    current_keywords = []
    current_pages = [None,None]
    # read each line to create bibtex entry
    RIS_field_entries = [i for i in file_contents if R1.match(i)]
    for line in RIS_field_entries:
        RIS_field,RIS_value = R1.findall(line).pop()
        # check if easily mappable field
        if RIS_field in bibtex_field_map.keys():
            # associated bibtex key
            bibtex_key = bibtex_field_map[RIS_field]
            current_entry[bibtex_key] = RIS_value
        elif (RIS_field == 'TY'):
            # RIS entry type
            current_key['entrytype'] = bibtex_entry_map[RIS_value]
        elif RIS_field in ('TI','T1'):
            # format titles in double curly brackets
            current_entry['title'] = '{{{0}}}'.format(RIS_value)
        elif RIS_field in ('AU','A1','A2','ED'):
            # check if author fields are initially uppercase: change to title
            RIS_value = RIS_value.title() if RIS_value.isupper() else RIS_value
            # output formatted author field = lastname, given name(s)
            if re.match(r'(.*?),\s(.*?)',RIS_value):
                # add to authors list
                if RIS_field in ('ED'):
                    current_editors.append(RIS_value)
                elif RIS_field in ('AU','A1','A2'):
                    current_authors.append(RIS_value)
            else:
                # flip given name(s) and lastname
                i = None; j = 0
                # check if lastname is in list of known compound surnames
                while (i is None) and (j < len(compound_surname_regex)):
                    R=re.compile(compound_surname_regex[j],flags=re.IGNORECASE)
                    i=R.search(RIS_value).start() if R.search(RIS_value) else None
                    j += 1
                # if the lastname was compound
                if i is not None:
                    ALN,AGN = RIS_value[i:],RIS_value[:i].rstrip()
                else:
                    # flip given name(s) and lastname
                    author_fields = RIS_value.split(' ')
                    ALN = author_fields[-1]
                    AGN = ' '.join(author_fields[:-1])
                # split initials if as a single variable
                if re.match(r'([A-Z])\.([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Za-z]+)\s([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Za-z]+)\s([A-Z])\.',AGN).pop())
                elif re.match(r'([A-Z])\.', AGN):
                    AGN=' '.join(re.findall(r'([A-Z])\.',AGN))
                # add to current authors or editors list
                if RIS_field in ('ED'):
                    current_editors.append('{0}, {1}'.format(ALN,AGN))
                elif RIS_field in ('AU','A1','A2'):
                    current_authors.append('{0}, {1}'.format(ALN,AGN))
        elif RIS_field in ('PY','Y1'):
            # partition between publication date to YY/MM/DD
            cal_date = [int(d) for d in re.findall(r'\d+',RIS_value)]
            # year = first entry
            current_entry['year'] = '{0:4d}'.format(cal_date[0])
            # months of the year
            if (len(cal_date) > 1):
                # month = second entry
                dt=datetime.datetime.strptime('{0:02d}'.format(cal_date[1]),'%m')
                current_entry['month'] = dt.strftime('%b').lower()
        elif (RIS_field == 'SP') and bool(re.search(r'\d+',RIS_value)):
            # add starting page to current_pages array
            pages = [int(p) for p in re.findall(r'\d+',RIS_value)]
            current_pages[0] = pages[0]
            if (len(pages) > 1):
                current_pages[1] = pages[1]
        elif RIS_field in ('EP','LP') and bool(re.search(r'\d+',RIS_value)):
            # add ending page to current_pages array
            current_pages[1] = RIS_value
        elif RIS_field in ('L3','DO','N1','M3','DOI') and bool(R2.search(RIS_value)):
            # extract DOI
            current_entry['doi'] = R2.search(RIS_value).group(3)
        elif (RIS_field == 'KW'):
            # add to keywords list
            current_keywords.append(RIS_value)
        elif VERBOSE:
            # print all other fields and values
            print(RIS_field, RIS_value)

    # extract surname of first author
    firstauthor = current_authors[0].split(',')[0]
    author_directory = current_authors[0].split(',')[0]
    # create entry for authors and editors if applicable
    current_entry['author'] = ' and '.join(current_authors)
    if current_editors:
        current_entry['editor'] = ' and '.join(current_editors)

    # firstauthor: replace unicode characters with plain text
    # bibtex entry for authors: replace unicode characters with latex symbols
    # 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        firstauthor = firstauthor.replace(UV, PV)
        author_directory = author_directory.replace(UV, CV)
        current_entry['author'] = current_entry['author'].replace(UV, LV)
        current_entry['title'] = current_entry['title'].replace(UV, LV)
        current_entry['journal'] = current_entry['journal'].replace(UV, LV)
        if current_editors:
            current_entry['editor'] = current_entry['editor'].replace(UV, LV)
    # encode as utf-8
    firstauthor = firstauthor.encode('utf-8')
    # remove line skips and series of whitespace from title
    current_entry['title'] = re.sub(r'\s+',r' ',current_entry['title'])
    # remove spaces, dashes and apostrophes from author_directory
    author_directory = re.sub(r'\s',r'_',author_directory)
    author_directory = re.sub(r'\-|\'',r'',author_directory)
    year_directory, = re.findall(r'\d+',current_entry['year'])

    # create list of article keywords if present in bibliography file
    if current_keywords:
        current_entry['keywords'] = ', '.join(current_keywords)

    # calculate the universal citekey
    current_key['citekey'] = reference_toolkit.gen_citekey(firstauthor.decode('utf-8'),
        current_entry['year'], current_entry['doi'], current_entry['title'])

    # create entry for pages
    if (current_pages[0] is None) and (current_pages[1] is None):
        current_entry['pages'] = 'n/a--n/a'
    elif (current_pages[1] is None):
        current_entry['pages'] = '{0}'.format(current_pages[0])
    else:
        current_entry['pages'] = '{0}--{1}'.format(*current_pages)

    # if printing to file: output bibtex file for author and year
    if OUTPUT:
        # parse universal citekey to generate output filename
        authkey,citekey,=re.findall(r'(\D+)\:(\d+\D+)',current_key['citekey']).pop()
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
    print('@{0}{{{1},'.format(current_key['entrytype'],current_key['citekey']),file=fid)
    # sort output bibtex files as listed above
    field_indices = [bibtex_field_sort[b] for b in current_entry.keys()]
    field_tuple=zip(field_indices,current_entry.keys(),current_entry.values())
    # for each field within the entry
    for s,k,v in sorted(field_tuple):
        # make sure ampersands are in latex format
        v = re.sub(r'(?<=\s)\&','\\\&',v) if re.search(r'(?<=\s)\&',v) else v
        # do not put the month field in brackets
        # do not print empty fields
        if (k == 'month'):
            print('{0} = {1},'.format(k,v.rstrip()),file=fid)
        elif not v:
            continue
        else:
            print('{0} = {{{1}}},'.format(k,v.rstrip()),file=fid)
    print('}',file=fid)

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

# main program that calls ris_to_bibtex()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Converts RIS bibliography files into bibtex files with
            Universal citekeys
            """
    )
    # command line parameters
    parser.add_argument('infile',
        type=pathlib.Path, nargs='+',
        help='RIS file to be copied into the reference path')
    parser.add_argument('--output','-O',
        default=False, action='store_true',
        help='Output to bibtex files')
    parser.add_argument('--cleanup','-C',
        default=False, action='store_true',
        help='Remove input RIS file after conversion')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Verbose output of input and output files')
    args = parser.parse_args()

    # for each file entered
    for FILE in args.infile:
        # run for the input file
        with FILE.open(mode='r', encoding='utf-8') as f:
            file_contents = f.readlines()
        try:
            ris_to_bibtex(file_contents,
                OUTPUT=args.output,
                VERBOSE=args.verbose)
        except:
            pass
        else:
            # remove the input file
            FILE.unlink() if args.cleanup else None


# run main program
if __name__ == '__main__':
    main()
