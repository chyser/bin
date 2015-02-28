#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import shutil

MUSIC_PATH = 'E:/music/car'
CAR_PATH = 'F:/'


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('x', 'extra')], [], main.__doc__ + __doc__)

    mp = set()

    oss.cd(MUSIC_PATH)
    for f in oss.find('.', '*.mp3'):
        dest = CAR_PATH + f[2:]
        d = dest.split('\\')[0] + '/'

        mp.add(f)

        if not oss.exists(d):
            oss.mkdir(d)

        if not oss.exists(dest) or oss.newerthan(f, dest):
            print(f, dest)
            cp(f, dest)

    if opts.extra:
        oss.cd(CAR_PATH)
        dp = set()

        for f in oss.find('.', '*.mp3'):
            dp.add(f)

        a = dp - mp
        for f in a:
            print(f)

    oss.exit(0)


#-------------------------------------------------------------------------------
def cp(src, dest):
#-------------------------------------------------------------------------------
    try:
        shutil.copyfile(src, dest)
    except IOError:
        print("Error: %s %s" % (src, dest))



if __name__ == "__main__":
    main(oss.argv)
