#!/usr/bin/env python
u"""
search_references.py (07/2017)
Reads bibtex files for each article in a given set of years to search for
	keywords, authors, journal, etc using regular expressions

CALLING SEQUENCE:
	python search_references.py -A Rignot -F -Y 2008 -J "Nature Geoscience"
		will return the bibtex entry for this publication

COMMAND LINE OPTIONS:
	-A X, --author=X: last name of author of publications to search
	-F, --first: Search only first authors
	-Y X, --year=X: years of publication to search (can be regular expression)
	-K X, --keyword=X: keywords to search
	-J X, --journal=X: publication journals to search
	-O, --open: open publication directory with found matches
	-W, --webpage: open publication webpage with found matches

PROGRAM DEPENDENCIES:
	language_conversion.py: Outputs map for converting symbols between languages

UPDATE HISTORY:
	Updated 07/2017: print number of matching articles in search query
	Updated 06/2017: added webbrowser to open the webpage of found articles
	Written 06/2017
"""
from __future__ import print_function

import sys
import re
import os
import inspect
import getopt
import subprocess
import webbrowser
from language_conversion import language_conversion

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- Reads bibtex files for each article stored in the working directory for
#-- keywords, authors, journal, etc
def search_references(AUTHOR, JOURNAL, YEAR, KEYWORDS, FIRST=False, OPEN=False,
	WEBPAGE=False):
	#-- bibtex fields to be printed in the output file
	bibtex_field_types = ['address','affiliation','annote','author',
		'booktitle','chapter','crossref','doi','edition','editor',
		'howpublished','institution','isbn','issn','journal','key',
		'keywords','month','note','number','organization','pages',
		'publisher','school','series','title','type','url','volume','year']
	field_regex = '[\s]?(' + '|'.join([i for i in bibtex_field_types]) + \
		')[\s]?\=[\s]?[\{]?[\{]?(.*?)[\}]?[\}]?[\,]?[\s]?\n'
	R1 = re.compile(field_regex, flags=re.IGNORECASE)

	#-- compile regular expression operators for input search terms
	if AUTHOR and FIRST:
		R2 = re.compile('^'+'|'.join(AUTHOR), flags=re.IGNORECASE)
	elif AUTHOR:
		R2 = re.compile('|'.join(AUTHOR), flags=re.IGNORECASE)
	if JOURNAL:
		R3 = re.compile('|'.join(JOURNAL), flags=re.IGNORECASE)
	if KEYWORDS:
		R4 = re.compile('|'.join(KEYWORDS), flags=re.IGNORECASE)

	#-- find directories of years
	regex_years = '|'.join(YEAR) if YEAR else '\d+'
	years = [sd for sd in os.listdir(filepath) if re.match(regex_years,sd) and
		os.path.isdir(os.path.join(filepath,sd))]
	match_count = 0
	query_count = 0
	for Y in sorted(years):
		#-- find author directories in year
		authors = [sd for sd in os.listdir(os.path.join(filepath,Y)) if
			os.path.isdir(os.path.join(filepath,Y,sd))]
		for A in sorted(authors):
			#-- find bibtex files
			bibtex_files = [fi for fi in os.listdir(os.path.join(filepath,Y,A))
				if re.match('(.*?)-(.*?).bib$',fi)]
			#-- read each bibtex file
			for fi in bibtex_files:
				with open(os.path.join(filepath,Y,A,fi), 'r') as f:
					bibtex_entry = f.read()
				#-- extract bibtex fields
				bibtex_field_entries = R1.findall(bibtex_entry)
				current_entry = {}
				for key,val in bibtex_field_entries:
					#-- replace latex symbols with unicode characters
					#-- 1: latex, 2: combining unicode, 3: unicode, 4: plain
					val = val.decode('unicode-escape')
					for LV, CV, UV, PV in language_conversion():
						val = val.replace(LV,CV)
					#-- add to current entry dictionary
					current_entry[key.lower()] = val
				#-- use search terms to find journals
				#-- Search bibtex author entries for AUTHOR
				FLAG1 = R2.search(current_entry['author']) if AUTHOR else True
				#-- Search bibtex journal entries for JOURNAL
				FLAG2 = False if JOURNAL else True
				if ('journal' in current_entry.keys() and JOURNAL):
					FLAG2 = R3.search(current_entry['journal'])
				#-- Search bibtex title entries for KEYWORDS
				FLAG3 = R4.search(current_entry['title']) if KEYWORDS else True
				#-- Search bibtex keyword entries for KEYWORDS
				FLAG4 = False if KEYWORDS else True
				if ('keywords' in current_entry.keys() and KEYWORDS):
					FLAG4 = R4.search(current_entry['keywords'])
				#-- print the complete bibtex entry if search was found
				if bool(FLAG1) & bool(FLAG2) & (bool(FLAG3) | bool(FLAG4)):
					print(bibtex_entry)
					file_opener(os.path.join(filepath,Y,A,fi)) if OPEN else None
					#-- URL to open if WEBPAGE (from url or using doi)
					if 'url' in current_entry.keys():
						URL = current_entry['url']
					elif 'doi' in current_entry.keys():
						URL = 'https://doi.org/{0}'.format(current_entry['doi'])
					#-- Open URL in a new tab, if browser window is already open
					webbrowser.open_new_tab(URL) if (WEBPAGE and URL) else None
					#-- add to total match count
					match_count += 1
				#-- add to total query count
				query_count += 1
	#-- print the number of matching and number of queried references
	args = (match_count, query_count)
	print('Matching references = {0:d} out of {1:d} queried'.format(*args))

#-- PURPOSE: platform independent file opener
def file_opener(filename):
	if (sys.platform == "win32"):
		os.startfile(filename, "explore")
	elif (sys.platform == "darwin"):
		subprocess.call(["open", "-R", filename])
	else:
		subprocess.call(["xdg-open", filename])

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -A X, --author=X\tAuthor of publications to search')
	print(' -F, --first\t\tSearch only first authors')
	print(' -J X, --journal=X\tPublication journals to search')
	print(' -Y X, --year=X\t\tYears of publication to search')
	print(' -K X, --keyword=X\tKeywords to search')
	print(' -O, --open\t\tOpen publication directory with found matches')
	print(' -W, --webpage\t\tOpen publication webpage with found matches\n')

#-- main program that calls search_references()
def main():
	long_options = ['help','author=','first','journal=','year=','keyword=',
		'open','webpage']
	optlist,arglist = getopt.getopt(sys.argv[1:],'hA:FJ:Y:K:OW',long_options)
	#-- default: none
	AUTHOR = None
	FIRST = False
	JOURNAL = None
	YEAR = None
	KEYWORDS = None
	OPEN = False
	WEBPAGE = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-A','--author'):
			AUTHOR = arg.split(',')
		elif opt in ('-F','--first'):
			FIRST = True
		elif opt in ('-J','--journal'):
			JOURNAL = arg.split(',')
		elif opt in ('-Y','--year'):
			YEAR = arg.split(',')
		elif opt in ('-K','--keyword'):
			KEYWORDS = arg.split(',')
		elif opt in ('-O','--open'):
			OPEN = True
		elif opt in ('-W','--webpage'):
			WEBPAGE = True

	#-- search references for requested fields
	search_references(AUTHOR, JOURNAL, YEAR, KEYWORDS, FIRST=FIRST, OPEN=OPEN,
		WEBPAGE=WEBPAGE)

#-- run main program
if __name__ == '__main__':
	main()
