#!/usr/local/bin/python

from osscripts import *

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    arg, opts = gopt(argv[1:], [("d", "dir")])

    if opts.dir:
        inf = file(".cd")
        lst = inf.readlines()
        lst.reverse()
        for i, n in enumerate(lst):
            print i, ':', n

        exit(0)

    print arg[0]

    if arg[0] != '..' or arg[0] != '.':
        of = file(".cd", "a")
        print >> of, arg[0]
