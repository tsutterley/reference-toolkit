#!/usr/bin/env python
u"""
scp_library.py (02/2019)
Exports complete library into a remote directory via scp
Will only copy new or overwritten files by checking the last modified dates

CALLING SEQUENCE:
	python scp_library.py -V remote:/path_to_remote_library

INPUTS:
	remote directory for outputting reference library

COMMAND LINE OPTIONS:
	-P, --pull: Transfer files from remote directory to library
	-L, --list: List files without transferring
	-C, --clobber: Overwrite existing data in transfer
	-V, --verbose: Print all transferred files
	-M X, --mode=X: Permission mode of files transferred

PYTHON DEPENDENCIES:
	paramiko: Native Python SSHv2 protocol library
		http://www.paramiko.org/
		https://github.com/paramiko/paramiko
	scp: scp module for paramiko
		https://github.com/jbardin/scp.py
	future: Compatibility layer between Python 2 and Python 3
		(http://python-future.org/)

PROGRAM DEPENDENCIES:
	read_referencerc.py: Sets default file path and file format for output files

UPDATE HISTORY:
	Written 02/2019
"""
from __future__ import print_function

import sys
import re
import os
import scp
import stat
import getopt
import getpass
import inspect
import logging
import builtins
import paramiko
import posixpath
from read_referencerc import read_referencerc

#-- current file path for the program
filename = inspect.getframeinfo(inspect.currentframe()).filename
filepath = os.path.dirname(os.path.abspath(filename))

#-- Reads BibTeX files for each article stored in the working directory
#-- exports as a single file sorted by BibTeX key
def scp_library(client, ftp, REMOTE, PULL=False, LIST=False,
	VERBOSE=False, CLOBBER=False, MODE=0o775):
	#-- get reference filepath and reference format from referencerc file
	datapath,dataformat=read_referencerc(os.path.join(filepath,'.referencerc'))

	#-- subdirectories with supplementary information
	S = 'Supplemental'

	#-- if pulling from remote directory to local
	if PULL:
		#-- iterate over yearly directories
		years = [s for s in ftp.listdir(REMOTE) if re.match('\d+',s) and
			stat.S_ISDIR(ftp.lstat(posixpath.join(REMOTE,s)).st_mode)]
		for Y in sorted(years):
			#-- find author directories in year
			authors = [s for s in ftp.listdir(posixpath.join(REMOTE,Y)) if
				stat.S_ISDIR(ftp.lstat(posixpath.join(REMOTE,Y,s)).st_mode)]
			for A in sorted(authors):
				#-- find BibTeX and article files within author directory
				regex = '((.*?)-(.*?)\.bib$)|({0}_(.*?)_{1}(.*?)$)'.format(A,Y)
				FILES = [f for f in ftp.listdir(posixpath.join(REMOTE,Y,A))
					if re.match(regex,f)]
				#-- transfer each article file (check if existing)
				for fi in FILES:
					local_dir = os.path.join(datapath,Y,A)
					remote_dir = os.path.join(REMOTE,Y,A)
					scp_pull_file(client,ftp,fi,local_dir,remote_dir,
						CLOBBER=CLOBBER,VERBOSE=VERBOSE,LIST=LIST,MODE=MODE)
				#-- if there is supplementary information
				if S in ftp.listdir(posixpath.join(REMOTE,Y,A)):
					#-- find supplementary files within Supplemental directory
					FILES=[f for f in ftp.listdir(posixpath.join(REMOTE,Y,A,S))
						if re.match(regex,f)]
					#-- transfer each supplementary file (check if existing)
					for fi in FILES:
						local_dir = os.path.join(datapath,Y,A,S)
						remote_dir = os.path.join(REMOTE,Y,A,S)
						scp_pull_file(client,ftp,fi,local_dir,remote_dir,
							CLOBBER=CLOBBER,VERBOSE=VERBOSE,LIST=LIST,MODE=MODE)
	else:
		#-- iterate over yearly directories
		years = [sd for sd in os.listdir(datapath) if re.match('\d+',sd) and
			os.path.isdir(os.path.join(datapath,sd))]
		for Y in sorted(years[:1]):
			#-- make remote directory if currently non-existent
			if (Y not in ftp.listdir(REMOTE)):
				ftp.mkdir(posixpath.join(REMOTE,Y), MODE)
			#-- find author directories in year
			authors = [sd for sd in os.listdir(os.path.join(datapath,Y)) if
				os.path.isdir(os.path.join(datapath,Y,sd))]
			for A in sorted(authors):
				#-- make remote directory if currently non-existent
				if (A not in ftp.listdir(posixpath.join(REMOTE,Y))):
					ftp.mkdir(posixpath.join(REMOTE,Y,A), MODE)
				#-- find BibTeX and article files within author directory
				regex = '((.*?)-(.*?)\.bib$)|({0}_(.*?)_{1}(.*?)$)'.format(A,Y)
				FILES = [f for f in os.listdir(os.path.join(datapath,Y,A))
					if re.match(regex,f)]
				#-- transfer each article file (check if existing)
				for fi in FILES:
					local_dir = os.path.join(datapath,Y,A)
					remote_dir = os.path.join(REMOTE,Y,A)
					scp_push_file(client,ftp,fi,local_dir,remote_dir,
						CLOBBER=CLOBBER,VERBOSE=VERBOSE,LIST=LIST,MODE=MODE)
				#-- if there is supplementary information
				if os.path.isdir(os.path.join(datapath,Y,A,S)):
					#-- make remote directory if currently non-existent
					if (S not in ftp.listdir(posixpath.join(REMOTE,Y,A))):
						ftp.mkdir(posixpath.join(REMOTE,Y,A,S), MODE)
					#-- find supplementary files within Supplemental directory
					FILES=[f for f in os.listdir(os.path.join(datapath,Y,A,S))
						if re.match(regex,f)]
					#-- transfer each supplementary file (check if existing)
					for fi in FILES:
						local_dir = os.path.join(datapath,Y,A,S)
						remote_dir = os.path.join(REMOTE,Y,A,S)
						scp_push_file(client,ftp,fi,local_dir,remote_dir,
							CLOBBER=CLOBBER,VERBOSE=VERBOSE,LIST=LIST,MODE=MODE)

