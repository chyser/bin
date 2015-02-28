#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import string


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: untabify.py [options] <file_name> [<file_name> ...]

        options:
            -t | --tabwidth   : number of space to use (default: 8)

        Replace tabs with spaces in argument files printing names of changed
        files.
    """
    args, opts = oss.gopt(argv[1:], [], [('t', 'tabwidth')], main.__doc__)

    tabsize = 8 if opts.tabwidth is None else int(opts.tabwidth)

    for f in args:
        process(f, tabsize)

    oss.exit(0)


#-------------------------------------------------------------------------------
def process(fn, tabsize):
#-------------------------------------------------------------------------------
    try:
        with open(fn, 'rU') as inf:
            text = inf.read()
    except IOError as msg:
        print("%s: I/O error: %s" % (fn, str(msg)), file=oss.stderr)
        return

    newtext = string.expandtabs(text, tabsize)
    if newtext == text:
        return

    backup = fn + "~"

    oss.rm(backup)
    oss.mv(fn, backup)

    with open(fn, 'w') as otf:
        otf.write(newtext)

    print(fn)


if __name__ == "__main__":
    main(oss.argv)

