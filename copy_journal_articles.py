#!/usr/bin/env python
u"""
copy_journal_articles.py (05/2017)
Copies a journal article and supplements from a website to a local directory

Enter Author names, journal name, publication year and volume will copy a pdf
	file (or any other file if supplement) to the reference path

CALLING SEQUENCE:
	python copy_journal_articles.py --author=Rignot --year=2008 \
		--journal="Nature Geoscience" --volume=1 \
		https://www.nature.com/ngeo/journal/v1/n2/pdf/ngeo102.pdf

	will download the copy to 2008/Rignot/Rignot_Nat._Geosci.-1_2008.pdf

INPUTS:
	url to file to be copied into the reference path

COMMAND LINE OPTIONS:
	-A X, --author=X: lead author of publications
	-J X, --journal=X: corresponding publication journal
	-Y X, --year=X: corresponding publication year
	-V X, --volume=X: corresponding publication volume
	-S, --supplement: file is a supplemental file

PROGRAM DEPENDENCIES:
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	Lists of journal abbreviations
		https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
	If using author name with unicode characters: put in quotes and check
		unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
	Updated 05/2017: Convert special characters with language_conversion program
	Written 05/2017
"""
from __future__ import print_function

import sys
import os
import re
import shutil
import inspect
import getopt
import urllib2
from language_conversion import language_conversion

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- PURPOSE: check internet connection and URL
def check_connection(remote_file):
	#-- attempt to connect to remote file
	try:
		urllib2.urlopen(remote_file, timeout=1)
	except urllib2.HTTPError:
		raise RuntimeError('Check URL: {0}'.format(remote_file))
	except urllib2.URLError:
		raise RuntimeError('Check internet connection')
	else:
		return True

#-- PURPOSE: create directories and copy a reference file after formatting
def copy_journal_articles(remote_file,author,journal,year,volume,SUPPLEMENT):
	#-- input remote file scrubbed of any additional html information
	fi = re.sub('\?[\_a-z]{1,4}\=(.*?)$','',remote_file)
	#-- get extension from file (assume pdf if extension cannot be extracted)
	fileExtension=os.path.splitext(fi)[1] if os.path.splitext(fi)[1] else '.pdf'

	#-- directory with journal abbreviation files
	#-- https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
	abbreviation_dir = os.path.join(filepath,'journals')
	abbreviation_file = 'journal_abbreviations_webofscience-ts.txt'
	#-- create regular expression pattern for extracting abbreviations
	arg = journal.replace(' ','\s+')
	rx=re.compile('\n{0}[\s+]?\=[\s+]?(.*?)\n'.format(arg),flags=re.IGNORECASE)
	#-- try to find journal article within filename from webofscience file
	with open(os.path.join(abbreviation_dir,abbreviation_file),'r') as f:
		abbreviation_contents = f.read()

	#-- if abbreviation not found: just use the whole journal name
	#-- else use the found journal abbreviation
	if not bool(rx.search(abbreviation_contents)):
		print('Abbreviation for {0} not found'.format(journal))
		abbreviation = journal
	else:
		abbreviation = rx.findall(abbreviation_contents)[0]

	#-- replace unicode characters with combining unicode version
	author = author.decode('unicode-escape')
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		author = author.replace(UV, CV)

	#-- directory path for local file
	if SUPPLEMENT:
		directory = os.path.join(filepath,year,author,'Supplemental')
	else:
		directory = os.path.join(filepath,year,author)
	#-- check if output directory currently exist and recursively create if not
	os.makedirs(directory) if not os.path.exists(directory) else None

	#-- create initial test case for output file (will add numbers if not)
	args = (author, abbreviation.replace(' ','_'), volume, year, fileExtension)
	local_file = os.path.join(directory,u'{0}_{1}-{2}_{3}{4}'.format(*args))
	#-- chunked transfer encoding size
	CHUNK = 16 * 1024
	#-- open url and copy contents to local file using chunked transfer encoding
	#-- transfer should work properly with ascii and binary data formats
	request=urllib2.Request(remote_file, headers={'User-Agent':"Magic Browser"})
	f_in = urllib2.urlopen(request)
	with create_unique_filename(local_file) as f_out:
		shutil.copyfileobj(f_in, f_out, CHUNK)
	f_in.close()

#-- PURPOSE: open a unique filename adding a numerical instance if existing
def create_unique_filename(filename):
	#-- split filename into fileBasename and fileExtension
	fileBasename, fileExtension = os.path.splitext(filename)
	#-- create counter to add to the end of the filename if existing
	counter = 1
	while counter:
		try:
			#-- open file descriptor only if the file doesn't exist
			fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
		except OSError:
			pass
		else:
			print(filename)
			return os.fdopen(fd, 'wb+')
		#-- new filename adds counter the between fileBasename and fileExtension
		filename = u'{0}-{1:d}{2}'.format(fileBasename, counter, fileExtension)
		counter += 1

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -A X, --author=X\tAuthors of publications')
	print(' -J X, --journal=X\tCorresponding publication journal')
	print(' -Y X, --year=X\t\tCorresponding publication year')
	print(' -V X, --volume=X\tCorresponding publication volume')
	print(' -S, --supplement\tFile is a supplemental file\n')

#-- main program that calls copy_journal_articles()
def main():
	long_options = ['help','author=','journal=','year=','volume=','supplement']
	optlist,arglist=getopt.getopt(sys.argv[1:],'hA:J:Y:V:S',long_options)
	#-- default: none
	AUTHOR = []
	JOURNAL = []
	YEAR = []
	VOLUME = None
	SUPPLEMENT = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-A','--author'):
			AUTHOR = arg.split(',')
		elif opt in ('-J','--journal'):
			JOURNAL = arg.split(',')
		elif opt in ('-Y','--year'):
			YEAR = arg.split(',')
		elif opt in ('-V','--volume'):
			VOLUME = arg.split(',')
		elif opt in ('-S','--supplement'):
			SUPPLEMENT = True

	#-- if no volume for articles
	if VOLUME is None:
		VOLUME = ['']*len(arglist)

	#-- run for each entered url to a remote file
	for FILE,A,J,Y,V in zip(arglist,AUTHOR,JOURNAL,YEAR,VOLUME):
		if check_connection(FILE):
			copy_journal_articles(FILE,A,J,Y,V,SUPPLEMENT)

#-- run main program
if __name__ == '__main__':
	main()