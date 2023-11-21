#!/usr/bin/env python
u"""
conversions.py (11/2023)
Mapping for converting to/from python unicode for special characters
    1st column: latex format for output bibtex files
    2nd column: character with combining modifier unicode
    3rd column: precomposed character and modifier unicode
    4th column: plain text "equivalent" (scrubbed of symbols for citekeys)

OPTIONS:
    greek: iterate through Greek letters
    symbols: iterate through miscellaneous symbols

NOTES:
    Check unicode characters with http://www.fileformat.info/
        can add more entries to conversions

UPDATE HISTORY:
    Updated 11/2023: lower case kwargs for greek and symbols
    Updated 03/2023: use numpy doc syntax for docstrings
    Updated 12/2019: added letters with acute, stroke and ogonek
    Updated 04/2018: added A with tilde and C with acute
    Updated 09/2017: options GREEK and SYMBOLS to make iterations optional
    Updated 06/2017: added more miscellaneous symbols for text to latex
        added uppercase and lowercase y with diaeresis
    Written 05/2017: extracted from individual programs and added entries
"""
def language_conversion(greek=True, symbols=True):
    """Mapping for converting to/from python unicode for special characters

    Parameters
    ----------
    greek: bool
        Iterate through Greek letters
    symbols: bool
        Iterate through miscellaneous symbols
    """
    # 1st column: latex
    # 2nd: combining unicode
    # 3rd: unicode
    # 4th: plain text
    conversions = []
    # Latin uppercase vowel letters with diaeresis (umlaut)
    conversions.append((r'{\"A}', 'A\u0308', '\u00C4', 'A'))
    conversions.append((r'{\"E}', 'E\u0308', '\u00CB', 'E'))
    conversions.append((r'{\"I}', 'I\u0308', '\u00CF', 'I'))
    conversions.append((r'{\"O}', 'O\u0308', '\u00D6', 'O'))
    conversions.append((r'{\"U}', 'U\u0308', '\u00DC', 'U'))
    conversions.append((r'{\"Y}', 'Y\u0308', '\u0178', 'Y'))
    # Latin lowercase vowel letters with diaeresis (umlaut)
    conversions.append((r'{\"a}', 'a\u0308', '\u00E4', 'a'))
    conversions.append((r'{\"e}', 'e\u0308', '\u00EB', 'e'))
    conversions.append((r'{\"i}', 'i\u0308', '\u00EF', 'i'))
    conversions.append((r'{\"o}', 'o\u0308', '\u00F6', 'o'))
    conversions.append((r'{\"u}', 'u\u0308', '\u00FC', 'u'))
    conversions.append((r'{\"y}', 'y\u0308', '\u00FF', 'y'))
    # Latin uppercase letters with acute (accent)
    conversions.append((r"{\'A}", 'A\u0301', '\u00C1', 'A'))
    conversions.append((r"{\'E}", 'E\u0301', '\u00C9', 'E'))
    conversions.append((r"{\'I}", 'I\u0301', '\u00CD', 'I'))
    conversions.append((r"{\'O}", 'O\u0301', '\u00D3', 'O'))
    conversions.append((r"{\'U}", 'U\u0301', '\u00DA', 'U'))
    conversions.append((r"{\'Y}", 'Y\u0301', '\u00DD', 'Y'))
    conversions.append((r"{\'C}", 'C\u0301', '\u0106', 'C'))
    conversions.append((r"{\'N}", 'N\u0301', '\u0143', 'N'))
    conversions.append((r"{\'S}", 'S\u0301', '\u015A', 'S'))
    # Latin lowercase letters with acute (accent)
    conversions.append((r"{\'a}", 'a\u0301', '\u00E1', 'a'))
    conversions.append((r"{\'e}", 'e\u0301', '\u00E9', 'e'))
    conversions.append((r"{\'i}", 'i\u0301', '\u00ED', 'i'))
    conversions.append((r"{\'o}", 'o\u0301', '\u00F3', 'o'))
    conversions.append((r"{\'u}", 'u\u0301', '\u00FA', 'u'))
    conversions.append((r"{\'y}", 'y\u0301', '\u00FD', 'y'))
    conversions.append((r"{\'c}", 'c\u0301', '\u0107', 'c'))
    conversions.append((r"{\'n}", 'n\u0301', '\u0144', 'n'))
    conversions.append((r"{\'s}", 's\u0301', '\u015B', 's'))
    # Latin uppercase vowel letters with grave (accent)
    conversions.append((r'{\`A}', 'A\u0060', '\u00C0', 'A'))
    conversions.append((r'{\`E}', 'E\u0060', '\u00C8', 'E'))
    conversions.append((r'{\`I}', 'I\u0060', '\u00CC', 'I'))
    conversions.append((r'{\`O}', 'O\u0060', '\u00D2', 'O'))
    conversions.append((r'{\`U}', 'U\u0060', '\u00D9', 'U'))
    conversions.append((r'{\`Y}', 'Y\u0060', '\u1EF2', 'Y'))
    # Latin lowercase vowel letters with grave (accent)
    conversions.append((r'{\`a}', 'a\u0060', '\u00E0', 'a'))
    conversions.append((r'{\`e}', 'e\u0060', '\u00E8', 'e'))
    conversions.append((r'{\`i}', 'i\u0060', '\u00EC', 'i'))
    conversions.append((r'{\`o}', 'o\u0060', '\u00F2', 'o'))
    conversions.append((r'{\`u}', 'u\u0060', '\u00F9', 'u'))
    conversions.append((r'{\`y}', 'y\u0060', '\u1EF3', 'y'))
    # Latin uppercase vowel letters with circumflex (^)
    conversions.append((r'{\^A}', 'A\u0302', '\u00C2', 'A'))
    conversions.append((r'{\^E}', 'E\u0302', '\u00CA', 'E'))
    conversions.append((r'{\^I}', 'I\u0302', '\u00CE', 'I'))
    conversions.append((r'{\^O}', 'O\u0302', '\u00D4', 'O'))
    conversions.append((r'{\^U}', 'U\u0302', '\u00DB', 'U'))
    # Latin lowercase vowel letters with circumflex (^)
    conversions.append((r'{\^a}', 'a\u0302', '\u00E2', 'a'))
    conversions.append((r'{\^e}', 'e\u0302', '\u00EA', 'e'))
    conversions.append((r'{\^i}', 'i\u0302', '\u00EE', 'i'))
    conversions.append((r'{\^o}', 'o\u0302', '\u00F4', 'o'))
    conversions.append((r'{\^u}', 'u\u0302', '\u00FB', 'u'))
    # Latin uppercase letters with caron (v)
    conversions.append((r'{\v A}', 'A\u030C', '\u01CD', 'A'))
    conversions.append((r'{\v E}', 'E\u030C', '\u011A', 'E'))
    conversions.append((r'{\v I}', 'I\u030C', '\u01CF', 'I'))
    conversions.append((r'{\v O}', 'O\u030C', '\u01D1', 'O'))
    conversions.append((r'{\v U}', 'U\u030C', '\u01D3', 'U'))
    conversions.append((r'{\v C}', 'C\u030C', '\u010C', 'C'))
    conversions.append((r'{\v N}', 'N\u030C', '\u0147', 'N'))
    conversions.append((r'{\v S}', 'S\u030C', '\u0160', 'S'))
    conversions.append((r'{\v Z}', 'Z\u030C', '\u017D', 'Z'))
    # Latin lowercase letters with caron (v)
    conversions.append((r'{\v a}', 'a\u030C', '\u01CE', 'a'))
    conversions.append((r'{\v e}', 'e\u030C', '\u011B', 'e'))
    conversions.append((r'{\v i}', 'i\u030C', '\u01D0', 'i'))
    conversions.append((r'{\v o}', 'o\u030C', '\u01D2', 'o'))
    conversions.append((r'{\v u}', 'u\u030C', '\u01D4', 'u'))
    conversions.append((r'{\v c}', 'c\u030C', '\u010D', 'c'))
    conversions.append((r'{\v n}', 'n\u030C', '\u0148', 'n'))
    conversions.append((r'{\v s}', 's\u030C', '\u0161', 's'))
    conversions.append((r'{\v z}', 'z\u030C', '\u017E', 'z'))
    # Latin uppercase letters with breve (u)
    conversions.append((r'{\u A}', 'A\u0306', '\u0102', 'A'))
    conversions.append((r'{\u E}', 'E\u0306', '\u0114', 'E'))
    conversions.append((r'{\u I}', 'I\u0306', '\u012C', 'I'))
    conversions.append((r'{\u O}', 'O\u0306', '\u014E', 'O'))
    conversions.append((r'{\u U}', 'U\u0306', '\u016C', 'U'))
    # Latin lowercase letters with breve (u)
    conversions.append((r'{\u a}', 'a\u0306', '\u0103', 'a'))
    conversions.append((r'{\u e}', 'e\u0306', '\u0115', 'e'))
    conversions.append((r'{\u i}', 'i\u0306', '\u012D', 'i'))
    conversions.append((r'{\u o}', 'o\u0306', '\u014F', 'o'))
    conversions.append((r'{\u u}', 'u\u0306', '\u016D', 'u'))
    # Latin uppercase letters with stroke
    conversions.append((r'{\A}', '\u023A', '\u023A', 'A'))
    conversions.append((r'{\I}', '\u2C65', '\u2C65', 'I'))
    conversions.append((r'{\O}', '\u00D8', '\u00D8', 'O'))
    conversions.append((r'{\L}', '\u0141', '\u0141', 'L'))
    conversions.append((r'{\Y}', '\u024E', '\u024E', 'Y'))
    conversions.append((r'{\Z}', '\u01B5', '\u01B5', 'Z'))
    # Latin lowercase letters with stroke
    conversions.append((r'{\a}', '\u2C65', '\u2C65', 'a'))
    conversions.append((r'{\i}', '\u0268', '\u0268', 'i'))
    conversions.append((r'{\o}', '\u00F8', '\u00F8', 'o'))
    conversions.append((r'{\l}', '\u0142', '\u0142', 'l'))
    conversions.append((r'{\y}', '\u024F', '\u024F', 'y'))
    conversions.append((r'{\z}', '\u01B6', '\u01B6', 'z'))
    # Latin uppercase letters with ogonek
    conversions.append((r'\\k{A}', 'A\u0328', '\u0104', 'A'))
    conversions.append((r'\\k{E}', 'E\u0328', '\u0118', 'E'))
    conversions.append((r'\\k{I}', 'I\u0328', '\u012E', 'I'))
    conversions.append((r'\\k{O}', 'O\u0328', '\u01EA', 'O'))
    conversions.append((r'\\k{U}', 'U\u0328', '\u0172', 'U'))
    # Latin lowercase letters with ogonek
    conversions.append((r'\\k{a}', 'a\u0328', '\u0105', 'a'))
    conversions.append((r'\\k{e}', 'e\u0328', '\u0119', 'e'))
    conversions.append((r'\\k{i}', 'i\u0328', '\u012F', 'i'))
    conversions.append((r'\\k{o}', 'o\u0328', '\u01EB', 'o'))
    conversions.append((r'\\k{u}', 'u\u0328', '\u0173', 'u'))
    # Latin uppercase and lowercase A with tilde
    conversions.append((r'{\~A}', 'A\u0303', '\u00C3', 'A'))
    conversions.append((r'{\~a}', 'a\u0303', '\u00E3', 'a'))
    # Latin uppercase and lowercase N with tilde (ene)
    conversions.append((r'{\~N}', 'N\u0303', '\u00D1', 'N'))
    conversions.append((r'{\~n}', 'n\u0303', '\u00F1', 'n'))
    # Latin uppercase and lowercase O with tilde
    conversions.append((r'{\~O}', 'O\u0303', '\u00D5', 'O'))
    conversions.append((r'{\~o}', 'o\u0303', '\u00F5', 'o'))
    # Latin lowercase sharp S (eszett)
    conversions.append((r'{\ss}', '\u00DF', '\u00DF', 'ss'))
    # Latin uppercase and lowercase A with ring (o)
    conversions.append((r'{\AA}', 'A\u030A', '\u00C5', 'A'))
    conversions.append((r'{\aa}', 'a\u030A', '\u00E5', 'a'))
    # Latin uppercase and lowercase ligature ash (ae)
    conversions.append((r'{\AE}', '\u00C6', '\u00C6', 'AE'))
    conversions.append((r'{\ae}', '\u00E6', '\u00E6', 'ae'))
    # Latin uppercase and lowercase ligature oe
    conversions.append((r'{\OE}', '\u0152', '\u0152', 'OE'))
    conversions.append((r'{\oe}', '\u0153', '\u0153', 'oe'))
    # Latin uppercase and lowercase eth
    conversions.append((r'{\DH}', '\u00D0', '\u00D0', 'dh'))
    conversions.append((r'{\dh}', '\u00F0', '\u00F0', 'dh'))
    # Latin uppercase and lowercase C with cedilla
    conversions.append((r'{\c C}', 'C\u0327', '\u00C7', 'C'))
    conversions.append((r'{\c c}', 'c\u0327', '\u00E7', 'c'))

    # if iterating through Greek letters
    if greek:
        # Greek uppercase letters
        conversions.append((r'{$\Gamma$}', '\u0393', '\u0393', 'G'))
        conversions.append((r'{$\Delta$}', '\u0394', '\u0394', 'D'))
        conversions.append((r'{$\Theta$}', '\u0398', '\u0398', 'Th'))
        conversions.append((r'{$\Lambda$}', '\u039B', '\u039B', 'L'))
        conversions.append((r'{$\Xi$}', '\u039E', '\u039E', 'X'))
        conversions.append((r'{$\Pi$}', '\u03A0', '\u03A0', 'P'))
        conversions.append((r'{$\Sigma$}', '\u03A3', '\u03A3', 'S'))
        conversions.append((r'{$\Phi$}', '\u03A6', '\u03A6', 'Ph'))
        conversions.append((r'{$\Psi$}', '\u03A8', '\u03A8', 'Ps'))
        conversions.append((r'{$\Omega$}', '\u03A9', '\u03A9', 'W'))
        # Greek lowercase letters
        conversions.append((r'{$\alpha$}', '\u03B1', '\u03B1', 'a'))
        conversions.append((r'{$\beta$}', '\u03B2', '\u03B2', 'b'))
        conversions.append((r'{$\gamma$}', '\u03B3', '\u03B3', 'g'))
        conversions.append((r'{$\delta$}', '\u03B4', '\u03B4', 'd'))
        conversions.append((r'{$\epsilon$}', '\u03B5', '\u03B5', 'e'))
        conversions.append((r'{$\zeta$}', '\u03B6', '\u03B6', 'z'))
        conversions.append((r'{$\zeta$}', '\u03B7', '\u03B7', 'h'))
        conversions.append((r'{$\theta$}', '\u03B8', '\u03B8', 'th'))
        conversions.append((r'{$\iota$}', '\u03B9', '\u03B9', 'i'))
        conversions.append((r'{$\kappa$}', '\u03BA', '\u03BA', 'k'))
        conversions.append((r'{$\lambda$}', '\u03BB', '\u03BB', 'l'))
        conversions.append((r'{$\mu$}', '\u03BC', '\u03BC', 'm'))
        conversions.append((r'{$\nu$}', '\u03BD', '\u03BD', 'n'))
        conversions.append((r'{$\xi$}', '\u03BE', '\u03BE', 'x'))
        conversions.append((r'{$\pi$}', '\u03C0', '\u03C0', 'p'))
        conversions.append((r'{$\rho$}', '\u03C1', '\u03C1', 'r'))
        conversions.append((r'{$\varrho$}', '\u03F1', '\u03F1', 'r'))
        conversions.append((r'{$\sigma$}', '\u03C3', '\u03C3', 's'))
        conversions.append((r'{$\tau$}', '\u03C4', '\u03C4', 't'))
        conversions.append((r'{$\upsilon$}', '\u03C5', '\u03C5', 'u'))
        conversions.append((r'{$\phi$}', '\u03C6', '\u03C6', 'ph'))
        conversions.append((r'{$\varphi$}', '\u03D5', '\u03D5', 'ph'))
        conversions.append((r'{$\chi$}', '\u03C7', '\u03C7', 'ch'))
        conversions.append((r'{$\psi$}', '\u03C8', '\u03C8', 'ps'))
        conversions.append((r'{$\omega$}', '\u03C9', '\u03C9', 'w'))

    # if iterating through symbols
    if symbols:
        # Miscellaneous Symbols
        conversions.append((" ", '\u2009', '\u2009', " "))
        conversions.append(("`", '\u2018', '\u2018', "'"))
        conversions.append(("'", "'", '\u2019', "'"))
        conversions.append(("``", "\"", '\u201C', "\""))
        conversions.append(("''", "\"", '\u201D', "\""))
        conversions.append(("-", "\u2010", '\u2010', "\u2010"))
        conversions.append(("--", "\u2013", '\u2013', "\u2013"))
        conversions.append(("---", "\u2014", '\u2014', "\u2014"))
        conversions.append((" ", " ", "\u00a0", " "))
        conversions.append((r"\$", "$", "\u0024", "$"))
        conversions.append((r"\#", "#", "\u0023", "#"))
        conversions.append((r"\&", "&", "\u0026", "&"))
        conversions.append((r"\_", "_", "\u005F", "_"))
        conversions.append((r"\~", "~", "\u223C", "~"))
        conversions.append((r"${\^\circ}$", "\u00B0", "\u00B0", "o"))
        conversions.append((r"$\times$", "\u2715", "\u2715", "x"))

    # return the list of symbols to iterate
    return conversions
