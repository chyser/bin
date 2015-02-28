#!/usr/bin/env python


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import math
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: isprime [options] <number to check>

        options:
            -s | --show     : show at least one set of factors

        determines if the specified mumber is prime.
"""
    args, opts = oss.gopt(argv[1:], [('s', 'show')], [], main.__doc__)

    if len(args) != 1:
        opts.usage(1, "must supply an integer")

    num = int(args[0])

    print("%d %s prime" % (num, (isPrime(num, opts.show) and "is") or "is not"))
    oss.exit(0)


#-------------------------------------------------------------------------------
def isPrime(num, show=None):
#-------------------------------------------------------------------------------
    end = int(math.floor(num/2.0))

    q, r = divmod(num, 2)
    if q != 1 and r == 0:
        if show: print('    2')
        return

    for i in xrange(3, end, 2):
        q, r = divmod(num, i)
        if q != 1 and r == 0:
            if show: print('   ', i, q)
            return
    return True


if __name__ == "__main__":
    main(oss.argv)

