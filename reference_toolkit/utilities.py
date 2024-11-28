#!/usr/bin/env python
u"""
utilities.py (11/2024)
Reads the supplied referencerc file for default file path and file format

UPDATE HISTORY:
    Updated 11/2024: improve unique filename creation
    Updated 11/2023: updated ssl context to fix deprecation errors
    Updated 05/2023: use pathlib to find and operate on paths
        added more file operation functions and renamed to utilities.py
    Updated 03/2023: use numpy doc syntax for docstrings
    Updated 09/2022: drop python2 compatibility
    Updated 02/2018: using str instead of unicode for python3 compatibility
    Written 10/2017
"""
from __future__ import annotations

import sys
import re
import ssl
import inspect
import pathlib
import urllib.request

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
def read_referencerc(referencerc_file: str | pathlib.Path):
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

# PURPOSE: open a unique filename adding a numerical instance if existing
def create_unique_filename(filename: str | pathlib.Path):
    # validate input filename
    filename = pathlib.Path(filename).expanduser().absolute()
    stem, suffix = filename.stem, filename.suffix
    # create counter to add to the end of the filename if existing
    counter = 1
    while counter:
        try:
            # open file descriptor only if the file doesn't exist
            fd = filename.open(mode='xb')
        except OSError:
            pass
        else:
            print(str(compressuser(filename)))
            return fd
        # new filename adds counter before the file extension
        filename = filename.with_name(f'{stem}-{counter:d}{suffix}')
        counter += 1

def compressuser(filename: str | pathlib.Path):
    """
    Tilde-compresses a file to be relative to the home directory

    Parameters
    ----------
    filename: str
        outptu filename
    """
    filename = pathlib.Path(filename).expanduser().absolute()
    try:
        relative_to = filename.relative_to(pathlib.Path().home())
    except ValueError as exc:
        return filename
    else:
        return pathlib.Path('~').joinpath(relative_to)

def _create_default_ssl_context() -> ssl.SSLContext:
    """Creates the default SSL context
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    _set_ssl_context_options(context)
    context.options |= ssl.OP_NO_COMPRESSION
    return context

def _create_ssl_context_no_verify() -> ssl.SSLContext:
    """Creates an SSL context for unverified connections
    """
    context = _create_default_ssl_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def _set_ssl_context_options(context: ssl.SSLContext) -> None:
    """Sets the default options for the SSL context
    """
    if sys.version_info >= (3, 10) or ssl.OPENSSL_VERSION_INFO >= (1, 1, 0, 7):
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    else:
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1

# default ssl context
_default_ssl_context = _create_ssl_context_no_verify()

# PURPOSE: check internet connection and URL
def check_connection(
        HOST: str,
        timeout: int | None = 20,
        context: ssl.SSLContext = _default_ssl_context,
    ):
    """
    Check internet connection with http host

    Parameters
    ----------
    HOST: str
        remote http host
    timeout: int
        timeout in seconds for blocking operations
    context: obj, default reference_toolkit.utilities._default_ssl_context
        SSL context for ``urllib`` opener object
    """
    # attempt to connect to remote url
    try:
        urllib.request.urlopen(HOST,
            timeout=timeout,
            context=context
        )
    except urllib.request.HTTPError:
        raise RuntimeError(f'Check URL: {HOST}')
    except urllib.request.URLError:
        raise RuntimeError('Check internet connection')
    else:
        return True
