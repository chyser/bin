#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

import difflib
import pprint

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: pydiff <file1> <file2>
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    df = difflib.Differ()

    f1 = open(args[0]).readlines()
    f2 = open(args[1]).readlines()

    for line in df.compare(f1, f2):
        print(line, end="")

    print('\n\n')

    for line in difflib.ndiff(f1, f2):
        print(line, end="")

    print()
    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
