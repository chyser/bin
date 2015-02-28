""" lex.py

This module contains a simple and regular lexical analyzer

"""

import sys
import re

SYMBOL = "[_a-zA-Z][_a-zA-Z0-9]*"
INTEGER = "[+-]?[0-9]+"
HEX = "0[xX][0-9a-fA-F]+"
FLOAT = r"[+-]?[0-9]+\.[0-9]+"
FILENAME = r"([a-zA-Z]:)?[-_1a-zA-Z0-9./\\]+"
STRING = r'".*?(?<!\\)"'
SSTRING = r"""'.*?(?<!\\)'"""
CCOMMENT = r"/\*(.|\n)*?\*/"
WHITESPACE = r"[ \t\r\f\v]+"
WCFILENAME = r"([a-zA-Z]:)?[-_?*1a-zA-Z0-9./\\]+"
NONWHITESPACE = r"[^ \t\r\f\v]+"
OTHERS = r"[^%s \t\r\f\v]+"

ALLCHARS = set([chr(i) for i in range(128)])

class LexException(Exception): pass


#-------------------------------------------------------------------------------
def allOthers(s):
#-------------------------------------------------------------------------------
    return OTHERS % re.escape(s)

#-------------------------------------------------------------------------------
class SLex(object):
#-------------------------------------------------------------------------------
    """ simple lexical analyzer returns a list of tokenized input w/o token
        names
    """
    SYMBOL = "[_a-zA-Z][_a-zA-Z0-9]*"
    INTEGER = "[+-]?[0-9]+"
    HEX = "0[xX][0-9a-fA-F]+"
    FLOAT = r"[+-]?[0-9]+\.[0-9]+"
    FILENAME = r"([a-zA-Z]:)?[-_1a-zA-Z0-9./\\]+"
    STRING = r'".*?(?<!\\)"'
    SSTRING = r"""'.*?(?<!\\)'"""
    CCOMMENT = r"/\*(.|\n)*?\*/"
    WHITESPACE = r"[ \t\r\f\v]+"
    NONWHITESPACE = r"[^ \t\r\f\v]+"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lst=None, flags=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.lst = lst if lst is not None else []
        self.needCompile = True
        self.pat = None
        self.flags = flags

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, sl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add one (string) or a list of non-regular expression tokens
        """
        self.needCompile = True

        if isinstance(sl, list):
            self.lst.extend(map(re.escape, sl))
        else:
            self.lst.append(re.escape(sl))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addRE(self, sl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add one or a list of regular expression tokens
        """
        self.needCompile = True

        if isinstance(sl, list):
            self.lst.extend(sl)
        else:
            self.lst.append(sl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compile(self, flags=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if flags is None : flags = self.flags
        pattern = ('|'.join(self.lst))
        self.pat = re.compile(pattern, flags)
        self.needCompile = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lex(self, buf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of tokenized input minus token names
        """
        if self.needCompile:
            self.compile()

        return re.findall(self.pat, buf)


#-------------------------------------------------------------------------------
class PLex(SLex):
#-------------------------------------------------------------------------------
    """ simple lexer that returns all specified tokens and any "non-white space"
        tokens
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compile(self, flags=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ compile regular expression. 'flags' overrides any flags specified
            during  '__init__'. defaults flags == 0
        """
        if flags is None : flags = self.flags
        ignore = ''.join([l[0] for l in self.lst])
        pattern = ('|'.join(self.lst)) + '|' + allOthers(ignore)
        self.pat = re.compile(pattern, flags)
        self.needCompile = False


#-------------------------------------------------------------------------------
def StringParse(s, lst=None, relst=None):
#-------------------------------------------------------------------------------
    """ like str.split() except splits on all whitespace and keeps strings
        surrounded by '"' together as a single string. Also support \\" as
        a quote escape

        returns a list
    """

    lx = SLex([SLex.STRING, SLex.SSTRING])
    if relst is not None: lx.addRE(relst)
    if lst is not None: lx.add(lst)
    lx.addRE(SLex.NONWHITESPACE)
    return lx.lex(s)


#-------------------------------------------------------------------------------
def Parse(s, lst=None, relst=None):
#-------------------------------------------------------------------------------
    lx = SLex()
    if relst is not None: lx.addRE(relst)
    if lst is not None: lx.add(lst)
    return lx.lex(s)


#-------------------------------------------------------------------------------
class Lex(object):
#-------------------------------------------------------------------------------
    """ a lexical analyzer that returns a list of 2-tuples, each tuple is the token
        name followed by its value
    """

    SYMBOL = ('SYMBOL', SLex.SYMBOL)
    INTEGER = ('INTEGER', SLex.INTEGER)
    HEX = ('HEX', SLex.HEX)
    FLOAT = ('FLOAT', SLex.FLOAT)
    FILENAME = ('FILENAME', SLex.FILENAME)
    STRING = ('STRING', SLex.STRING)
    SSTRING = ('SSTRING', SLex.SSTRING)
    CCOMMENT = ('CCOMMENT', SLex.CCOMMENT)
    WHITESPACE = ('WHITESPACE', SLex.WHITESPACE)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lst=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ lst -- a list of 2-tuples: (token_name, regular_expression)
        """

        object.__init__(self)
        self.tokTbl = {}
        self.lst = []
        self.pat = None
        self.needCompile = True

        if lst is not None:
            self.addRE(lst)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, sl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ adds one or a list of 2-tuples or non-regular expression strings.
            the tuple is: (token_name, string). if sl is a string instead of a
            tuple, the token name is set to the string value
        """
        self.needCompile = True

        if isinstance(sl, list):
            for s in sl:
                self.add(s)
        else:
            if isinstance(sl, tuple):
                self.lst.append((sl[0], re.escape(sl[1])))
            else:
                self.lst.append((sl, re.escape(sl)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addRE(self, tl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ adds one or a list of 2-tuples: (token_name, regular_expression)
        """
        self.needCompile = True

        if isinstance(tl, list):
            for t in tl:
                self.addRE(t)
        else:
            if isinstance(tl, tuple):
                self.lst.append((tl[0], tl[1]))
            else:
                raise LexException("bad RE value: not a tuple")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compile(self, flags = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.tokTbl = {}
        d = [];  i = 0
        for nm, l in self.lst:
            d.append(('(?P<_%d>' % i) + l + ')')
            self.tokTbl["_%d" % i] = nm
            i += 1

        self.pat = re.compile('|'.join(d), flags)
        self.needCompile = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lex(self, buf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of 2-tuples: (token_name, value)
        """
        if self.needCompile:
            self.compile()

        d = []
        for i in re.finditer(self.pat, buf):
            d.append((self.tokTbl[i.lastgroup], i.group(i.lastgroup)))
        return d

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print self.lst
        print self.tokTbl


#-------------------------------------------------------------------------------
class KWLex(Lex):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, kw, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Lex.__init__(self, lst)
        self.kw = kw

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lex(self, buf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dd = Lex.lex(self, buf)

        l = []
        for d in dd:
            if d[1] in self.kw:
                l.append((d[1], d[1]))
            else:
                l.append(d)
        return l


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    from pylib.tester import Assert

    lst = StringParse('cool "something\\" wierd" more stuff')
    Assert(len(lst) == 4, str(lst))
    lst = StringParse('cool "something wierd" more stuff')
    Assert(len(lst) == 4, str(lst))


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    inf = file(argv[1])
    lex = Lex([Lex.CCOMMENT, Lex.HEX, Lex.FLOAT, Lex.SYMBOL, Lex.INTEGER, Lex.FILENAME, Lex.STRING, Lex.SSTRING, Lex.WHITESPACE])
    lex.add(["==", "<=", ">=", "!=", "+=", "-=", "*=", "/="])
    lex.addRE(('op', "[*+-/=]"))
    lex.addRE(('OTHER', '.'))
    lex.compile()

    lex.dump()

    buf = inf.read()
    print buf
    print lex.lex(buf)




#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)




