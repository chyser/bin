#!/usr/bin/env python

import pylib.osscripts as oss
import sys

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: beautify.py [options] <file_name> [<file_name> ...]

        options:
            -f | --force   : force overwrite of the backup file

        beautifies python and eventually c/cpp code
    """
    args, opts = oss.gopt(argv[1:], [('f', 'force')], [], main.__doc__)

    for f in args:
        ext = oss.splitext(f)
        if ext == '.py':
            DoPython(f, opts.force)

        elif ext in set(['.c', '.cpp', '.h', '.cxx', '.hxx', '.java']):
            d = CppDoer()
            d.run(f, opts.force)

    oss.exit(0)


LINE = """#-------------------------------------------------------------------------------"""
DLINE = """#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"""

gDEBUG = 0

#-------------------------------------------------------------------------------
class PythonTokenizer(object):
#-------------------------------------------------------------------------------
    class PythonTokenizerError(Exception): pass

    INDENT_SPACE = "    "

    NL_KEYWORDS = ["if", "for", "while", "try", "except", "finally", 'global']
    NNL_KEYWORDS = ['pass', 'continue', 'and', 'or', 'not', 'in', 'print']
    LN_KEYWORDS = ['def', 'class']

    KEYWORDS = NNL_KEYWORDS + NL_KEYWORDS + LN_KEYWORDS

    KEYWDS = ['NL_KEYWORD', 'NNL_KEYWORD', 'LN_KEYWORD', 'KEYWORD']
    SYMBOLS = KEYWDS + ['NAME', 'STRING', 'NUMBER']

    S0_OP = [".", "(", ")", "[", "]", "{", "}", '**', '`']       # word<op>word
    S1_OP = [',', ':', ';']                                      # word<op> word

    S2_OP = ['+', '+=', '-', '-=', '&', '&=', '|', '|=', '^',
        '^=', '*', '*=', '/', '//', '/=', '<', '>', '<=', '>>', '<<',
        '>=', '=', '==', '!=', '%']                              # word <op> word

    S3_OP = ['!', '~']                                           # word <op>word

    SP_OP = ['(', '[', '{', ':']
    SP1_OP = [')', ']', '}']

    OPS = ['S0_OP', 'S1_OP', 'S2_OP', 'S3_OP']


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, InputFileName, OutputFileName = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import tokenize
        object.__init__(self)

        self.inf = open(InputFileName)
        self.opf = open(OutputFileName, 'w') if OutputFileName else sys.stdout

        self.LastLineEmpty = False
        self.LnLst = []
        self.IndentLvl = 0

        tokenize.tokenize(self.inf.readline, self.__FormatIt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __GetType(self, idx, ret = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
       try:
           if ret == 0: return self.LnLst[idx][0]
           if ret == 1: return self.LnLst[idx][1]
           return self.LnLst[idx]
       except:
           return ' '

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __PrintIt1(self, Line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in Line:
            if i not in [' ', '\n']:
                print >> self.opf, Line,
                self.LastLineEmpty = False
                return

        if self.LastLineEmpty:
            return

        self.LastLineEmpty = True
        print >> self.opf, '\n',

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __PrintIt(self, Line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lns = Line.split('\n')
        for i in lns[:-1]:
            self.__PrintIt1(i + '\n')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __FormatIt(self, type, Str, st, end, ln):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import tokenize

        if Str and Str[-1] == "\n":
            name = Str[:-1]
        else:
            name = Str

        tp = tokenize.tok_name[type]

        if tp == 'NAME':
            if name in PythonTokenizer.NL_KEYWORDS:
                tp = 'NL_KEYWORD'
            elif name in PythonTokenizer.NNL_KEYWORDS:
                tp = 'NNL_KEYWORD'
            elif name in PythonTokenizer.LN_KEYWORDS:
                tp = 'LN_KEYWORD'
            elif name in PythonTokenizer.KEYWORDS:
                tp = 'KEYWORD'

        elif tp == "OP":
            if name in PythonTokenizer.S0_OP:
                tp = 'S0_OP'
            elif name in PythonTokenizer.S1_OP:
                tp = 'S1_OP'
            elif name in PythonTokenizer.S2_OP:
                tp = 'S2_OP'
            elif name in PythonTokenizer.S3_OP:
                tp = 'S3_OP'
            else:
                raise PythonTokenizer.PythonTokenizerError("Unknown OP Error '%s' Line: %d" % (name, end[0]))

        self.LnLst.append((tp, name))

        if tp == 'NL' or tp == 'NEWLINE':
            self.Format()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Format(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx = 0;  cmt = -1
        l = len(self.LnLst)

        for idx in xrange(l):
            type, name = self.LnLst[idx]
            if type == 'INDENT':
                self.IndentLvl += 1
            elif type == 'DEDENT':
                self.IndentLvl -= 1
                assert(self.IndentLvl >= 0)
            elif type == 'COMMENT':
                if cmt == -1: cmt = idx
            else:
                break

        Template = PythonTokenizer.INDENT_SPACE * self.IndentLvl + "%s\n"
        Str = ''

        if cmt != -1: idx = cmt

        for idx in xrange(0, l):
            type, name = self.LnLst[idx]

            if type == 'NL_KEYWORD' and self.__GetType(idx-1) != 'INDENT':
                fnl = (self.__GetType(l-2) != 'COMMENT' and '\n') or ""
                Template = '\n' + PythonTokenizer.INDENT_SPACE * self.IndentLvl + "%s" + fnl + PythonTokenizer.INDENT_SPACE * self.IndentLvl

            #
            # keywords for which "lines" are added
            #
            elif type == 'LN_KEYWORD' and self.IndentLvl <= 1:
                ln = (self.IndentLvl == 0 and LINE) or DLINE
                sp = (self.IndentLvl == 1 and PythonTokenizer.INDENT_SPACE) or ""
                nl = (self.__GetType(l-2) != 'COMMENT' and '\n') or ""
                fnl = '\n'

                Template = fnl + sp + ln + "\n" + sp + "%s" + nl + sp + ln + '\n'


            NType = self.__GetType(idx+1)
            LType, LName = self.__GetType(idx-1, 2)
            if LType in PythonTokenizer.OPS and LName in PythonTokenizer.SP1_OP and type in PythonTokenizer.SYMBOLS:
                Str += ' '

            if type in PythonTokenizer.KEYWDS and NType != 'S2_OP' and NType != 'S1_OP':
                Str += name + ' '

            elif type in PythonTokenizer.SYMBOLS and NType in PythonTokenizer.SYMBOLS:
                Str += name + ' '

            elif type in PythonTokenizer.OPS:
                if type == 'S1_OP':
                    Str += name + ' '
                elif type == 'S2_OP':
                    if name == '-':
                        if LType == 'SYMBOL':
                            Str += ' ' + name + ' '
                        else:
                            if LName in PythonTokenizer.SP_OP:
                                Str += name
                            else:
                                Str += ' ' + name
                    else:
                        Str += ' ' + name + ' '

                elif type == 'S3_OP':
                    Str += ' ' + name
                else:
                    Str += name

            elif type == "COMMENT":
                if not (name == LINE or name == DLINE):
                    Str += name + '\n' + PythonTokenizer.INDENT_SPACE * self.IndentLvl

            elif type == "INDENT":
                pass

            elif type == "DEDENT":
                fnl = (self.__GetType(l-2) != 'COMMENT' and '\n') or ""
                Template = '\n' + PythonTokenizer.INDENT_SPACE * self.IndentLvl + "%s" + fnl + PythonTokenizer.INDENT_SPACE * self.IndentLvl

            else:
                Str += name

        if gDEBUG == 2: print self.LnLst
        self.__PrintIt(Template % Str)
        self.LnLst = []


#from osscripts import *


#-------------------------------------------------------------------------------
class FileDoer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.tabWidth = 8
        self.indent = 4

        self.lastCnt = 0
        self.lastIndent = 0
        self.lastStack = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getIndent(self, line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(line) == 0:
            return self.lastIndent

        cnt = 0
        for ch in line:
            if ch != ' ': break
            cnt += 1

        if cnt > self.lastCnt:
            self.lastIndent += 1
            self.lastCnt = cnt
            self.lastStack.append((self.lastCnt, self.lastIndent))
            return self.lastIndent

        if cnt < self.lastCnt:
            while 1:
                try:
                    self.lastCnt, self.lastIndent = self.lastStack[-1]
                except IndexError:
                    self.lastCnt = self.lastIndent = 0
                    return 0

                if cnt >= self.lastCnt:
                    self.lastCnt = cnt
                    return self.lastIndent
                else:
                    del self.lastStack[-1]

        return self.lastIndent

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def makeBU(self, fn, force=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bfn = oss.basename(fn) + ".beautify"
        if not oss.exists(bfn) or force:
            oss.mv(fn, bfn)
        return bfn


#-------------------------------------------------------------------------------
def DoPython(InputFileName, Force=None):
#-------------------------------------------------------------------------------
    if gDEBUG:
        PythonTokenizer(InputFileName)
        return

    BUFileName = oss.basename(InputFileName) + ".beautify"
    OutputFileName = InputFileName

    if not Force and oss.exists(BUFileName):
        print >> sys.stderr, "Cannot make backup file '%s'" % BUFileName
        sys.exit(3)

    oss.mv(InputFileName, BUFileName)
    PythonTokenizer(BUFileName, OutputFileName)


#-------------------------------------------------------------------------------
class CppDoer(FileDoer):
#-------------------------------------------------------------------------------
    indentOptions = ("-l180  -ppi4 -saf -sai -saw -bbo -c70 -cd70 -ci4 -nlp -sc " +
        "-nut -ss -ncs  -npcs -ci4 -bap -bad -psl -npsl -brs -brf " +
        "-bfda -bfde -cli4 -i4 -ce -br ")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, fn, force=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        oss.r('indent1.exe ' + self.indentOptions + ' ' + fn)
        return
        bfn = self.makeBU(fn, force)

        inf = open(bfn, 'rU')
        otf = open(fn, 'w')

        ol2 = ol1 = ls = None

        for line in inf:
            ol2 = ol1
            ol1 = ls
            ls = line.strip()

            if not ls:
                otf.write('\n')
                continue

            if ls.startswith('if') or ls.startswith('for') or ls.startswith('while') or ls.startswith('switch'):
                if ol1: otf.write('\n')
                otf.write(line)

            elif ls.endswith('('):
                if line[0] not in [' '] or (len(ls.split()) > 1 and '=' not in line):
                    if ol2: otf.write('\n')
                    if ol1: otf.write('\n')
                    otf.write('//' + ('-'*78) +'\n')
                    otf.write(line)
                    otf.write('//' + ('-'*78) +'\n')

            elif ls.startswith('break'):
                otf.write(line)
                otf.write('\n')

            else:
                otf.write(line)


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    fd = FileDoer()

    print fd.getIndent('cool')
    print fd.getIndent('cool')
    print fd.getIndent('  cool')
    print fd.getIndent('    cool')
    print fd.getIndent('    cool')
    print fd.getIndent('               cool')
    print fd.getIndent('               cool')
    print fd.getIndent('  cool')
    print fd.getIndent('cool')
    print fd.getIndent('    cool')
    print fd.getIndent('  cool')

    return 0


if __name__ == "__main__":
    main(oss.argv)

