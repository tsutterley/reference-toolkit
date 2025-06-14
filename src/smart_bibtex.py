#!/usr/bin/env python
u"""
smart_bibtex.py (06/2025)
Creates a bibtex entry by parsing JSON responses
from crossref.org or datacite.org

Enter DOI's of journals to generate a bibtex entry with "universal" keys
https://github.com/CrossRef/rest-api-doc

CALLING SEQUENCE:
    python smart_bibtex.py 10.1038/ngeo102

COMMAND LINE OPTIONS:
    -A X, --author-field X: Author field in JSON response
    -O, --output: Output to bibtex files (default to terminal)
    -V, --verbose: Verbose output of output files (if output)

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        http://python-future.org/

PROGRAM DEPENDENCIES:
    gen_citekeys.py: Generates Papers2-like cite keys for BibTeX
    utilities.py: Sets default file path and file format for output files
    language_conversion.py: mapping to convert symbols between languages

NOTES:
    May get capitalization incorrect for authors with lowercase first letters
        possible for cases when author fields are initially fully capitalized
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
    Updated 06/2025: can try fetching JSON data from datacite.org
        added option to choose the author field from the JSON response
    Updated 01/2025: put issn search within a try/except statement
    Updated 11/2024: use f-strings for print statements
    Updated 11/2023: updated ssl context to fix deprecation errors
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 09/2022: drop python2 compatibility
    Updated 12/2020: using argparse to set command line options
    Updated 07/2018: using python3 urllib.request with future library
    Updated 11/2017: remove line skips and series of whitespace from title
    Updated 10/2017: if --output place file in reference directory
        use data path and data file format from referencerc file
    Updated 09/2017: use timeout of 20 to prevent socket.timeout
    Updated 06/2017: use language_conversion for journal name
        separate initials of authors if listed as singular variable
    Written 06/2017
"""
from __future__ import print_function

import sys
import re
import datetime
import argparse
import reference_toolkit

