# describe.py is copied from TTFQuery-1.0.5:
# https://pypi.org/project/TTFQuery/#files
#
# Upstream website is abandoned and doesn't even have the 1.0.5 version:
# https://ttfquery.sourceforge.net/
# https://sourceforge.net/projects/ttfquery/files/ttfquery/

# This file was modified from the upstream version to port it from Python 2 to
# Python 3. Look at the git history to see the changes.

# TTFQuery (and thus this file) is licensed under the simplified BSD license:
#
# THIS SOFTWARE IS NOT FAULT TOLERANT AND SHOULD NOT BE USED IN ANY
# SITUATION ENDANGERING HUMAN LIFE OR PROPERTY.
#
# TTFQuery License
#
# 	Copyright (c) 2003, Michael C. Fletcher and Contributors
# 	All rights reserved.
#
# 	Redistribution and use in source and binary forms, with or without
# 	modification, are permitted provided that the following conditions
# 	are met:
#
# 		Redistributions of source code must retain the above copyright
# 		notice, this list of conditions and the following disclaimer.
#
# 		Redistributions in binary form must reproduce the above
# 		copyright notice, this list of conditions and the following
# 		disclaimer in the documentation and/or other materials
# 		provided with the distribution.
#
# 		The name of Michael C. Fletcher, or the name of any Contributor,
# 		may not be used to endorse or promote products derived from this
# 		software without specific prior written permission.
#
# 	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 	``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# 	LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# 	FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# 	COPYRIGHT HOLDERS AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# 	INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# 	(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# 	SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# 	HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# 	STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# 	ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# 	OF THE POSSIBILITY OF SUCH DAMAGE.


"""Extract meta-data from a font-file to describe the font"""
from fontTools import ttLib
import sys

# Modification from upstream code: don't even try loading OpenGLContext.
#try:
#    from OpenGLContext.debug.logs import text_log
#except ImportError:
#    text_log = None
text_log = None

def openFont( filename ):
    """Get a new font object"""
    if isinstance( filename, str):
        filename = open( filename, 'rb')
    return ttLib.TTFont(filename)

FONT_SPECIFIER_NAME_ID = 4
FONT_SPECIFIER_FAMILY_ID = 1
def shortName( font ):
    """Get the short name from the font's names table"""
    name = ""
    family = ""
    for record in font['name'].names:
        if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
            if b'\000' in record.string:
                # Modification from upstream code: return str instead of bytes.
                #name = str(record.string, 'utf-16-be').encode('utf-8')
                name = str(record.string, 'utf-16-be')
            else:
                # Modification from upstream code: return str instead of bytes.
                #name = record.string
                name = str(record.string, 'utf-8')
        elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
            if b'\000' in record.string:
                # Modification from upstream code: return str instead of bytes.
                #family = str(record.string, 'utf-16-be').encode('utf-8')
                family = str(record.string, 'utf-16-be')
            else:
                # Modification from upstream code: return str instead of bytes.
                #family = record.string
                family = str(record.string, 'utf-8')
        if name and family:
            break
    return name, family


