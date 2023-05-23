#!/usr/bin/env python
u"""
scp_library.py (05/2023)
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
    -M X, --mode X: Permission mode of files transferred

PYTHON DEPENDENCIES:
    paramiko: Native Python SSHv2 protocol library
        http://www.paramiko.org/
        https://github.com/paramiko/paramiko
    scp: scp module for paramiko
        https://github.com/jbardin/scp.py
    future: Compatibility layer between Python 2 and Python 3
        (http://python-future.org/)

PROGRAM DEPENDENCIES:
    utilities.py: Sets default file path and file format for output files

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 12/2020: using argparse to set command line options
    Written 02/2019
"""
from __future__ import print_function, division

import sys
import re
import stat
import getpass
import logging
import pathlib
import argparse
import builtins
import paramiko
import scp
import reference_toolkit

# Reads BibTeX files for each article stored in the working directory
# exports as a single file sorted by BibTeX key
def scp_library(client, ftp, R, PULL=False, LIST=False,
    VERBOSE=False, CLOBBER=False, MODE=0o775):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # subdirectories with supplementary information
    S = 'Supplemental'

    # if pulling from remote directory to local
    if PULL:
        # iterate over yearly directories
        years = [R.joinpath(s) for s in ftp.listdir(str(R)) if
            re.match(r'\d+',s) and stat.S_ISDIR(ftp.lstat(str(R.joinpath(s))).st_mode)]
        for Y in sorted(years):
            # find author directories in year
            authors = [Y.joinpath(s) for s in ftp.listdir(str(Y)) if
                stat.S_ISDIR(ftp.lstat(str(Y.joinpath(s))).st_mode)]
            for A in sorted(authors):
                # find BibTeX and article files within author directory
                regex = rf'((.*?)-(.*?)\.bib$)|({A}_(.*?)_{Y}(.*?)$)'
                FILES = [A.joinpath(f) for f in ftp.listdir(str(A))
                    if re.match(regex,f)]
                # transfer each article file (check if existing)
                for f_in in FILES:
                    f_out = datapath.joinpath(Y.name,A.name,f_in.name)
                    scp_pull_file(client, ftp, f_out, f_in,
                        CLOBBER=CLOBBER,
                        VERBOSE=VERBOSE,
                        LIST=LIST,
                        MODE=MODE)
                # if there is supplementary information
                if S in ftp.listdir(str(A)):
                    # find supplementary files within Supplemental directory
                    FILES = [A.joinpath(S,f) for f in ftp.listdir(str(A.joinpath(S)))
                        if re.match(regex,f)]
                    # transfer each supplementary file (check if existing)
                    for f_in in FILES:
                        f_out = datapath.joinpath(Y.name,A.name,S,f_in.name)
                        scp_pull_file(client, ftp, f_out, f_in,
                            CLOBBER=CLOBBER,
                            VERBOSE=VERBOSE,
                            LIST=LIST,
                            MODE=MODE)
    else:
        # iterate over yearly directories
        years = [sd for sd in datapath.iterdir() if re.match(r'\d+',sd.name) and
            sd.is_dir()]
        for Y in sorted(years):
            # find author directories in year
            authors = [sd for sd in Y.iterdir() if sd.is_dir()]
            for A in sorted(authors):
                # find BibTeX and article files within author directory
                regex = rf'((.*?)-(.*?)\.bib$)|({A.name}_(.*?)_{Y.name}(.*?)$)'
                FILES = [f for f in A.iterdir() if re.match(regex,f.name)]
                # transfer each article file (check if existing)
                for f_in in FILES:
                    f_out = R.joinpath(Y.name,A.name,f_in.name)
                    scp_push_file(client, ftp, f_in, f_out,
                        CLOBBER=CLOBBER,
                        VERBOSE=VERBOSE,
                        LIST=LIST,
                        MODE=MODE)
                # if there is supplementary information
                SI = A.joinpath(S)
                if SI.exists() and SI.is_dir():
                    # find supplementary files within Supplemental directory
                    FILES = [f for f in SI.iterdir() if re.match(regex,f)]
                    # transfer each supplementary file (check if existing)
                    for f_in in FILES:
                        f_out = R.joinpath(Y.name,A.name,S,f_in.name)
                        scp_push_file(client, ftp, f_in, f_out,
                            CLOBBER=CLOBBER,
                            VERBOSE=VERBOSE,
                            LIST=LIST,
                            MODE=MODE)