# PURPOSE: create a formatted bibtex entry for a doi
def smart_bibtex(doi,
        AUTHOR_FIELD='author',
        OUTPUT=False,
        VERBOSE=False
    ):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)

    # fetch json data for the given doi
    resp = reference_toolkit.utilities.citeproc_json(doi)

    # sort bibtex fields in output
    bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
        'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
        'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
        'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
        'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
        'volume':5,'year':3}
    # map between JSON type entries and bibtex entries
    bibtex_entry_map = {
        'journal-article':'article', 'article':'article',
        'book-chapter':'inbook', 'book':'book', 'monograph':'book',
        'proceedings-article':'inproceedings',
        'dataset':'misc'
    }

    # create python dictionaries with entries and citekey
    current_entry = {}
    current_key = {}
    # create lists of authors, pages and keywords
    current_authors = []
    current_pages = [None,None]
    current_keywords = []

    # bibtex entry type
    current_key['entrytype'] = bibtex_entry_map[resp['type']]
    # add entered doi to current_entry dictionary
    current_entry['doi'] = doi

    # check if author fields are initially uppercase: change to title
    for a in resp[AUTHOR_FIELD]:
        # check if author is given as a literal string
        if 'literal' in a.keys():
            # do not change case or order of literal strings
            current_authors.append(a['literal'])
            continue
        # if family and given names are present, use them
        family = a['family'].title() if a['family'].isupper() else a['family']
        given = a['given'].title() if a['given'].isupper() else a['given']
        # split initials if as a single variable
        if re.match(r'([A-Z])\.([A-Z])\.', given):
            given = ' '.join(re.findall(r'([A-Z])\.([A-Z])\.', given).pop())
        elif re.match(r'([A-Za-z]+)\s([A-Z])\.', given):
            given = ' '.join(re.findall(r'([A-Za-z]+)\s([A-Z])\.', given).pop())
        elif re.match(r'([A-Z])\.', given):
            given = ' '.join(re.findall(r'([A-Z])\.',given))
        # add to current authors list
        current_authors.append(f'{family}, {given}')

    # get publication date (prefer date when in print)
    for P in ['published-print','published-online','issued']:
        try:
            date_parts, = resp[P]['date-parts']
        except:
            pass
        else:
            break

    # extract year from date parts and convert to string
    current_entry['year'] = f'{date_parts[0]:4d}'
    # months of the year
    if (len(date_parts) > 1):
        # month = second entry
        dt = datetime.datetime.strptime(f'{date_parts[1]:02d}','%m')
        current_entry['month'] = dt.strftime('%b').lower()

    # get journal name
    if 'container-title' in resp.keys() and bool(resp['container-title']):
        if isinstance(resp['container-title'], list):
            current_entry['journal'], = resp['container-title']
        elif isinstance(resp['container-title'], str):
            current_entry['journal'] = resp['container-title']
    # get entry/article title
    if 'title' in resp.keys() and bool(resp['title']):
        if isinstance(resp['title'], list):
            current_entry['title'], = resp['title']
        elif isinstance(resp['title'], str):
            current_entry['title'] = resp['title']

    # get publication volume
    if 'volume' in resp.keys() and bool(resp['volume']):
        current_entry['volume'] = resp['volume']

    # get publication number
    if 'issue' in resp.keys() and bool(resp['issue']):
        current_entry['number'] = resp['issue']

    # get URL
    if 'URL' in resp.keys() and bool(resp['URL']):
        current_entry['url'] = resp['URL']

    # get pages
    if 'page' in resp.keys() and bool(resp['page']):
        if bool(re.search(r'\d+',resp['page'])):
            # add starting page to current_pages array
            pages = [int(p) for p in re.findall(r'\d+',resp['page'])]
            current_pages[0] = pages[0]
            if (len(pages) > 1):
                current_pages[1] = pages[1]

    # get ISSN (prefer issn for print)
    for T in['print','electronic']:
        try:
            current_entry['issn'], = [i['value'] for i in
                resp['issn-type'] if i['type'] == T]
        except:
            pass
        else:
            break

    # get publisher
    if 'publisher' in resp.keys() and bool(resp['publisher']):
        current_entry['publisher'] = resp['publisher']

    # extract surname of first author
    firstauthor = str(current_authors[0].split(',')[0])
    author_directory = str(current_authors[0].split(',')[0])
    # create entry for authors
    current_entry['author'] = ' and '.join(current_authors)
    # firstauthor: replace unicode characters with plain text
    # author_directory: replace unicode characters with combined unicode
    # bibtex entry for authors: replace unicode characters with latex symbols
    # 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in reference_toolkit.language_conversion():
        firstauthor = firstauthor.replace(UV, PV)
        author_directory = author_directory.replace(UV, CV)
        current_entry['author'] = current_entry['author'].replace(UV, LV)
        if 'title' in current_entry.keys():
            current_entry['title'] = current_entry['title'].replace(UV, LV)
        if 'journal' in current_entry.keys():
            current_entry['journal'] = current_entry['journal'].replace(UV, LV)

    # remove line skips and series of whitespace from title
    if 'title' in current_entry.keys():
        current_entry['title'] = re.sub(r'\s+',r' ',current_entry['title'])
    # remove spaces, dashes and apostrophes from author_directory
    author_directory = re.sub(r'\s',r'_',author_directory)
    author_directory = re.sub(r'\-|\'',r'',author_directory)
    year_directory, = re.findall(r'\d+',current_entry['year'])

    # create list of article keywords if present in bibliography file
    if current_keywords:
        current_entry['keywords'] = ', '.join(current_keywords)

    # calculate the universal citekey
    current_key['citekey'] = reference_toolkit.gen_citekey(firstauthor,
        current_entry['year'], doi, None)

    # create entry for pages
    if (current_pages[0] is None) and (current_pages[1] is None):
        # no entry for pages available
        pass
    elif (current_pages[1] is None):
        current_entry['pages'] = str(current_pages[0])
    else:
        current_entry['pages'] = f'{current_pages[0]}--{current_pages[1]}'

    # if printing to file: output bibtex file for author and year
    if OUTPUT:
        # parse universal citekey to generate output filename
        authkey,citekey, = re.findall(r'(\D+)\:(\d+\D+)',current_key['citekey']).pop()
        # output directory
        bibtex_dir = datapath.joinpath(year_directory,author_directory)
        bibtex_dir.mkdir(parents=True, exist_ok=True)
        # create file object for output file
        bibtex_file = bibtex_dir.joinpath(f'{authkey}-{citekey}.bib')
        fid = bibtex_file.open(mode='w', encoding='utf-8')
        compressed = reference_toolkit.compressuser(bibtex_file)
        print(f'  --> {str(compressed)}') if VERBOSE else None
    else:
        fid = sys.stdout

    # print the bibtex citation
    entrytype, citekey = current_key['entrytype'], current_key['citekey']
    print(f'@{entrytype}{{{citekey},', file=fid)
    # sort output bibtex files as listed above
    field_indices = [bibtex_field_sort[b] for b in current_entry.keys()]
    field_tuple=zip(field_indices,current_entry.keys(),current_entry.values())
    # for each field within the entry
    for s,k,v in sorted(field_tuple):
        # make sure ampersands are in latex format
        v = re.sub(r'(?<=\s)\&',r'\\\&',v) if re.search(r'(?<=\s)\&',v) else v
        # do not put the month field in brackets
        if (k == 'month'):
            print(f'{k} = {v.rstrip()},', file=fid)
        elif (k == 'title'):
            print(f'{k} = {{{{{v.rstrip()}}}}},', file=fid)
        else:
            print(f'{k} = {{{v.strip()}}},', file=fid)
    print('}', file=fid)

    # close the output file
    if OUTPUT:
        fid.close()

# main program that calls smart_bibtex()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Creates a bibtex entry using information from
            crossref.org or datacite.org
            """
    )
    # command line parameters
    parser.add_argument('doi',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--author-field','-A',
        default='author', type=str, 
        help='Author field in JSON response')
    parser.add_argument('--output','-O',
        default=False, action='store_true',
        help='Output to bibtex file')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Verbose output of output files')
    args = parser.parse_args()

    # run for each DOI entered after the program
    for doi in args.doi:
        smart_bibtex(doi,
            AUTHOR_FIELD=args.author_field,
            OUTPUT=args.output,
            VERBOSE=args.verbose)

# run main program
if __name__ == '__main__':
    main()
