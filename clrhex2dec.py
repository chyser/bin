#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)


    r = args[0][0:2]
    g = args[0][2:4]
    b = args[0][4:6]

    print(int(r, 16), int(g, 16), int(b, 16))

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
