#!/usr/bin/env python
"""
usage:

"""

import time
import thread
import pylib.osscripts as oss

DB = [
    (80, 'flu-03', 80),
    (5901, 'flu-03', 5901),
    (9008, 'flu-02', 9008),
    (9009, 'flu-02', 9009),
    (8057, 'flu-02', 8057),
    (8088, 'flu-02', 8088),
    (9337, 'flu-02', 9337),
    (8443, 'flu-73', 8443),
]

#-------------------------------------------------------------------------------
def makeTunnel(loc, mach, rmt):
#-------------------------------------------------------------------------------
    idx = 1

    while 1:
        st = time.time()

        print 'Connecting local port %d to %s:%d' % (loc, mach, rmt)
        oss.r('plink -l chrish -pw kibsop) -N -L %d:%s:%d compflu-02.hpl.hp.com ' % (loc, mach, rmt))

        if st + 60 < time.time():
            time.sleep(10 * idx)
            idx += 1
            if idx > 6:
                idx = 1
        else:
            idx = 1


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    for a in DB:
        thread.start_new_thread(makeTunnel, a)

    while 1:
        time.sleep(5 * 60)

    oss.exit(0)


#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


