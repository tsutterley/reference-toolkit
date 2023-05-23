#!/usr/bin/env python
u"""
sync_library.py (05/2023)
Exports complete library into a new directory (such as a mounted-drive)
Will only copy new or overwritten files by checking the last modified dates

CALLING SEQUENCE:
    python sync_library.py -V /path_to_external_library

INPUTS:
    Directory for outputting reference library

COMMAND LINE OPTIONS:
    -P, --pull: Transfer files from external directory to library
    -L, --list: List files without transferring
    -C, --clobber: Overwrite existing data in transfer
    -V, --verbose: Print all transferred files
    -M X, --mode X: Permission mode of files transferred

PROGRAM DEPENDENCIES:
    utilities.py: Sets default file path and file format for output files

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 12/2020: using argparse to set command line options
    Updated 02/2019: added option list to only print the files to be transferred
    Written 02/2018
"""
from __future__ import print_function, division

import re
import os
import shutil
import pathlib
import argparse
import reference_toolkit

# Reads BibTeX files for each article stored in the working directory
# exports as a single file sorted by BibTeX key
def sync_library(DIRECTORY, PULL=False, LIST=False, VERBOSE=False,
    CLOBBER=False, MODE=0o775):
    # get reference filepath and reference format from referencerc file
    referencerc = reference_toolkit.get_data_path(['assets','.referencerc'])
    datapath, dataformat = reference_toolkit.read_referencerc(referencerc)
    # subdirectories with supplementary information
    S = 'Supplemental'

    # if transferring from DIRECTORY to library
    d_in,d_out = (DIRECTORY,datapath) if PULL else (datapath,DIRECTORY)
    # iterate over yearly directories
    years = [sd for sd in d_in.iterdir() if
        re.match(r'\d+',sd.name) and sd.is_dir()]
    for Y in sorted(years):
        # find author directories in year
        authors = [sd for sd in Y.iterdir() if sd.is_dir()]
        for A in sorted(authors):
            # find BibTeX and article files within author directory
            regex = rf'((.*?)-(.*?)\.bib$)|({A.name}_(.*?)_{Y.name}(.*?)$)'
            FILES = [fi for fi in A.iterdir() if re.match(regex,fi.name)]
            # transfer each article file (check if existing)
            for f_in in FILES:
                f_out = d_out.joinpath(Y.name,A.name,f_in.name)
                transfer_push_file(f_in, f_out, LIST=LIST,
                    CLOBBER=CLOBBER, VERBOSE=VERBOSE, MODE=MODE)
            # if there is supplementary information
            SI = A.joinpath(S)
            if SI.exists() and SI.is_dir():
                # find supplementary files within Supplemental directory
                FILES = [fi for fi in SI.iterdir() if re.match(regex,fi.name)]
                # transfer each supplementary file (check if existing)
                for f_in in FILES:
                    f_out = d_out.joinpath(Y.name,A.name,S,f_in.name)
                    transfer_push_file(f_in, f_out, LIST=LIST,
                        CLOBBER=CLOBBER, VERBOSE=VERBOSE, MODE=MODE)

# PURPOSE: push an input file to an output directory checking if file exists
# and if the input file is newer than any existing output file
# set the permissions mode of the transferred file to MODE
def transfer_push_file(input_file, output_file, LIST=False,
    CLOBBER=False, VERBOSE=False, MODE=0o775):
    # check if input file is newer than the output file
    TEST = False
    overwrite = ' (clobber)'
    # last modification time of the input file
    input_mtime = input_file.stat().st_mtime
    if output_file.exists():
        output_mtime = output_file.stat().st_mtime
        # if input file is newer: overwrite the output file
        # verifying based on even mtimes for different file systems
        if (even(input_mtime) > even(output_mtime)):
            TEST = True
            overwrite = ' (overwrite)'
    else:
        TEST = True
        overwrite = ' (new)'
    # if output file does not exist, is to be overwritten, or CLOBBER is set
    if TEST or CLOBBER:
        if VERBOSE or LIST:
            print(f'{str(input_file)} -->\n\t{str(output_file)}{overwrite}\n')
        # if transferring files and not only printing the filenames
        if not LIST:
            # recursively create output directory if not currently existing
            output_file.parent.mkdir(mode=MODE, parents=True, exist_ok=True)
            # check if input_file is a directory (e.g. unzipped Supplementary)
            if input_file.isdir():
                # copy input directory to storage output directory
                shutil.copytree(input_file, output_file)
            else:
                # copy input files to storage output
                shutil.copyfile(input_file, output_file)
            # change the permissions level of the transported file to MODE
            output_file.chmod(mode=MODE)
            # set modification times of the output file
            os.utime(output_file, (output_file.stat().st_atime,input_mtime))

# PURPOSE: rounds a number to an even number less than or equal to original
def even(i):
    return 2*int(i//2)

# main program that calls sync_library()
def main():
    # Read the system arguments listed after the program
    parser = argparse.ArgumentParser(
        description="""Exports complete library into a new directory
            """
    )
    # command line parameters
    parser.add_argument('directory',
        type=pathlib.Path, default=pathlib.Path.cwd(),
        help='External reference directory')
    parser.add_argument('--pull','-P',
        default=False, action='store_true',
        help='Transfer files from external directory to library')
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

    # export references to a new directory
    sync_library(args.directory, PULL=args.pull, LIST=args.list,
        VERBOSE=args.verbose, CLOBBER=args.clobber, MODE=args.mode)

# run main program
if __name__ == '__main__':
    main()
