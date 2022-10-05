import os
from setuptools import setup, find_packages

# package description and keywords
description = 'Python-based tools for managing bibliographies using BibTeX'
keywords = 'bibliographies, bibtex, reference management'
# get long_description from README.rst
with open("README.rst", mode="r", encoding="utf8") as fh:
    long_description = fh.read()
long_description_content_type = "text/x-rst"

# get version
with open('version.txt', mode="r", encoding="utf8") as fh:
    version = fh.read()

# list of all scripts to be included with package
scripts=[os.path.join('scripts',f) for f in os.listdir('scripts') if f.endswith('.py')]
scripts.append(os.path.join('reference_toolkit','gen_citekeys.py'))

setup(
    name='reference-toolkit',
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url='https://github.com/tsutterley/reference-toolkit',
    author='Tyler Sutterley',
    author_email='tsutterl@uw.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords=keywords,
    packages=find_packages(),
    install_requires=['future'],
    scripts=scripts,
    include_package_data=True,
)
