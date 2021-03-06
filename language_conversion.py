#!/usr/bin/env python
u"""
language_conversion_list.py (12/2019)
Mapping for converting to/from python unicode for special characters
    1st column: latex format for output bibtex files
    2nd column: character with combining modifier unicode
    3rd column: precomposed character and modifier unicode
    4th column: plain text "equivalent" (scrubbed of symbols for citekeys)

OPTIONS:
    GREEK: iterate through Greek letters
    SYMBOLS: iterate through miscellaneous symbols

NOTES:
    Check unicode characters with http://www.fileformat.info/
        can add more entries to language_conversion_list

UPDATE HISTORY:
    Updated 12/2019: added letters with acute, stroke and ogonek
    Updated 04/2018: added A with tilde and C with acute
    Updated 09/2017: added options GREEK and SYMBOLS to make iterations optional
    Updated 06/2017: added more miscellaneous symbols for text to latex
        added uppercase and lowercase y with diaeresis
    Written 05/2017: extracted from individual programs and added entries
"""
def language_conversion(GREEK=True, SYMBOLS=True):
    #-- 1st column: latex, 2nd: combining unicode, 3rd: unicode, 4th: plain text
    language_conversion_list = []
    #-- Latin uppercase vowel letters with diaeresis (umlaut)
    language_conversion_list.append(('{\\"A}', u'A\u0308', u'\u00C4','A'))
    language_conversion_list.append(('{\\"E}', u'E\u0308', u'\u00CB','E'))
    language_conversion_list.append(('{\\"I}', u'I\u0308', u'\u00CF','I'))
    language_conversion_list.append(('{\\"O}', u'O\u0308', u'\u00D6','O'))
    language_conversion_list.append(('{\\"U}', u'U\u0308', u'\u00DC','U'))
    language_conversion_list.append(('{\\"Y}', u'Y\u0308', u'\u0178','Y'))
    #-- Latin lowercase vowel letters with diaeresis (umlaut)
    language_conversion_list.append(('{\\"a}', u'a\u0308', u'\u00E4','a'))
    language_conversion_list.append(('{\\"e}', u'e\u0308', u'\u00EB','e'))
    language_conversion_list.append(('{\\"i}', u'i\u0308', u'\u00EF','i'))
    language_conversion_list.append(('{\\"o}', u'o\u0308', u'\u00F6','o'))
    language_conversion_list.append(('{\\"u}', u'u\u0308', u'\u00FC','u'))
    language_conversion_list.append(('{\\"y}', u'y\u0308', u'\u00FF','y'))
    #-- Latin uppercase letters with acute (accent)
    language_conversion_list.append(("{\\'A}", u'A\u0301', u'\u00C1','A'))
    language_conversion_list.append(("{\\'E}", u'E\u0301', u'\u00C9','E'))
    language_conversion_list.append(("{\\'I}", u'I\u0301', u'\u00CD','I'))
    language_conversion_list.append(("{\\'O}", u'O\u0301', u'\u00D3','O'))
    language_conversion_list.append(("{\\'U}", u'U\u0301', u'\u00DA','U'))
    language_conversion_list.append(("{\\'Y}", u'Y\u0301', u'\u00DD','Y'))
    language_conversion_list.append(("{\\'C}", u'C\u0301', u'\u0106','C'))
    language_conversion_list.append(("{\\'N}", u'N\u0301', u'\u0143','N'))
    language_conversion_list.append(("{\\'S}", u'S\u0301', u'\u015A','S'))
    #-- Latin lowercase letters with acute (accent)
    language_conversion_list.append(("{\\'a}", u'a\u0301', u'\u00E1','a'))
    language_conversion_list.append(("{\\'e}", u'e\u0301', u'\u00E9','e'))
    language_conversion_list.append(("{\\'i}", u'i\u0301', u'\u00ED','i'))
    language_conversion_list.append(("{\\'o}", u'o\u0301', u'\u00F3','o'))
    language_conversion_list.append(("{\\'u}", u'u\u0301', u'\u00FA','u'))
    language_conversion_list.append(("{\\'y}", u'y\u0301', u'\u00FD','y'))
    language_conversion_list.append(("{\\'c}", u'c\u0301', u'\u0107','c'))
    language_conversion_list.append(("{\\'n}", u'n\u0301', u'\u0144','n'))
    language_conversion_list.append(("{\\'s}", u's\u0301', u'\u015B','s'))
    #-- Latin uppercase vowel letters with grave (accent)
    language_conversion_list.append(('{\\`A}', u'A\u0060', u'\u00C0','A'))
    language_conversion_list.append(('{\\`E}', u'E\u0060', u'\u00C8','E'))
    language_conversion_list.append(('{\\`I}', u'I\u0060', u'\u00CC','I'))
    language_conversion_list.append(('{\\`O}', u'O\u0060', u'\u00D2','O'))
    language_conversion_list.append(('{\\`U}', u'U\u0060', u'\u00D9','U'))
    language_conversion_list.append(('{\\`Y}', u'Y\u0060', u'\u1EF2','Y'))
    #-- Latin lowercase vowel letters with grave (accent)
    language_conversion_list.append(('{\\`a}', u'a\u0060', u'\u00E0','a'))
    language_conversion_list.append(('{\\`e}', u'e\u0060', u'\u00E8','e'))
    language_conversion_list.append(('{\\`i}', u'i\u0060', u'\u00EC','i'))
    language_conversion_list.append(('{\\`o}', u'o\u0060', u'\u00F2','o'))
    language_conversion_list.append(('{\\`u}', u'u\u0060', u'\u00F9','u'))
    language_conversion_list.append(('{\\`y}', u'y\u0060', u'\u1EF3','y'))
    #-- Latin uppercase vowel letters with circumflex (^)
    language_conversion_list.append(('{\\^A}', u'A\u0302', u'\u00C2','A'))
    language_conversion_list.append(('{\\^E}', u'E\u0302', u'\u00CA','E'))
    language_conversion_list.append(('{\\^I}', u'I\u0302', u'\u00CE','I'))
    language_conversion_list.append(('{\\^O}', u'O\u0302', u'\u00D4','O'))
    language_conversion_list.append(('{\\^U}', u'U\u0302', u'\u00DB','U'))
    #-- Latin lowercase vowel letters with circumflex (^)
    language_conversion_list.append(('{\\^a}', u'a\u0302', u'\u00E2','a'))
    language_conversion_list.append(('{\\^e}', u'e\u0302', u'\u00EA','e'))
    language_conversion_list.append(('{\\^i}', u'i\u0302', u'\u00EE','i'))
    language_conversion_list.append(('{\\^o}', u'o\u0302', u'\u00F4','o'))
    language_conversion_list.append(('{\\^u}', u'u\u0302', u'\u00FB','u'))
    #-- Latin uppercase letters with caron (v)
    language_conversion_list.append(('{\\v A}', u'A\u030C', u'\u01CD','A'))
    language_conversion_list.append(('{\\v E}', u'E\u030C', u'\u011A','E'))
    language_conversion_list.append(('{\\v I}', u'I\u030C', u'\u01CF','I'))
    language_conversion_list.append(('{\\v O}', u'O\u030C', u'\u01D1','O'))
    language_conversion_list.append(('{\\v U}', u'U\u030C', u'\u01D3','U'))
    language_conversion_list.append(('{\\v C}', u'C\u030C', u'\u010C','C'))
    language_conversion_list.append(('{\\v N}', u'N\u030C', u'\u0147','N'))
    language_conversion_list.append(('{\\v S}', u'S\u030C', u'\u0160','S'))
    language_conversion_list.append(('{\\v Z}', u'Z\u030C', u'\u017D','Z'))
    #-- Latin lowercase letters with caron (v)
    language_conversion_list.append(('{\\v a}', u'a\u030C', u'\u01CE','a'))
    language_conversion_list.append(('{\\v e}', u'e\u030C', u'\u011B','e'))
    language_conversion_list.append(('{\\v i}', u'i\u030C', u'\u01D0','i'))
    language_conversion_list.append(('{\\v o}', u'o\u030C', u'\u01D2','o'))
    language_conversion_list.append(('{\\v u}', u'u\u030C', u'\u01D4','u'))
    language_conversion_list.append(('{\\v c}', u'c\u030C', u'\u010D','c'))
    language_conversion_list.append(('{\\v n}', u'n\u030C', u'\u0148','n'))
    language_conversion_list.append(('{\\v s}', u's\u030C', u'\u0161','s'))
    language_conversion_list.append(('{\\v z}', u'z\u030C', u'\u017E','z'))
    #-- Latin uppercase letters with breve (u)
    language_conversion_list.append(('{\\u A}', u'A\u0306', u'\u0102','A'))
    language_conversion_list.append(('{\\u E}', u'E\u0306', u'\u0114','E'))
    language_conversion_list.append(('{\\u I}', u'I\u0306', u'\u012C','I'))
    language_conversion_list.append(('{\\u O}', u'O\u0306', u'\u014E','O'))
    language_conversion_list.append(('{\\u U}', u'U\u0306', u'\u016C','U'))
    #-- Latin lowercase letters with breve (u)
    language_conversion_list.append(('{\\u a}', u'a\u0306', u'\u0103','a'))
    language_conversion_list.append(('{\\u e}', u'e\u0306', u'\u0115','e'))
    language_conversion_list.append(('{\\u i}', u'i\u0306', u'\u012D','i'))
    language_conversion_list.append(('{\\u o}', u'o\u0306', u'\u014F','o'))
    language_conversion_list.append(('{\\u u}', u'u\u0306', u'\u016D','u'))
    #-- Latin uppercase letters with stroke
    language_conversion_list.append(('{\\A}', u'\u023A', u'\u023A','A'))
    language_conversion_list.append(('{\\I}', u'\u2C65', u'\u2C65','I'))
    language_conversion_list.append(('{\\O}', u'\u00D8', u'\u00D8','O'))
    language_conversion_list.append(('{\\L}', u'\u0141', u'\u0141','L'))
    language_conversion_list.append(('{\\Y}', u'\u024E', u'\u024E','Y'))
    language_conversion_list.append(('{\\Z}', u'\u01B5', u'\u01B5','Z'))
    #-- Latin lowercase letters with stroke
    language_conversion_list.append(('{\\a}', u'\u2C65', u'\u2C65','a'))
    language_conversion_list.append(('{\\i}', u'\u0268', u'\u0268','i'))
    language_conversion_list.append(('{\\o}', u'\u00F8', u'\u00F8','o'))
    language_conversion_list.append(('{\\l}', u'\u0142', u'\u0142','l'))
    language_conversion_list.append(('{\\y}', u'\u024F', u'\u024F','y'))
    language_conversion_list.append(('{\\z}', u'\u01B6', u'\u01B6','z'))
    #-- Latin uppercase letters with ogonek
    language_conversion_list.append(('\\k{A}', u'A\u0328', u'\u0104','A'))
    language_conversion_list.append(('\\k{E}', u'E\u0328', u'\u0118','E'))
    language_conversion_list.append(('\\k{I}', u'I\u0328', u'\u012E','I'))
    language_conversion_list.append(('\\k{O}', u'O\u0328', u'\u01EA','O'))
    language_conversion_list.append(('\\k{U}', u'U\u0328', u'\u0172','U'))
    #-- Latin lowercase letters with ogonek
    language_conversion_list.append(('\\k{a}', u'a\u0328', u'\u0105','a'))
    language_conversion_list.append(('\\k{e}', u'e\u0328', u'\u0119','e'))
    language_conversion_list.append(('\\k{i}', u'i\u0328', u'\u012F','i'))
    language_conversion_list.append(('\\k{o}', u'o\u0328', u'\u01EB','o'))
    language_conversion_list.append(('\\k{u}', u'u\u0328', u'\u0173','u'))
    #-- Latin uppercase and lowercase A with tilde
    language_conversion_list.append(('{\\~A}', u'A\u0303', u'\u00C3','A'))
    language_conversion_list.append(('{\\~a}', u'a\u0303', u'\u00E3','a'))
    #-- Latin uppercase and lowercase N with tilde (ene)
    language_conversion_list.append(('{\\~N}', u'N\u0303', u'\u00D1','N'))
    language_conversion_list.append(('{\\~n}', u'n\u0303', u'\u00F1','n'))
    #-- Latin uppercase and lowercase O with tilde
    language_conversion_list.append(('{\~O}', u'O\u0303', u'\u00D5','O'))
    language_conversion_list.append(('{\~o}', u'o\u0303', u'\u00F5','o'))
    #-- Latin lowercase sharp S (eszett)
    language_conversion_list.append(('{\\ss}', u'\u00DF', u'\u00DF','ss'))
    #-- Latin uppercase and lowercase A with ring (o)
    language_conversion_list.append(('{\\AA}', u'A\u030A', u'\u00C5','A'))
    language_conversion_list.append(('{\\aa}', u'a\u030A', u'\u00E5','a'))
    #-- Latin uppercase and lowercase ligature ash (ae)
    language_conversion_list.append(('{\\AE}', u'\u00C6', u'\u00C6','AE'))
    language_conversion_list.append(('{\\ae}', u'\u00E6', u'\u00E6','ae'))
    #-- Latin uppercase and lowercase ligature oe
    language_conversion_list.append(('{\\OE}', u'\u0152', u'\u0152','OE'))
    language_conversion_list.append(('{\\oe}', u'\u0153', u'\u0153','oe'))
    #-- Latin uppercase and lowercase eth
    language_conversion_list.append(('{\\DH}', u'\u00D0', u'\u00D0','dh'))
    language_conversion_list.append(('{\\dh}', u'\u00F0', u'\u00F0','dh'))
    #-- Latin uppercase and lowercase C with cedilla
    language_conversion_list.append(('{\\c C}', u'C\u0327', u'\u00C7','C'))
    language_conversion_list.append(('{\\c c}', u'c\u0327', u'\u00E7','c'))

    #-- if iterating through Greek letters
    if GREEK:
        #-- Greek uppercase letters
        language_conversion_list.append(('{$\\Gamma$}', u'\u0393', u'\u0393','G'))
        language_conversion_list.append(('{$\\Delta$}', u'\u0394', u'\u0394','D'))
        language_conversion_list.append(('{$\\Theta$}', u'\u0398', u'\u0398','Th'))
        language_conversion_list.append(('{$\\Lambda$}', u'\u039B', u'\u039B','L'))
        language_conversion_list.append(('{$\\Xi$}', u'\u039E', u'\u039E','X'))
        language_conversion_list.append(('{$\\Pi$}', u'\u03A0', u'\u03A0','P'))
        language_conversion_list.append(('{$\\Sigma$}', u'\u03A3', u'\u03A3','S'))
        language_conversion_list.append(('{$\\Phi$}', u'\u03A6', u'\u03A6','Ph'))
        language_conversion_list.append(('{$\\Psi$}', u'\u03A8', u'\u03A8','Ps'))
        language_conversion_list.append(('{$\\Omega$}', u'\u03A9', u'\u03A9','W'))
        #-- Greek lowercase letters
        language_conversion_list.append(('{$\\alpha$}', u'\u03B1', u'\u03B1','a'))
        language_conversion_list.append(('{$\\beta$}', u'\u03B2', u'\u03B2','b'))
        language_conversion_list.append(('{$\\gamma$}', u'\u03B3', u'\u03B3','g'))
        language_conversion_list.append(('{$\\delta$}', u'\u03B4', u'\u03B4','d'))
        language_conversion_list.append(('{$\\epsilon$}', u'\u03B5', u'\u03B5','e'))
        language_conversion_list.append(('{$\\zeta$}', u'\u03B6', u'\u03B6','z'))
        language_conversion_list.append(('{$\\zeta$}', u'\u03B7', u'\u03B7','h'))
        language_conversion_list.append(('{$\\theta$}', u'\u03B8', u'\u03B8','th'))
        language_conversion_list.append(('{$\\iota$}', u'\u03B9', u'\u03B9','i'))
        language_conversion_list.append(('{$\\kappa$}', u'\u03BA', u'\u03BA','k'))
        language_conversion_list.append(('{$\\lambda$}', u'\u03BB', u'\u03BB','l'))
        language_conversion_list.append(('{$\\mu$}', u'\u03BC', u'\u03BC','m'))
        language_conversion_list.append(('{$\\nu$}', u'\u03BD', u'\u03BD','n'))
        language_conversion_list.append(('{$\\xi$}', u'\u03BE', u'\u03BE','x'))
        language_conversion_list.append(('{$\\pi$}', u'\u03C0', u'\u03C0','p'))
        language_conversion_list.append(('{$\\rho$}', u'\u03C1', u'\u03C1','r'))
        language_conversion_list.append(('{$\\varrho$}', u'\u03F1', u'\u03F1','r'))
        language_conversion_list.append(('{$\\sigma$}', u'\u03C3', u'\u03C3','s'))
        language_conversion_list.append(('{$\\tau$}', u'\u03C4', u'\u03C4','t'))
        language_conversion_list.append(('{$\\upsilon$}', u'\u03C5', u'\u03C5','u'))
        language_conversion_list.append(('{$\\phi$}', u'\u03C6', u'\u03C6','ph'))
        language_conversion_list.append(('{$\\varphi$}', u'\u03D5', u'\u03D5','ph'))
        language_conversion_list.append(('{$\\chi$}', u'\u03C7', u'\u03C7','ch'))
        language_conversion_list.append(('{$\\psi$}', u'\u03C8', u'\u03C8','ps'))
        language_conversion_list.append(('{$\\omega$}', u'\u03C9', u'\u03C9','w'))

    #-- if iterating through symbols
    if SYMBOLS:
        #-- Miscellaneous Symbols
        language_conversion_list.append((" ",u'\u2009',u'\u2009'," "))
        language_conversion_list.append(("`",u'\u2018',u'\u2018',"'"))
        language_conversion_list.append(("'","'",u'\u2019',"'"))
        language_conversion_list.append(("``","\"",u'\u201C',"\""))
        language_conversion_list.append(("''","\"",u'\u201D',"\""))
        language_conversion_list.append(("-",u"\u2010",u'\u2010',u"\u2010"))
        language_conversion_list.append(("--",u"\u2013",u'\u2013',u"\u2013"))
        language_conversion_list.append(("---",u"\u2014",u'\u2014',u"\u2014"))
        language_conversion_list.append((" "," ",u"\u00a0", " "))
        language_conversion_list.append(("\$","$",u"\u0024","$"))
        language_conversion_list.append(("\#","#",u"\u0023","#"))
        language_conversion_list.append(("\&","&",u"\u0026","&"))
        language_conversion_list.append(("\_","_",u"\u005F","_"))
        language_conversion_list.append(("\~","~",u"\u223C","~"))
        language_conversion_list.append(("${\^\\circ}$",u"\u00B0",u"\u00B0","o"))
        language_conversion_list.append(("$\\times$",u"\u2715",u"\u2715","x"))

    #-- return the list of symbols to iterate
    return language_conversion_list
