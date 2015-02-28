#!/usr/bin/env python
""" usage: mvmusic [options]

    copies music from current dir hierarchy to C:/music/car. it uses ID3 tags
    to get artist and song title

    options:
        -d | --dup    : copy song over assuming same ID3, but different bits
        -s | --show   : show what would happen, but not copies
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import shutil
import string

import id3


BU_PATH = 'C:/music/car'

class MyException(Exception): pass


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('d', 'dup'), ('s', 'show')], [], __doc__)

    ign = getIgnoreSet()

    print("Cur Dir:", oss.pwd())
    for i in oss.find('.', '*.mp3'):
        ii = id3.ID3(i)
        err = True

        try:
            artist = translate(ii['ARTIST'])

            if artist in ['*', '<<unknown artist>>']:
                print(i, "artist name error: *")
                raise MyException('artist name error')

            if artist in ign:
                continue

            title = translate(ii['TITLE'])

            dir = BU_PATH + '/' + artist
            try:
                if not oss.exists(dir):
                    oss.mkdir(dir)
            except IOError as ex:
                print(i, "IOError: %s" % str(ex))
                raise MyException('artist name error')
            except TypeError as ex:
                print(i, "IOError: %s" % str(ex))
                raise MyException('artist name error')

            fn = dir + '/' + title + '.mp3'
            if not oss.exists(fn):
                print('%s --> %s' % (i, fn))
                if not opts.show:
                    cp(i, fn)
            elif opts.dup and not oss.cmp(i, fn):
                raise MyException('duplicate song')

            err = False

        except KeyError as ex:
            print('%s -- KeyError: %s' % (i, str(ex)))
        except UnicodeDecodeError as ex:
            print('%s -- UnicodeDecodeError: %s' % (i, str(ex)))
        except IOError as ex:
            print('%s -- IOError: %s' % (i, str(ex)))
        except TypeError as ex:
            print('%s -- TypeError: %s' % (i, str(ex)))
        except MyException as ex:
            print('%s -- MyExceptionError: %s' % (i, str(ex)))

        if 0 and err:
            dir = BU_PATH + '/id3_errors'
            f = dir + '/' + oss.basename(i)
            if not oss.exists(f):
                print('error:', i)
                cp(i, f)

    oss.exit(0)


#-------------------------------------------------------------------------------
def translate(s):
#-------------------------------------------------------------------------------
    d = []
    for c in s:
        if c in {',', "'", ';', '!', '`', '?'}:
            pass
        elif c in {'/'}:
            d.append('-')
        elif c in {'(', '['}:
            break
        elif c == '&':
            d.append(' and ')
        else:
            d.append(c)

    v = ''.join(d).strip()

    state = 0; d = []
    for c in v:
        if state == 0:
            if c == ' ':
                state = 1
            d.append(c)
        elif state == 1:
            if c != ' ':
                d.append(c)
                state = 0

    return ''.join(d).strip()


#-------------------------------------------------------------------------------
def cp(src, dest):
#-------------------------------------------------------------------------------
    shutil.copyfile(src, dest)


#-------------------------------------------------------------------------------
def getIgnoreSet():
#-------------------------------------------------------------------------------
    s = set()
    try:
        with open('ignore') as inf:
            for line in inf:
                s.add(line.strip())
    except IOError:
        pass
    return s


if __name__ == "__main__":
    main(oss.argv)
