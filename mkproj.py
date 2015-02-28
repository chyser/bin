import pylib.osscripts as oss

VERSION = "1.0"

#-------------------------------------------------------------------------------
def CreateMakefile(project):
#-------------------------------------------------------------------------------
    otf = file("makefile", "wU")

    print >> otf, """
#
# makefile - created by mkproj version(%s)
#
include make.pmk.mak

make.pmk.mak: make.pmk
\tpmake -bp

project:
\tpmake -bp
""" % VERSION

    otf.close()

    otf = file("make.pmk", "wU")

    if project == "python":
        print >> otf, "PROJECT = PYTHON"
    elif project == "vc6":
        print >> otf, "PROJECT = CPP VC 6"
    elif project == "vc7":
        print >> otf, "PROJECT = CPP VC 7"
    elif project == "gcc":
        print >> otf, "PROJECT = CPP GCC"
    else:
        print >> oss.stderr, "Unknown Project Type:", project

    print >> otf, """

all:

"""

    otf.close()

#-------------------------------------------------------------------------------
def usage(rc, s=""):
#-------------------------------------------------------------------------------
    print >> oss.stderr, """
usage: mkproj [options] <type>
    <type>
      vc6  - visual c++ 6 project
      vc7  - visual c++ 7 project
      gcc  - gcc project
      python - python project

   [options]
      -f | --force  : overwrite any exisitng project files
"""
    oss.exit(rc)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    arg, opts = oss.gopt(oss.argv[1:], [('f', 'force')], [])

    if not(opts.force or (not oss.exists('makefile') and not oss.exists('make.pmk'))):
        print >> oss.stderr, "makefile or make.pmk already exist"
        oss.exit(1)

    if not arg:
        usage(2)

    CreateMakefile(arg[0])
