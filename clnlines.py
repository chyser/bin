#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

TMP_FILE="/tmp/t.clean"

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)


    for a in args:
        clean(a)

    oss.exit(0)


#-------------------------------------------------------------------------------
def clean(fn):
#-------------------------------------------------------------------------------
    oss.cp(fn, "/tmp")

    with open(fn) as inf:
        with open(TMP_FILE, "w") as outf:
            for line in inf:
                outf.write(line.rstrip() + '\n')

    if not oss.cmp(TMP_FILE, fn):
        print("cleaning lines: %s" % fn)
        oss.cp(TMP_FILE, fn)


if __name__ == "__main__":
    main(oss.argv)
