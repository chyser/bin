#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import win32file as w32
import win32wnet as wnet

import pylib.osscripts as oss
import pylib.util as util


S = ["UNKNOWN", "NO_ROOT_DIR", "removable", "fixed", "remote", "cdrom", "ramdisk"]


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: drives.py

    shows the available drives on the system and (free space/total space)
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    drives = w32.GetLogicalDrives()

    for i in range(26):
        if drives & (1 << i):
            dl = chr(i + ord('A'))
            rootpath = dl + ':\\'
            tp = w32.GetDriveType(rootpath)
            print("  %s:" % dl, S[tp], end='')

            try:
                f, t, d = w32.GetDiskFreeSpaceEx(rootpath)

                if tp == 4:
                    print(" (%s/%s)" % (util.CvtGigMegKBytes(f), util.CvtGigMegKBytes(t)), end='')
                    print(" [%s]" % wnet.WNetGetUniversalName(rootpath, 1))
                else:
                    print(" (%s/%s)" % (util.CvtGigMegKBytes(f), util.CvtGigMegKBytes(t)))

            except:
                print("  -- not ready")

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

