#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    for i in oss.ls(r'C:\windows\fonts\*.ttf'):
        print(i.split('\\')[-1])

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
