#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import datetime
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: newerthan.py [options[ <date>

        options:
            -i | --ignore   : extentions to ignore (may be specified multiple times)

        finds file newer than the specified data
        date formats ['%b %d %y', '%b %d %Y', '%B %d %y', '%B %d %Y']
    """
    args, opts = oss.gopt(argv[1:], [], [], [], [('i', 'ignore')], main.__doc__)

    td = cvtDateExpr(' '.join(args))
    if td is None:
        opts.usage(1, "Can't parse date")

    for f in oss.find('.'):
        bn, _, ext = f.rpartition('.')

        if ext in set(['bak']) or ext.startswith('bk'):
            continue

        s = os.stat(f)
        fd = datetime.datetime.fromtimestamp(s.st_mtime)
        if fd > td:
            print(f)


    oss.exit(0)


#-------------------------------------------------------------------------------
def cvtDateExpr(s):
#-------------------------------------------------------------------------------
    for fmt in ['%b %d %y', '%b %d %Y', '%B %d %y', '%B %d %Y']:
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass


if __name__ == "__main__":
    main(oss.argv)
