#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss
import threading
import random
import time

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
def makeTunnel(lp, host, rp):
#-------------------------------------------------------------------------------
    cmd = "plink.exe -pw kibsop) -N -L %d:%s:%d chrish@compflu-01.hpl.hp.com" % (lp, host, rp)
    print cmd
    oss.r(cmd)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('r', 'rmtport'), ('l', 'locport')], usage)

    if opts.locport:
        locport = int(opts.locport)
    else:
        locport = random.randint(5905, 5930)

    display = locport - 5900
    rmtport = 5901

    if len(args) != 1:
        usage(1)

    if ':' in args[0]:
        mach, rp = args[0].split(':')
        rmtport = int(rp) + 5900
    else:
        mach = args[0]

    if opts.rmtport:
        rmtport = int(opts.rmtport)

    t = threading.Thread(target=makeTunnel, args=(locport, mach, rmtport))
    t.setDaemon(True)
    t.start()

    time.sleep(5)
    oss.cd("C:/Program Files/tightvnc/")
    oss.r('vncviewer.exe %s:%d' % ('localhost', display))

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)