# PURPOSE: try logging onto the server and catch authentication errors
def attempt_login(HOST, USER, IDENTITYFILE=None):
    # open HOST ssh client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    tryagain = True
    attempts = 1
    # use identification file
    if IDENTITYFILE:
        try:
            client.connect(HOST, username=USER, key_filename=IDENTITYFILE)
        except paramiko.ssh_exception.AuthenticationException:
            pass
        else:
            return client
        attempts += 1
    # enter password securely from command-line
    while tryagain:
        PASSWORD = getpass.getpass(f'Password for {USER}@{HOST}: ')
        try:
            client.connect(HOST, username=USER, password=PASSWORD)
        except paramiko.ssh_exception.AuthenticationException:
            pass
        else:
            del PASSWORD
            return client
        # retry with new password
        print(f'Authentication Failed (Attempt {attempts:d})')
        tryagain = builtins.input('Try Different Password? (Y/N): ') in ('Y','y')
        attempts += 1
    # exit program if not trying again
    sys.exit()

# PURPOSE: recursively create remote directories if not currently existing
def client_mkdir(ftp, remote, MODE=0o775):
    R = pathlib.PosixPath()
    # iterate over parents of remote path
    for p in remote.parents[-2::-1]:
        # create directory if non-existent
        if (p.name not in ftp.listdir(str(R))):
            ftp.mkdir(str(R.joinpath(p.name)), MODE)
        # append to remote path
        R = R.joinpath(p.name)

# PURPOSE: push a local file to a remote host checking if file exists
# and if the local file is newer than the remote file
# set the permissions mode of the remote transferred file to MODE
def scp_push_file(client, client_ftp, local_file, remote_file,
    CLOBBER=False, VERBOSE=False, LIST=False, MODE=0o775):
    # check if local file is newer than the remote file
    TEST = False
    overwrite = ' (clobber)'
    try:
        local_mtime = local_file.stat().st_mtime
        remote_mtime = client_ftp.stat(str(remote_file)).st_mtime
    except FileNotFoundError:
        TEST = True
        overwrite = ' (new)'
    else:
        # if local file is newer: overwrite the remote file
        if (even(local_mtime) > even(remote_mtime)):
            TEST = True
            overwrite = ' (overwrite)'
    # if file does not exist remotely, is to be overwritten, or CLOBBER is set
    if TEST or CLOBBER:
        if VERBOSE or LIST:
            print(f'{str(local_file)} --> ')
            print(f'\t{str(remote_file)}{overwrite}\n')
        # if not only listing files
        if not LIST:
            # make remote directory if currently non-existent
            client_mkdir(client_ftp, remote_file, MODE=MODE)
            # copy local files to remote server
            with scp.SCPClient(client.get_transport(), socket_timeout=20) as s:
                s.put(local_file, remote_file, preserve_times=True)
            # change the permissions level of the transported file to MODE
            client_ftp.chmod(str(remote_file), MODE)

