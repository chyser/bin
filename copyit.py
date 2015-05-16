#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.util as util

import pprint
import time


DELAY_TIME = 37
IGNORE_EXTENSIONS = set(('.part', '.ob!', '.dap', '.dwn', '.st'))
SRC_DIRS = ["C:/home/chrish/tmp", 'C:/home/test', "C:/home/me/tmp"]
DEST_DIRS = ['E:/tests/', 'L:/tests/', 'S:/tests/', 'W:/dst1/', 'K:/tests/', 'C:/home/chrish/tmp1/']

rec = {}


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: copyit <options>

        options
            -o | --once  : run through loop once and then halt
            -d | --dest  : specify detination directory
            -s | --src   : specifly source directory
    """
    args, opts = oss.gopt(argv[1:], [('o', 'once')], [('d', 'dest'), ('s', 'src')], main.__doc__)

    if opts.dest is None:
        opts.dest = getDir(DEST_DIRS)

    if opts.src is None:
        opts.src = getDir(SRC_DIRS)

    if not oss.exists(opts.dest):
        opts.usage(1, "Destination dir '%s' doesn't exist" % opts.dest)

    if not oss.exists(opts.src):
        opts.usage(1, "Source dir '%s' doesn't exist" % opts.src)

    print("Destination:", opts.dest)
    print("Source:", opts.src)
    oss.cd(opts.src)

    destDirName = opts.dest + ''.join(map(lambda s: "%02d" % s, time.localtime()[:6]))
    print("Making", destDirName)
    oss.mkdir(destDirName)

    xfrc = XferFileClass()

    id = fileCount = idx = 0
    doneMsg = False
    while 1:
        done = True

        files = oss.ls()
        if not files:
            if not doneMsg:
                print('\n--- All files Done ---')
            doneMsg = True
        else:
            doneMsg = False

        for ef in files:
            if oss.isDir(ef):
                continue

            ext = oss.splitext(ef)

            ## mozzilla
            if ext in IGNORE_EXTENSIONS:
                continue

            fn = destDirName + '/%08d' % (id) + ext
            fs = xfrc.xferFile(ef,  fn)

            if fs:
                print('  xfer: %s <-- %s, %d' % (fn, ef, fs))
                fileCount += 1
            else:
                done = False

            id += 1

        if done and opts.once:
            break


        ch = util.delayKey(DELAY_TIME)
        if ch in ['q', 'Q']:
            break

        elif ch == 'x':
            pprint.pprint(xfrc.xfers)

        elif ch == 'p':
            print('pausing')
            while util.delayKey(1000) == None:
                pass
            print('\npausing stopped')

        idx += 1

        if idx > 30:
            idx = 0
            xfrc.bad = set()

    if fileCount == 0:
        print("Removing unused directory '%s'" % destDirName)
        oss.rmdir(destDirName)
    else:
        print("Copied %d files" % fileCount)

    print('Bad Files:', xfrc.bad)


#-------------------------------------------------------------------------------
def getDir(dl):
#-------------------------------------------------------------------------------
    for d in dl:
        print("trying:", d)
        if oss.exists(d):
            return d


class CopyException(Exception): pass

#-------------------------------------------------------------------------------
class XferFileClass(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XferFileClass, self).__init__()
        self.rec = {}
        self.bad = set()
        self.xfers = util.LimitedCircularBuffer(50)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xferFile(self, srcFileName, destFileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if srcFileName in self.bad:
            return

        try:
            fs = oss.filesize(srcFileName)
        except WindowsError:
            return

        ## ensure file is completed
        if srcFileName not in self.rec:
            self.rec[srcFileName] = fs
            return

        if self.rec[srcFileName] == fs:
            try:
                oss.mv(srcFileName, destFileName)
                if not oss.exists(destFileName):
                    raise CopyException("bad copy")

                del self.rec[srcFileName]
                self.xfers.append('%s -> %s' % (srcFileName, destFileName))
                return fs
            except:
                oss.rm(destFileName)
                self.bad.add(srcFileName)
        else:
            print("  @@", srcFileName, self.rec[srcFileName], fs)
            self.rec[srcFileName] = fs

        return


if __name__ == "__main__":
    main(oss.argv)

