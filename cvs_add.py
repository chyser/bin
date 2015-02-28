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

BinExts = set([
'.exe', 'bmp', '.jpg', '.doc', '.dll', '.pyd', '.png', '.gif'
])


#-------------------------------------------------------------------------------
def CvsRootCheck():
#-------------------------------------------------------------------------------
    root = oss.readf('CVS/Root', 0)

    if root is None:
        root = oss.env['CVSROOT']

    if root[:9] != ':pserver:' and not oss.exists(root):
        return False

    return True

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    cvsdwn = not CvsRootCheck()

    for f in oss.paths(args):
        ext = oss.splitext(f).lower()
        opts = '-kb' if ext in BinExts else ''

        if cvsdwn:
            otf = file('CVS/offline', 'a')
            print >> otf, 'add ' + opts + ' ' + f
            otf.close()
        else:
            if oss.exists('CVS/offline'):
                inf = file('CVS/offline')
                for cmd in inf:
                    oss.r('cvs.exe ' + cmd)
                inf.close()
                oss.rm('CVS/offline')

            oss.r('cvs.exe add ' + opts + ' ' + f)

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)
