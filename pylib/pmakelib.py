"""
This module is imported into makefiles parsed by pmake and thus these functions
and classes are availble without an explicit import
"""

from osscripts import *
import types, sys

_MAKEFILE_NAME = ""

#-------------------------------------------------------------------------------
def SetMakeFileName(mfn):
#-------------------------------------------------------------------------------
    global _MAKEFILE_NAME
    _MAKEFILE_NAME = mfn

#-------------------------------------------------------------------------------
def ChgExt(name, ext):
#-------------------------------------------------------------------------------
    """ change the extension of name or list of names to extension ext
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
    print " ".join(CPPMkDepsList(fname))

#-------------------------------------------------------------------------------
def GetObjectObjs(fname):
#-------------------------------------------------------------------------------
    hlist = CPPMkDepsList(fname)
    clist = []

    for i in hlist:
        nm = splitnm(i) + '.cpp'
        if exists(nm):
            clist.append(nm)
    return hlist, clist

#-------------------------------------------------------------------------------
def BuildUnit(fname):
#-------------------------------------------------------------------------------
    fname1 = splitnm(fname)

    hlist, clist = GetObjectObjs(fname1 + '.cpp')
    olist = ChgExt(clist, '.obj')
    print "\n\n#" + "-"*79
    print "# %s" % fname1
    print "#" + "-"*79
    print "%s.obj: %s.cpp %s" % (fname1, fname1, " ".join(hlist))
    print "\t$(CC) @$(OPTSFILE) -c %s.cpp\n" % fname1

    objs = " ".join(olist)
    print "%s.rsp: %s.cpp %s" % (fname1, fname1, _MAKEFILE_NAME)
    print "\techo %s $(LIBS) > %s.rsp\n" % (objs, fname1)

    print "%s: %s.exe" % (fname1, fname1)
    print "%s.exe: %s.rsp %s %s" % (fname1, fname1, " ".join(hlist), objs)
    print "\tset LIB=$(LIBPATH)"
    print "\t$(CC) @$(OPTSFILE) -DUNITTEST /Fe%s.exe  %s.cpp @%s.rsp" % (fname1, fname1, fname1)


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

