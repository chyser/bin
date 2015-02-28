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

    inf0 = open(args[0])
    inf1 = open(args[1])

    f0 = inf0.read()
    f1 = inf1.read()

    i = 0
    j = 0
    while 1:
        ch = getChar(f0, i)

        if ch != f1[j]:
            print(ch, f1[j], i)

            l = 0
            while ch != f1[j]:
                i += 1
                ch = getChar(f0, i)
                l += 1
            print('recover:', l)

        i += 1
        j += 1

    oss.exit(0)


#-------------------------------------------------------------------------------
def getChar(f0, i):
#-------------------------------------------------------------------------------
    try:
        return f0[i]
    except IndexError:
        return None



if __name__ == "__main__":
    main(oss.argv)
