"""
usage: secure.py <dir>
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
    args, opts = oss.gopt(argv[1:], [], [], usage)

    for fn in args:
        if not oss.exists(fn):
            usage(1, "%s does not exist" % fn)

        oss.r('python C:/bin/zippy.py -z -c tt.zip %s/*' % fn)
        oss.r('crypt <tt.zip > %s.sec' % (fn))
        oss.rm('tt.zip')

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)





