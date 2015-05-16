#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import shutil
import string
import re

import id3


BU_PATH = 'C:/music/car'
AMAZON_PATH = "C:/users/chrish/Music/Amazon MP3"

class MyException(Exception): pass


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('s', 'sync'), ('d', 'dup')], [], main.__doc__ + __doc__)

    path = AMAZON_PATH
    tbl = string.maketrans('/\',', '-  ')

    for i in oss.find(path, '*.mp3'):
        ii = id3.ID3(i)
        try:
            title = chkName(ii['TITLE'])
            artist = chkName(ii['ARTIST'])
            print(artist, '---', title)

            if opts.sync:
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
                    cp(i, fn)
                elif opts.dup and not oss.cmp(i, fn):
                    raise MyException('duplicate song')

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

    oss.exit(0)


#-------------------------------------------------------------------------------
def chkName(s):
#-------------------------------------------------------------------------------
    def f(m):
        a = m.group(0)

        if a == '/': return '-'
        if a in set("',?"): return ''
        if a == "&": return 'and'
        return ''

    return re.sub('/|\'|,|&|!|\?|\(.*|\[.*', f, s)

#-------------------------------------------------------------------------------
def cp(src, dest):
#-------------------------------------------------------------------------------
    shutil.copyfile(src, dest)


#-------------------------------------------------------------------------------
def getIgnoreSet():
#-------------------------------------------------------------------------------
    s = set()
    with open('ignore') as inf:
        for line in inf:
            s.add(line.strip())

    print(s)
    return s


if __name__ == "__main__":
    main(oss.argv)
