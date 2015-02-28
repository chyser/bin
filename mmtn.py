#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)


#-------------------------------------------------------------------------------
def getDB():
#-------------------------------------------------------------------------------
    return "_MTN/mtn.db"

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('m', 'msg'), ('d', 'db')], usage)

    options = "--db " + opts.db if opts.db else ''

    if args and args[0] == 'ci':
        f = oss.r('mtn.exe %s ci -m "%s"' % (options, args[2]), '<')
        f.write('kibsop)')
        f.close()
    else:
        oss.r("mtn.exe " + options + ' ' + ' '.join(args))


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)
