#!/usr/bin/env python
u"""
smart_citekeys.py (09/2017)
Generates Papers2-like cite keys for BibTeX using information from crossref.org

Enter DOI's of journals to generate "universal" keys

CALLING SEQUENCE:
	python gen_citekeys.py "11.1234/abc.222.987654"
	will result in Smith:1997ct as the citekey

PROGRAM DEPENDENCIES:
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	Papers2 Universal Citekey generation javascript
		https://github.com/cparnot/universal-citekey-js
	Check unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
	Updated 09/2017: use timeout of 20 to prevent socket.timeout
	Forked 05/2017 from gen_citekeys.py to use information from crossref.org
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
import json
import urllib2
import binascii
from language_conversion import language_conversion

#-- PURPOSE: check internet connection and URL
def check_connection(doi):
	#-- attempt to connect to remote url
	remote_url = 'https://api.crossref.org/works/{0}'.format(doi)
	try:
		urllib2.urlopen(remote_url,timeout=20)
	except urllib2.HTTPError:
		raise RuntimeError('Check URL: {0}'.format(remote_url))
	except urllib2.URLError:
		raise RuntimeError('Check internet connection')
	else:
		return True

#-- PURPOSE: create a Papers2-like cite key using the DOI
def smart_citekey(doi):
	#-- open connection with crossref.org for DOI
	req = urllib2.Request(url='https://api.crossref.org/works/{0}'.format(doi))
	resp = json.loads(urllib2.urlopen(req,timeout=20).read())

	#-- get author and replace unicode characters in author with plain text
	author = resp['message']['author'][0]['family'].decode('unicode-escape')
	#-- check if author fields are initially uppercase: change to title
	author = author.title() if author.isupper() else author
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		author = author.replace(UV, PV)
	author = re.sub('\s|\-|\'','',author.encode('utf-8'))

	#-- get publication date (prefer date when in print)
	if 'published-print' in resp['message'].keys():
		date_parts, = resp['message']['published-print']['date-parts']
	elif 'published-online' in resp['message'].keys():
		date_parts, = resp['message']['published-online']['date-parts']
	#-- extract year from date parts
	year = date_parts[0]

	#-- create citekey suffix using a DOI-based universal citekey
	crc = binascii.crc32(doi)
	#-- convert to unsigned 32-bit int if needed
	if (crc < 0):
		crc += 4294967296
	#-- generate individual hashes
	hash1 = chr(int(ord('b') + math.floor((crc % (10*26))/26)))
	hash2 = chr(int(ord('a') + (crc % 26)))
	#-- concatenate to form DOI-based universal citekey suffix
	key = hash1 + hash2
	#-- return the final citekey from the function
	return '{0}:{1:4d}{2}'.format(author,year,key)

#-- main program that calls smart_citekey()
def main():
	#-- run for each DOI entered after the program
	for doi in sys.argv[1:]:
		if check_connection(doi):
			citekey = smart_citekey(doi)
		print(citekey)

#-- run main program
if __name__ == '__main__':
	main()
