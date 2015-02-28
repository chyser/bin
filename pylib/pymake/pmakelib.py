"""
This module is imported into makefiles parsed by pmake and thus these functions
and classes are availble without an explicit import
"""

from osscripts import *
import types, sys

_MAKEFILE_NAME = "make.pmk"

#-------------------------------------------------------------------------------
def SetMakeFileName(mfn):
#-------------------------------------------------------------------------------
    global _MAKEFILE_NAME
    _MAKEFILE_NAME = mfn

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
    clist = []

    for i in hlist:
        nm = splitnm(i) + '.cpp'
        if exists(nm):
            clist.append(nm)
    return hlist, clist


#-------------------------------------------------------------------------------
def AutoObjs(sfnlst):
#-------------------------------------------------------------------------------
    """ convert list of source file names to object file names
    """
    objs = ' '.join([splitnm(fn) + '.obj' for fn in sfnlst])
    return objs

#-------------------------------------------------------------------------------
def appendPath(a, b, sep=';'):
#-------------------------------------------------------------------------------
    """ append path elements being smart about quotes
    """
    if a[-1] == '"':
        return a[:-1] + sep + b + '"'
    if ' ' in a or ' ' in b:
        return '"' + a + sep + b + '"'
    return a + sep + b


#-------------------------------------------------------------------------------
def BuildUnit(fname, eobjs=''):
#-------------------------------------------------------------------------------
    fname = splitnm(fname)

    hlist, clist = GetObjectObjs(fname + '.cpp')
    olist = ChgExt(clist, '.obj')
    print "\n\n#" + "-"*79
    print "# %s" % fname
    print "#" + "-"*79
    print "%s.obj: %s.cpp %s" % (fname, fname, " ".join(hlist))
    print "\t$(CC) @$(OPTSFILE) -c %s.cpp\n" % fname

    objs = " ".join(olist) + ' ' + eobjs

    print "%s.rsp: %s.cpp %s" % (fname, fname, _MAKEFILE_NAME)
    print "\tpecho.exe %s $(LIBS) > %s.rsp\n" % (objs, fname)

    print "%s: %s.exe" % (fname, fname)
    print "%s.exe: %s.rsp %s %s" % (fname, fname, " ".join(hlist), objs)
    #print "\tset LIB=$(LIBPATH)"
    print "\t$(CC) @$(OPTSFILE) -DUNITTEST /Fe%s.exe  %s.cpp @%s.rsp\n" % (fname, fname, fname)


#-------------------------------------------------------------------------------
def BuildWinUnit(fname, eobjs=''):
#-------------------------------------------------------------------------------
    fname = splitnm(fname)

    hlist, clist = GetObjectObjs(fname + '.cpp')
    olist = ChgExt(clist, '.obj')
    print "\n\n#" + "-"*79
    print "# %s" % fname
    print "#" + "-"*79
    print "%s.obj: %s.cpp %s" % (fname, fname, " ".join(hlist))
    print "\t$(CC) @$(OPTSFILE) -c %s.cpp\n" % fname

    objs = " ".join(olist) + ' ' + eobjs
    print "%s.rsp: %s.cpp %s" % (fname, fname, _MAKEFILE_NAME)
    print "\tpecho.exe %s %s.res $(LIBS) > %s.rsp\n" % (objs, fname, fname)

    print "%s.res: %s.rc" % (fname, fname)
    print '\tset INCLUDE="$(INCPATH)"'
    print "\t$(RC) -r %s.rc\n" % fname

    print "%s: %s.exe" % (fname, fname)
    print "%s.exe: %s.rsp %s.res %s %s" % (fname, fname, fname, " ".join(hlist), objs)
    print "\t$(CC) @$(OPTSFILE) -DUNITTEST /Fe%s.exe  %s.cpp @%s.rsp\n" % (fname, fname, fname)


#-------------------------------------------------------------------------------
def mkres():
#-------------------------------------------------------------------------------
    """ make a .res file from a .rc file
    """
    print "$(RC) -r $^\n"


#-------------------------------------------------------------------------------
def BuildDLL(fname, eobjs=''):
#-------------------------------------------------------------------------------
    """ Builds a dll from file named 'fname' with objects provided
        by 'GetObjectObjs()'.
        'eobjs' is a list of extra objects or libraries to tack on
    """
    fname = splitnm(fname)

    hlist, clist = GetObjectObjs(fname + '.cpp')
    olist = ChgExt(clist, '.obj')

    print "\n\n#" + "-"*79
    print "# %s" % fname
    print "#" + "-"*79
    print "%s.obj: %s.cpp %s" % (fname, fname, " ".join(hlist))
    print "\t$(CC) @$(OPTSFILE) -c %s.cpp\n" % fname

    objs = " ".join(olist) + ' ' + eobjs
    print "%s.rsp: %s.cpp %s" % (fname, fname, _MAKEFILE_NAME)
    print "\tpecho.exe %s $(LIBS) > %s.rsp\n" % (objs, fname)

    print "%s.dll: %s.rsp %s %s" % (fname, fname, " ".join(hlist), objs)
    print "\t$(CC) @$(OPTSFILE) -D__DLL__ /LD /Fe%s.dll  %s.cpp @%s.rsp\n" % (fname, fname, fname)


#-------------------------------------------------------------------------------
def OptsFile(fname='opts', opts=""):
#-------------------------------------------------------------------------------
    print """\nOPTSFILE = %s
$(OPTSFILE): debug $(MAKEFILE_NAME)

debug:
\tpecho.exe -c -- $(DBGOPTS) %s $(CFLAGS) > $(OPTSFILE)
product:
\tpecho.exe -c -- $(PRODOPTS) %s $(CFLAGS) > $(OPTSFILE)

""" % (fname, opts, opts)


#-------------------------------------------------------------------------------
def mkexe(opts = ""):
#-------------------------------------------------------------------------------
    print "\t$(CC) /Fe$@ %s $(CFLAGS) $(DBGOPTS)  /Tp $^ $(LIBS)\n" % opts

#-------------------------------------------------------------------------------
def mkpreprocessor(ofile, opts = ""):
#-------------------------------------------------------------------------------
    print "\t$(CC) /E %s $(CFLAGS) $^ > %s\n" % (opts, ofile)


import pylib.xmlparse
#-------------------------------------------------------------------------------
class VSProj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ProjectName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(VSProj, self).__init__()
        self.ProjectName = ProjectName
        self.files = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetFiles(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.files is not None:
            return self.files

        xp = pylib.xmlparse.XMLParser(self.ProjectName)
        self.files = []
        for attr, cdata in xp.Parse("Project/Files/Folder/F"):
            self.files.append(attr['N'])
        return self.files


