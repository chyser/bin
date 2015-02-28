#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import time

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: timeit [options] cmd-args

    This cmd executes the command line specified and provides the time in
    secs of execution.

    Options:
       -f | --func   : function to eval on output (initial value == n)
       -r | --runs   : number of times to run cmd

    """
    args, opts = oss.gopt(argv[1:], [], [('f', 'func'), ('r', 'runs')], main.__doc__)

    if not args:
        opts.usage(1, "must specify a command")

    opts.runs = int(opts.runs) if opts.runs is not None else 1

    cmd = " ".join(args)
    print(cmd)
    print("\n\n====================================================")

    n = 1000000000000000
    for i in range(opts.runs):
        t = timeOneRun(cmd)
        if t < n: n = t

    print("\n\n====================================================")

    if opts.func is not None:
        gbls = {'n' : n}
        print(eval(opts.func, gbls))
    else:
        print(n)

    oss.exit(0)


#-------------------------------------------------------------------------------
def timeOneRun(cmd):
#-------------------------------------------------------------------------------
    st = time.time()
    oss.r(cmd)
    et = time.time()
    return et - st


if __name__ == "__main__":
    main(oss.argv)
