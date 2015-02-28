#!/usr/bin/env python
"""
FileObject:

    - represents a local or remote file object

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import osscripts as oss

#-------------------------------------------------------------------------------
def FileObjectFactory(FileName, uri=None):
#-------------------------------------------------------------------------------
    if uri is None or uri.startswith('file:'):
        return LocalFileObject(FileName, uri)

    if uri.startswith('scp:'):
        return SCPFileObject(FileName, uri)


#-------------------------------------------------------------------------------
class FileObject(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName, uri=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.FileName = FileName
        self.uri = uri

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Remove(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ removes the file object
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Uncache(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ removes any local cache of the file
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the contents of the file

        @rtype: string
        @return: buffer with file contents
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self, buf, fullSave=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ saves the buffer into the file. if fullSave is False, the save may
        be a hint or a cache update

        @type  buf: string
        @param buf: buffer to write to file and save
        @type  fullSave: boolean
        @param fullSave: cache update hint versus full save to store
        """
        pass

#-------------------------------------------------------------------------------
class LocalFileObject(FileObject):
#-------------------------------------------------------------------------------
    """ file accessible through the file system
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName, fdb = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        FileObject.__init__(self, FileName, fdb)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Remove(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        oss.rm(self.FileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("load", self.FileName)
        inf = file(self.FileName)
        buf = inf.read()
        inf.close()
        return buf

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self, buf, fullSave=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        otf = file(self.FileName, 'w')
        try:
            otf.write(buf)
        except UnicodeEncodeError:
            otf.write(buf.encode('utf_8'))
        otf.close()


#-------------------------------------------------------------------------------
class SCPFileObject(LocalFileObject):
#-------------------------------------------------------------------------------
    """ file accessible through scp/ssh
    """

    uid = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName, uri):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        LocalFileObject.__init__(self, "C:/tmp/scp_%d_%s" % (SCPFileObject.uid, FileName), uri)
        SCPFileObject.uid += 1

        ## example scp URI ->  scp:root@compflu-01.hpl.hp.com:/tmp/cool
        self.rmtfile = self.uri[4:]
        self.realFileName = FileName

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Uncache(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        LocalFileObject.Remove(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("pscp " + self.rmtfile + " " + self.FileName)
        oss.r("pscp " + self.rmtfile + " " + self.FileName)
        return LocalFileObject.Load(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self, buf, fullSave=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        LocalFileObject.Save(self, buf)
        if fullSave:
            print("pscp " + self.FileName + " " + self.rmtfile)
            oss.r("pscp " + self.FileName + " " + self.rmtfile)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import time

    def usage(rc, errmsg=""):
        print__doc__, file=oss.stderr
        if errmsg:
            print("""
Error:
""" + str(errmsg), file=oss.stderr)
        oss.exit(rc)

    args, opts = oss.gopt(oss.argv[1:], [], [], usage)

    fo = FileObjectFactory("test1.txt", "scp:root@compflu-01.hpl.hp.com:/tmp/test1.txt")

    print(fo.Load())

    fo.Save("new contents: " + time.ctime())

    fo.Uncache()

    print(fo.Load())


    oss.exit(0)