# PURPOSE: pull file from a remote host checking if file exists locally
# and if the remote file is newer than the local file
# set the permissions mode of the local transferred file to MODE
def scp_pull_file(client, client_ftp, local_file, remote_file,
    CLOBBER=False, VERBOSE=False, LIST=False, MODE=0o775):
    # check if remote file is newer than the local file
    TEST = False
    overwrite = ' (clobber)'
    try:
        local_mtime = local_file.stat().st_mtime
        remote_mtime = client_ftp.stat(str(remote_file)).st_mtime
    except FileNotFoundError:
        TEST = True
        overwrite = ' (new)'
    else:
        # if remote file is newer: overwrite the local file
        if (even(remote_mtime) > even(local_mtime)):
            TEST = True
            overwrite = ' (overwrite)'
    # if file does not exist locally, is to be overwritten, or CLOBBER is set
    if TEST or CLOBBER:
        if VERBOSE or LIST:
            print(f'{str(remote_file)} --> ')
            print(f'\t{str(local_file)}{overwrite}\n')
        # if not only listing files
        if not LIST:
            # recursively create local directories if not currently existing
            local_file.parent.mkdir(mode=MODE, parents=True, exist_ok=True)
            # copy local files from remote server
            with scp.SCPClient(client.get_transport(), socket_timeout=20) as s:
                s.get(remote_file, local_path=local_file, preserve_times=True)
            # change the permissions level of the transported file to MODE
            local_file.chmod(mode=MODE)

# PURPOSE: rounds a number to an even number less than or equal to original
def even(i):
    return 2*int(i//2)

# main program that calls scp_library()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Exports complete library into a remote directory via scp
            """
    )
    # command line parameters
    parser.add_argument('remote',
        type=str, nargs='+',
        help='Remote reference directory')
    parser.add_argument('--pull','-P',
        default=False, action='store_true',
        help='Transfer files from remote directory to library')
    parser.add_argument('--list','-L',
        default=False, action='store_true',
        help='List files without transferring')
    parser.add_argument('--clobber','-C',
        default=False, action='store_true',
        help='Overwrite existing files in transfer')
    parser.add_argument('--verbose','-V',
        default=False, action='store_true',
        help='Print all transferred files')
    # permissions mode of the local directories and files (number in octal)
    parser.add_argument('--mode','-M',
        type=lambda x: int(x,base=8), default=0o775,
        help='Permission mode of directories and files transferred')
    args = parser.parse_args()

    # for each system argument
    for arg in args.remote:
        # separate between remote hostname and remote path
        rx = re.compile(r'((.*?)[?=\@])?((.*?)[?=\:])(.*?)$',re.VERBOSE)
        USER,HOST,REMOTE = rx.match(arg).group(2,4,5)
        # use ssh configuration file to extract hostname, user and identityfile
        user_config_file = pathlib.Path().home().joinpath('.ssh','config')
        if user_config_file.exists():
            # read ssh configuration file and parse with paramiko
            ssh_config = paramiko.SSHConfig()
            with user_config_file.open(mode='r', encoding='utf-8') as f:
                ssh_config.parse(f)
            # lookup hostname from list of hosts
            user_config = ssh_config.lookup(HOST)
            HOST = user_config['hostname']
            # get username if not entered from command-line
            if USER is None and 'user' in user_config.keys():
                USER = user_config['user']
            # use identityfile if in ssh configuration file
            if 'identityfile' in user_config.keys():
                IDENTITYFILE = user_config['identityfile']

        # open HOST ssh client for USER (and use password if no IDENTITYFILE)
        client = attempt_login(HOST, USER, IDENTITYFILE=IDENTITYFILE)
        # open secure FTP client
        client_ftp = client.open_sftp()
        # verbosity settings
        if args.verbose or args.list:
            logging.getLogger("paramiko").setLevel(logging.WARNING)
            print(f'{USER}@{HOST}:\n')

        # export references to a new directory
        scp_library(client, client_ftp, pathlib.PosixPath(REMOTE),
            PULL=args.pull,
            LIST=args.list,
            VERBOSE=args.verbose,
            CLOBBER=args.clobber,
            MODE=args.mode)

        # close the secure FTP server
        client_ftp.close()
        # close the scp client
        client = None

# run main program
if __name__ == '__main__':
    main()
