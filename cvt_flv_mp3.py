#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

FFMPEG = "ffmpeg -i '%s' -acodec copy '%s'"


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    print(argv)
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)
    la = len(args)
    print(la)

    print(args)
    if not (0 < la < 3):
        oss.usage(1, "usage: cvt_flv_mp3.py <file_name.flv> [<output_file_name.mp3>]")
    elif la == 2:
        pth, fn, ext = oss.splitFilename(args[0])
        if not pth: pth = '.'
        infn = fn + '.flv'
        print(infn)
        pth, fn, ext = oss.splitFilename(args[1])
        if not pth: pth = '.'
        outfn = pth + '\\' + fn + '.mp3'
    else:
        pth, fn, ext = oss.splitFilename(args[0])
        if not pth: pth = '.'
        infn = fn + '.flv'
        outfn = pth + '\\' + fn + '.mp3'

    print("Pulling '%s' from '%s'" % (outfn, infn))
    oss.r(FFMPEG % (infn, outfn))
    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
