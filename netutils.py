#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.net.util as util

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
            netutils.py -c <address>    | print network and netmask
    """
    args, opts = oss.gopt(argv[1:], [('c', 'cidr')], [], main.__doc__)


    if opts.cidr:
        a, m = util.ConvertCIDR(args[0])
        s, g, b = util.getGatewayBroadcast(a, m)
        print('address:  ', s)
        print('netmask:  ', m)
        print('gateway:  ', g)
        print('broadcast:', b)





    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
