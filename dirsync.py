#!/usr/bin/env python
"""
usage: dirsync options [[excludes]...]
    -s | --src      : source directory
    -d | --dest     : destination directory

    -u | --updest   : update destination only, no add, no remove
    -p | --pretend  : show but make no changes

"""

import pylib.osscripts as oss
import pylib.syncdir as dsync

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    excludes, opts = oss.gopt(oss.argv[1:], [('u', 'updest'), ('p', 'pretend')], [('s', 'src'), ('d', 'dest'), ('f', 'filters')], usage)

    if opts.src is None or opts.dest is None:
        usage(1, "Must specify src and dest directories")

    print "src  =", opts.src
    print "dest =", opts.dest
    print "excludes:", excludes

    if opts.filters is None:
        opts.filters = []
    else:
        if not isinstance(opts.filters, list):
            opts.filters = [opts.filters]
    print "filters:", opts.filters

    if not oss.exists(opts.src):
        usage(2, "Source directory '%s' does not exist" % opts.src)

    if not oss.exists(opts.dest):
        usage(2, "Destination directory '%s' does not exist" % opts.dest)

    if opts.updest:
        dsync.DirSync(opts.src, opts.dest, excludes, opts.filters).UpdateDest(pretend=opts.pretend)
    else:
        dsync.DirSync(opts.src, opts.dest, excludes, opts.filters).SyncDirs(pretend=opts.pretend)
