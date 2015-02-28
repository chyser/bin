#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import time
import shutil
import zipfile

import pylib.osscripts as oss

try:
    ## external library
    import UnRAR
except ImportError:
    print("UnRAR library unavailable. No RAR support", file=oss.stderr)

try:
    ## included since python 2.3
    import gzip
    import tarfile
    import bz2
except ImportError:
    print("gzip, bzip2 and tar libraries are unavailable", file=oss.stderr)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: zippy.py

        zippy can create and extract from various archive formats. Format can
        normally be deduced from file extensions for extraction, but must be
        specified for creation.

            -c | --create  <archive>  : create a new archive
            -a | --append  <archive>  : append files to archive

            // create/extract archive formats
            -z | --zip                : archive is a zip file
            -g | --gzip               : archive is a gzip
            -t | --tgz                : archive is a gzipped tar file

            // extract only archive formats
            -r | --rar                : archive is an rar file

            -p | --path               : extraction path for relative file names
            -l | --list               : list contents of archive
            -v | --verbose            : verbose actions
    """

    args, opt = oss.gopt(argv[1:], [('z', 'zip'), ('g', 'gzip'), ('l', 'list'), ('t', 'tgz'), ('r', 'rar'),
        ('v', 'verbose')], [('a', 'append'), ('c', 'create'), ('p', 'path')], main.__doc__)

    if opt.path is None:
        opt.path = '.'

    ## create or add to an archive
    if opt.create or opt.append:
        archive = opt.create if opt.create else opt.append

        archtype = getType(opt, archive)
        aa = _Archives[archtype](archive, archtype, verbose=opt.verbose)
        aa.Create(args, opt.append)
        return

    ## explode some archives
    for archive in args:
        archtype = getType(opt, archive)

        aa = _Archives[archtype](archive, archtype, opt.path, opt.verbose)
        if opt.list:
            aa.List()
            continue

        aa.Extract()

    oss.exit(0)


class ZippyException(Exception): pass


#-------------------------------------------------------------------------------
class Archive(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, archtype, path='.', verbose = True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Archive, self).__init__()
        self.name = name
        if path is None:
            path = '.'
        self.path = path
        self.verbose = verbose
        self.archtype = archtype

        if verbose:
            self.vp = sys.__stdout__.write
        else:
            self.vp = self._nop_print

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _nop_print(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cd(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print(self.path)
        oss.mkdirs(self.path)
        oss.cd(self.path)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, file_lst, doAppend = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise ZippyException('Create not implemented')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Append(self, files):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise ZippyException('Append not implemented')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def List(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise ZippyException('Extract not implemented')


#-------------------------------------------------------------------------------
class ZipArchive(Archive):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, at, path=".", verbose=True, typ=zipfile.ZIP_DEFLATED):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ZipArchive, self).__init__(name, path, verbose)
        self.typ = typ

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, files, doAppend=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if doAppend:
            attr = 'a'
            self.vp("Appending: " + self.name +'\n')
        else:
            attr = 'w'
            self.vp("Creating: " + self.name + '\n')

        zf = zipfile.ZipFile(self.name, attr)
        allfiles = list(files)
        for fname in files:
            if oss.IsDir(fname):
                allfiles.extend(oss.find(fname))

        for fname in allfiles:
            if oss.IsDir(fname):
                continue
            zf.write(fname)
        zf.close()
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _openExisting(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        zf = zipfile.ZipFile(self.name, 'r', self.typ)

        if zf.testzip() is not None:
            raise ZippyException("Bad Archive: " + self.name)
        return zf

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Append(self, files):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._openExisting().close()
        return self.Create(files, doAppend=True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def List(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        zf = self._openExisting()

        for zi in zf.infolist():
            l = list(zi.date_time);  l.extend([0,0,0])
            print("%-39s" % zi.filename, time.asctime(l), "  %d/%d" % (zi.compress_size, zi.file_size))

        zf.close()
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        zf = self._openExisting()

        self.cd()
        for fname in zf.namelist():
            self.vp('    ' + fname)

            ## make directory(s)
            oss.mkdirs(oss.getpath(fname))
            if fname[-1] == '/': continue

            otf = file(fname, 'wb')
            otf.write(zf.read(fname))
            otf.close()

        zf.close()
        return True


#-------------------------------------------------------------------------------
class TarArchive(Archive):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, files, doAppend=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        attr = 'w:gz' if self.archtype == 'tgz' else 'w:bz2'
        tf = tarfile.open(self.name, attr)

        for fl in files:
            self.vp("   adding: " + fl +'\n')
            tf.add(fl)
        self.vp('\n')
        tf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def List(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tf = tarfile.open(self.name, "r")
        tf.list()
        tf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cd()
        tf = tarfile.open(self.name, "r")
        tf.extractall(self.path)
        tf.close()
        return True


#-------------------------------------------------------------------------------
class GZipArchive(Archive):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, files, doAppend=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        p, fname, ext = oss.splitFilename(self.name)
        otf = gzip.GzipFile(self.name, 'wb')

        with open(fname, "rb") as inf:
            shutil.copyfileobj(inf, otf)
            otf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def List(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        p, fname, ext = oss.splitFilename(self.name)
        print(fname)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cd()
        p, fname, ext = oss.splitFilename(self.name)
        inf = gzip.GzipFile(self.name, 'rb')
        with open(fname, 'wb') as otf:
            shutil.copyfileobj(inf, otf)
        inf.close()
        return fname


#-------------------------------------------------------------------------------
class BZip2Archive(Archive):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, files, doAppend=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        p, fname, ext = oss.splitFilename(self.name)
        otf = bz2.BZ2File(self.name, 'w')
        inf = file(fname, "rb")
        shutil.copyfileobj(inf, otf)
        otf.close();  inf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cd()
        p, fname, ext = oss.splitFilename(self.name)
        inf = bz2.BZ2File(self.name, 'rb')
        otf = file(fname, 'wb')
        shutil.copyfileobj(inf, otf)
        otf.close();  inf.close()
        return fname


#-------------------------------------------------------------------------------
class RARArchive(Archive):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def List(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for fileInArchive in UnRAR.Archive(self.name).iterfiles():
            print(fileInArchive.filename, fileInArchive.size)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Extract(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cd()
        UnRAR.Archive(self.name).extract()
        return True


#-------------------------------------------------------------------------------
def getType(opt, archive, args=None):
#-------------------------------------------------------------------------------
    """ determines the type of archive
    """

    ext = oss.splitext(archive)

    if opt.zip or ext == '.zip':
        archtype = 'zip'
    elif opt.tgz or ext == '.tgz' or archive.endswith('.tar.gz'):
        archtype = 'tgz'
    elif archive.endswith('.tar.bz2'):
        archtype = 'tbz'
    else:
        if args and (len(args) > 1 or oss.IsDir(args[0])):
            if opt.gzip or ext == '.gz':
                archtype = 'tgz'
            elif opt.bzip or ext == '.bz2':
                archtype = 'tbz'
            else:
                return
        else:
            if opt.gzip or ext == '.gz':
                archtype = 'gz'
            elif opt.bzip or ext == '.bz2':
                archtype = 'bz'
            else:
                return

    return archtype


_Archives = {
    'zip' : ZipArchive,
    'gz'  : GZipArchive,
    'bz'  : BZip2Archive,
    'tgz' : TarArchive,
    'tbz' : TarArchive,
    'rar' : RARArchive,
}


if __name__ == "__main__":
    main(oss.argv)
