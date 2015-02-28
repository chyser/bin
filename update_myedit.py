#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('p', 'pause')], [], __doc__ + main.__doc__)

    install_dir = oss.env['MYEDIT_DIRECTORY']
    print('MyEdit installed at: "%s"' % install_dir)
    print('\nUpdating "myedit"')
    oss.cd(install_dir)
    t = oss.r('cvs.exe up -d', '|')
    printResults(t)

    print('\nUpdating "pylib"')
    oss.cd('C:/bin/pylib/pylib')
    t = oss.r('cvs.exe up -d', '|')
    printResults(t)

    print('\nIf MyEdit is running, it must be restarted.')

    if opts.pause:
        raw_input('\n<Hit key to continue>')
    oss.exit(0)


#-------------------------------------------------------------------------------
def printResults(t):
#-------------------------------------------------------------------------------
    for l in t.split('\n'):
        try:
            if l[0] != '?':
                print(l)
        except IndexError:
            pass

if __name__ == "__main__":
    main(oss.argv)
