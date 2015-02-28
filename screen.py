#!/usr/bin/env python
"""
usage: screen [options] [<diagonal in inches> | <horizontal width in inches>]

calculate equivelents between wide and normal TV screen formats

[options]
    -w | --wide  : use 16:9 widescreen
    -h | --horiz : value specified is horozontal width

"""

import math
import pylib.osscripts as oss

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
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('w', "wide"), ('h', 'horiz')], [], usage)

    size = float(args[0])
    if opts.horiz is None:
        if opts.wide is None:
            x =  size/math.sqrt(25.0)
            print 3*x, 4*x
        else:
            x =  size/math.sqrt(337.0)
            print 9*x, 16*x
    else:
        if opts.wide is not None:
            x =  size/16.0
            print math.sqrt(pow(16*x, 2) + pow(9*x, 2))
        else:
            x =  size/4.0
            print math.sqrt(pow(4*x, 2) + pow(3*x, 2))


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

