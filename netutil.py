#!/usr/bin/env python
"""
"""

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
    """
    args, opts = oss.gopt(argv[1:], [], [('n', 'net'), ('m', 'mask')], main.__doc__ + __doc__)
    
    mask = util.ConvertNetMaskToInt(opts.mask)
    net = util.ConvertNetMaskToInt(opts.net) & mask
    
    nete = util.ConvertIntToAddr(net + (0xffffffffL - mask))
    net = util.ConvertIntToAddr(net)
    print("Start {0} -> {1}\n".format(net, nete))
    oss.exit(0)
        
        
if __name__ == "__main__":
    main(oss.argv)
