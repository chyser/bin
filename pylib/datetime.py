#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

#-------------------------------------------------------------------------------
def cvtDateTimeExpr(s):
#-------------------------------------------------------------------------------
    for fmt in ['%b %d %y', '%b %d %Y', '%B %d %y', '%B %d %Y']:
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    usage = oss.mkusage(__test__.__doc__)
    args, opts = oss.gopt(oss.argv[1:], [], [], usage)

    res = not __test__(verbose=True)
    oss.exit(res)


