#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: uncvs [<dir>]

    Remove CVS from a directory if specified, else the current directory
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    if args:
        oss.cd(args[0])

    for dd in oss.find('.', 'CVS'):
        if oss.exists(dd + '/ROOT'):
            print("Removing:", dd)
            oss.r("rm -rf " + dd)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

