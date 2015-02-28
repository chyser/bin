#!/usr/bin/env python


import pylib.osscripts as oss
import Image


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: cvtimage -t <type> file [file ...]

        converts one or more image files to the specified image file type

        types include:
            jpg  : jpeg
            bmp  : bitmaps
            png  :
            gif  : (input only)
    """
    args, opts = oss.gopt(argv[1:], [], [('t', 'type')], main.__doc__)

    if opts.type is None:
        opts.usage(1, "must specify type")

    args = oss.paths(args)

    for a in args:
        otfn = a.drive_path_name + '.' + opts.type
        if otfn != a:
            try:
                print "Converting", a, "to", otfn
                Image.open(a).save(otfn)
            except IOError:
                print >> oss.stderr, "Cannot convert", a, "to", otfn



    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

