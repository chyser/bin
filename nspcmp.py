#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

WS = set([" ", '\t', '\n'])

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('i', 'stdin')], [], main.__doc__ + __doc__)


    inf = open(args[0]) if opts.stdin is None else oss.stdin
    otf = oss.stdout

    state = 0
    for line in inf:
        line = unicode(line, 'Latin-1', errors='strict')
        if line.startswith('//---'):
            continue

        for ch in line:
            if state == 0:
                if ch in WS:
                    state = 1
                    otf.write(' ')
                else:
                    try:
                        otf.write(ch)
                    except UnicodeEncodeError:
                        pass
            elif state == 1:
                if ch not in WS:
                    otf.write(ch)
                    state = 0


    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
