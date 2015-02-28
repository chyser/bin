#!/usr/bin/env python
"""
usage: dirsync options [[excludes]...]
    -s | --src      : source directory (default=.)
    -d | --dest     : destination directory

    -u | --updest   : update destination only, no add, no remove
    -p | --pretend  : show but make no changes

"""

import pylib.osscripts as oss
import pylib.syncdir as dsync


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    excludes, opts = oss.gopt(argv[1:], [('u', 'updest'), ('p', 'pretend')],
            [('s', 'src'), ('d', 'dest'), ('f', 'filters')], __doc__)

    if not opts.dest:
        opts.usage(1, "Must specify directories")

    src = opts.get('src', '.')
    print "src  =", src
    print "dest =", opts.dest
    print "excludes:", excludes

    if opts.filters is None:
        opts.filters = []
    else:
        if not isinstance(opts.filters, list):
            opts.filters = [opts.filters]
    print "filters:", opts.filters

    if not oss.exists(src):
        opts.usage(2, "Source directory '%s' does not exist" % src)

    if not oss.exists(opts.dest):
        opts.usage(2, "Destination directory '%s' does not exist" % opts.dest)

    if opts.updest:
        dsync.DirSync(src, opts.dest, excludes, opts.filters).UpdateDest(pretend=opts.pretend)
    else:
        dsync.DirSync(src, opts.dest, excludes, opts.filters).SyncDirs(pretend=opts.pretend)


if __name__ == "__main__":
    main(oss.argv)
