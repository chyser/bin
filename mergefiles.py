#!/usr/bin/env python

import pylib.osscripts as oss
import difflib

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: mergefiles <left_input_file> <right_input_file> <output_file>

        merges input files into a single output file
    """

    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    ibuf0 = open(args[0], 'rU').readlines()
    ibuf1 = open(args[1], 'rU').readlines()

    otf = open(args[2], 'w')

    df = difflib.Differ()

    state = None
    for line in df.compare(ibuf0, ibuf1):
        ch = line[0]

        if ch == '?':
            continue

        if state == None:
            if ch == '-':
                otf.write('\n<<<<<<<<<<<<<[\n')
                otf.write(line[2:])
                state = '-'
            elif ch == '+':
                otf.write('\n>>>>>>>>>>>>>[\n')
                otf.write(line[2:])
                state = '+'
            else:
                otf.write(line[2:])

        elif state == '+':
            if ch == '-':
                otf.write('>>>>>>>>>>>>>]\n')
                otf.write('\n<<<<<<<<<<<<<[\n')
                otf.write(line[2:])
                state = '-'
            elif ch == '+':
                otf.write(line[2:])
            else:
                otf.write('>>>>>>>>>>>>>]\n\n')
                otf.write(line[2:])
                state = None

        elif state == '-':
            if ch == '-':
                otf.write(line[2:])
            elif ch == '+':
                otf.write('-------------\n')
                otf.write(line[2:])
                state = '+'
            else:
                otf.write('<<<<<<<<<<<<<]\n\n')
                otf.write(line[2:])
                state = None

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