#-- PURPOSE: try logging onto the server and catch authentication errors
def attempt_login(HOST, USER, IDENTITYFILE=None):
	#-- open HOST ssh client
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	tryagain = True
	attempts = 1
	#-- use identification file
	if IDENTITYFILE:
		try:
			client.connect(HOST, username=USER, key_filename=IDENTITYFILE)
		except paramiko.ssh_exception.AuthenticationException:
			pass
		else:
			return client
		attempts += 1
	#-- enter password securely from command-line
	while tryagain:
		PASSWORD = getpass.getpass('Password for {0}@{1}: '.format(USER,HOST))
		try:
			client.connect(HOST, username=USER, password=PASSWORD)
		except paramiko.ssh_exception.AuthenticationException:
			pass
		else:
			del PASSWORD
			return client
		#-- retry with new password
		print('Authentication Failed (Attempt {0:d})'.format(attempts))
		tryagain=builtins.input('Try Different Password? (Y/N): ') in ('Y','y')
		attempts += 1
	#-- exit program if not trying again
	sys.exit()

#-- PURPOSE: push a local file to a remote host checking if file exists
#-- and if the local file is newer than the remote file
#-- set the permissions mode of the remote transferred file to MODE
def scp_push_file(client, client_ftp, transfer_file, local_dir, remote_dir,
	CLOBBER=False, VERBOSE=False, LIST=False, MODE=0o775):
	#-- local and remote versions of file
	local_file = os.path.join(local_dir,transfer_file)
	remote_file = os.path.join(remote_dir,transfer_file)
	#-- check if local file is newer than the remote file
	TEST = False
	OVERWRITE = 'clobber'
	if (transfer_file in client_ftp.listdir(remote_dir)):
		local_mtime = os.stat(local_file).st_mtime
		remote_mtime = client_ftp.stat(remote_file).st_mtime
		#-- if local file is newer: overwrite the remote file
		if (even(local_mtime) > even(remote_mtime)):
			TEST = True
			OVERWRITE = 'overwrite'
	else:
		TEST = True
		OVERWRITE = 'new'
	#-- if file does not exist remotely, is to be overwritten, or CLOBBER is set
	if TEST or CLOBBER:
		if VERBOSE or LIST:
			print('{0} --> '.format(local_file))
			print('\t{0} ({1})\n'.format(remote_file,OVERWRITE))
		#-- if not only listing files
		if not LIST:
			#-- copy local files to remote server
			with scp.SCPClient(client.get_transport(), socket_timeout=20) as s:
			    s.put(local_file, remote_file, preserve_times=True)
			#-- change the permissions level of the transported file to MODE
			client_ftp.chmod(remote_file, MODE)

