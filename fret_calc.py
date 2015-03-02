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
    """ usage: fret_calc.py <scale_length>
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    for i in range(1, 25):
        print("%2d: %5.2f" % (i, fret_pos(float(args[0]), i)))

    oss.exit(0)


#-------------------------------------------------------------------------------
def fret_pos(sc, fn):
#-------------------------------------------------------------------------------
    return sc - (sc / pow(2, fn/12.0))

if __name__ == "__main__":
    main(oss.argv)
