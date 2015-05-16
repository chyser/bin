#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import pylib.osscripts as oss

import re
import sys
import time
import os.path
import logging
import datetime
import traceback
import threading

try:
    import msvcrt
except ImportError:
    pass

#-------------------------------------------------------------------------------
def delayKey(delaySecs=0):
#-------------------------------------------------------------------------------
    xt = time.time() + delaySecs
    while 1:
        if msvcrt.kbhit():
            return msvcrt.getch()

        tm = time.time()
        v = xt - tm
        if v <= 0:
            return

        time.sleep(min(0.31456, v))


#-------------------------------------------------------------------------------
class TimeElapsed(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.ct = time.time()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self, valSecs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tm = time.time()
        if tm > self.ct + valSecs:
            self.ct = tm
            return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def poll(self, valSecs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return time.time() > self.ct + valSecs

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ct = time.time()


#-------------------------------------------------------------------------------
def UTC(secs=None):
#-------------------------------------------------------------------------------
    """ return standard ISO string for UTC from 'secs' seconds. If 'secs' is None
        use time.gmtime()
    """
    return time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(secs))


#-------------------------------------------------------------------------------
def UTC_YAML(secs=None, secFmt=False):
#-------------------------------------------------------------------------------
    """ return YAML friendly string for UTC from 'secs' seconds. If 'secs' is None
        use time.gmtime(). 'secFmt' indicates whether seconds should be included
    """
    s = '%S' if secFmt else ''
    return time.strftime("%Y%m%d_%H%M{0}Z".format(s), time.gmtime(secs))


#-------------------------------------------------------------------------------
def utcYaml2DateTime(tm):
#-------------------------------------------------------------------------------
    """ return a datetime.datetime() object repsenting the 'yaml_friendly' string
        'tm'.
    """
    fmt = '%Y%m%d_%H%M%S' if len(tm) == 16 else '%Y%m%d_%H%M'
    return datetime.datetime.strptime(tm[:-1], fmt)


#-------------------------------------------------------------------------------
def dateTime2UtcYaml(dt, secFmt=False):
#-------------------------------------------------------------------------------
    s = '%S' if secFmt else ''
    return dt.strftime("%Y%m%d_%H%M{0}Z".format(s))


#-------------------------------------------------------------------------------
def yaml2DateTime(tm):
#-------------------------------------------------------------------------------
    fmt = '%Y%m%d_%H%M%S' if len(tm) == 15 else '%Y%m%d_%H%M'
    return datetime.datetime.strptime(tm, fmt)


#-------------------------------------------------------------------------------
def dateTime2Yaml(dt, secFmt=False):
#-------------------------------------------------------------------------------
    s = '%S' if secFmt else ''
    return dt.strftime("%Y%m%d_%H%M{0}".format(s))


#-------------------------------------------------------------------------------
def localUtcTimedelta():
#-------------------------------------------------------------------------------
    return datetime.datetime.utcnow() - datetime.datetime.now()


#-------------------------------------------------------------------------------
class UTCFormatter(logging.Formatter):
#-------------------------------------------------------------------------------
    """ UTC time formatter for logging standard module
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def formatTime(self, rec, df=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return UTC(rec.created)


#-------------------------------------------------------------------------------
def getExcelColumns():
#-------------------------------------------------------------------------------
    """ yields a generator for Excel spreadsheet column headings
    """
    for i in range(ord('A'), ord('Z')+1):
        yield chr(i)

    for i in range(ord('A'), ord('Z')+1):
        for j in range(ord('A'), ord('Z')+1):
            yield chr(i) + chr(j)


#-------------------------------------------------------------------------------
def getKeyWordArg(kwds, arg):
#-------------------------------------------------------------------------------
    val = kwds.get(arg, None)
    try:
        del kwds[arg]
    except KeyError:
        pass
    return val


#-------------------------------------------------------------------------------
def leadingSpaces(line, tabCnt=8):
#-------------------------------------------------------------------------------
    """ remove the leading spaces from a line returning the number of spaces
        and the lstrip()ed line with tabs replaced
    """
    line = re.sub('\t', ' '*tabCnt, line)
    a = len(line)
    line = line.lstrip()
    b = len(line)
    return a - b, line.rstrip()


#-------------------------------------------------------------------------------
class ignoreException(object):
#-------------------------------------------------------------------------------
    """ context 'with (ignoreException(exceptions):' that ignores exceptions
        passed as arguments
    """
    def __init__(self, *exceptions):
        object.__init__(self)
        self.exceptions = None if len(exceptions) == 0 else set(exceptions)

    def __enter__(self):
        pass

    def __exit__(self, type, val, tb):
        if self.exceptions is None:
            return True
        return type in self.exceptions


#-------------------------------------------------------------------------------
def safe_unicode(obj, *args):
#-------------------------------------------------------------------------------
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)


#-------------------------------------------------------------------------------
def mkBackups(fileName, num=1):
#-------------------------------------------------------------------------------
    """ keep backup files
    """
    dir, fn = os.path.split(fileName)
    if not dir:
        dir = '.'

    bdir = dir + '/bak'
    oss.mkdir(bdir)
    bdf = bdir + '/' + fn

    for i in range(num, 1, -1):
        ef = bdf + '.bk%d' % (i - 1)
        if os.path.exists(ef):
            oss.cp(ef, bdf + '.bk%d' % i)

    if num > 2:
        ef = bdf + '.bak'
        if os.path.exists(ef):
            oss.cp(ef, bdf + '.bk1')

    if os.path.exists(fileName):
        oss.cp(fileName, bdf + '.bak')


#-------------------------------------------------------------------------------
class ErrRet(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.val = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.val = val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.val)


#-------------------------------------------------------------------------------
class SafeFile(object):
#-------------------------------------------------------------------------------
    """ allows writes to a file such that any error does not alter the file
    """
    TMPPATH = '/tmp/'
    TMPEXT = '.tmp'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName, seed=None, text=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.fileName = fileName
        self.tmpName = TMPPATH + seed + TMPEXT if seed else TMPPATH + fileName + TMPEXT
        self.text = text
        self.outf = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def fn(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.tmpName

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def open(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.outf = open(self.tmpName, 'w')
        return self.outf

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.outf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def doCopy(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.close()
        if not oss.cmp(self.tmpName, self.fileName):
            if self.text:
                if '{0}' in text:
                    text = text.format(self.fileName)
                print(text)
            oss.cp(self.tmpName, self.fileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __enter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.open()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __exit__(self, typ, value, traceback):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.close()
        if type is None:
            self.doCopy()


#-------------------------------------------------------------------------------
def cvtU2A(s, errHandling='ignore'):
#-------------------------------------------------------------------------------
    """ convert unicode 's' to ascii
    """
    return s.encode('ascii', errHandling)


#-------------------------------------------------------------------------------
def wait(tm, secs):
#-------------------------------------------------------------------------------
    """ wait for 'secs' after time 'tm'. if 'tm' has already passed, return
        after a thread switching opportunity. return the current time
    """
    t = time.time()
    if t < tm + secs:
        time.sleep(tm + secs - t)
    else:
        time.sleep(0.001)
    return time.time()


#-------------------------------------------------------------------------------
def Num2Str(num):
#-------------------------------------------------------------------------------
    """ add 'th', 'st', 'cd', or 'rd' to a number when converting to a string
    """
    t, o = divmod(num, 10)
    if o > 3 or t % 10 == 1:
        return '%dth' % num
    return '%d%s' % (num, ['th', 'st', 'cd', 'rd'][o])


#-------------------------------------------------------------------------------
def mkProperty(c):
#-------------------------------------------------------------------------------
    """ this is meant to be a decorator for nested properties
    """
    return property(**c())


#-------------------------------------------------------------------------------
def CvtGigMegKBytes(num, fmt="1.3"):
#-------------------------------------------------------------------------------
    """ convert a number 'num' to kilobytes, megabytes, gigabytes or terrabytes
        depending on the size. Use format 'fmt' default: "1.3f"
    """
    sfmt = "%" + fmt + "f%s"
    for i in range(5):
        nn = num / 1024.0
        if nn < 1.0:
            return sfmt % (num, [' ', 'K', 'M', 'G', 'T'][i])
        num = nn

#
# list manipulation routines
#

#-------------------------------------------------------------------------------
def list_str(lst, func=None):
#-------------------------------------------------------------------------------
    """ convert a list of items to a decorative string using either str() or
        'func' if specified
    """
    if not isinstance(lst, list):
        return str(lst)

    s = []
    if func is None: func = list_str
    for l in lst:
        s.append(func(l))
    return '[' + ', '.join(s) + ']'


#-------------------------------------------------------------------------------
def dict_str(dct, func=None):
#-------------------------------------------------------------------------------
    """ convert a dictionary of items to a decorative string using either str() or
        'func' if specified
    """

    s = []
    if func is None: func = str
    for k, v in dct.items():
        s.append("'%s':" % k)
        s.append(func(v))
    return '{' + ', '.join(s) + '}'


#-------------------------------------------------------------------------------
def isListInList(a, b):
#-------------------------------------------------------------------------------
    """ is list 'a' a proper subset of list 'b'. return a boolean
    """

    for i in a:
        if i not in b:
            return False
    return True


#-------------------------------------------------------------------------------
def RmListFromList(a, b):
#-------------------------------------------------------------------------------
    """ removes list a from list b, returning the result
    """

    _b = []
    for i in b:
        if i not in a:
            _b.append(i)
    return _b


#-------------------------------------------------------------------------------
class Dlist(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.nvl = {}
        for i in lst:
            self.nvl[i] = i

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __sub__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        r = self.nvl.copy()
        for k in a.nvl.keys():
            if k in r: del r[k]
        return r.values()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def intersection(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        h = self.nvl.keys()
        r = []
        for k in a.nvl.keys():
            if k in h: r.append(k)
        return r

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def union(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        r = self.nvl.copy()
        r.update(a)
        return r.keys()


#-------------------------------------------------------------------------------
def DiffLists(a, b):
#-------------------------------------------------------------------------------
    """ return:
         list of items in b, not in a
         list of items in a, not in b
    """
    return [i for i in b if i not in a], [i for i in a if i not in b]


#-------------------------------------------------------------------------------
def DiffLists2(a, b):
#-------------------------------------------------------------------------------
    return RmListFromList(a, b), RmListFromList(b, a)


#-------------------------------------------------------------------------------
def DiffLists1(a, b):
#-------------------------------------------------------------------------------
    db = []
    da = []

    for i in a:
        if i not in b:
            da.append(i)
    for i in b:
        if i not in a:
            db.append(i)
    return db, da


#-------------------------------------------------------------------------------
def IntersectLists(a, b):
#-------------------------------------------------------------------------------
    da = Dlist(a)
    db = Dlist(b)
    return da.intersection(db)


#-------------------------------------------------------------------------------
def UnionLists(a, b):
#-------------------------------------------------------------------------------
    da = Dlist(a)
    db = Dlist(b)
    return da.union(db)


#-------------------------------------------------------------------------------
def DiffIntersectLists(a, b):
#-------------------------------------------------------------------------------
    """ returns a tuple of
           - what is in b not in a
           - what is in a not in b
           - what is in both
    """
    da = Dlist(a)
    db = Dlist(b)
    return db - da, da - db, da.intersection(db)


#-------------------------------------------------------------------------------
def permutations(n):
#-------------------------------------------------------------------------------
    s = set()
    for a in range(n):
        for b in range(a+1, n):
            if a < b:
                s.add((a, b))
            elif b < a:
                s.add((b, a))

    return sorted(list(s))


#-------------------------------------------------------------------------------
class PrintOnce(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, supress=False, indent=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.done = False
        self.indent = indent
        self.do = not supress

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self, setSupress=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.done = False
        if setSupress is not None:
            self.do = not setSupress

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printOnce(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.do and not self.done:
            self.done = True
            if args:
                print('    '*self.indent, end='')
            print(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def print(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.do:
            if args:
                print('    '*self.indent, end='')
            print(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def didPrint(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.do and self.done:
            if args:
                print('    '*self.indent, end='')
            print(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def didntPrint(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.do and not self.done:
            if args:
                print('    '*self.indent, end='')
            print(*args)


#-------------------------------------------------------------------------------
class LimitedCircularBuffer(list):
#-------------------------------------------------------------------------------
    """ a list composed of a circular buffer such that appending and extending
        do not increase the size beyond a specified size
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, size, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(LimitedCircularBuffer, self).__init__(*args)
        self._size = size

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def append(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self) >= self._size:
            self.pop(0)
        super(LimitedCircularBuffer, self).append(v)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def extend(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in v:
            self.append(i)


#-------------------------------------------------------------------------------
class LargeIndexLimitedBuffer(LimitedCircularBuffer):
#-------------------------------------------------------------------------------
    """ like a list w.r.t to indexing except limited to a specified size. indexes
        outside the current range are ignored
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, size, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(LargeIndexLimitedBuffer, self).__init__(size, *args)
        self.idx = len(args)
        self.min = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx -= self.min
        if idx < 0: idx = 0
        return super(LargeIndexLimitedBuffer, self).__getitem__(idx)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, idx, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx -= self.min
        if idx < 0: return
        return super(LargeIndexLimitedBuffer, self).__setitem__(idx, v)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getslice__(self, i, j):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        i -= self.min
        if i < 0: i = 0
        j -= self.min
        if j < 0: j = 0

        return super(LargeIndexLimitedBuffer, self).__getslice__(i, j)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setslice__(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise Exception('not implemented')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def append(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(LargeIndexLimitedBuffer, self).append(v)
        self.idx += 1
        if len(self) > self._size:
            self.min += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getLastIdx(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return the last current index
        """

        return self.idx

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def extend(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in v:
            self.append(i)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def values(self, last_idx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a tuple of index and values
        """
        idx = self.idx
        return idx, self[last_idx:idx]


#-------------------------------------------------------------------------------
class MultiKeyDict(dict):
#-------------------------------------------------------------------------------
    """ a dictionary that allows key/item to be added multiple times. If a key
        already exists, its value is converted to a list and subsequent insertions
        are appended.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, value):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if key not in self:
            dict.__setitem__(self, key, [value])
        else:
            ary = self[key]
            ary.append(value)
            dict.__setitem__(self, key, ary)


#-------------------------------------------------------------------------------
class DictList(dict):
#-------------------------------------------------------------------------------
    """ an ordered dictionary
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dict.__init__(self, *args, **kwds)
        self.lst = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self._next()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, value):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if key not in self:
            self.lst.append(key)
        dict.__setitem__(self, key, value)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _next(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for k in self.lst:
            yield k

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.lst

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def items(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [(l, self[l]) for l in self.lst]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def values(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [self[l] for l in self.lst]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _p__reconcile(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        keys = set(dict.keys(self))
        l = []
        for v in self.lst:
            if v in keys and v not in l:
                l.append(v)
        self.lst = l


OrderedDict = DictList

#-------------------------------------------------------------------------------
class OrderedMultiKeyDict(dict):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dict.__init__(self)
        self.lst = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self._next()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, value):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if key not in self:
            self.lst.append(key)
            dict.__setitem__(self, key, [value])
        else:
            ary = self[key]
            ary.append(value)
            dict.__setitem__(self, key, ary)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _next(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for k in self.lst:
            yield k

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.lst

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def items(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [(l, self[l]) for l in self.lst]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def values(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [self[l] for l in self.lst]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _p__reconcile(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        keys = set(dict.keys(self))
        l = []
        for v in self.lst:
            if v in keys and v not in l:
                l.append(v)
        self.lst = l

import math
#-------------------------------------------------------------------------------
def log2(num):
#-------------------------------------------------------------------------------
    """ return log2 of 'num'
    """
    return math.log(num)/math.log(2)


#-------------------------------------------------------------------------------
def logN(num, N):
#-------------------------------------------------------------------------------
    """ return log 'N' of 'num'
    """
    return math.log(num)/math.log(N)


#-------------------------------------------------------------------------------
def GetTraceback():
#-------------------------------------------------------------------------------
    """ wrapper to get a trace back
    """
    type, value, tb = sys.exc_info()
    return ''.join(traceback.format_exception(type, value, tb, None))


#-------------------------------------------------------------------------------
def GetTracebackInfo():
#-------------------------------------------------------------------------------
    """ get a traceback at the point this function is called w/o disruption
    """
    class GetTracebackInfoException: pass
    try:
        raise GetTracebackInfoException
    except GetTracebackInfoException:
        return GetTraceback()


#-------------------------------------------------------------------------------
def CvtNewLines(buf, nl="\n"):
#-------------------------------------------------------------------------------
    """ converts new lines in a string to the 'nl' specified. Particularly
        useful if python has escaped the '\' in an input string
    """
    return re.sub(r"\r?\n|\\n|\\r\\n", nl, buf)


#-------------------------------------------------------------------------------
def StrFmtArgs(args):
#-------------------------------------------------------------------------------
    """ generate a string of all of the arguments
    """
    return " ".join([str(arg) for arg in args])


#-------------------------------------------------------------------------------
def CallNoException(func, args=None, *exceptions):
#-------------------------------------------------------------------------------
    """ a wrapper that surpresses any exception
    """
    if args is None:
        args = tuple()

    with ignoreException(*exceptions):
        return func(*args)


#-------------------------------------------------------------------------------
class HierDecomp(object):
#-------------------------------------------------------------------------------
    """ hiearchically decompose a python object
    """
    USE_DICT = 1
    EXCLUDED_TYPES = ['instancemethod', 'builtin_function_or_method', 'module', 'function', 'type', 'classobj']
    EXCLUDED_VARS = ['__doc__']

    DEFAULT_PREFIX = "%(ident)s%(typ)s %(tag)s#%(id)s {"
    DEFAULT_SUFFIX = "%(ident)s}"

    #---------------------------------------------------------------------------
    class HierDecompException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, flags = 0, fmtDict = {}, Excludes = None, actionDict = {}):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(HierDecomp, self).__init__()

        self.fmtDict = fmtDict
        self.ident = self.fmtDict.get('ident', '    ')

        if Excludes is None:
            self.Excludes = []
        else:
            self.Excludes = Excludes


        self.simpleMeth = {
            'NoneType' : self._simple,
            'int'      : self._simple,
            'long'     : self._simple,
            'float'    : self._simple,
            'complex'  : self._simple,
            'bool'     : self._simple,
            'str'      : self._simple,
            'unicode'  : self._simple,
            }

        if flags & HierDecomp.USE_DICT:
            obj = self._obj2
        else:
            obj = self._obj1

        self.meth = {
            'list'     : self._list_tup,
            'tuple'    : self._list_tup,
            'dict'     : self._dict,

            'obj'      : obj,
            'ref'      : self._ref
            }

        self.meth.update(self.simpleMeth)
        self.meth.update(actionDict)
        self.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa = []
        self.visited = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def typeDispatch(self, obj, tag, val, ident):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print self.sa

        typ = type(obj).__name__

        if typ in HierDecomp.EXCLUDED_TYPES:
            return

        if tag in HierDecomp.EXCLUDED_VARS:
            return

        if (typ, tag) in self.Excludes:
            return

        ii = id(obj)

        if ii in self.visited and typ not in self.simpleMeth:
            meth = self.meth['ref']
            ref = self.visited[ii]
        else:
            ref = ''
            self.visited[ii] = '%s:%s' % (typ, tag)
            if typ in self.meth:
                meth = self.meth[typ]
            else:
                meth = self.meth['obj']

        self.valDict = {'ident':(self.ident*ident), 'id': ii, 'typ':typ, 'tag':tag, 'val':str(val), 'ref':ref}
        return meth(typ, tag, val, ident, self.valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _simple(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ in ['str', 'unicode']:
            fmt = self.fmtDict.get(typ, ("%(ident)s%(typ)s %(tag)s = \"%(val)s\""))
        else:
            fmt = self.fmtDict.get(typ, ("%(ident)s%(typ)s %(tag)s = %(val)s"))
        self.sa.append(fmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _ref(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fmt = self.fmtDict.get(typ, (("%(ident)s%(typ)s %(tag)s -> %(ref)s#%(id)s")))
        self.sa.append(fmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _list_tup(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        prefixFmt, suffixFmt = self.fmtDict.get(typ, (HierDecomp.DEFAULT_PREFIX, HierDecomp.DEFAULT_SUFFIX))
        self.sa.append(prefixFmt % valDict)
        for idx, itm in enumerate(val):
            self.typeDispatch(itm, '%s[%i]' % (tag, idx), itm, ident+1)
        self.sa.append(suffixFmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _dict(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        prefixFmt, suffixFmt = self.fmtDict.get(typ, (HierDecomp.DEFAULT_PREFIX, HierDecomp.DEFAULT_SUFFIX))
        self.sa.append(prefixFmt % valDict)
        for k,v in val.items():
            self.typeDispatch(v, k, v, ident+1)
        self.sa.append(suffixFmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _obj1(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        prefixFmt, suffixFmt = self.fmtDict.get(typ, (HierDecomp.DEFAULT_PREFIX, HierDecomp.DEFAULT_SUFFIX))
        self.sa.append(prefixFmt % valDict)

        _cls = getattr(val, '__class__', None)
        cls = (_cls and dir(_cls)) or []

        for attr in dir(val):
            if attr not in cls:
                v = getattr(val, attr)
                self.typeDispatch(v, attr, v, ident+1)

        self._obj0(typ, tag, val, ident, valDict)
        self.sa.append(suffixFmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _obj2(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        prefixFmt, suffixFmt = self.fmtDict.get(typ, (HierDecomp.DEFAULT_PREFIX, HierDecomp.DEFAULT_SUFFIX))
        self.sa.append(prefixFmt % valDict)

        for attr in getattr(val, '__dict__', []):
            v = getattr(val, attr)
            self.typeDispatch(v, attr, v, ident+1)

        self._obj0(typ, tag, val, ident, valDict)
        self.sa.append(suffixFmt % valDict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _obj0(self, typ, tag, val, ident, valDict):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(val, list):
            for idx,itm in enumerate(val):
                self.typeDispatch(itm, '%s[%i]' % (tag, idx), itm, ident+1)
        elif isinstance(val, dict):
            for k,v in val.items():
                self.typeDispatch(v, k, v, ident+1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decompose(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa = []
        self.typeDispatch(val, tag, val, ident)
        return '\n'.join(self.sa)


#-------------------------------------------------------------------------------
class KeyRefDict(dict):
#-------------------------------------------------------------------------------
    """ a dictionary such that 'keys' can be retrieved by specifiying the value
        in 'getkey(self, val)'.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dict.__init__(self)
        self._val = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __contains__(self, kv):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return dict.__contains__(self, kv) or kv in self._val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getkey(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self._val[val]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._val[val] = key
        dict.__setitem__(self, key, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __delitem__(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = self[key]
        del self[key]
        del self._val[v]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def has_key(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.__contains__(key)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.clear()
        self._val.clear()


#-------------------------------------------------------------------------------
class DictCache(dict):
#-------------------------------------------------------------------------------
    """ A dictionary used as a cache
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, size, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dict.__init__(self, *args, **kwds)
        self.size = size
        self.keyary = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, k, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self.keyary) >= self.size:
            key = self.keyary.pop(0)
            try:
                del self[key]
            except KeyError as ex:
                ## TODO[20110628_125313]: trying to track down how the key may not be in the dict
                print(ex)
                print(key)
                print(self.keyary)

        self.keyary.append(k)
        dict.__setitem__(self, k, v)


#-------------------------------------------------------------------------------
def updateObjWDict(obj, dct):
#-------------------------------------------------------------------------------
    for k, v in dct.items():
        if k in obj.__dict__:
            obj.__dict__[k] = v
        else:
            pass
            assert False, 'illegal field: ' + k


#-------------------------------------------------------------------------------
def startDaemonThread(func, *args):
#-------------------------------------------------------------------------------
    t = threading.Thread(target=func, args=args)
    t.daemon = True
    t.start()
    return t


#-------------------------------------------------------------------------------
class sstruct(object):
#-------------------------------------------------------------------------------
    """ acts as a simple struct such that defined fields are remembered.
        constructor takes keyword arguemts where each keyword is a field in the
        struct.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(sstruct, self).__init__()
        self.__dict__["_u___dict"] = {}
        self._u___dict.update(kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add additional fields as keywords
        """
        self._u___dict.update(kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        updateObjWDict(self, kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def asDict(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return struct as a dictionary
        """
        return self._u___dict

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self._u___dict)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setattr__(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._u___dict[attr] = val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if attr.startswith('_u___'):
            return self.__dict__[attr]

        if attr in self.__dict__["_u___dict"]:
            return self.__dict__["_u___dict"][attr]
        raise AttributeError, attr


#-------------------------------------------------------------------------------
class SimpleDate(object):
#-------------------------------------------------------------------------------
    MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, month, year):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.year = year

        if month in self.MONTHS:
            self.month = self.MONTHS.index(month)
        else:
            self.month = month

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextMonth(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        m = self.month + 1
        y = self.year
        if m >= 12:
            y += 1
            m = 0

        return SimpleDate(m, y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prevMonth(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        m = self.month - 1
        y = self.year
        if m < 0:
            y -= 1
            m = 11

        return SimpleDate(m, y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isMonth(self, month):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.MONTHS.index(month) == self.month

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "%s %d" % (self.MONTHS[self.month], self.year)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    import timeit as ti
    print("util self test run")

    a = [1, 2, 3, 4, 5, 6, 7]
    b = [9, 8, 1, 2, 3]

    print(DiffLists(a, b))
    print(DiffLists1(a, b))
    print(DiffLists2(a, b))

    t = ti.Timer("DiffLists([1, 2, 3, 4, 5, 6, 7], [9, 8, 1, 2, 3])", "from __main__ import DiffLists")
    print(t.timeit(100000))

    t = ti.Timer("DiffLists1([1, 2, 3, 4, 5, 6, 7], [9, 8, 1, 2, 3])", "from __main__ import DiffLists1")
    print(t.timeit(100000))

    t = ti.Timer("DiffLists2([1, 2, 3, 4, 5, 6, 7], [9, 8, 1, 2, 3])", "from __main__ import DiffLists2")
    print(t.timeit(100000))


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------

    class cool(dict):
        class_var = "cv"

        def __init__(self):
            self.a = 4
            self.b = [1, 2, 3, 4, 5, 6, 7]
            self.c = (self.a, self.b)
            self.d = "been there"
            self.e = {'cool': 12, 'bob': ('weak', 3.4)}
            self.ref = self

    cc = cool()

    cc["fred"] = "is ref"

    hd = HierDecomp(flags = HierDecomp.USE_DICT)
    #hd = HierDecomp()
    print(hd.decompose("cc", cc))

    cc.b.append(120)
    print(hd.decompose("cc", cc))

    cc.a = 9
    print(hd.decompose("cc", cc))

    print(hd.decompose("cool", cool))


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    dc = DictCache(5)
    dc[1] = 1
    dc[2] = 2
    dc[3] = 3
    dc[4] = 4
    dc[5] = 5

    tester.Assert(dc == {1: 1, 2: 2, 3: 3, 4: 4, 5: 5})
    dc[6] = 6
    tester.Assert(dc == {2: 2, 3: 3, 4: 4, 5: 5, 6: 6})
    dc[7] = 7
    tester.Assert(dc == {3: 3, 4: 4, 5: 5, 6: 6, 7: 7})

    dl = DictList()
    dl['a'] = 'apple'
    dl['b'] = 'boo'
    dl['c'] = 'cat'
    dl['d'] = 'dog'

    tester.Assert(list(dl.keys()) == [u'a', u'b', u'c', u'd'])
    tester.Assert(list(dl.values()) == [u'apple', u'boo', u'cat', u'dog'])
    tester.Assert(list(dl.items()) == [(u'a', u'apple'), (u'b', u'boo'), (u'c', u'cat'), (u'd', u'dog')])

    tester.Assert(log2(8) == 3)

    class CoolException(Exception): pass

    with ignoreException(CoolException):
        raise CoolException('what')


    s = sstruct(cool = 5, dog = "bad")
    s.cat = "cool"
    tester.Assert("%(cool)d and %(dog)s and %(cat)s" % s.asDict() == "5 and bad and cool")


    krd = KeyRefDict()

    krd['cool'] = 'sara'
    tester.Assert(krd.getkey('sara') == 'cool')

    def cool():
        raise CoolException('what')

    CallNoException(cool, None, CoolException)

    tester.Assert(CvtGigMegKBytes(123432543) == '117.714M')

    return 0


if __name__ == "__main__":
    usage = oss.mkusage(__test__.__doc__)
    args, opts = oss.gopt(oss.argv[1:], [], [], usage)

    res = not __test__(verbose=True)
    oss.exit(res)


