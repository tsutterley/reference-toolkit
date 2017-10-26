#!/usr/bin/env python
u"""
read_referencerc.py (10/2017)
Reads the supplied referencerc file for default file path and file format
"""
#-- PURPOSE: read referencerc file and extract parameters
def read_referencerc(referencerc_file):
	import os, re
	#-- variable with parameter definitions
	parameters = {}
	#-- Opening parameter file and assigning file ID (f)
	with open(os.path.expanduser(referencerc_file), 'r') as f:
		#-- read entire line and keep all uncommented lines
		fin = [i for i in f.read().splitlines() if i and re.match('^(?!#)',i)]
	#-- for each line in the file will extract the parameter (name and value)
	for fileline in fin:
		#-- Splitting the input line between parameter name and value
		part = fileline.split(':')
		#-- filling the parameter definition variable
		parameters[part[0].strip()] = part[1].strip()
	#-- return the file path and file format
	datapath = os.path.expanduser(parameters['datapath'])
	dataformat = unicode(parameters['dataformat'])
	return datapath, dataformat
