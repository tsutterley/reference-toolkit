#!/usr/bin/env python
u"""
smart_bibtex.py (12/2020)
Creates a bibtex entry using information from crossref.org

Enter DOI's of journals to generate a bibtex entry with "universal" keys
https://github.com/CrossRef/rest-api-doc

CALLING SEQUENCE:
    python smart_bibtex.py 10.1038/ngeo102

COMMAND LINE OPTIONS:
    -O, --output: Output to bibtex files (default to terminal)
    -V, --verbose: Verbose output of output files (if output)

PYTHON DEPENDENCIES:
    future: Compatibility layer between Python 2 and Python 3
        http://python-future.org/

PROGRAM DEPENDENCIES:
    gen_citekeys.py: Generates Papers2-like cite keys for BibTeX
    read_referencerc.py: Sets default file path and file format for output files
    language_conversion.py: Outputs map for converting symbols between languages

NOTES:
    May get capitalization incorrect for authors with lowercase first letters
        possible for cases when author fields are initially fully capitalized
    Papers2 Universal Citekey generation javascript
        https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
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
import future.standard_library

import sys
import os
import re
import ssl
import json
import inspect
import datetime
import argparse
import posixpath
from gen_citekeys import gen_citekey
from read_referencerc import read_referencerc
from language_conversion import language_conversion
with future.standard_library.hooks():
    import urllib.request
    import urllib.parse

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- PURPOSE: check internet connection and URL
def check_connection(doi):
    #-- attempt to connect to remote url
    remote_url = posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    try:
        urllib.request.urlopen(remote_url,timeout=20,context=ssl.SSLContext())
    except urllib.request.HTTPError:
        raise RuntimeError('Check URL: {0}'.format(remote_url))
    except urllib.request.URLError:
        raise RuntimeError('Check internet connection')
    else:
        return True

#-- PURPOSE: create a formatted bibtex entry for a doi
def smart_bibtex(doi, OUTPUT=False, VERBOSE=False):
    #-- get reference filepath and reference format from referencerc file
    datapath,dataformat=read_referencerc(os.path.join(filepath,'.referencerc'))
    #-- open connection with crossref.org for DOI
    crossref = posixpath.join('https://api.crossref.org','works',
        urllib.parse.quote_plus(doi))
    context = ssl.SSLContext()
    request = urllib.request.Request(url=crossref)
    response = urllib.request.urlopen(request,timeout=60,context=context)
    resp = json.loads(response.read())

    #-- sort bibtex fields in output
    bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
        'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
        'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
        'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
        'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
        'volume':5,'year':3}
    #-- map between crossref type entries and bibtex entries
    bibtex_entry_map = {'journal-article':'article','book-chapter':'inbook',
        'proceedings-article':'inproceedings'}

    #-- create python dictionaries with entries and citekey
    current_entry = {}
    current_key = {}
    #-- create lists of authors, pages and keywords
    current_authors = []
    current_pages = [None,None]
    current_keywords = []

    #-- bibtex entry type
    current_key['entrytype'] = bibtex_entry_map[resp['message']['type']]
    #-- add entered doi to current_entry dictionary
    current_entry['doi'] = doi

    #-- check if author fields are initially uppercase: change to title
    for a in resp['message']['author']:
        family = a['family'].title() if a['family'].isupper() else a['family']
        given = a['given'].title() if a['given'].isupper() else a['given']
        #-- split initials if as a single variable
        if re.match('([A-Z])\.([A-Z])\.', given):
            given = ' '.join(re.findall('([A-Z])\.([A-Z])\.', given).pop())
        elif re.match('([A-Za-z]+)\s([A-Z])\.', given):
            given = ' '.join(re.findall('([A-Za-z]+)\s([A-Z])\.', given).pop())
        elif re.match('([A-Z])\.', given):
            given = ' '.join(re.findall('([A-Z])\.',given))
        #-- add to current authors list
        current_authors.append(u'{0}, {1}'.format(family, given))

    #-- get publication date (prefer date when in print)
    for P,T in zip(['published-print','published-online'],['print','electronic']):
        try:
            date_parts, = resp['message'][P]['date-parts']
        except:
            pass
        else:
            break

    #-- extract year from date parts and convert to string
    current_entry['year'] = '{0:4d}'.format(date_parts[0])
    #-- months of the year
    if (len(date_parts) > 1):
        #-- month = second entry
        dt = datetime.datetime.strptime('{0:02d}'.format(date_parts[1]),'%m')
        current_entry['month'] = dt.strftime('%b').lower()

    #-- get journal name and article title
    current_entry['journal'], = resp['message']['container-title']
    current_entry['title'], = resp['message']['title']

    #-- get publication volume
    if 'volume' in resp['message'].keys():
        current_entry['volume'] = resp['message']['volume']
    #-- get publication number
    if 'issue' in resp['message'].keys():
        current_entry['number'] = resp['message']['issue']
    #-- get URL
    if 'URL' in resp['message'].keys():
        current_entry['url'] = resp['message']['URL']
    #-- get pages
    if 'page' in resp['message'].keys():
        if bool(re.search('\d+',resp['message']['page'])):
            #-- add starting page to current_pages array
            pages = [int(p) for p in re.findall('\d+',resp['message']['page'])]
            current_pages[0] = pages[0]
            if (len(pages) > 1):
                current_pages[1] = pages[1]
    #-- get ISSN (prefer issn for print)
    if 'issn-type' in resp['message'].keys():
        current_entry['issn'], = [i['value'] for i in
            resp['message']['issn-type'] if i['type'] == T]
    #-- get publisher
    if 'publisher' in resp['message'].keys():
        current_entry['publisher'] = resp['message']['publisher']

    #-- extract surname of first author
    firstauthor = current_authors[0].split(',')[0]
    author_directory = current_authors[0].split(',')[0]
    #-- create entry for authors
    current_entry['author'] = ' and '.join(current_authors)
    #-- firstauthor: replace unicode characters with plain text
    #-- author_directory: replace unicode characters with combined unicode
    #-- bibtex entry for authors: replace unicode characters with latex symbols
    #-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    for LV, CV, UV, PV in language_conversion():
        firstauthor = firstauthor.replace(UV, PV)
        author_directory = author_directory.replace(UV, CV)
        current_entry['author'] = current_entry['author'].replace(UV, LV)
        current_entry['title'] = current_entry['title'].replace(UV, LV)
        current_entry['journal'] = current_entry['journal'].replace(UV, LV)
    #-- encode as utf-8
    firstauthor = firstauthor.encode('utf-8')
    #-- remove line skips and series of whitespace from title
    current_entry['title'] = re.sub('\s+',' ',current_entry['title'])
    #-- remove spaces, dashes and apostrophes from author_directory
    author_directory = re.sub('\s','_',author_directory)
    author_directory = re.sub('\-|\'','',author_directory)
    year_directory, = re.findall('\d+',current_entry['year'])

    #-- create list of article keywords if present in bibliography file
    if current_keywords:
        current_entry['keywords'] = ', '.join(current_keywords)

    #-- calculate the universal citekey
    current_key['citekey']=gen_citekey(firstauthor,current_entry['year'],doi,None)

    #-- create entry for pages
    if (current_pages[0] is None) and (current_pages[1] is None):
        current_entry['pages'] = 'n/a--n/a'
    elif (current_pages[1] is None):
        current_entry['pages'] = '{0}'.format(current_pages[0])
    else:
        current_entry['pages'] = '{0}--{1}'.format(*current_pages)

    #-- if printing to file: output bibtex file for author and year
    if OUTPUT:
        #-- parse universal citekey to generate output filename
        authkey,citekey,=re.findall('(\D+)\:(\d+\D+)',current_key['citekey']).pop()
        bibtex_file = '{0}-{1}.bib'.format(authkey,citekey)
        #-- output directory
        bibtex_dir = os.path.join(datapath,year_directory,author_directory)
        os.makedirs(bibtex_dir) if not os.path.exists(bibtex_dir) else None
        #-- create file object for output file
        fid = open(os.path.join(bibtex_dir,bibtex_file),'w')
        print('  --> {0}'.format(bibtex_file)) if VERBOSE else None
    else:
        fid = sys.stdout

    #-- print the bibtex citation
    print('@{0}{{{1},'.format(current_key['entrytype'],current_key['citekey']),file=fid)
    #-- sort output bibtex files as listed above
    field_indices = [bibtex_field_sort[b] for b in current_entry.keys()]
    field_tuple=zip(field_indices,current_entry.keys(),current_entry.values())
    #-- for each field within the entry
    for s,k,v in sorted(field_tuple):
        #-- make sure ampersands are in latex format
        v = re.sub('(?<=\s)\&','\\\&',v) if re.search('(?<=\s)\&',v) else v
        #-- do not put the month field in brackets
        if (k == 'month'):
            print('{0} = {1},'.format(k,v.rstrip()),file=fid)
        elif (k == 'title'):
            print('{0} = {{{{{1}}}}},'.format(k,v.rstrip()),file=fid)
        else:
            print('{0} = {{{1}}},'.format(k,v.rstrip()),file=fid)
    print('}',file=fid)

    #-- close the output file
    if OUTPUT:
        fid.close()

#-- main program that calls smart_bibtex()
def main():
    #-- Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Creates a bibtex entry using information from
            crossref.org
            """
    )
    #-- command line parameters
    parser.add_argument('doi',
        type=str, nargs='+',
        help='Digital Object Identifier (DOI) of the publication')
    parser.add_argument('--output','-O',
        default=False, action='store_true',
        help='Output to bibtex file')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Verbose output of output files')
    args = parser.parse_args()

    #-- run for each DOI entered after the program
    for DOI in args.doi:
        if check_connection(DOI):
            smart_bibtex(DOI, OUTPUT=args.output, VERBOSE=args.verbose)

#-- run main program
if __name__ == '__main__':
    main()
