"""
usage: unsecure.py <file>
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
        print fn
        oss.r('crypt <%s >tt.zip' % (fn))
        oss.r('python C:/bin/zippy.py tt.zip')
    oss.rm('tt.zip')



#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)





