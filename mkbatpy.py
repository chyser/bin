
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: mkbatpy <python file>

    make a batchfile for a python file, both in the C:/bin directory
       -p | --python   : specify the python executable (default: python.exe)
       -f | --force    : overwrite existing bat file (default: no overwrite)

    """
    args, opts = oss.gopt(argv[1:], [('f', 'force')], [('p', 'python')], main.__doc__)

    py = opts.python if opts.python else "python.exe"

    for a in args:
        create(a, opts.force, py)

    oss.exit(0)


#-------------------------------------------------------------------------------
def create(fn, force = False, python="python.exe"):
#-------------------------------------------------------------------------------
    if not oss.exists(fn):
        return

    oname = oss.replaceExt(fn, '.bat')

    if not force and oss.exists(oname):
        print(oname, "already exists")
        return True

    with open(oname, 'w') as otf:
        print("""echo off\n%s C:\\bin\\%s %%1 %%2 %%3 %%4 %%5 %%6 %%7 %%8 %%9""" % (python, fn), file=otf)

    oss.r("cvs add %s" % oname)
    oss.r('cvs ci -m "new file" %s' % oname)
    return True


if __name__ == "__main__":
    main(oss.argv)


