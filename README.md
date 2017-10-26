reference-toolkit
=================

#### Python-based tools for managing bibliographies using BibTeX

- [BibTeX](http://www.bibtex.org/)  
- [Papers2 universal-citekey-js](https://github.com/cparnot/universal-citekey-js)  
- [ReadCube Papers](https://www.readcube.com/papers/)  

Stores journal articles in a tree structure based from directory provided in the .referencerc file   
Saves journal articles and article supplements with name format provided in the .referencerc file   
Formats `*.ris` and `*.bib` bibliography files into a standard format  

#### Functions
gen_citekeys.py: Generates Papers2-like cite keys for BibTeX  
```bash
python gen_citekeys.py --author=Rignot --year=2008 --doi="10.1038/ngeo102"
```
smart_citekeys.py: Creates Papers2-like cite keys using information from crossref.org  
```bash
python smart_citekeys.py "10.1038/ngeo102"
```

format_bibtex.py: Reformats BibTeX files into a standard format with Universal cite keys  
```bash
python format_bibtex.py -C -O example.bib
```
smart_bibtex.py: Creates a BibTeX entry with Universal cite keys using information from crossref.org  
```bash
python smart_bibtex.py -O "10.1038/ngeo102"
```
ris_to_bibtex.py: Converts RIS bibliography files into BibTeX files with Universal cite keys  
```bash
python ris_to_bibtex.py -C -O example.ris
```

copy_journal_article.py: Copies a journal article and supplements from a website to the reference directory  
```bash
python copy_journal_articles.py --author=Rignot --year=2008 \
	--journal="Nature Geoscience" --volume=1 \
	https://www.nature.com/ngeo/journal/v1/n2/pdf/ngeo102.pdf
```
smart_copy_articles.py: Copies a journal article and supplements from a website to the reference directory using DOI's  
```bash
python smart_copy_articles.py --doi=10.1038/ngeo102 \
	https://www.nature.com/ngeo/journal/v1/n2/pdf/ngeo102.pdf
```

move_journal_article.py: Moves a journal article and supplements from a local directory to the reference directory  
```bash
python move_journal_article.py --author=Rignot --year=2008 \
	--journal="Nature Geoscience" --volume=1 ~/Downloads/ngeo102.pdf
```
smart_move_articles.py: Copies a journal article and supplements from a local directory to the reference directory using DOI's  
```bash
python smart_move_articles.py --doi=10.1038/ngeo102 ~/Downloads/ngeo102.pdf
```

search_references.py: Searches all managed BibTeX files for keywords, authors and/or journal  
```bash
python search_references.py -A Rignot -F -Y 2008 -J "Nature Geoscience"
```

open_doi.py: Opens the webpages associated with a Digital Object Identifier (DOI)  
```bash
python open_doi.py 10.1038/ngeo102
```

language_conversion.py: Mapping function that converts to/from LaTeX and python unicode for special characters  
```python
#-- 1st column: latex format for output bibtex files
#-- 2nd column: character with combining modifier unicode
#-- 3rd column: precomposed character and modifier unicode
#-- 4th column: plain text "equivalent" (scrubbed of symbols for citekeys)
for LV, CV, UV, PV in language_conversion():
	author = author.replace(UV, CV)
```

#### Journal Abbreviations
[List of Journal Name and Abbreviation modified from Web of Science](https://github.com/JabRef/abbrv.jabref.org/tree/master/journals)  

#### Download
The program homepage is:   
https://github.com/tsutterley/reference-toolkit   
A zip archive of the latest version is available directly at:    
https://github.com/tsutterley/reference-toolkit/archive/master.zip  

#### Disclaimer  
This program is not sponsored or maintained by the Universities Space Research Association (USRA) or NASA.  It is provided here for your convenience but _with no guarantees whatsoever_.  
