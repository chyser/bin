#!/usr/bin/env python
"""
usage:

"""

import math
import pylib.osscripts as oss
import pylib.util as util

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def HaarWaveletTransform(s):
#-------------------------------------------------------------------------------
    """ In place fast Haar wavelet transform
    """

    ln = len(s)

    n = util.log2(ln)
    assert n - int(n) == 0
    n = int(n)

    i = 1
    j = 2
    m = int(math.pow(2, n))
    for l in range(n):
        m = m/2
        for k in range(m):
            ak = (s[j*k] + s[j*k+i])/2
            ck = (s[j*k] - s[j*k+i])/2
            s[j*k] = ak
            s[j*k+i] = ck
        i = j
        j *= 2

    return s

#-------------------------------------------------------------------------------
def InverseHaarWaveletTransform(s):
#-------------------------------------------------------------------------------
    """ In place inverse Haar wavelet transform
    """

    ln = len(s)

    n = util.log2(ln)
    assert n - int(n) == 0
    n = int(n)

    i = int(math.pow(2, n-1))
    j = 2*i
    m = 1

    for l in range(n):
        for k in range(m):
            a2k  = s[j*k] + s[j*k+i]
            a2k1 = s[j*k] - s[j*k+i]
            s[j*k] = a2k
            s[j*k+i] = a2k1
        j = i
        i = i/2
        m = 2*m

    return s


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    s = [3, 1, 0, 4, 8, 6, 9, 9]
    print s

    s = HaarWaveletTransform(s)
    print s

    s = InverseHaarWaveletTransform(s)
    print s

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


