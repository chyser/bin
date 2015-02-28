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
    """ usage: chk_modules.py [python dir]

    determines which python modules are python version specific and which aren't

    """
    args, opts = oss.gopt(argv[1:], [], [], __doc__ + main.__doc__)

    if len(args) != 1:
        opts.usage(1, 'must specify a python installation directory')


    path = args[0] + '/lib/site-packages'

    if not oss.exists(path):
        opts.usage(2, '"%s" not a python installation directory' % args[0])

    specific, nonSpecific = findModules(path)

    print('\nSpecific Modules:')
    for f in sorted(specific):
        print('   ', f)

    print('\nNon-Specific Modules:')
    for f in sorted(nonSpecific):
        print('   ', f)


    specific, nonSpecific = findModules('C:/workspace/pylibs')
    print('\nGeneric Modules:')
    for f in sorted(nonSpecific):
        print('   ', f)

    if len(specific) != 0:
        print('Error: installation specific module(s) in /workspace/pylibs')
        print(specific)

    oss.exit(0)


#-------------------------------------------------------------------------------
def clean(name):
#-------------------------------------------------------------------------------
    if name.startswith('.\\'):
        return name[2:]
    return name


#-------------------------------------------------------------------------------
def readPthFile(pth):
#-------------------------------------------------------------------------------
    dirs = set()
    for line in oss.readf(pth):
        line = line.strip()
        if not line or line[0] == '#' or line.startswith('import'):
            continue
        dirs.add(line)
    return dirs


#-------------------------------------------------------------------------------
def findModules(path):
#-------------------------------------------------------------------------------
    oss.cd(path)

    dirs = set()
    pyFiles = set()
    specific = set()
    nonSpecific = set()

    for f in oss.ls():
        if f.endswith('.py'):
            pyFiles.add(oss.path(f))

        elif f.endswith('.pyd'):
            specific.add(oss.path(f).name)

        elif oss.isDir(f) and oss.exists(f + '/__init__.py'):
            dirs.add(f)

        elif f.endswith('.pth'):
            dirs |= readPthFile(f)

        else:
            #print('what:', f)
            pass

    for f in pyFiles:
        f = f.name
        for ff in oss.ls():
            if ff.endswith(f + '.pyd'):
                specific.add(f)
                break
        else:
            nonSpecific.add(f)

    for d in dirs:
        code = False
        for f in oss.find(d):
            if f.endswith('.pyd') or f.endswith('.dll'):
                specific.add(clean(d))
                break
            if f.endswith('.py'):
                code = True
        else:
            if code:
                nonSpecific.add(clean(d))


    return specific, nonSpecific


if __name__ == "__main__":
    main(oss.argv)
