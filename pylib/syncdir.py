#!/usr/bin/env python

import pylib.osscripts as oss
import pylib.util as util
import pylib.debug as dbg

import fnmatch
import os.path
import hashlib


#-------------------------------------------------------------------------------
class DirSync(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, srcPath, destPath, excludes, filters=None, verbose=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(DirSync, self).__init__()
        self.srcPath = srcPath
        self.destPath = destPath
        self.excludes = set(excludes)

        self.filters = filters if filters else ['*']
        self.verbose = verbose

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetFileInfo(self, tdir):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get info about files in target directory.
        """

        def __p(hist, dirn, names):
            for n in list(names):
                if n in self.excludes:
                    names.remove(n)
                    continue

                fn = dirn + '\\' + n

                for filter in self.filters:
                    if fnmatch.fnmatch(fn, filter):
                        break
                else:
                    continue

                bn = oss.basename2(tdir, fn)

                try:
                    hist[bn] = hashlib.md5(file(fn).read()).hexdigest()
                except IOError:
                    hist[bn] = 0


        hist = {}
        os.path.walk(tdir, __p, hist)
        return hist

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, msg, nl='', bl=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print msg

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SyncDirs(self, dst=None, pretend=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        src = self.GetFileInfo(self.srcPath)

        if not dst:
            dst = self.GetFileInfo(self.destPath)

        d, a = util.DiffLists(src.keys(), dst.keys())

        #print src.keys()
        #print dst.keys()

        self.log("\nremoving: " + str(d), nl='\n')

        for f in d:
            if not pretend:
                oss.rm('-rf', self.destPath + '/' + f)

        self.log("\nadding: " +  str(a))

        for f in a:
            df = oss.normpath(self.destPath + '/' + f)
            sf = oss.normpath(self.srcPath + '/' + f)
            if oss.IsDir(sf):
                if not pretend:
                    util.CallNoException(oss.mkdirs, (df))
            else:
                pth, nm, ext = oss.splitFilename(df)
                if not pretend:
                    oss.mkdirs(pth)
                    oss.cp(sf, df)

        chgd = []
        dm, chk = util.DiffLists(src.keys(), a)

        for f in chk:
            if src[f] != dst[f]:
                df = oss.normpath(self.destPath + '/' + f)
                sf = oss.normpath(self.srcPath + '/' + f)
                chgd.append(f)

                pth, nm, ext = oss.splitFilename(df)
                if not pretend:
                    oss.mkdirs(pth)
                    util.CallNoException(oss.cp, (sf, df))


        self.log("\nchanged: " +  str(chgd), bl='@')
        return self.GetFileInfo(self.destPath)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def UpdateDest(self, dst=None, pretend=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        src = self.GetFileInfo(self.srcPath)

        if not dst:
            dst = self.GetFileInfo(self.destPath)

        d, a = util.DiffLists(src.keys(), dst.keys())

        chgd = []
        dm, chk = util.DiffLists(src.keys(), a)

        for f in chk:
            if src[f] != dst[f]:
                df = oss.normpath(self.destPath + '/' + f)
                sf = oss.normpath(self.srcPath + '/' + f)
                chgd.append(f)

                pth, nm, ext = oss.splitFilename(df)
                if not pretend:
                    oss.mkdirs(pth)
                    util.CallNoException(oss.cp, (sf, df))

        self.log("\nchanged: " +  str(chgd), bl='@')
        return self.GetFileInfo(self.destPath)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        msg = """    src : '%s'
    dest: '%s'
    excludes: %s
    filters : %s
    verbose : %s
""" % (self.srcPath, self.destPath, self.excludes, self.filters, self.verbose)

        self.log(msg, nl='\n')

        try:
            dst = self.SyncDirs()
        except:
            self.log(util.GetTraceback(), nl='\n\n', bl='@')


