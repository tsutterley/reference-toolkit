#!/usr/bin/env python
u"""
format_bibtex.py (05/2017)
Reformats journal bibtex files into a standard form with Universal citekeys

COMMAND LINE OPTIONS:
	-O, --output: Output to new bibtex file
	-V, --verbose: Verbose output of input files and entries

PROGRAM DEPENDENCIES:
	gen_citekeys.py: Generates Papers2-like cite keys for BibTeX
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	May get capitalization incorrect for authors with lowercase first letters
		possible for cases when author fields are initially fully capitalized
	Check unicode characters with http://www.fileformat.info/
		can add more entries to the language_conversion matrix
	Papers2 Universal Citekey generation javascript
		https://github.com/cparnot/universal-citekey-js

UPDATE HISTORY:
	Written 05/2017
"""
from __future__ import print_function

import sys
import os
import re
import getopt
from gen_citekeys import gen_citekey
from language_conversion import language_conversion

#-- PURPOSE: formats an input bibtex file
def format_bibtex(file_contents, OUTPUT=False, VERBOSE=False):
	#-- valid bibtex entry types
	bibtex_entry_types = ['article','book','booklet','conference','inbook',
		'incollection','inproceedings','manual','mastersthesis','phdthesis',
		'proceedings','techreport','unpublished','webpage']
	entry_regex = '[?<=\@](' + '|'.join([i for i in bibtex_entry_types]) + \
		')[\s]?\{(.*?)[\s]?,[\s]?'
	R1 = re.compile(entry_regex, flags=re.IGNORECASE)
	#-- bibtex fields to be printed in the output file
	bibtex_field_types = ['address','affiliation','annote','author','booktitle',
		'chapter','crossref','doi','edition','editor','howpublished','institution',
		'isbn','issn','journal','key','keywords','month','note','number','organization',
		'pages','publisher','school','series','title','type','url','volume','year']
	field_regex = '[\s]?(' + '|'.join([i for i in bibtex_field_types]) + \
		')[\s]?\=[\s]?[\"|\']?[\{]?[\{]?[\s]?(.*?)[\s+]?[\}]?[\}]?[\"|\']?[\s]?[\,]?[\s]?\n'
	R2 = re.compile(field_regex, flags=re.IGNORECASE)
	#-- sort bibtex fields in output files
	bibtex_field_sort = {'address':15,'affiliation':16,'annote':25,'author':0,
		'booktitle':12,'chapter':13,'crossref':27,'doi':10,'edition':19,'editor':21,
		'howpublished':22,'institution':17,'isbn':8,'issn':7,'journal':2,'key':24,
		'keywords':28,'month':4,'note':23,'number':6,'organization':17,'pages':11,
		'publisher':14,'school':18,'series':20,'title':1,'type':26,'url':9,
		'volume':5,'year':3}
	#-- regular expression pattern to extract doi from webpages or "doi:"
	doi_regex = '(doi\:[\s]?|http[s]?\:\/\/(dx\.)?doi\.org\/)?(10\.(.*?))$'
	R3 = re.compile(doi_regex, flags=re.IGNORECASE)

	#-- list of known compound surnames to search for
	compound_surname_regex = []
	compound_surname_regex.append('(?<=\s)van\s[de|den]?[\s]?(.*?)')
	compound_surname_regex.append('(?<=\s)von\s[de|den]?[\s]?(.*?)')
	compound_surname_regex.append('(?<![van|von])(?<=\s)de\s(.*?)')
	compound_surname_regex.append('(?<!de)(?<=\s)(la|los)\s?(.*?)')

	#-- create python dictionary with entry
	bibtex_entry = {}
	bibtex_key = {}
	#-- extract bibtex entry type and bibtex cite key
	bibentry,bibkey = R1.findall(file_contents).pop()
	bibtex_key['entrytype'] = bibentry.lower()
	bibtex_key['citekey'] = bibkey
	bibtex_field_entries = R2.findall(file_contents)
	bibtex_keywords = []
	for key,val in bibtex_field_entries:
		if (key.lower() == 'title'):
			#-- format titles in double curly brackets
			bibtex_entry[key.lower()] = '{{{0}}}'.format(val)
		elif (key.lower() == 'author') and (',' not in val):
			#-- format authors in surname, given name(s)
			current_authors = []
			for A in val.split(' and '):
				#-- flip given name(s) and lastname
				i = None; j = 0
				#-- check if lastname is in list of known compound surnames
				while (i is None) and (j < len(compound_surname_regex)):
					R = re.compile(compound_surname_regex[j],flags=re.IGNORECASE)
					i = R.search(A).start() if R.search(A) else None
					j += 1
				#-- if the lastname was compound
				if i is not None:
					ALN,AGN = A[i:],A[:i].rstrip()
					current_authors.append('{0}, {1}'.format(ALN,AGN))
				else:
					#-- flip given name(s) and lastname
					author_fields = A.split(' ')
					ALN = author_fields[-1]
					AGN = ' '.join(author_fields[:-1])
					current_authors.append('{0}, {1}'.format(ALN,AGN))
			#-- merge authors list
			bibtex_entry[key.lower()] = ' and '.join(current_authors)
		elif (key.lower() == 'doi') and bool(R3.match(val)):
			bibtex_entry[key.lower()] = R3.match(val).group(3)
		elif (key.lower() == 'pages') and re.match('(.*?)\s\-\s(.*?)$',val):
			pages, = re.findall('(.*?)\s\-\s(.*?)$',val)
			bibtex_entry[key.lower()] = '{0}--{1}'.format(pages[0],pages[1])
		elif (key.lower() == 'keywords'):
			bibtex_keywords.append(val)
		else:
			bibtex_entry[key.lower()] = val

	#-- if author fields are initially completely uppercase: change to title()
	if bibtex_entry['author'].isupper():
		bibtex_entry['author'] = bibtex_entry['author'].title()
	#-- extract surname of first author
	firstauthor = bibtex_entry['author'].split(',')[0].decode('utf-8')
	bibtex_entry['author'] = bibtex_entry['author'].decode('utf-8')
	bibtex_entry['title'] = bibtex_entry['title'].decode('utf-8')
	#-- firstauthor: replace unicode characters with plain text
	#-- bibtex entry for authors: replace unicode characters with latex symbols
	#-- bibtex entry for titles: replace unicode characters with latex symbols
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		firstauthor = firstauthor.replace(UV, PV)
		bibtex_entry['author'] = bibtex_entry['author'].replace(UV, LV)
		bibtex_entry['title'] = bibtex_entry['title'].replace(UV, LV)
	#-- encode as utf-8
	firstauthor = firstauthor.encode('utf-8')

	#-- create list of article keywords if present in bibliography file
	if bibtex_keywords:
		bibtex_entry['keywords'] = ', '.join(bibtex_keywords)

	#-- extract DOI and title for generating universal citekeys
	doi = bibtex_entry['doi'] if 'doi' in bibtex_entry.keys() else None
	title = bibtex_entry['title'] if 'title' in bibtex_entry.keys() else None
	#-- calculate the universal citekey
	univ_key = gen_citekey(firstauthor,bibtex_entry['year'],doi,title)

	#-- parse universal citekey
	authkey,citekey,=re.findall('(\D+)\:(\d+\D+)',univ_key).pop()
	#-- if printing to file: output bibtex file for author and year
	fid = open('{0}-{1}.bib'.format(authkey,citekey),'w') if OUTPUT else sys.stdout
	if VERBOSE and OUTPUT:
		print('  --> {0}-{1}.bib'.format(authkey,citekey))

	#-- print the bibtex citation
	print('@{0}{{{1},'.format(bibtex_key['entrytype'],univ_key),file=fid)
	#-- sort output bibtex files as listed above
	field_indices = [bibtex_field_sort[b] for b in bibtex_entry.keys()]
	field_tuple = zip(field_indices,bibtex_entry.keys(),bibtex_entry.values())
	#-- for each field within the entry
	for s,k,v in sorted(field_tuple):
		#-- make sure ampersands are in latex format (marked with symbol)
		v = re.sub('(?<=\s)\&','\\\&',v) if re.search('(?<=\s)\&',v) else v
		#-- do not put the month field in brackets
		if (k == 'month'):
			print('{0} = {1},'.format(k,v.lower()),file=fid)
		else:
			print('{0} = {{{1}}},'.format(k,v),file=fid)
	print('}', file=fid)

	#-- close the output file
	if OUTPUT:
		fid.close()

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -O, --output\tOutput to new bibtex file')

#-- main program that calls format_bibtex()
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
			format_bibtex(f.read(), OUTPUT=OUTPUT, VERBOSE=VERBOSE)

#-- run main program
if __name__ == '__main__':
	main()