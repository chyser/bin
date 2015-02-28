#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import time
import shutil

import id3


AMAZON_PATH = r"C:\Documents and Settings\chrish\My Documents\My Music\Amazon MP3"
RIP_PATH = r"C:\Program Files\CDex\my music"
MUSIC_PATH  = "Q:/"
IMPORT_PATH = "I:"
BU_PATH = 'C:/music/'

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: listMusicPlayer.py [options]

    options:
        -s | --sync : sync computer with player
        -l | --list : list the songs
        -v | --verbose : extra info dump
    """
    args, opts = oss.gopt(argv[1:], [('l', 'list'), ('s', 'sync'), ('v', 'verbose')], [], main.__doc__ + __doc__)

    ## get computer songs
    m0, d0 = getSongs(BU_PATH, 1)
    print('Found computer songs from "%s num: %d"' % (BU_PATH, len(m0)))

    if opts.list:
        for i in sorted(m0):
            print(i)
        oss.exit(0)

    ## get music box songs
    print('Searching musicplayer songs from "%s"' % MUSIC_PATH)
    m1, d1 = getSongs(MUSIC_PATH, 1)
    print('Found musicplayer songs from "%s" num: %d' % (MUSIC_PATH, len(m1)))

    ## what needs transfered
    m = m0 - m1

    l = len(m)
    print('Need to copy :', l)

    ## doit
    for i in sorted(m):
        f = d0[i]
        if opts.sync:
            try:
                print(f)
                cp(f, IMPORT_PATH + '\\' + oss.basename(f))
                time.sleep(13)
            except oss.OSScriptsError as ex:
                print('EXCEPTION:\n' + str(ex))
        else:
            print(i)
            if opts.verbose:
                print('   ', d0[i])

    print(l)
    oss.exit(0)



#-------------------------------------------------------------------------------
def cp(src, dest):
#-------------------------------------------------------------------------------
    shutil.copyfile(src, dest)


#-------------------------------------------------------------------------------
def getSongs(path, verbose=None):
#-------------------------------------------------------------------------------
    m = set()
    d = {}

    for i in oss.find(path, '*.mp3'):
        if verbose:
            print('*', end='')

        ii = id3.ID3(i)
        try:
            tag = ii['ARTIST'] + '/' + ii['TITLE']
            m.add(tag)
            d[tag] = i
        except KeyError:
            pass
        except UnicodeDecodeError:
            pass

    if verbose:
        print('\n')
    return m, d


#-------------------------------------------------------------------------------
def backup():
#-------------------------------------------------------------------------------
    for f in oss.find(MUSIC_PATH, '*.mp3'):
        print(f)

        ff = BU_PATH + '\\' + oss.basename(f)
        if not oss.exists(ff):
            print('   ', "copied")
            cp(f, ff)


if __name__ == "__main__":
    main(oss.argv)
