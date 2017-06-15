#!/usr/bin/env python
u"""
ris_to_bibtex.py (06/2017)
Converts RIS bibliography files into bibtex files with Universal citekeys
	https://en.wikipedia.org/wiki/RIS_(file_format)

COMMAND LINE OPTIONS:
	-O, --output: Output to bibtex files (default to terminal)
	-V, --verbose: Verbose output of input and output files

PROGRAM DEPENDENCIES:
	gen_citekey.py: Generates Papers2-like cite keys for BibTeX
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	May get capitalization incorrect for authors with lowercase first letters
		possible for cases when author fields are initially fully capitalized
	Checked to be working with RIS files from Nature and Journal of Glaciology
	Papers2 Universal Citekey generation javascript
		https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
	Updated 06/2017: added T2 for RIS entries with journal in T2 field
		some RIS files use LP for the end page (not just EP)
		separate initials of authors if listed as singular variable
	Updated 05/2017: Convert special characters with language_conversion program
	Written 05/2017
"""
from __future__ import print_function

import sys
import re
import os
import getopt
from gen_citekeys import gen_citekey
from language_conversion import language_conversion

def ris_to_bibtex(file_contents, OUTPUT=False, VERBOSE=False):
	#-- easily mappable RIS and bibtex fields
	bibtex_field_map = {'JA':'journal','JO':'journal','T2':'journal',
		'VL':'volume','IS':'number','PB':'publisher','SN':'issn','UR':'url'}
	#-- map between RIS TY entries and bibtex entries
	bibtex_entry_map = {'JOUR':'article','BOOK':'book','CHAP':'inbook',
		'CONF':'proceedings','RPRT':'techreport','THES':'phdthesis'}
	#-- fields of interest for parsing an RIS file
	RIS_fields = ['TY','AU','A1','TI','T1','T2','JA','JO','PY','Y1','VL','IS',
		'SP','EP','LP','PB','SN','UR','L3','M3','ER','DO','N1','KW','AB','KW']
	#-- regular expression for reading RIS files
	RIS_regex = '({0})\s+\-\s+(.*?)[\s]?$'.format('|'.join(RIS_fields))
	R1 = re.compile(RIS_regex, flags=re.IGNORECASE)
	#-- regular expression pattern to extract doi from webpages or "doi:"
	doi_regex = '(doi\:[\s]?|http[s]?\:\/\/(dx\.)?doi\.org\/)?(10\.(.*?))$'
	R2 = re.compile(doi_regex, flags=re.IGNORECASE)
	#-- months of the year
	M=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
	#-- sort bibtex fields in output
	bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
		'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
		'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
		'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
		'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
		'volume':5,'year':3}

	#-- list of known compound surnames to search for
	compound_surname_regex = []
	compound_surname_regex.append('(?<=\s)van\s[de|den]?[\s]?(.*?)')
	compound_surname_regex.append('(?<=\s)von\s[de|den]?[\s]?(.*?)')
	compound_surname_regex.append('(?<![van|von])(?<=\s)de\s(.*?)')
	compound_surname_regex.append('(?<!de)(?<=\s)(la|los)\s?(.*?)')

	#-- create python dictionaries with entries and citekey
	current_entry = {}
	current_key = {}
	#-- set initial setting for DOI to None
	current_entry['doi'] = ''
	#-- list of authors for current entry
	current_authors = []
	current_keywords = []
	current_pages = [None,None]
	#-- read each line to create bibtex entry
	RIS_field_entries = [i for i in file_contents if R1.match(i)]
	for line in RIS_field_entries:
		RIS_field,RIS_value = R1.findall(line).pop()
		#-- check if easily mappable field
		if RIS_field in bibtex_field_map.keys():
			#-- associated bibtex key
			bibtex_key = bibtex_field_map[RIS_field]
			current_entry[bibtex_key] = RIS_value
		elif (RIS_field == 'TY'):
			#-- RIS entry type
			current_key['entrytype'] = bibtex_entry_map[RIS_value]
		elif RIS_field in ('TI','T1'):
			#-- format titles in double curly brackets
			current_entry['title'] = '{{{0}}}'.format(RIS_value)
		elif RIS_field in ('AU','A1'):
			#-- check if author fields are initially uppercase: change to title
			RIS_value = RIS_value.title() if RIS_value.isupper() else RIS_value
			#-- output formatted author field = lastname, given name(s)
			if re.match('(.*?),\s(.*?)',RIS_value):
				#-- add to authors list
				current_authors.append(RIS_value)
			else:
				#-- flip given name(s) and lastname
				i = None; j = 0
				#-- check if lastname is in list of known compound surnames
				while (i is None) and (j < len(compound_surname_regex)):
					R=re.compile(compound_surname_regex[j],flags=re.IGNORECASE)
					i=R.search(RIS_value).start() if R.search(RIS_value) else None
					j += 1
				#-- if the lastname was compound
				if i is not None:
					ALN,AGN = RIS_value[i:],RIS_value[:i].rstrip()
				else:
					#-- flip given name(s) and lastname
					author_fields = RIS_value.split(' ')
					ALN = author_fields[-1]
					AGN = ' '.join(author_fields[:-1])
				#-- split initials if as a single variable
				if re.match('([A-Z])\.([A-Z])\.', AGN):
					AGN = ' '.join(re.findall('([A-Z])\.([A-Z])\.', AGN).pop())
				elif re.match('([A-Z])\.', AGN):
					AGN, = re.findall('([A-Z])\.', AGN).pop()
				#-- add to current authors list
				current_authors.append('{0}, {1}'.format(ALN,AGN))
		elif RIS_field in ('PY','Y1'):
			#-- partition between publication date to YY/MM/DD
			cal_date = [int(d) for d in re.findall('\d+',RIS_value)]
			#-- year = first entry
			current_entry['year'] = '{0:4d}'.format(cal_date[0])
			if (len(cal_date) > 1):
				#-- month = second entry
				current_entry['month'] = M[cal_date[1]-1]
		elif (RIS_field == 'SP') and bool(re.search('\d+',RIS_value)):
			#-- add starting page to current_pages array
			pages = [int(p) for p in re.findall('\d+',RIS_value)]
			current_pages[0] = pages[0]
			if (len(pages) > 1):
				current_pages[1] = pages[1]
		elif RIS_field in ('EP','LP') and bool(re.search('\d+',RIS_value)):
			#-- add ending page to current_pages array
			current_pages[1] = RIS_value
		elif RIS_field in ('L3','DO','N1','M3') and bool(R2.search(RIS_value)):
			#-- extract DOI
			current_entry['doi'] = R2.search(RIS_value).group(3)
		elif (RIS_field == 'KW'):
			#-- add to keywords list
			current_keywords.append(RIS_value)
		elif VERBOSE:
			#-- print all other fields and values
			print(RIS_field, RIS_value)

	#-- extract surname of first author
	firstauthor = current_authors[0].split(',')[0].decode('utf-8')
	#-- create entry for authors and decode from utf-8
	current_entry['author'] = ' and '.join(current_authors).decode('utf-8')
	current_entry['title'] = current_entry['title'].decode('utf-8')
	#-- firstauthor: replace unicode characters with plain text
	#-- bibtex entry for authors: replace unicode characters with latex symbols
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		firstauthor = firstauthor.replace(UV, PV)
		current_entry['author'] = current_entry['author'].replace(UV, LV)
		current_entry['title'] = current_entry['title'].replace(UV, LV)
	#-- encode as utf-8
	firstauthor = firstauthor.encode('utf-8')

	#-- create list of article keywords if present in bibliography file
	if current_keywords:
		current_entry['keywords'] = ', '.join(current_keywords)

	#-- calculate the universal citekey
	current_key['citekey'] = gen_citekey(firstauthor,current_entry['year'],
		current_entry['doi'], current_entry['title'])

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
	print(' -V, --verbose\tVerbose output of input and output files\n')

#-- main program that calls ris_to_bibtex()
def main():
	#-- Read the system arguments listed after the program
	long_options = ['help','output','verbose']
	optlist,arglist=getopt.getopt(sys.argv[1:],'hOV',long_options)
	#-- command line arguments
	OUTPUT = False
	VERBOSE = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-O','--output'):
			OUTPUT = True
		elif opt in ('-V','--verbose'):
			VERBOSE = True

	#-- for each file entered
	for FILE in arglist:
		#-- run for the input file
		print(os.path.basename(FILE)) if VERBOSE else None
		with open(os.path.expanduser(FILE),'r') as f:
			ris_to_bibtex(f.read().splitlines(), OUTPUT=OUTPUT, VERBOSE=VERBOSE)

#-- run main program
if __name__ == '__main__':
	main()
