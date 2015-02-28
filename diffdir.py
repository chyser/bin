#!/usr/bin/env python
"""
usage: dirdiff [OPTIONS] dir2

show files which are different in 2 directories

Options:
    -d <dir> | --dir <dir> : specify first directory (default is current directory)
    -b | --binary          : files are binary (don't print differences)
"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('d', 'dir')], usage)

    dir = opts.get('dir', '.')

    s = set(oss.basename(oss.ls(dir)))
    d = set(oss.basename(oss.ls(args[0])))

    print "Files in '%s' not in '%s':" % (dir, args[0])
    for f in s.difference(d):
        print "   ", f
    print

    print "Files in '%s' not in '%s':" % (args[0], dir)
    for f in d.difference(s):
        print "   ", f
    print

    print "Files with diferences:"
    for f in s.intersection(d):
        if not oss.cmp(dir + '/' + f, args[0] + '/' + f):
            print dir + '/' + f + " : " + args[0] + '/' + f





    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

