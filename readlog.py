#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import time

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: readlog.py <file> [<file> ...]

        continuously prints new lines added to files (like tail -f)
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    fs = {};  last = None
    while 1:
        for f in args:
            if f not in fs and oss.exists(f):
                if last != f:
                    print('\n%s : -------------' % f)
                    last = f

                print("Opening:", f)
                last = f
                fs[f] = open(f, 'rU')
            else:
                if f in fs:
                    buf = fs[f].read(-1)
                    if buf:
                        if last != f:
                            print('\n%s : -------------' % f)
                            last = f
                        oss.stderr.write(buf)

            time.sleep(0.5)


if __name__ == "__main__":
    main(oss.argv)
    oss.exit(0)
