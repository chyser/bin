#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

import webbrowser

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    with open('/tmp/af.txt') as inf:
        dd = inf.read()

    d = []
    exec(dd)

    for name, mv, html in d:
        print(html)
        ch = raw_input()
        if ch != 'n':
            webbrowser.open(html)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
