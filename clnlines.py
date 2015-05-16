#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.util as util

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
    with open(fn) as inf:
        with util.SafeFile(fn, 't.clean', 'cleaning file: {0}') as outf:
            for line in inf:
                outf.write(line.rstrip() + '\n')


if __name__ == "__main__":
    main(oss.argv)