FAMILY_NAMES = {
    0: ("ANY",{}),
    1: ("SERIF-OLD", {
        0: "ANY",
        1: "ROUNDED-LEGIBILITY",
        2: "GARALDE",
        3: "VENETIAN",
        4: "VENETIAN-MODIFIED",
        5: "DUTCH-MODERN",
        6: "DUTCH-TRADITIONAL",
        7: "CONTEMPORARY",
        8: "CALLIGRAPHIC",
        15: "MISCELLANEOUS",
    }),
    2: ("SERIF-TRANSITIONAL", {
        0: "ANY",
        1: "DIRECT-LINE",
        2: "SCRIPT",
        15: "MISCELLANEOUS",
    }),
    3: ("SERIF", {
        0: "ANY",
        1: "ITALIAN",
        2: "SCRIPT",
        15: "MISCELLANEOUS",
    }),
    4: ("SERIF-CLARENDON",{
        0: "ANY",
        1: "CLARENDON",
        2: "MODERN",
        3: "TRADITIONAL",
        4: "NEWSPAPER",
        5: "STUB-SERIF",
        6: "MONOTYPE",
        7: "TYPEWRITER",
        15: "MISCELLANEOUS",
    }),
    5: ("SERIF-SLAB",{
        0: 'ANY',
        1: 'MONOTONE',
        2: 'HUMANIST',
        3: 'GEOMETRIC',
        4: 'SWISS',
        5: 'TYPEWRITER',
        15: 'MISCELLANEOUS',
    }),
    7: ("SERIF-FREEFORM",{
        0: 'ANY',
        1: 'MODERN',
        15: 'MISCELLANEOUS',
    }),
    8: ("SANS",{
        0: 'ANY',
        1: 'GOTHIC-NEO-GROTESQUE-IBM',
        2: 'HUMANIST',
        3: 'ROUND-GEOMETRIC-LOW-X',
        4: 'ROUND-GEOMETRIC-HIGH-X',
        5: 'GOTHIC-NEO-GROTESQUE',
        6: 'GOTHIC-NEO-GROTESQUE-MODIFIED',
        9: 'GOTHIC-TYPEWRITER',
        10: 'MATRIX',
        15: 'MISCELLANEOUS',
    }),
    9: ("ORNAMENTAL",{
        0: 'ANY',
        1: 'ENGRAVER',
        2: 'BLACK-LETTER',
        3: 'DECORATIVE',
        4: 'THREE-DIMENSIONAL',
        15: 'MISCELLANEOUS',
    }),
    10:("SCRIPT",{
        0: 'ANY',
        1: 'UNCIAL',
        2: 'BRUSH-JOINED',
        3: 'FORMAL-JOINED',
        4: 'MONOTONE-JOINED',
        5: 'CALLIGRAPHIC',
        6: 'BRUSH-UNJOINED',
        7: 'FORMAL-UNJOINED',
        8: 'MONOTONE-UNJOINED',
        15: 'MISCELLANEOUS',
    }),
    12:("SYMBOL",{
        0: 'ANY',
        3: 'MIXED-SERIF',
        6: 'OLDSTYLE-SERIF',
        7: 'NEO-GROTESQUE-SANS',
        15: 'MISCELLANEOUS',
    }),
}

WEIGHT_NAMES = {
    'thin':100,
    'extralight':200,
    'ultralight':200,
    'light':300,
    'normal':400,
    'regular':400,
    'plain':400,
    'medium':500,
    'semibold':600,
    'demibold':600,
    'bold':700,
    'extrabold':800,
    'ultrabold':800,
    'black':900,
    'heavy':900,
}
WEIGHT_NUMBERS = {}
for key,value in WEIGHT_NAMES.items():
    WEIGHT_NUMBERS.setdefault(value,[]).append(key)

def weightNumber( name ):
    """Convert a string-name to a weight number compatible with this module"""
    if isinstance( name, str):
        name = name.lower()
        name = name.replace( '-','').replace(' ','')
        if name and name[-1] == '+':
            name = name[:-1]
            adjust = 50
        elif name and name[-1] == '-':
            name = name[:-1]
            adjust = -50
        else:
            adjust = 0
        return WEIGHT_NAMES[ name ]+ adjust
    else:
        return int(name) or 400 # for cases where number isn't properly specified

def weightName( number ):
    """Convert integer number to a human-readable weight-name"""
    number = int(number) or 400
    if number in WEIGHT_NUMBERS:
        return WEIGHT_NUMBERS[number]
    name = 'thin-'
    for x in range(100,1000, 100):
        if number >= x:
            name = WEIGHT_NUMBERS[x]+'+'
    return name

def family( font ):
    """Get the family (and sub-family) for a font"""
    HIBYTE = 65280
    LOBYTE = 255
    familyID = (font['OS/2'].sFamilyClass&HIBYTE)>>8
    subFamilyID = font['OS/2'].sFamilyClass&LOBYTE
    return familyNames( familyID, subFamilyID )
def familyNames( familyID, subFamilyID=0 ):
    """Convert family integers to human-readable names"""
    familyName, subFamilies = FAMILY_NAMES.get( familyID, ('RESERVED',None))
    if familyName == 'RESERVED':
        if text_log:
            text_log.warn( 'Font has invalid (reserved) familyID: %s', familyID )
    if subFamilies:
        subFamily = subFamilies.get(subFamilyID, 'RESERVED')
    else:
        subFamily = 'ANY'
    return (
        familyName,
        subFamily
    )

def modifiers( font ):
    """Get weight and italic modifiers for a font

    weight is taken from the OS/2 usWeightClass field
    italic is taken from either OS/2 fsSelection or
    head macStyle, if either indicates italics we
    report italics
    """
    return (
        # weight as an integer
        font['OS/2'].usWeightClass,
        ( # italic
            font['OS/2'].fsSelection &1 or
            font['head'].macStyle&2
        ),
    )

# REMOVED guessEncoding( font, given=None ) function
# It was unused.
# It wasn't "complete", as the docstring said:
#   "This needs some work, particularly for non-win32 platforms"
