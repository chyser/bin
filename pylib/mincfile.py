#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


class MacroIncludeFileException(Exception): pass

#-------------------------------------------------------------------------------
class MacroObj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, params=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.params = params
        self.lines = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.lines.append(line)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self, params=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if params is None:
            params = []

        if len(params) != len(self.params):
            raise MacroIncludeFileException("Incorrect number of parameters")

        pp = {}
        for idx, name in enumerate(self.params):
            pp[name] = params[idx]

        ol = []
        for line in self.lines:
            ol.append(line.format(**pp))

        return ol

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class MacroIncludeFile(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName, incStr=None, macTup=(None, None, None), includedFiles=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        self.macro = {}
        self.txtlines = []
        self.includedFiles = set() if includedFiles is None else includedFiles

        curMacro = ''
        macroBegin, macroEnd, macroExpand = macTup

        with open(fileName) as inf:
            state = 0

            ln = 0
            for line in inf:
                ln += 1
                w = line.strip().split()

                if state == 0:
                    if not w:
                        self.txtlines.append(line)

                    elif w[0] == incStr:
                        if w[1] in self.includedFiles:
                            raise MacroIncludeFileException("Infinite File Include: '%s'  line: %d" % (w[1], ln))

                        self.includedFiles.add(w[1])

                        try:
                            with MacroIncludeFile(w[1], incStr, macTup, self.includedFiles) as incf:
                                self.txtlines.extend(incf.readlines())
                        except IOError:
                            raise MacroIncludeFileException("Include File IOError: '%s' line: %d" % (w[1], ln))

                    elif w[0] == macroBegin:
                        state = 1

                        try:
                            curMacro = self.macro[w[1]] = MacroObj(w[2:])
                        except IndexError:
                            raise MacroIncludeFileException("Improper macro definition: '%s'  line: %d" % (line, ln))

                    elif w[0] == macroExpand:
                        if w[1] in self.macro:
                            self.txtlines.extend(self.macro[w[1]].expand(w[2:]))
                        else:
                            raise MacroIncludeFileException("Include File Error: '%s' line: %d " % (w[1], ln))

                    else:
                        self.txtlines.append(line)

                elif state == 1:
                    if w and w[0] == macroEnd:
                        state = 0
                        continue

                    curMacro.add(line)


        self.idx = 0
        self.linenum = 1


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __enter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __exit__(self, type, value, traceback):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readlines(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.txtlines

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            try:
                ln = self.txtlines[self.idx]
            except IndexError:
                raise StopIteration

            self.idx += 1
            self.linenum += 1
            yield ln

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)

    with MacroIncludeFile(args[0], None, ('#mdef', '#mend', '#mx')) as inf:
        for ln in inf:
            print(ln, end='')

    oss.exit(res)


