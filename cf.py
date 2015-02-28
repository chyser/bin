#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: cf.py [options]

        options:
            -n | --nocheck    : don't check for CVSROOT

        show files in CVS/MTN that are changed in local directory
    """
    args, opt = oss.gopt(oss.argv[1:], [('n', 'nocheck')], [], main.__doc__)

    if oss.exists('CVS'):
        if opt.nocheck is None: CvsRootCheck()

        if not args:
            oss.r(r'C:\bin\cvs.exe -qn up -A | C:\mksnt\fgrep.exe -v "?"')
        else:
            for dir in args:
                oss.cd(dir)
                oss.r(r'C:\bin\cvs.exe -qn up -A | C:\mksnt\fgrep.exe -v "?"')

    elif oss.findFilePathUp('_MTN'):
        oss.r('mtn status')
        #print '\nunknown files:'
        #oss.r('mtn ls unknown')

    oss.exit(0)


#-------------------------------------------------------------------------------
def CvsRootCheck():
#-------------------------------------------------------------------------------
    root = oss.readf('CVS/Root', 0)

    if root is None:
        root = oss.env['CVSROOT']

    if root[:9] != ':pserver:' and not oss.exists(root):
        print("CVSROOT('%s') is down" % root)
        oss.exit(1)

    print("CVS Root: '%s'" % root)


if __name__ == "__main__":
    main(oss.argv)
