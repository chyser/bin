#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: pylibs.py <python directory>
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    if not args:
        opts.usage(1, 'must specify a python install directory')

    print('\nSpecific:', args[0])
    print(checkPath(args[0] + '/lib/site-packages'))
    print('\nGeneral:')
    print(checkPath('/workspace/pylibs'))

    oss.exit(0)


#-------------------------------------------------------------------------------
def checkPath(path):
#-------------------------------------------------------------------------------
    oss.cd(path)

    libs = []
    covered = set()
    for i in oss.paths(oss.ls('*.pth')):
        libs.append(i.name)
        for line in oss.readf(i):
            if line.strip().startswith('#'):
                continue
            covered.add(line)

    for i in oss.paths(oss.ls()):
        if i in covered:
            continue

        if i.ext == '.py':
            libs.append(i.name)

        if oss.IsDir(i):
            if oss.exists(i + '/__init__.py'):
                libs.append(i.name)

    return libs


if __name__ == "__main__":
    main(oss.argv)
