#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import difflib
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [('o', 'out')], main.__doc__ + __doc__)

    if len(args) != 2:
        opts.usage(1, 'must specify 2 files')

    otf = oss.stdout if opts.out is None else open(opts.out, 'w')

    if opts.out in set(args):
        opts.usage(3, 'output file must be different than input files')


    try:
        gf = open(args[0], 'rU').readlines()
        mf = open(args[1], 'rU').readlines()
    except IOError as ex:
        opts.usage(4, ex)

    state = None

    l0 = l1 = 0
    for line in difflib.ndiff(gf, mf):
        c = line[0]
        if c == '?':
            continue

        if c == '+':
            l1 += 1
            if state != '>':
                if state == '<':
                    otf.write('@-----      %s : %d\n' % (args[1], l1))
                else:
                    otf.write('@>>>>>      %s : %d\n' % (args[1], l1))
            otf.write(line[2:])
            state = '>'

        elif c == '-':
            l0 += 1
            if state != '<':
                if state == '>':
                    otf.write('@>>>>>\n')

                otf.write('@<<<<<      %s : %d\n' % (args[0], l0))
            otf.write(line[2:])
            state = '<'

        else:
            l1 += 1
            l0 += 1
            if state == '>':
                otf.write('@>>>>>\n')
            elif state == '<':
                otf.write('@<<<<<\n')
            otf.write(line[2:])
            state = None

    if state == '>':
        otf.write('@>>>>>\n')
    elif state == '<':
        otf.write('@<<<<<\n')

    if opts.out is not None:
        otf.close()

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
