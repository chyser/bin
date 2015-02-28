"""
usage: analyzeClass  [options] <python file>
   Options:
     -p | --path   : specify path to file
     -c | --clss   : analyze a particular class

Compares methods of a subclass with defined methods of parents.

"""

import sys
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
def GetClassInfo(clss, nest=0, ident=0):
#-------------------------------------------------------------------------------
    n = nest
    for d in clss.__bases__:
        i = GetClassInfo(d, nest+1, ident+1)
        if i > n: n = i

    nest = n

    print '\n\n', ('    '*(nest-ident)) + clss.__module__ + '.' + clss.__name__
    dl = dir(clss)
    dk = clss.__dict__.keys()
    dl.sort()
    dk.sort()

    for d in dl:
        if d not in dk:
            print ('    '*(nest+1-ident)) + d, ' ', type(getattr(clss, d))

    print
    for d in dk:
        print ('    '*(nest+1-ident)) + d, ' ', type(getattr(clss, d))
    return nest

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('p', 'path'), ('c', 'clss')], usage)

    if opts.path is not None:
        sys.path.insert(0, opts.path)

    modn = oss.splitnm(args[0])

    mod = __import__(modn)

    if opts.clss is not None:
        clss = mod.__dict__[opts.clss]

        GetClassInfo(clss)

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


