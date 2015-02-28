#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import hashlib
import pylib.osscripts as oss

BLOCKSIZE = 1024*1024

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: md5sum <file_name> [<file_name> ...]
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    if not args:
        opts.usage(1, 'must supply file names')

    for fn in args:
        with open(fn, 'rbU') as inf:
            sum = hashlib.md5()
            while 1:
                block = inf.read(BLOCKSIZE)
                sum.update(block)
                if not block:
                    break

            print(hexify(sum.digest()), fn)

    oss.exit(0)


#-------------------------------------------------------------------------------
def hexify(s):
#-------------------------------------------------------------------------------
    return "%02x"*len(s) % tuple(map(ord, s))


if __name__ == "__main__":
    main(oss.argv)
