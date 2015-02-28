#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import parse
import os.path

import pylib.mincfile as mincfile

VERSION = "1.5"


#-------------------------------------------------------------------------------
def generateEntry(otf, id, proc, text, xpos, ypos, xsize, ysize, style, cntl, dlm, par, func):
#-------------------------------------------------------------------------------
    if text == '""':
        print("    %scntl[%s%s%s] = %s(%s, %s, style = %s)" % (cntl, dlm, id, dlm, proc, par, id, style), file=otf)
    else:
        print("    %scntl[%s%s%s] = %s(%s, %s, %s, style = %s)" % (cntl, dlm, id, dlm, proc, par, id, text, style), file=otf)

    print("    %scnvt[%s%s%s] = %s" % (cntl, dlm, id, dlm, func), file=otf)

    if xsize != '-1':
        print("    %scntl[%s%s%s].SetDimensions(%s, %s, %s, %s)" % (cntl, dlm, id, dlm, xpos, ypos, xsize, ysize), file=otf)
    else:
        print("    %scntl[%s%s%s].SetPosition(wx.Point(%s, %s))" % (cntl, dlm, id, dlm, xpos, ypos), file=otf)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: genlo <input file>
    """
    args, opts = oss.gopt(argv[1:], [], [('o', 'out')], main.__doc__ + __doc__)

    if len(args) != 1:
        opts.usage(1, "No input")

    if opts.out:
        otfn = opts.out
        flnm = oss.path(otfn).drive_path_name
    else:
        flnm = oss.path(args[0]).drive_path_name
        otfn = flnm + '.py'
    incfn = flnm + '.incf'

    with open(otfn, 'w') as otf, open(incfn, 'w') as incf, mincfile.MacroIncludeFile(args[0], 'include:', ('macro:', ':endm', 'mx:')) as inf:
        print("Generating file:", flnm + '.py')

        print("#\n# Generated by 'genlo.py' version: %s\n#" % VERSION, file=otf)
        print("import wx", file=otf)
        print("from pylib.mx import ADlg" + '\n', file=otf)


        sym = parse.PARSE_SYM + '.+-/|'
        p = parse.Parser((0, sym), (1, '#'), (2, '"', ' "' + sym + '()'), (0, '(', ' )' + sym))

        mode = ''

        lnum = 0
        for ln in inf:
            lnum += 1

            l = p.Parse(ln)

            if not l or l[0] == '#':
                continue
            cmd = l[0]

            if cmd == 'setup':
                try:
                    print(('\n\n#' + ('-'*80) + "\ndef %s(parent):\n" + '#' + ('-'*80)) % l[1], file=otf)
                    print("    cntl = {}", file=otf)
                    print("    cnvt = {}", file=otf)
                except IndexError:
                    print("%s(%d): Error: 'setup' name missing" % (args[0], lnum), file=oss.stderr)

                mode = 'S'

            elif cmd == 'dialog':
                try:
                    print(('\n\n#' + ('-'*80) + "\nclass %s(ADlg):\n"  + '#' + ('-'*80))% l[1], file=otf)
                    print("    #" + (('- ')*38), file=otf)
                    print("    def __init__(self, parent, title, size):", file=otf)
                    print("    #" + (('- ')*38), file=otf)
                    print("        ADlg.__init__(self, parent, title, size)", file=otf)
                except:
                    print("%s(%d): Error: 'dialog' name missing" % (args[0], lnum), file=oss.stderr)

                mode = 'D'

            elif cmd == 'from':
                try:
                    print("from %s import *" % l[1], file=otf)
                except:
                    print("%s(%d): Error: 'from' name missing" % (args[0], lnum), file=oss.stderr)

            elif cmd == 'import':
                try:
                    print("\nimport %s" % l[1], file=otf)
                except:
                    print("%s(%d): Error: 'import' name missing" % (args[0], lnum), file=oss.stderr)

            elif cmd == 'define':
                try:
                    print("%s = %s" % (l[1], l[2]), file=otf)
                except:
                    print("%s(%d): Error: 'define' name missing" % (args[0], lnum), file=oss.stderr)

            elif l[0] == 'done':
                if mode == 'S':
                    print("    return cntl\n\n", file=otf)
                else:
                    print("\n", file=otf)

            else:
                ln = len(l)
                if ln == 7:
                    proc, id, text, xpos, ypos, xsize, ysize = l
                    flags = "0"
                    func = "str"

                elif ln == 8:
                    proc, id, text, xpos, ypos, xsize, ysize, flags = l
                    func = "str"

                elif ln == 9:
                    proc, id, text, xpos, ypos, xsize, ysize, flags, func = l

                else:
                    print("%s(%d): Error: Missing line elements" % (args[0], lnum), file=oss.stderr)
                    print(l, file=oss.stderr)

                ## generating a setup
                if mode == 'S':
                    generateEntry(otf, id, proc, text, xpos, ypos, xsize, ysize, flags, "", "", "parent", func)

                ## generating a dialog
                else:
                    generateEntry(otf, id, proc, text, xpos, ypos, xsize, ysize, flags, "    self.", "'", "self.win", func)

        incf.writelines(inf.readlines())

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
