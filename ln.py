"""
usage:
    ln TARGET                 : create link basename(TARGET) to TARGET in the current directory
    ln TARGET LINK_NAME       : create link LINK_NAME to TARGET in directory specified by LINK_NAME
    ln (-d | --delete) TARGET : remove link named TARGET
"""

import pylib.osscripts as oss

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
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('d', 'delete')], [], usage)

    la = len(args)

    if la < 1:
        usage('insufficient arguments')

    tgt = args[0]

    if la == 1:
        if opts.delete:
            rc = oss.r('linkd.exe "%s" /D' % tgt)
        else:
            rc = oss.r('linkd.exe "%s" "%s"' % (oss.basename(tgt), tgt))
    else:
        rc = oss.r('linkd.exe "%s" "%s"' % (args[1], tgt))

    oss.exit(rc)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

