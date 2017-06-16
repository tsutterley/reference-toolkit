#!/usr/bin/env python
u"""
smart_bibtex.py (06/2017)
Creates a entry using information from crossref.org

Enter DOI's of journals to generate a bibtex entry with "universal" keys
https://github.com/CrossRef/rest-api-doc

CALLING SEQUENCE:
	python smart_bibtex.py 10.1038/ngeo102

COMMAND LINE OPTIONS:
	-O, --output: Output to bibtex files (default to terminal)
	-T, --type: pubication type (print or electronic).  Prefer print
	-V, --verbose: Verbose output of output files (if output)

PROGRAM DEPENDENCIES:
	language_conversion.py: Outputs map for converting symbols between languages
	gen_citekeys.py: Generates Papers2-like cite keys for BibTeX

NOTES:
	May get capitalization incorrect for authors with lowercase first letters
		possible for cases when author fields are initially fully capitalized
	Papers2 Universal Citekey generation javascript
		https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
	Updated 06/2017: use language_conversion for journal name
		separate initials of authors if listed as singular variable
	Written 06/2017
"""
from __future__ import print_function

import sys
import os
import re
import json
import getopt
import urllib2
from gen_citekeys import gen_citekey
from language_conversion import language_conversion

#-- PURPOSE: check internet connection and URL
def check_connection(doi):
	#-- attempt to connect to remote url
	remote_url = 'https://api.crossref.org/works/{0}'.format(doi)
	try:
		urllib2.urlopen(remote_url,timeout=1)
	except urllib2.HTTPError:
		raise RuntimeError('Check URL: {0}'.format(remote_url))
	except urllib2.URLError:
		raise RuntimeError('Check internet connection')
	else:
		return True

#-- PURPOSE: create a formatted bibtex entry for a doi
def smart_bibtex(doi, OUTPUT=False, TYPE='print', VERBOSE=False):
	#-- open connection with crossref.org for DOI
	req = urllib2.Request(url='https://api.crossref.org/works/{0}'.format(doi))
	resp = json.loads(urllib2.urlopen(req).read())

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
	if TYPE == 'print' and 'published-print' in resp['message'].keys():
		date_parts, = resp['message']['published-print']['date-parts']
	elif TYPE == 'electronic' and 'published-online' in resp['message'].keys():
		date_parts, = resp['message']['published-online']['date-parts']
	#-- extract year from date parts and convert to string
	current_entry['year'] = '{0:4d}'.format(date_parts[0])
	#-- months of the year
	M=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
	if (len(date_parts) > 1):
		#-- month = second entry
		current_entry['month'] = M[date_parts[1]-1]

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
			resp['message']['issn-type'] if i['type'] == TYPE]
	#-- get publisher
	if 'publisher' in resp['message'].keys():
		current_entry['publisher'] = resp['message']['publisher']

	#-- extract surname of first author
	firstauthor = current_authors[0].split(',')[0]
	#-- create entry for authors
	current_entry['author'] = ' and '.join(current_authors)
	#-- firstauthor: replace unicode characters with plain text
	#-- bibtex entry for authors: replace unicode characters with latex symbols
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		firstauthor = firstauthor.replace(UV, PV)
		current_entry['author'] = current_entry['author'].replace(UV, LV)
		current_entry['title'] = current_entry['title'].replace(UV, LV)
		current_entry['journal'] = current_entry['journal'].replace(UV, LV)
	#-- encode as utf-8
	firstauthor = firstauthor.encode('utf-8')

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

	#-- parse universal citekey
	authkey,citekey=re.findall('(\D+)\:(\d+\D+)',current_key['citekey']).pop()
	#-- if printing to file: output bibtex file for author and year
	fid = open('{0}-{1}.bib'.format(authkey,citekey),'w') if OUTPUT else sys.stdout
	if VERBOSE and OUTPUT:
		print('  --> {0}-{1}.bib'.format(authkey,citekey))

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

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -O, --output\tOutput to bibtex files (default to terminal)')
	print(' --T, --type: pubication type (print or electronic)')
	print(' -V, --verbose\tVerbose output of output files\n')

#-- main program that calls smart_bibtex()
def main():
	long_options = ['help','output','type=','verbose']
	optlist,arglist=getopt.getopt(sys.argv[1:],'hOT:V',long_options)
	#-- command line arguments
	OUTPUT = False
	TYPE = 'print'
	VERBOSE = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-O','--output'):
			OUTPUT = True
		elif opt in ('-T','--type'):
			TYPE = arg.lower()
		elif opt in ('-V','--verbose'):
			VERBOSE = True

	#-- run for each DOI entered after the program
	for DOI in arglist:
		if check_connection(DOI):
			smart_bibtex(DOI, OUTPUT=OUTPUT, TYPE=TYPE, VERBOSE=VERBOSE)

#-- run main program
if __name__ == '__main__':
	main()
