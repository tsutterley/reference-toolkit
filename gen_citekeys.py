#!/usr/bin/env python
u"""
gen_citekeys.py (10/2017)
Generates Papers2-like cite keys for BibTeX

Enter Author names and publication years
Uses DOI's or titles to generate "universal" keys
Alternatively can generate a random suffix

CALLING SEQUENCE:
	python gen_citekeys.py --author=Smith --year=1997 \
		--doi="11.1234/abc.222.987654"

	will result in Smith:1997ct as the citekey

	python gen_citekeys.py --author=Smith --year=1997 \
		--title="Direct Evidence Of Flying Birds Found In Sky Pictures"

	will result in Smith:1997wo as the citekey

COMMAND LINE OPTIONS:
	-A X, --author=X: authors of publications
	-Y X, --year=X: corresponding publication years
	-D X, --doi=X: corresponding DOI of the publication
	-T X, --title=X: corresponding title of the publication
		if the DOI is not available

PROGRAM DEPENDENCIES:
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	Papers2 Universal Citekey generation javascript
		https://github.com/cparnot/universal-citekey-js
	Check unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
	Updated 10/2017: use modulus of 0xffffffff (4294967295)
	Updated 05/2017: removing whitespace from authors.
		Converting special characters with language_conversion program
	Updated 02/2017: universal citekeys from DOI or title hashes
		(will create the same citekeys as the Papers2 application)
	Written 02/2017
"""
from __future__ import print_function

import sys
import os
import re
import math
import string
import getopt
import random
import binascii
from language_conversion import language_conversion

#-- PURPOSE: create a Papers2-like cite key using the DOI
def gen_citekey(author,year,doi,title):
	#-- replace unicode characters in author with plain text
	author = author.decode('unicode-escape')
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		author = author.replace(UV, PV)
	author = re.sub('\s|\-\'','',author.encode('utf-8'))

	#-- create citekey suffix first attempting:
	#-- a DOI-based universal citekey
	#-- then attempting a title-based universal citekey
	#-- finally generating a random citekey (non-universal)
	if doi:
		#-- convert to unsigned 32-bit int if needed
		crc = binascii.crc32(doi) & 0xffffffff
		#-- generate individual hashes
		hash1 = chr(int(ord('b') + math.floor((crc % (10*26))/26)))
		hash2 = chr(int(ord('a') + (crc % 26)))
		#-- concatenate to form DOI-based universal citekey suffix
		key = hash1 + hash2
	elif title:
		#-- scrub special characters from title and set as lowercase
		title = re.sub('[\_\-\=\/\|\.]',' ',title.lower())
		title = ''.join(re.findall('[a-zA-Z0-9\s]',title))
		#-- convert to unsigned 32-bit int if needed
		crc = binascii.crc32(title) & 0xffffffff
		#-- generate individual hashes
		hash1 = chr(int(ord('t') + math.floor((crc % (4*26))/26)))
		hash2 = chr(int(ord('a') + (crc % 26)))
		#-- concatenate to form title-based universal citekey suffix
		key = hash1 + hash2
	else:
		key = ''.join(random.sample(string.ascii_lowercase,2))
	#-- return the final citekey from the function
	return '{0}:{1}{2}'.format(author,year,key)

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -A X, --author=X\tAuthors of publications')
	print(' -Y X, --year=X\t\tCorresponding publication year')
	print(' -D X, --doi=X\t\tCorresponding publication DOI')
	print(' -T X, --title=X\tCorresponding title if no DOI\n')

#-- main program that calls gen_citekey()
def main():
	long_options = ['help','author=','year=','doi=','title=']
	optlist,arglist=getopt.getopt(sys.argv[1:],'hA:Y:D:T:',long_options)
	#-- default: none
	AUTHOR = []
	YEAR = []
	DOI = None
	TITLE = None
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-A','--author'):
			AUTHOR = arg.split(',')
		elif opt in ('-Y','--year'):
			YEAR = arg.split(',')
		elif opt in ('-D','--doi'):
			DOI = arg.split(',')
		elif opt in ('-T','--title'):
			TITLE = arg.split(',')

	#-- if not using DOIs to set citekeys
	if DOI is None:
		DOI = [None]*len(AUTHOR)
	#-- if not using titles to set citekeys
	if TITLE is None:
		TITLE = [None]*len(AUTHOR)

	#-- run for each author-year pair
	for A,Y,D,T in zip(AUTHOR,YEAR,DOI,TITLE):
		citekey = gen_citekey(A,Y,D,T)
		print(citekey)

#-- run main program
if __name__ == '__main__':
	main()
