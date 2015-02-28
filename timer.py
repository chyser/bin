#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import time
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: timer <time in minutes>

        run a timer with display update for the specifed time in
        minutes (can be float)
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    if not args:
        opts.usage(1, "must specify a time in minutes")

    smins = 0
    waypoints = []

    for arg in args:
        v = float(arg)
        smins += v
        waypoints.append(v)

    print("Total: %6.1f" % smins)
    st = time.time()

    print("============")
    for wp in waypoints:
        wst = time.time()

        twp = wp
        while twp > 0:
            t = time.time()
            twp = wp - ((t - wst)/60.0)
            print("%6.1f minutes left" % twp, end='')
            print("%6.1f minutes left" % (smins - (t - st)/60.0))

            if twp < 0.1:
                break
            elif twp < 2:
                time.sleep(10)
            else:
                time.sleep(30)

        print("-------------")


    print("============")
    print("done")
    print("============")
    st = time.time()
    while 1:
        time.sleep(30)
        print("%6.1f minutes" % ((st - time.time())/60.0))

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

