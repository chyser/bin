#!/usr/bin/env python
"""
usage: cc [---cc, ---lib] stuff

a wrapper for MS VC++ compilers dealing with all the path and env manipulation
that must be dealt with to make it work

Ex:
    cc.py ---cc cl7 ---lib "C:/Program Files/Microsoft Visual C++ Toolkit 2003/lib" <normal compiler options>

    sets exit code to that of compiler

"""

import pylib.osscripts as oss
import subprocess

compilerMap = {
    'cl7' : "C:/Program Files/Microsoft Visual C++ Toolkit 2003/bin",
    'cl8' : "C:/Program Files/Microsoft Visual Studio 8/VC/bin;C:/Program Files/Microsoft Visual Studio 8/Common7/IDE",
    'cl9' : "C:/Program Files/Microsoft Visual Studio 9.0/VC/bin;C:/Program Files/Microsoft Visual Studio 9.0/Common7/IDE",
    'dmp' : ("C:/tmp", "dumpenv.bat"),

}

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------

    args, opts = oss.gopt(argv[1:], [('v', 'verbose')], [('L', 'lib'), ('C', 'cc')], __doc__, longOpMarker='---', shortOpMarker='---')

    if opts.cc is None:
        oss.usage(1, __doc__, 'must specify compiler path')

    if opts.cc in compilerMap:
        path = compilerMap[opts.cc]
        if isinstance(path, tuple):
            opts.cc = path[1]
            path = path[0]
        else:
            opts.cc = 'cl.exe'
    else:
        path = oss.getpath(opts.cc)

    ## get environment
    env = oss.env.env

    env['PATH'] = path + ';' + env['PATH']

    if opts.lib is not None:
        env['LIB'] = opts.lib

    if opts.verbose:
        print path
        print opts.cc
        print opts.lib
        print args

    rc = subprocess.call(opts.cc + ' ' + ' '.join(args), env=env, shell=True)
    oss.exit(rc)


if __name__ == "__main__":
    main(oss.argv)
