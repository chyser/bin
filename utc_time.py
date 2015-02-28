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
    """ usage: utc_time.py [options]

        options:
            -p | --pplan    : use power plan format

    """
    args, opts = oss.gopt(argv[1:], [('p', 'pplan')], [], main.__doc__ + __doc__)

    fmtStr = "%Y%m%d_%H%MZ" if opts.pplan else "%Y-%m-%d %H:%M:%SZ"
    print(time.strftime(fmtStr, time.gmtime()))
    oss.exit(0)

if __name__ == "__main__":
    main(oss.argv)
