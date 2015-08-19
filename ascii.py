#!/bin/env python

"""
usage: ascii [options]

Shows the ascii character set

Options:
    -h | --hex       : show hex (default)
    -d | --decimal   : show decimal
    -o | --octal     : show octal

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('h', 'hex'), ('d', 'decimal'), ('o', 'octal')], [], __doc__)

    disp = "%03x"

    if opts.decimal:
        disp = "%3d"
    elif opts.octal:
        disp = "%3o"


    for j in xrange(0,32):
        for i in xrange(0,8):
            l = 32*i + j

            if 0 < l and l < 27 :
                print (disp + ' : ^%c  ') % (l, chr(l + ord('a')-1)),
            elif l == 0 :
                print (disp + ' : \\0  ') % l,
            else:
                print (disp + ' : %c   ') %  (l, chr(l)),
        print '\n',

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)


