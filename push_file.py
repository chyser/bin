#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

DIR = "~/push/"
DB = DIR + "push.db"



#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    for a in oss.paths(args):

        if not oss.exists(a):
            continue

        pth = a.fpath
        nm = a.name


        print(pth, nm)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