#-- PURPOSE: pull file from a remote host checking if file exists locally
#-- and if the remote file is newer than the local file
#-- set the permissions mode of the local transferred file to MODE
def scp_pull_file(client, client_ftp, transfer_file, local_dir, remote_dir,
	CLOBBER=False, VERBOSE=False, LIST=False, MODE=0o775):
	#-- local and remote versions of file
	local_file = os.path.join(local_dir,transfer_file)
	remote_file = os.path.join(remote_dir,transfer_file)
	#-- check if remote file is newer than the local file
	TEST = False
	OVERWRITE = 'clobber'
	if os.access(local_file, os.F_OK):
		local_mtime = os.stat(local_file).st_mtime
		remote_mtime = client_ftp.stat(remote_file).st_mtime
		#-- if remote file is newer: overwrite the local file
		if (even(remote_mtime) > even(local_mtime)):
			TEST = True
			OVERWRITE = 'overwrite'
	else:
		TEST = True
		OVERWRITE = 'new'
	#-- if file does not exist locally, is to be overwritten, or CLOBBER is set
	if TEST or CLOBBER:
		if VERBOSE or LIST:
			print('{0} --> '.format(remote_file))
			print('\t{0} ({1})\n'.format(local_file,OVERWRITE))
		#-- if not only listing files
		if not LIST:
			#-- recursively create local directories if not currently existing
			os.makedirs(local_dir) if not os.access(local_dir,os.F_OK) else None
			#-- copy local files from remote server
			with scp.SCPClient(client.get_transport(), socket_timeout=20) as s:
				s.get(remote_file, local_path=local_file, preserve_times=True)
			#-- change the permissions level of the transported file to MODE
			os.chmod(local_file, MODE)

#-- PURPOSE: rounds a number to an even number less than or equal to original
def even(i):
	return 2*int(i/2)

#-- PURPOSE: help module to describe the optional input parameters
def usage():
	print('\nHelp: {}'.format(os.path.basename(sys.argv[0])))
	print(' -P, --pull\t\tTransfer files from external directory to library')
	print(' -L, --list\t\tList files without transferring')
	print(' -C, --clobber\t\tOverwrite existing data in transfer')
	print(' -V, --verbose\t\tPrint all transferred files')
	print(' -M X, --mode=X\t\tPermission mode of files transferred\n')

#-- main program that calls scp_library()
def main():
	long_options = ['help','pull','list','clobber','verbose','mode=']
	optlist,arglist = getopt.getopt(sys.argv[1:],'hPLCVM:',long_options)
	#-- command-line options
	PULL = False
	LIST = False
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
		elif opt in ('-L','--list'):
			LIST = True
		elif opt in ('-C','--clobber'):
			CLOBBER = True
		elif opt in ('-V','--verbose'):
			VERBOSE = True
		elif opt in ('-M','--mode'):
			MODE = int(arg,8)

	#-- for each system argument
	for arg in arglist:
		#-- separate between remote hostname and remote path
		rx = re.compile('((.*?)[?=\@])?((.*?)[?=\:])(.*?)$',re.VERBOSE)
		USER,HOST,REMOTE = rx.match(arg).group(2,4,5)
		#-- use ssh configuration file to extract hostname, user and identityfile
		user_config_file = os.path.join(os.environ['HOME'],".ssh","config")
		if os.path.exists(user_config_file):
			#-- read ssh configuration file and parse with paramiko
			ssh_config = paramiko.SSHConfig()
			with open(user_config_file) as f:
				ssh_config.parse(f)
			#-- lookup hostname from list of hosts
			user_config = ssh_config.lookup(HOST)
			HOST = user_config['hostname']
			#-- get username if not entered from command-line
			if USER is None and 'user' in user_config.keys():
				USER = user_config['user']
			#-- use identityfile if in ssh configuration file
			if 'identityfile' in user_config.keys():
				IDENTITYFILE = user_config['identityfile']

		#-- open HOST ssh client for USER (and use password if no IDENTITYFILE)
		client = attempt_login(HOST, USER, IDENTITYFILE=IDENTITYFILE)
		#-- open secure FTP client
		client_ftp = client.open_sftp()
		#-- verbosity settings
		if VERBOSE or LIST:
			logging.getLogger("paramiko").setLevel(logging.WARNING)
			print('{0}@{1}:\n'.format(USER, HOST))

		#-- export references to a new directory
		scp_library(client, client_ftp, REMOTE, PULL=PULL, LIST=LIST,
			VERBOSE=VERBOSE, CLOBBER=CLOBBER, MODE=MODE)

		#-- close the secure FTP server
		client_ftp.close()
		#-- close the scp client
		client = None

#-- run main program
if __name__ == '__main__':
	main()
