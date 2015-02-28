#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import re
import pylib.osscripts as oss


TMPFILE = '/tmp/t.crlf'
BUFILE = '/tmp/t.bu.crlf'

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: crlf [options] <file> [<file> ...]

        options:
            -i | --identify  : identify line ending in file (default)
            -w | --win       : convert line endings to windows
            -u | --unix      : convert line ending to unix
            -m | --mac       : convert line endings to mac

        converts line endings in a file to the specifed type
    """
    args, opts = oss.gopt(argv[1:], [('w', 'win'), ('u', 'unix'), ('m', 'mac'), ('i', 'identify')], [], main.__doc__)

    if not args:
        opts.usage(1, "must specify files")

    src = r"\r|\n|\r\n"

    if opts.identify:
        mode = "id"
    elif opts.mac:
        mode = "mac"
        dest = "\r"
    elif opts.unix:
        mode = "unix"
        src = r"\r?\n"
        dest = "\n"
    elif opts.win:
        mode = "win"
        dest = "\r\n"
    else:
        mode = "id"

    for fName in oss.paths(args):
        if oss.IsDir(fName):
            print(fName, "Directory!")
            continue

        oss.cp(fName, BUFILE)
        with open(fName, "rb") as inf:
            data = inf.read()

            if '\0' in data:
                print(fName, "Binary!")
                continue

            if mode == "id":
                if re.search(r"[^\r]\n", data):
                    res = 'unix'
                elif re.search(r"\r\n", data):
                    res = 'win'
                elif re.search(r"\r[^\n]", data):
                    res = 'mac'
                else:
                    res = 'unkn'

                print('{0} -> {1}'.format(fName, res))

            else:
                newdata = re.sub(src, dest, data)
                if newdata != data:
                    with open(TMPFILE, 'wb') as f:
                        f.write(newdata)
                    oss.cp(TMPFILE, fName)
                    print(fName)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
