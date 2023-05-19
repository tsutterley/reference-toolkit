#!/usr/bin/env python
u"""
read_referencerc.py (05/2023)
Reads the supplied referencerc file for default file path and file format

UPDATE HISTORY:
    Updated 05/2023: use pathlib to find and operate on paths
    Updated 03/2023: use numpy doc syntax for docstrings
    Updated 09/2022: drop python2 compatibility
    Updated 02/2018: using str instead of unicode for python3 compatibility
    Written 10/2017
"""
import re
import inspect
import pathlib

# PURPOSE: get absolute path within a package from a relative path
def get_data_path(relpath: list | str | pathlib.Path):
    """
    Get the absolute path within a package from a relative path

    Parameters
    ----------
    relpath: list, str or pathlib.Path
        relative path
    """
    # current file path
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    filepath = pathlib.Path(filename).absolute().parent
    if isinstance(relpath, list):
        # use *splat operator to extract from list
        return filepath.joinpath(*relpath)
    elif isinstance(relpath, (str, pathlib.Path)):
        return filepath.joinpath(relpath)

# PURPOSE: read referencerc file and extract parameters
def read_referencerc(referencerc_file):
    """Read referencerc fil

    Parameters
    ----------
    referencerc_file: str
        path to referencerc file for setting parameters
    """
    # variable with parameter definitions
    parameters = {}
    # Opening parameter file and assigning file ID (f)
    referencerc_file = pathlib.Path(referencerc_file).expanduser().absolute()
    with referencerc_file.open(mode='r', encoding='utf8') as f:
        # read entire line and keep all uncommented lines
        fin = [i for i in f.readlines() if i and re.match(r'^(?!\#|\n)', i)]
    # for each line in the file will extract the parameter (name and value)
    for fileline in fin:
        # Splitting the input line between parameter name and value
        part = fileline.split(':')
        # filling the parameter definition variable
        parameters[part[0].strip()] = part[1].strip()
    # return the file path and file format
    datapath = pathlib.Path(parameters['datapath']).expanduser().absolute()
    dataformat = str(parameters['dataformat'])
    return datapath, dataformat
