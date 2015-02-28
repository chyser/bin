#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.util as util

import pprint
import time
import msvcrt


IGNORE_EXTENSIONS = set(('.part', '.ob!'))

## setup some default directories
if 0 and oss.exists('L:/tests'):
    ROOTDIR = "L:/tests/"
elif oss.exists('K:/tests'):
    ROOTDIR = "K:/tests/"
elif oss.exists('W:/dst1'):
    ROOTDIR = "W:/dst1/"
else:
    ROOTDIR = "C:/home/chrish/tmp1/"

if oss.exists('C:/home/chrish/tmp'):
    SRC_DIR = "C:/home/chrish/tmp"
else:
    SRC_DIR = 'C:/home/test'
DELAY_TIME = 37

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
        opts.dest = ROOTDIR

    if opts.src is None:
        opts.src = SRC_DIR

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
    while 1:
        done = True

        for ef in oss.ls():
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

        if msvcrt.kbhit():
            ch = msvcrt.getch()
            print(ch)

            if ch in ['q', 'Q']:
                break

            if ch == 'x':
                pprint.pprint(xfrc.xfers)

            elif ch == 'p':
                print('pausing')
                while 1:
                    time.sleep(1.5)
                    oss.stdout.write('.')
                    if msvcrt.kbhit():
                        ch = msvcrt.getch()
                        break
                print('\npausing stopped')


        time.sleep(DELAY_TIME)

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
            return 0

        try:
            fs = oss.filesize(srcFileName)
        except WindowsError:
            return 0

        ## ensure file is completed
        if srcFileName not in self.rec:
            self.rec[srcFileName] = fs
            return False

        if self.rec[srcFileName] == fs:

            ## mozzilla
            if oss.exists(srcFileName + '.part'):
                return False

            try:
                oss.mv(srcFileName, destFileName)
                del self.rec[srcFileName]
                self.xfers.append('%s -> %s' % (srcFileName, destFileName))
                return fs
            except:
                oss.rm(destFileName)
                self.bad.add(srcFileName)
        else:
            print("  @@", srcFileName, self.rec[srcFileName], fs)
            self.rec[srcFileName] = fs
        return 0


if __name__ == "__main__":
    main(oss.argv)

