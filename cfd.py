#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

from cf import *

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: cfd.py [options] <file_name> [<filename> ...]

    options:
        -n | --nocheck     : do not check for CVS root

    displays diffs for files versus top of truck for either a CVS or monotone
    archive
    """
    args, opts = oss.gopt(argv[1:], [('n', 'nocheck')], [], main.__doc__)

    if oss.exists('CVS'):
        if opts.nocheck is None:
            CvsRootCheck()

        cmd = r"C:\bin\cvs.exe diff %s"
    else:
        cmd = "mtn diff --context  %s"

    for arg in args:
        oss.r(cmd % arg)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

