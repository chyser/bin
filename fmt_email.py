#!/usr/bin/env python
"""
usage: fmt_email.py [options] [<input file> [<output file>]]

if input file not present, use stdin, if output file not present, dumps to stdout

options:
    -w | --width   : testwrap lines to this width (default: 70)

"""

import pylib.osscripts as oss
import textwrap

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('w', 'width')], usage)

    otf = oss.stdout
    if not args:
        inf = oss.stdin
    else:
        inf = file(args[0])
        if len(args) == 3:
            otf = file(args[1], 'w')

    if opts.width is None:
        opts.width = 70

    for line in inf:
        lines = textwrap.wrap(line, int(opts.width))
        print >> otf, '>', '\n> '.join(lines)

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


