#!/usr/bin/env python
"""
usage: dirdiff [OPTIONS] dir2

show files which are different in 2 directories

Options:
    -d | --dir <dir> : specify first directory (default is current directory)
    -b | --binary    : files are binary (don't print differences)
"""

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('d', 'dir'), ('x', 'ext')], __doc__)

    if not args:
        opts.usage(1)

    dir = opts.get('dir', '.')
    cdir = args[0]

    if opts.ext:
       dir  += '/*.' + opts.ext
       cdir += '/*.' + opts.ext

    s = set(oss.basename(oss.ls(dir)))
    d = set(oss.basename(oss.ls(cdir)))

    print "Files in '%s' not in '%s':" % (dir, cdir)
    for f in s.difference(d):
        print "   ", f
    print

    print "Files in '%s' not in '%s':" % (cdir, dir)
    for f in d.difference(s):
        print "   ", f
    print

    print "Files with diferences:"
    for f in s.intersection(d):
        if not oss.cmp(dir + '/' + f, cdir + '/' + f):
            print dir + '/' + f + " : " + cdir + '/' + f

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

