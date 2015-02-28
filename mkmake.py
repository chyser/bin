#!/usr/bin/env python
"""
usage: mkmake <file> [<file> ...]

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
def ChgExt(name, ext):
#-------------------------------------------------------------------------------
    """ ChgExt(name, ext):
          change the extension of name or list of names to extension ext
    """
    if type(name) == types.StringType:
        return splitnm(name) + ext
    else:
        o = []
        for i in name:
            o.append(splitnm(i) + ext)
        return o

import re
__inc = re.compile(r'#[ ]*include[ ]+"([_A-Za-z][_A-Za-z0-9]*[.]*[_A-Z-a-z0-9]*)"')

#-------------------------------------------------------------------------------
def CPPMkDepsList(fname):
#-------------------------------------------------------------------------------
    """ CPPMkDepsList(fname):
          return a list of dependencies for file 'fname'
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def chkdep(fname, list):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        inf = None
        try:
            inf = file(fname, 'rU')

            for line in inf:
                m = __inc.match(line)
                if m is not None:
                    hdr = m.group(1)
                    if hdr not in list:
                        list.append(hdr)
                        chkdep(hdr, list)
        except IOError:
            pass
        if inf: inf.close()

    lst = []
    chkdep(fname, lst)
    return lst

#-------------------------------------------------------------------------------
def CPPMkDeps(fname):
#-------------------------------------------------------------------------------
    """ CPPMkDeps(fname):
          return a string of dependencies for file 'fname'
    """

    print " ".join(CPPMkDepsList(fname))

#-------------------------------------------------------------------------------
def GetObjectObjs(fname):
#-------------------------------------------------------------------------------
    """ (hlist, clist) = GetObjectObjs(fname)
          hlist: list of header dependecies
          clist: list of obj dependecies
    """

    hlist = CPPMkDepsList(fname)
    clist = [fname]

    for i in hlist:
        nm = oss.splitnm(i) + '.cpp'
        if oss.exists(nm):
            clist.append(nm)
    return hlist, clist

TOP = """
.PHONY: remake

#
# add stuff here
#
include mak.inc

remake:
	rm mak.inc
mak.inc:
	python C:/bin/mkmake.py
"""

MSMAIN = """
default: all
.PHONY: all clean

RC = rc.exe
RM = rm.exe
INCPATH = C:/Program Files/Microsoft Visual Studio/VC98/include
LIBS = user32.lib advapi32.lib comdlg32.lib uuid.lib
INCLUDE = -I"C:/Program Files/Microsoft Visual Studio/VC98/include"
CC = cl1.exe
OPTS = /MT  /G5 /GX /nologo -D WIN98
PRODOPTS = /O2

LIBPATH = C:/Program Files/Microsoft Visual Studio/VC98/lib
DBGOPTS = /Zi
AR = lib.exe
MS_INCLUDE = -I"C:/Program Files/Microsoft Visual Studio/VC98/include"

CFLAGS += /O2 /Oi /Og /Ot /G6 /GX /nologo -D WIN98 -I"C:/Program Files/Microsoft Visual Studio/VC98/include"
#DBGOPTS =


clean:
	$(RM) -f *.obj *.exe *.lib *.dll *.pdb *.ilk *.res *.pp

%.obj : %.cpp
	$(CC) -c $(CFLAGS) $(DBGOPTS) $(CPPFLAGS) $< -o $@

%.obj : %.c
	$(CC) -c $(CFLAGS) $(DBGOPTS) $< -o $@
"""

MSEXE = """
%s.obj : %s %s
	$(CC) -c $(CFLAGS) $(DBGOPTS) $(CPPFLAGS) %s -o $@

%s_objs += %s
%s: %s.exe
%s.exe: %s %s $(%s_objs)
	$(CC) /Fe$@  -DUNIT_TEST $(CFLAGS) $(DBGOPTS) %s $(%s_objs) $(LIBS)

"""

#-------------------------------------------------------------------------------
def handleFile(ff):
#-------------------------------------------------------------------------------
    pass

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    #
    # handle options
    #
    args, opts = oss.gopt(argv[1:], [('u', 'unittest'), ('m', 'main')], [('t', 'target'), ('f', 'file')], usage)

    if opts.main:
        if opts.file is None:
            opts.file = "makefile"
        mf = file(opts.file, "w")

        print >> mf, TOP
        mf.close()
        oss.exit(0)

    if opts.target is None:
        MAIN = MSMAIN
        EXE = MSEXE

    if opts.file is None:
        opts.file = "mak.inc"

    #
    # create the file
    #
    mf = file(opts.file, "w")

    print >> mf, MAIN

    t_objs = []
    if opts.unittest:
        for f in oss.paths(args):
            hdrs, objs = GetObjectObjs(f)
            t_objs.extend(objs)
    else:
        t_objs = args

    print t_objs

    for f in oss.paths(t_objs):
        print "f:", f
        hdrs, objs = GetObjectObjs(f)

        objs.remove(f)
        oo = []
        for o in oss.paths(objs):
            oo.append("%s.obj" % o.drive_path_name)

        ff = f.drive_path_name
        print >> mf, "#\n# %s\n#" % (ff)
        print >> mf, EXE % (ff, f, ' '.join(hdrs), f, ff, ' '.join(oo), ff, ff, ff, f, " ".join(hdrs), ff, f, ff)

    mf.close()

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

