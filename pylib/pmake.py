import sys, getopt, re, parse, os, os.path
from osscripts import *

import BldDefs

gJustBuilt = []

#Dbg = False
Dbg = True

#-------------------------------------------------------------------------------
def Newer(Name, deps):
#-------------------------------------------------------------------------------
    for i in deps:
       if newerthan(i, Name):
           return True
    return False

#-------------------------------------------------------------------------------
def Build1(Target, sf, src, SrcFiles, BldRules, D, Force, TopLevel):
#-------------------------------------------------------------------------------
    global gJustBuilt
    assert(src)

    if Target in gJustBuilt:
        return True

    deps = []
    slist = (sf and sf.SList[:]) or []

    ## if specified src file exists, serach it for deps if it exists
    if exists(src):
        if os.path.splitext(src)[1] in [".c", ".cpp", ".h"]:
            deps = BldDefs.GenCPPHDeps(src)[0]

            if TopLevel and (not sf or sf.AutoSrc):
                for i in deps:
                    nm = os.path.splitext(i)[0]
                    if exists(nm + ".cpp") or exists(nm + ".c"):
                        slist.append(nm + ".obj")

    ## build all specified source files from slist
    for k in slist:
        if k != Target or k in gJustBuilt: Build(k, SrcFiles, BldRules, D, Force, False)

    for k in deps:
        if k != Target or k in gJustBuilt: Build(k, SrcFiles, BldRules, D, Force, False)

    ## at this point we either have a src or we built one
    if Force or not exists(Target) or Newer(Target, slist) or Newer(Target, deps):
        if not exists(src):
            return False

        BldDefs.BuildIt(src, Target, BldRules, D, slist)
    else:
        print "'%s' up to date" % Target

    return True

#-------------------------------------------------------------------------------
def DetSrcFile(Target, sf, BldRules):
#-------------------------------------------------------------------------------
    sl = []
    if sf:
        for src in sf.SList:
            for k in BldRules:
                if k.ExactMatch(src, Target): sl.append(src)

        for src in sf.SList:
            for k in BldRules:
                if k.Match(src, Target): sl.append(src)

    for i in BldRules:
        src = i.GetExactSrc(Target)
        if src: sl.append(src)

    for i in BldRules:
        src = i.GetSrc(Target)
        if src: sl.append(src)

    return sl

#-------------------------------------------------------------------------------
def Build(Name, SrcFiles, BldRules, D, Force = False, TopLevel = True):
#-------------------------------------------------------------------------------
    if Dbg: print "Building:", Name

    for sf in SrcFiles:
        if Name == sf.Name: break
    else: sf = None

    for src in DetSrcFile(Name, sf, BldRules):
        if Dbg: print "    trying:", src
        if Build1(Name, sf, src, SrcFiles, BldRules, D, Force, TopLevel): break

    if not exists(Name):
        print >> sys.stderr, "Unable to build '%s'" % Name
    else:
        gJustBuilt.append(Name)

#-------------------------------------------------------------------------------
def usage(err):
#-------------------------------------------------------------------------------
    print >> sys.stderr, "usage: pmake <file>"
    sys.exit(err)

#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-f:D:c:")
    except getopt.GetoptError:
        usage(1)

    mkfile = "make.pmk"; nd = None
    defs = []
    for o,a in opts:
        if o == '-f':
            mkfile = a
        elif o == '-D':
            defs.append(a)
        elif o == '-c':
            nd = a
        else:
            usage(1)



    ## create an environment to execute in
    D = {}
    D['Rules'] = []
    D['BldRules'] = []
    D['SrcFiles'] = []
    D['default'] = ""

    for d in defs:
        try:
            a,b = d.split('=')
            D[a] = '"' + b + '"'
        except:
            D[d] = True

    ## execute file using crafted environment
    if exists(mkfile):
        execfile(mkfile, D)

    ## create reasonable defaults
    os.environ["LIB"] = (("LIBPATH" in D) and D["LIBPATH"]) or BldDefs.LIBPATH
    os.environ["INCLUDE"] = (("INCPATH" in D) and D["INCPATH"]) or BldDefs.INCPATH

    if "LIBS" not in D: D["LIBS"] = BldDefs.LIBS
    if "COPTS" not in D: D["COPTS"] = BldDefs.OPTS + BldDefs.DBGOPTS
    if "Rules" not in D: D["Rules"] = BldDefs.CRules
    if "BldRules" not in D: D["BldRules"] = BldDefs.WinBldRules

    if len(args) > 0:
        for a in args:
            if a == "all":
                d = D['default']
                if type(d) == type([]):
                    for i in d:
                        Build(i, D['SrcFiles'], D['BldRules'], D)
                else:
                    Build(d, D['SrcFiles'], D['BldRules'], D)
            else:
                for i in D['Rules']:
                    if i.Match(a):
                        BldDefs.Spawn(i.GetCmdLine(D))
                        break
                else:
                    Build(a, D['SrcFiles'], D['BldRules'], D)

    elif D['default']:
        d = D['default']
        if type(d) == type([]):
            for i in d:
                Build(i, D['SrcFiles'], D['BldRules'], D)
        else:
            Build(d, D['SrcFiles'], D['BldRules'], D)


if __name__ == "__main__":
    main()
