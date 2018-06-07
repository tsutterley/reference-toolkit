#!/usr/bin/env python
u"""
smart_move_articles.py (10/2017)
Moves a journal article and supplements to the references local directory
	using information from crossref.org

Enter DOI's of journals to move a file to the reference path

CALLING SEQUENCE:
	python smart_move_articles.py --doi=10.1038/ngeo102 ~/Downloads/ngeo102.pdf

	will move the file to 2008/Rignot/Rignot_Nat._Geosci.-1_2008.pdf

INPUTS:
	file to be moved into the reference path

COMMAND LINE OPTIONS:
	-D X, --doi=X: DOI of the publication
	-S, --supplement: file is a supplemental file
	-C, --cleanup: Remove the input file after moving

PROGRAM DEPENDENCIES:
	read_referencerc.py: Sets default file path and file format for output files
	language_conversion.py: Outputs map for converting symbols between languages

NOTES:
	Lists of journal abbreviations
		https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
	If using author name with unicode characters: put in quotes and check
		unicode characters with http://www.fileformat.info/

UPDATE HISTORY:
	Updated 10/2017: use data path and data file format from referencerc file
	Updated 09/2017: use timeout of 20 to prevent socket.timeout
	Updated 06/2017: use language_conversion for journal name
	Forked 05/2017 from move_journal_articles.py to use info from crossref.org
	Written 05/2017
"""
from __future__ import print_function

import sys
import os
import re
import json
import shutil
import inspect
import getopt
import urllib2
from read_referencerc import read_referencerc
from language_conversion import language_conversion

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- PURPOSE: create directories and move a reference file after formatting
def smart_move_articles(fi,doi,SUPPLEMENT,CLEANUP):
	#-- get reference filepath and reference format from referencerc file
	datapath,dataformat=read_referencerc(os.path.join(filepath,'.referencerc'))
	#-- get extension from file (assume pdf if extension cannot be extracted)
	fileExtension=os.path.splitext(fi)[1] if os.path.splitext(fi)[1] else '.pdf'

	#-- open connection with crossref.org for DOI
	req = urllib2.Request(url='https://api.crossref.org/works/{0}'.format(doi))
	resp = json.loads(urllib2.urlopen(req, timeout=20).read())

	#-- get author and replace unicode characters in author with plain text
	author = resp['message']['author'][0]['family']
	#-- check if author fields are initially uppercase: change to title
	author = author.title() if author.isupper() else author
	#-- get journal name
	journal, = resp['message']['container-title']
	#-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
	for LV, CV, UV, PV in language_conversion():
		author = author.replace(UV, CV)
		journal = journal.replace(UV, PV)
	#-- remove spaces, dashes and apostrophes
	author = re.sub('\s','_',author); author = re.sub('\-|\'','',author)

	#-- get publication date (prefer date when in print)
	if 'published-print' in resp['message'].keys():
		date_parts, = resp['message']['published-print']['date-parts']
	elif 'published-online' in resp['message'].keys():
		date_parts, = resp['message']['published-online']['date-parts']
	#-- extract year from date parts and convert to string
	year = '{0:4d}'.format(date_parts[0])

	#-- get publication volume and number
	vol=resp['message']['volume'] if 'volume' in resp['message'].keys() else ''
	num=resp['message']['issue'] if 'issue' in resp['message'].keys() else ''

	#-- file listing journal abbreviations modified from
	#-- https://github.com/JabRef/abbrv.jabref.org/tree/master/journals
	abbreviation_file = 'journal_abbreviations_webofscience-ts.txt'
	#-- create regular expression pattern for extracting abbreviations
	arg = re.sub('[^a-zA-z0-9\&\s\,]',"",journal)
	rx=re.compile('\n{0}[\s+]?\=[\s+]?(.*?)\n'.format(arg),flags=re.IGNORECASE)
	#-- try to find journal article within filename from webofscience file
	with open(os.path.join(filepath,abbreviation_file),'r') as f:
		abbreviation_contents = f.read()

	#-- if abbreviation not found: just use the whole journal name
	#-- else use the found journal abbreviation
	if not bool(rx.search(abbreviation_contents)):
		print('Abbreviation for {0} not found'.format(journal))
		abbreviation = journal
	else:
		abbreviation = rx.findall(abbreviation_contents)[0]

	#-- directory path for local file
	if SUPPLEMENT:
		directory = os.path.join(datapath,year,author,'Supplemental')
	else:
		directory = os.path.join(datapath,year,author)
	#-- check if output directory currently exist and recursively create if not
	os.makedirs(directory) if not os.path.exists(directory) else None

	#-- format used for saving articles using string formatter
	#-- 0) Author Last Name
	#-- 1) Journal Name
	#-- 2) Journal Abbreviation
	#-- 3) Publication Volume
	#-- 4) Publication Number
	#-- 5) Publication Year
	#-- 6) File Extension (will include period)
	#-- initial test case for output file (will add numbers if not unique in fs)
	args = (author, journal.replace(' ','_'), abbreviation.replace(' ','_'),
		vol, num, year, fileExtension)
	local_file = os.path.join(directory, dataformat.format(*args))

	#-- open input file and copy contents to local file
	with open(fi, 'rb') as f_in, create_unique_filename(local_file) as f_out:
		shutil.copyfileobj(f_in, f_out)
	#-- remove the input file
	os.remove(fi) if CLEANUP else None

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
			print(filename.replace(os.path.expanduser('~'),'~'))
			return os.fdopen(fd, 'wb+')
		#-- new filename adds counter the between fileBasename and fileExtension
		filename = u'{0}-{1:d}{2}'.format(fileBasename, counter, fileExtension)
		counter += 1

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -D X, --doi=X\tDOI of the publication')
	print(' -S, --supplement\tFile is a supplemental file')
	print(' -C, --cleanup\t\tRemove the input file after moving\n')

#-- main program that calls smart_move_articles()
def main():
	long_options = ['help','doi=','supplement','cleanup']
	optlist,arglist = getopt.getopt(sys.argv[1:],'hD:SC',long_options)
	#-- default: none
	DOI = []
	SUPPLEMENT = False
	CLEANUP = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-D','--doi'):
			DOI = arg.split(',')
		elif opt in ('-S','--supplement'):
			SUPPLEMENT = True
		elif opt in ('-C','--cleanup'):
			CLEANUP = True

	#-- run for each entered file
	for FILE,D in zip(arglist,DOI):
		smart_move_articles(FILE,D,SUPPLEMENT,CLEANUP)

#-- run main program
if __name__ == '__main__':
	main()
