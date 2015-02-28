#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.options as optlib

MTNCMD = 'mtn1.exe'

def r(cmd):
    #print(cmd, file=oss.stderr)
    oss.r(cmd)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = optlib.mopt(argv[1:], [], [('m', 'msg'), ('r', 'rev')], main.__doc__ + __doc__, nonOpStopOp=False, skipUnknownOps=True)

    msg = opts.get('msg', '')

    if not args:
        opts.usage(1)

    cmd = args[0]
    cnt = len(args[1:])
    files = ' '.join([relativizeName(f) for f in args[1:]])

    if cmd == 'add':
        r(MTNCMD + ' add ' + files)

    elif cmd == 'cf':
        if files:
            r(MTNCMD + ' status ' + files)
        else:
            r(MTNCMD + ' status .')

    elif cmd == 'log':
        options = '--brief'
        r(MTNCMD + ' log ' + options + ' ' + files)

    elif cmd == 'ci':
        r(MTNCMD + ' ci -m "%s" %s' % (msg, files))

    elif cmd == 'up':
        r(MTNCMD + ' up')

    elif cmd == 'diff':
        opt = '--revision ' + opts.rev if opts.rev else ''
        r(MTNCMD + ' diff --context ' + opt + ' ' + files)

    elif cmd == 'revert':
        r(MTNCMD + ' revert --missing ' + files)

    elif cmd == 'cat':
        if cnt == 1:
            opt = '--revision ' + opts.rev if opts.rev else ''
            r(MTNCMD + ' cat ' + opt + ' ' + files)
        else:
            opts.usage(1, "Cat only handles a single file")

    else:
        r(MTNCMD + ' ' + cmd + ' ' + files)

    oss.exit(0)


#-------------------------------------------------------------------------------
def relativizeName(nm):
#-------------------------------------------------------------------------------
    p = oss.pwd()
    return oss.relativePath(p, nm)

if __name__ == "__main__":
    main(oss.argv)
