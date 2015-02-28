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
    """ usage: myedit.py <files> [<files> ...]

        frontend to myedit
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)
    ff = [oss.canonicalPath(arg) for arg in args]

    for f in ff:
        if not oss.exists(f):
            oss.touch(f)

    oss.r('C:/python26/python.exe C:/home/chrish/work/myedit/myedit.py -X -s ' + ' '.join(ff))
    oss.exit(0)

if __name__ == "__main__":
    main(oss.argv)
