#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  generator of CJK subfonts.pe for Fontforge  - Copyright 2017 Hin-Tak Leung
#  Distributed under the terms of the new BSD license.
#
#  Usage:
#    python subfonts-script-generate.py NotoSerifCJKtc-Medium.otf > subfonts.pe
#
# -----------------------------------------------------------------------------
from __future__ import print_function
from freetype import *

subfont_script_header = '''
# Generate CJK subfonts from master font.
# The fonts are created in the current directory.
#
# $1: The master font (e.g., `bsmi00lp.ttf').
# $2: The name stem for the subfonts (e.g., `bsmilp').
# $3: The subfont definition file, mapping from Unicode to whatever
#     (e.g., `UBig5.sfd', which maps to Big 5).
#
# A collection of useful subfont definition files for CJK fonts can be found
# in the ttf2pk package.

# Copyright (C) 1994-2015  Werner Lemberg <wl@gnu.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program in doc/COPYING; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

if (Strtol($version) < 20071105)
  Print("Can't use FontForge version before 2007-11-05.  Aborting.");
  Quit(1);
endif;

if ($argc != 4)
  Print("usage: [fontforge -script] ", $0, " master-font name-stem SFD-file");
  Quit(1);
endif;

Print("Loading ", $1, "...");
Open($1);

if ($cidfontname != "")
  CIDFlatten();
endif;

Reencode("ucs4");

'''

subfont_script_footer = '''
copyright = $copyright \\
            + Chr(10) + Chr(10) \\
            + "Subfont version " \\
            + Strftime("%F", 1, "C") \\
            + ".";
SetFontNames("", "", "", "", copyright, "");

Print("Ensure third order curves...");
SetFontOrder(3);

Print("Scaling to PostScript units...");
ScaleToEm(900, 100);

num_chars = CharCnt();
count = 0;
delta = 100;

while (count + delta < num_chars)
  Print(count, "/", num_chars - 1, ":");
  Select(count, count + delta);

  Print("  Add extrema...");
  AddExtrema();

  Print("  Simplifying outlines...");
  Simplify(0, 2);

  count += delta;
endloop;

Print(count, "/", num_chars - 1, ":");
Select(count, num_chars - 1);

Print("  Add extrema...");
AddExtrema();

Print("  Simplifying outlines...");
Simplify(0, 2);

SelectAll();

# generate AFM and TFM files, no PS hints, and rounded PS coordinates
Print("Generating subfonts...");
Generate($2 + "%s.pfb", "", \\
         0x1 | 0x100 | 0x10000 | 0x80000 | 0x200000, \\
         -1, $3);

Quit(0);
'''

def Print_Fixups( face ):
    face.set_charmap( face.charmap )
    reverse_lookup = {}
    charcode, gindex = face.get_first_char()
    while ( gindex ):
        #print( "      0x%04lx => %d" % (charcode, gindex) )
        if ( gindex in reverse_lookup.keys() ):
            reverse_lookup[gindex].append( charcode )
        else:
            reverse_lookup[gindex] = [charcode]
        charcode, gindex = face.get_next_char( charcode, gindex )
    for gindex in reverse_lookup.keys():
        if ( len(reverse_lookup[gindex]) > 1 ):
            for x in range( len(reverse_lookup[gindex]) - 1 ):
                print( "Select(%d); "
                       "if ( !WorthOutputting() ) Print ( 'Source Empty!' ) endif ; "
                       "Copy(); "
                       "Select(%d); "
                       "if ( WorthOutputting() ) Print ( 'Destination Full!' ) endif ; "
                       "Paste()"
                       % (reverse_lookup[gindex][-1], reverse_lookup[gindex][x]) )

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    face = Face(sys.argv[1])
    print( subfont_script_header )
    Print_Fixups( face )
    print( subfont_script_footer )
