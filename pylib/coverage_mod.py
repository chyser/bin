#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import hashlib

import pylib.runpy
import pylib.tester as tester
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
class Coverage(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, moduleName, ranMark='@', missMark=' ', useDB=False, mods=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.moduleName = moduleName

        self.ranMark = ranMark
        self.missMark = missMark

        self.mods = set([] if mods is None else [m + '.py' for m in mods])
        if moduleName is not None:
            self.mods.add(moduleName + '.py')
        self.module = None

        self.hits = {}

        if useDB:
            for nm in self.mods:
                self.hits[nm] = loadDB(nm)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def trace(self, frame, event, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print(event, '\t', frame.f_code.co_filename, frame.f_lineno)

        if event in set(['call', 'return', 'exception', 'c_call', 'c_return', 'c_exception']):
            bn = oss.basename(frame.f_code.co_filename)
            self.module = bn if bn in self.mods else None

        if self.module is not None and event == 'line':
            try:
                self.hits[self.module].add(frame.f_lineno)
            except KeyError:
                self.hits[self.module] = set([frame.f_lineno])

        return self.trace

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dumpDB(self, fn, lns):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        saveDB(fn, lns)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def annotateFile(self, fn, lns):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with open(fn, 'rU') as inf:
            with open(fn + '.cov.py', 'w') as otf:

                ln = last = state = 0
                for line in inf:
                    ln += 1
                    line_s = line.strip()

                    if state == 0:
                        if ln in lns:
                            otf.write(self.ranMark + ' ' + line)
                            last = True

                        elif line.startswith(('#', '"', 'def', 'class')):
                            otf.write(self.ranMark + ' ' + line)
                            last = True

                        elif last and line_s.startswith(('"""', "'''")):
                            otf.write(self.ranMark + ' ' + line)
                            last = True

                            if not ('"""' in line_s[3:] or "'''" in line_s[3:]):
                                state = 1

                        elif last and (not line_s or line_s.startswith(('#', '"', 'else:'))):
                            otf.write(self.ranMark + ' ' + line)
                            last = True

                        elif line_s.startswith(('else:', '#')) and ln + 1 in lns:
                            otf.write(self.ranMark + ' ' + line)
                            last = True

                        else:
                            otf.write(self.missMark + ' ' + line)
                            last = False

                    elif state == 1:
                        otf.write(self.ranMark + ' ' + line)
                        last = True

                        if '"""' in line_s or "'''" in line_s:
                            state = 0
                            continue

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runTest(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sys.settrace(self.trace)
        try:
            success = 0
            t = tester.test_it(self.moduleName)
        except tester.TesterException:
            success = t = 1
        sys.settrace(None)

        return t, success

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, path, prgm, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        prgm, globd = pylib.runpy.RunPrep(path, prgm, arg)

        sys.settrace(self.trace)
        execfile(prgm, globd)
        sys.settrace(None)

        self.genReport()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def start(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sys.settrace(self.trace)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def stop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sys.settrace(None)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def genReport(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lst = []
        for f, val in self.hits.items():
            f = oss.basename(f)
            lst.append(f)
            self.annotateFile(f, val)
            self.dumpDB(f, val)
        return lst


#-------------------------------------------------------------------------------
def saveDB(fileName, data):
#-------------------------------------------------------------------------------
    with open(fileName) as inf:
        md5 = hashlib.md5(inf.read()).hexdigest()

    with open(fileName + '.cov.db', 'w') as otf:
        otf.write(md5 + '\n')
        for i in data:
            otf.write(str(i) + '\n')


#-------------------------------------------------------------------------------
def loadDB(fileName):
#-------------------------------------------------------------------------------
    data = set()

    with open(fileName) as inf:
        md5 = hashlib.md5(inf.read()).hexdigest()

    with open(fileName + '.cov.db') as inf:
        line = inf.next()
        if line.strip() != md5:
            return data

        for line in inf:
            data.add(int(line))

    return data


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    fileName = oss.tmpfile()
    with open(fileName, 'w') as otf:
        otf.write('sara aidan boo connor')

    ts0 = set([1, 3, 5, 6, 7, 10])
    saveDB(fileName, ts0)
    ts1 = loadDB(fileName)
    tester.Assert(ts0 == ts1)

    with open(fileName, 'w') as otf:
        otf.write('sara aidan boo connor stuff')
    ts1 = loadDB(fileName)
    tester.Assert(set() == ts1)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


