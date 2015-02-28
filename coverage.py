#/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.coverage_mod as cvg


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:  coverage.py [options] <module_name>

        options:
            -s | --swap   : swap the ran and miss marks
            -u | --useDB  : use prior run db if exists
            -m | --mods   : modules to report (accepts multiple)
    """
    args, opts = oss.gopt(argv[1:], [('s', 'swap'), ('u', 'useDB')], [], [], [('m', 'mods')], main.__doc__)

    if not args:
        opts.usage(1, 'Specify program or module')

    rm, mm = ('@', ' ') if opts.swap else (' ', '@')

    co = cvg.Coverage(args[0], rm, mm, opts.useDB, opts.mods)
    t, success = co.runTest()

    print("Tester: ran %d test(s) with %s\n" % (t, ['success', 'failure'][success]))
    print("Coverage generated files for:")

    for f in co.genReport():
        print('   ', f)

    oss.exit(0)

if __name__ == "__main__":
    main(oss.argv)

