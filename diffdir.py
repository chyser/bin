#!/usr/bin/env python
"""
usage: dirdiff [OPTIONS] path1 [path2] [path3] ... [path<n>]

Show files which are different in multiple directories. If only one directory
specified the other directory is '.'

Options:
    -x | --exts <ext> : specify an extension (no leading dot) can repeat.
    -r | --recurse    : do a recursive search
    -q | --quick      : do quick file compare (size equals)
    -s | --supress    : supress most printed output
    -d | --dir <dir>  : base part of dir name (path1/<dir> path2/<dir>)
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import pylib.util as util
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('r', 'recurse'), ('q', 'quick'), ('s', 'supress')],
                          [('d', 'dir')], [], [('x', 'exts')], __doc__)

    if not args:
        opts.usage(1, 'Must specify directories')

    if len(args) == 1:
        args.append('.')

    if opts.dir:
        args = ['{0}/{1}'.format(a, opts.dir) for a in args]

    for a in args:
        if not oss.exists(a):
            opts.usage(2, '"{0}" does not exist'.format(a))

    exts = set(['.{0}'.format(e) for e in opts.exts]) if opts.exts else None

    p = []
    for a0, a1 in util.permutations(len(args)):
        same = checkDir(args[a0], args[a1], exts, opts.quick, opts.recurse, opts.supress)
        p.append('    {0} {1} {2}'.format(args[a0], '==' if same else '!=', args[a1]))

    print('Status:')
    for i in p:
        print(i)
    oss.exit(0)


#-------------------------------------------------------------------------------
def checkDir(dir1, dir2, exts=None, quick=False, recurse=False, supress=False, indent=0):
#-------------------------------------------------------------------------------
    d1 = set(oss.basename(oss.ls(dir1)))
    d2 = set(oss.basename(oss.ls(dir2)))

    same = True

    p = util.PrintOnce(supress, indent)
    for f in sorted(d1.difference(d2)):
        if oss.IsDir(dir1 + '/' + f):
            same = False
            p.printOnce("Objects in '%s' not in '%s':" % (dir1, dir2))
            p.print('    /{0}'.format(f))
        elif checkFile(f, exts):
            same = False
            p.printOnce("Objects in '%s' not in '%s':" % (dir1, dir2))
            p.print('    {0}'.format(f))
    p.didPrint()

    p.reset()
    for f in sorted(d2.difference(d1)):
        if oss.IsDir(dir2 + '/' + f):
            same = False
            p.printOnce("Objects in '%s' not in '%s':" % (dir2, dir1))
            p.print('    /{0}'.format(f))
        elif checkFile(f, exts):
            same = False
            p.printOnce("Objects in '%s' not in '%s':" % (dir2, dir1))
            p.print('    {0}'.format(f))
    p.didPrint()

    dirs = []
    p.reset()
    for f in sorted(d1.intersection(d2)):
        if oss.IsDir(dir1 + '/' + f):
            if recurse:
                dirs.append(f)
        elif checkFile(f, exts):
            if not compare(dir1 + '/' + f, dir2 + '/' + f, quick):
                same = False
                p.printOnce("Files with Differences{0}:".format(' (quick)' if quick else ''))
                #p.print('   ', dir1 + '/' + f + " != " + dir2 + '/' + f)
                p.print('   ', f)
    p.didPrint()

    if recurse:
        p.reset()
        for f in dirs:
            p.printOnce("Directories in {0} and {1}:".format(dir1, dir2))
            p.print('    /{0}'.format(f))
            same = checkDir(dir1 + '/' + f, dir2 + '/' + f, exts, quick, recurse, supress, indent+1) and same
        p.didPrint()

    return same


#-------------------------------------------------------------------------------
def checkFile(f, exts):
#-------------------------------------------------------------------------------
    if not exts:
        return True
    return oss.splitext(f) in exts


#-------------------------------------------------------------------------------
def compare(a, b, quick=False):
#-------------------------------------------------------------------------------
    r = os.stat(a).st_size == os.stat(b).st_size
    if quick:
        return r
    return r and oss.cmp(a, b)


if __name__ == "__main__":
    main(oss.argv)

