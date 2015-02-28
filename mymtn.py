#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

MTNCMD = 'mtn'

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [('m', 'msg'), ('r', 'rev')], main.__doc__ + __doc__)

    if opts.msg is None:
        opts.msg = ''

    cmd = args[0]
    files = ' '.join(args[1:])

    if cmd == 'add':
        oss.r(MTNCMD + ' add ' + files)

    elif cmd == 'cf':
        if files:
            oss.r(MTNCMD + ' status ' + files)
        else:
            oss.r(MTNCMD + ' status .')

    elif cmd == 'log':
        oss.r(MTNCMD + ' log --brief ' + files)

    elif cmd == 'ci':
        oss.r(MTNCMD + ' ci -m "%s" %s' + (opts.msg, files))

    elif cmd == 'up':
        oss.r(MTNCMD + ' up')

    elif cmd == 'diff':
        opt = '--revision ' + opts.rev if opts.rev else ''

        oss.r(MTNCMD + ' diff --context ' + opt + ' ' + files)

    elif cmd == 'revert':
        oss.r(MTNCMD + ' revert --missing')

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
