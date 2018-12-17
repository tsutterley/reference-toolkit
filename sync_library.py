#!/usr/bin/env python
u"""
sync_library.py (02/2018)
Exports complete library into a new directory (such as a mounted-drive)
Will only copy new or overwritten files by checking the last modified dates

CALLING SEQUENCE:
	python sync_library.py -V ~/references.dir

INPUTS:
	Directory for outputting reference library

COMMAND LINE OPTIONS:
	-P, --pull: Transfer files from external directory to library
	-C, --clobber: Overwrite existing data in transfer
	-V, --verbose: Print all transferred files
	-M X, --mode=X: Permission mode of files transferred

PROGRAM DEPENDENCIES:
	read_referencerc.py: Sets default file path and file format for output files

UPDATE HISTORY:
	Written 02/2018
"""
from __future__ import print_function

import sys
import re
import os
import getopt
import shutil
import inspect
from read_referencerc import read_referencerc

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- Reads BibTeX files for each article stored in the working directory
#-- exports as a single file sorted by BibTeX key
def sync_library(DIRECTORY,PULL=False,CLOBBER=False,VERBOSE=False,MODE=0o775):
	#-- get reference filepath and reference format from referencerc file
	datapath,dataformat=read_referencerc(os.path.join(filepath,'.referencerc'))

	#-- if transferring from DIRECTORY to library
	d_in,d_out = (DIRECTORY,datapath) if PULL else (datapath,DIRECTORY)
	#-- subdirectories with supplementary information
	S = 'Supplemental'

	#-- iterate over yearly directories
	years = [sd for sd in os.listdir(d_in) if re.match('\d+',sd) and
		os.path.isdir(os.path.join(d_in,sd))]
	for Y in sorted(years):
		#-- find author directories in year
		authors = [sd for sd in os.listdir(os.path.join(d_in,Y)) if
			os.path.isdir(os.path.join(d_in,Y,sd))]
		for A in sorted(authors):
			#-- find BibTeX and article files within author directory
			regex = '((.*?)-(.*?)\.bib$)|({0}_(.*?)_{1}(.*?)$)'.format(A,Y)
			FILES = [f for f in os.listdir(os.path.join(d_in,Y,A))
				if re.match(regex,f)]
			#-- transfer each article file (check if existing)
			for fi in FILES:
				input_dir = os.path.join(d_in,Y,A)
				output_dir = os.path.join(d_out,Y,A)
				transfer_push_file(fi, input_dir, output_dir,
					CLOBBER=CLOBBER, VERBOSE=VERBOSE, MODE=MODE)
			#-- if there is supplementary information
			if os.path.isdir(os.path.join(d_in,Y,A,S)):
				#-- find supplementary files within Supplemental directory
				FILES = [f for f in os.listdir(os.path.join(d_in,Y,A,S))
					if re.match(regex,f)]
				#-- transfer each supplementary file (check if existing)
				for fi in FILES:
					input_dir = os.path.join(d_in,Y,A,S)
					output_dir = os.path.join(d_out,Y,A,S)
					transfer_push_file(fi, input_dir, output_dir,
						CLOBBER=CLOBBER, VERBOSE=VERBOSE, MODE=MODE)

#-- PURPOSE: push an input file to an output directory checking if file exists
#-- and if the input file is newer than any existing output file
#-- set the permissions mode of the transferred file to MODE
def transfer_push_file(transfer_file, input_dir, output_dir, CLOBBER=False,
	VERBOSE=False, MODE=0o775):
	#-- input and output versions of file
	input_file = os.path.join(input_dir,transfer_file)
	output_file = os.path.join(output_dir,transfer_file)
	#-- recursively create output directory if not currently existing
	os.makedirs(output_dir,MODE) if not os.access(output_dir, os.F_OK) else None
	#-- check if input file is newer than the output file
	TEST = False
	OVERWRITE = ' (clobber)'
	#-- last modification time of the input file
	input_mtime = os.stat(input_file).st_mtime
	if os.access(output_file, os.F_OK):
		output_mtime = os.stat(output_file).st_mtime
		#-- if input file is newer: overwrite the output file
		#-- verifying based on even mtimes for different file systems
		if (even(input_mtime) > even(input_mtime)):
			TEST = True
			OVERWRITE = ' (overwrite)'
	else:
		TEST = True
		OVERWRITE = ' (new)'
	#-- if output file does not exist, is to be overwritten, or CLOBBER is set
	if TEST or CLOBBER:
		args = (input_file,output_file,OVERWRITE)
		print('{0} -->\n\t{1}{2}\n'.format(*args)) if VERBOSE else None
		#-- check if input_file is a directory (e.g. unzipped Supplementary)
		if os.path.isdir(input_file):
			#-- copy input directory to storage output directory
			shutil.copytree(input_file, output_file)
		else:
			#-- copy input files to storage output
			shutil.copyfile(input_file, output_file)
		#-- change the permissions level of the transported file to MODE
		os.chmod(output_file, MODE)
		#-- set modification times of the output file
		os.utime(output_file, (os.stat(output_file).st_atime,input_mtime))

#-- PURPOSE: rounds a number to an even number less than or equal to original
def even(i):
	return 2*int(i/2)

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -P, --pull\t\tTransfer files from external directory to library')
	print(' -C, --clobber\t\tOverwrite existing data in transfer')
	print(' -V, --verbose\t\tPrint all transferred files')
	print(' -M X, --mode=X\t\tPermission mode of files transferred\n')

#-- main program that calls sync_library()
def main():
	long_options = ['help','pull','clobber','verbose','mode=']
	optlist,arglist = getopt.getopt(sys.argv[1:],'hPCVM:',long_options)
	#-- command-line options
	PULL = False
	CLOBBER = False
	VERBOSE = False
	MODE = 0o775
	#-- for each input argument
	for opt, arg in optlist:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-P','--pull'):
			PULL = True
		elif opt in ('-C','--clobber'):
			CLOBBER = True
		elif opt in ('-V','--verbose'):
			VERBOSE = True
		elif opt in ('-M','--mode'):
			MODE = int(arg,8)

	#-- verify that an output directory was entered as a system argument
	if not arglist:
		raise Exception('No Directory Listed as System Argument')

	#-- export references to a new directory
	for DIRECTORY in arglist:
		sync_library(os.path.expanduser(DIRECTORY), PULL=PULL, VERBOSE=VERBOSE,
			CLOBBER=CLOBBER, MODE=MODE)

#-- run main program
if __name__ == '__main__':
	main()
