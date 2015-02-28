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

    for a in args:
        processFile(a)

    oss.exit(0)


#-------------------------------------------------------------------------------
def processFile(fn):
#-------------------------------------------------------------------------------
    fw = 10
    stack = []
    lineno = 0

    with open(fn) as inf:
        for line in inf:
            lineno += 1
            line = line.rstrip()
            ln = line.lstrip()

            if not ln or ln[0] == '#':
                print(line)
                continue

            if '::' in ln:
                eq = ln.rfind(':')
                fw = len(ln) - eq - 2
                ss = ln[eq+1:].strip()
                if ss:
                    stack.append(eval(ss))
                print(line)

            elif ln.startswith('$s:'):
                print(line[:line.rfind(':')+1], ('%%%ds' % fw) % ('%3.2f' % sum(stack)))

            elif ln.startswith('$t:'):
                print(line[:line.rfind(':')+1], ('%%%ds' % fw) % ('%3.2f' % sum(stack)))
                stack = []

            else:
                print(line)


#-------------------------------------------------------------------------------
def syntaxError(lineno, s):
#-------------------------------------------------------------------------------
    print("Syntax Error - %d '%s'" % (lineno, s))


if __name__ == "__main__":
    main(oss.argv)
