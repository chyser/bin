#!/usr/bin/env python
"""
usage: cutfile [options] <input file> <output file>

cuts specified lines from the input file and writes them to the output file

options:
    -s | --start    : starting line number (defaults to 0)
    -e | --end      : ending line number (defaults to end of file)

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('s', 'start'), ('e', 'end')], usage)

    start = 0
    end = 100000000000000000

    if opts.start is not None:
        start = int(opts.start)

    if opts.end is not None:
        end = int(opts.end)

    inf = file(args[0])
    try:
        otf = file(args[1], 'w')
    except IndexError:
        otf = oss.stdout

    idx = 0
    for line in inf:
        if start <= idx < end:
            otf.write(line)
        else:
            if idx >= end:
                break
        idx += 1

    otf.close()
    inf.close()
    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

