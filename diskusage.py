#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.util as util
import os


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: diskusage [options] [path]

    calculates the bytes used by the sub directories of the specified path. defaults
    to the current directory

    options:
        -d | --dir_only    : show directories only
        -p | --progress    : show progress
        -x | --exclude     : specifiy path to be excluded (can be issued multiple times)

    """
    args, opts = oss.gopt(argv[1:], [('p', 'progress'), ('d', 'dir_only')], [], [], [('x', 'exclude')], main.__doc__)

    if not args:
        args = ['.']

    if opts.exclude:
        global gExcludes
        gExcludes = [oss.canonicalPath('./' + x) for x in opts.exclude]
        print('Excludes:', gExcludes)

    for pth in oss.paths(args):
        for ss in sizeDir(pth, opts.dir_only, opts.progress):
            print("%8s" % util.CvtGigMegKBytes(ss.size, "1.1"), ss.pth)

    oss.exit(0)


gExcludes = set()
gVisited = set()

#-------------------------------------------------------------------------------
def calcSize(pth, progress=False, lvl=2):
#-------------------------------------------------------------------------------
    size = 0
    for p, d, f in os.walk(pth):
        for dd in d:
            dd = oss.canonicalPath(dd)
            if dd in gExcludes:
                print('excluding:', dd, file=oss.stderr)
                continue

            if dd in gVisited:
                continue

            gVisited.add(dd)

            if progress:
                print('...'*lvl, dd.encode('utf8', 'ignore'))

            size += calcSize(pth + '/' + dd, progress, lvl+1)

        for ff in f:
            try:
                s = os.stat(p + '/' + ff)[6]
                size += s
            except WindowsError as ex:
                print('Error: "%s"' % str(ex), file=oss.stderr)

    return size


#-------------------------------------------------------------------------------
def sizeDir(pth, dirOnly, progress=False):
#-------------------------------------------------------------------------------
    res = []
    tsize = 0

    if pth == '/' or pth == r'\\':
        pth += '*'

    for df in oss.ls(pth):
        df = oss.canonicalPath(df)
        if df in gExcludes:
            print('excluding:', df, file=oss.stderr)
            continue

        if progress:
            print('...', df.encode('utf8', 'ignore'))

        gVisited.add(df)

        if os.path.isdir(df):
            size = calcSize(df, progress)
            res.append(util.sstruct(size=size, pth=df+'\\'))
        else:
            try:
                size = os.stat(df).st_size
            except WindowsError as ex:
                print('Error: "%s"' % str(ex), file=oss.stderr)

            if not dirOnly:
                res.append(util.sstruct(size=size, pth=df))
        tsize += size

    res.append(util.sstruct(size=tsize, pth=pth))
    res.sort(key=lambda ss: int(ss.size), reverse=True)
    return res


if __name__ == "__main__":
    main(oss.argv)

