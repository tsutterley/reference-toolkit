#!/usr/bin/env python
u"""
open_doi.py (10/2017)
Opens the webpages and crossref.org API webpages associated with a Digital
	Object Identifier (DOI)

CALLING SEQUENCE:
	python open_doi.py 10.1038/ngeo102

COMMAND LINE OPTIONS:
	-C, --crossref: Open crossref.org API associated with a DOI
	-V, --verbose: Verbose output of webpages opened

UPDATE HISTORY:
	Written 10/2017
"""
from __future__ import print_function
import sys, os, getopt, webbrowser

#-- PURPOSE: open webpage associated with a Digital Object Identifier (DOI)
def doiopen(DOI, VERBOSE=False):
	#-- Open URL for DOI in a new tab, if browser window is already open
	URL = 'https://doi.org/{0}'.format(DOI)
	print(URL) if VERBOSE else None
	webbrowser.open_new_tab(URL)

#-- PURPOSE: open crossref.org API associated with a DOI
def crossrefopen(DOI, VERBOSE=False):
	#-- Open URL for DOI in a new tab, if browser window is already open
	URL = 'https://api.crossref.org/works/{0}'.format(DOI)
	print(URL) if VERBOSE else None
	webbrowser.open_new_tab(URL)

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -C, --crossref\tOpen crossref.org API associated with a DOI')
	print(' -V, --verbose\tVerbose output of webpages opened\n')

#-- main program that calls doiopen() and crossrefopen()
def main():
	long_options = ['help','crossref','verbose']
	optlist,arglist=getopt.getopt(sys.argv[1:],'hCV',long_options)
	#-- command line arguments
	CROSSREF = False
	VERBOSE = False
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-C','--crossref'):
			CROSSREF = True
		elif opt in ('-V','--verbose'):
			VERBOSE = True

	#-- run for each DOI entered after the program
	for DOI in arglist:
		doiopen(DOI, VERBOSE=VERBOSE)
		crossrefopen(DOI, VERBOSE=VERBOSE) if CROSSREF else None

#-- run main program
if __name__ == '__main__':
	main()
