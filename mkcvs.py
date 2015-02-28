

import pylib.osscripts as oss

IGNORE_PATTERNS = ["*.bak", "*.vpb", "*.vtg", "*.chk", "*.vpwhist", "RCS", "SCCS", "CVS",
  "*.obj", "*.exe", "*.lib", "*.dll", "core", "*.ilk", "*.pdb", "*.pmk.mak", "*.rsp", "*.pyo", "*.pyc"]



#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: mkcvs [OPTIONS] <dir>
        Makes a cvs archive from the specified directory

        Options:
            -i | --ignore    :  specify extensions or files or directories to ignore
                                example: -i .bmp -i .jpg  or  -i badfile

"""
    args, opts = oss.gopt(argv[1:], [], [], [], [('i', 'ignore')], main.__doc__)

    if not oss.exists(oss.env['CVSROOT']):
        print "CVSROOT is down"
        oss.exit(1)

    if args:
       oss.cd(args[0])

    name = oss.basename(oss.pwd())

    if oss.exists(oss.env['CVSROOT'] + '/' + name):
        print >> oss.stderr, "Already exists:", oss.env['CVSROOT'] + '/' + name
        oss.exit(1)

    if opts.ignore is not None:
        if isinstance(opts.ignore, list):
            IGNORE_PATTERNS.extend(opts.ignore)
        else:
            IGNORE_PATTERNS.append(opts.ignore)

    il = bldIgnoreList()
    print "Ignoring Files: '%s'" % il

    oss.r(r'C:\bin\cvs.exe import %s %s %s %s1' % (il, name, name, name))
    oss.cd('..')
    oss.r("mv %s /tmp/%s.bak" % (name, name))

    oss.r(r'C:\bin\cvs.exe co %s' % name)

    oss.cd(name)
    for f in oss.ls():
        print f

    oss.r("C:\bin\cf.py")
    oss.exit(0)


#-------------------------------------------------------------------------------
def bldIgnoreList():
#-------------------------------------------------------------------------------
    s = ['"-I !"']
    for i in IGNORE_PATTERNS:
        s.append('-I "%s"' % i)
    return ' '.join(s)


if (__name__ == "__main__"):
    main(oss.argv)

