#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: printbin <num>

        print the binary of the number
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    for v in args:
        pbin(int(v))

    oss.exit(0)


#-------------------------------------------------------------------------------
def pbin(a):
#-------------------------------------------------------------------------------
    s = []
    while a:
        s.append('1' if a & 0x1 == 0x1 else '0')
        a /= 2

    s.reverse()
    i = 4 - len(s) % 4
    print(i)
    for c in s:
        if i != 0 and i % 4 == 0:
            oss.stdout.write(' ')
        oss.stdout.write(c)
        i += 1
    print()


if __name__ == "__main__":
    main(oss.argv)

