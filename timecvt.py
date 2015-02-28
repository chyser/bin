#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import datetime
import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: timecvt.py [options] <time>

        convert times between UTC and other timezones and back

        options:
            -o | --offset   : timezone offset
    """
    args, opts = oss.gopt(argv[1:], [('u', 'utc')], [('o', 'offset')], main.__doc__)

    offset = -4 if opts.offset is None else float(opts.offset)

    isUtc = args[0][-1] == 'Z'

    if not isUtc:
        offset *= -1

    if '_' in args[0]:
        fmt = '%Y%m%d_%H%M%S'
        ln = 15
    else:
        fmt = '%Y-%m-%d %H:%M:%S'
        ln = 19

    dt = datetime.datetime.strptime(args[0][:ln], fmt)

    print(str(dt + datetime.timedelta(hours=offset)) +  ((' UTC%d' % offset) if isUtc else 'Z'))



    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
