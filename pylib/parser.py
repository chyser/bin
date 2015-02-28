#!/usr/bin/env python
"""

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
class ParseObj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lst = None, func = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ParseObj, self).__init__()

        self.f = func

        if isinstance(lst, ParseObj):
            self.lst = []
            for l in lst.lst:
                self.lst.append(list(l))
            return

        if lst is None:
            self.lst = []
        elif isinstance(lst[0], list):
            self.lst = lst
        else:
            self.lst = [lst]



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(lst, list):
            self.lst.append(lst)
        else:
            self.lst.append([lst])

        self.lst.sort(key=len, reverse = True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def chkElem(self, tokl, sidx, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(v, ParseObj):
            return v.parse(tokl, sidx)

        try:
            if v != tokl[sidx][0]:
                #print 'f:', v, '!=', tokl[sidx][0]
                return -1, None

            #print 't:', v, '==', tokl[sidx][0]
            return sidx, [tokl[sidx][1]]
        except IndexError:
            #print 'f:', v, '-> <empty>  ', sidx
            return -1, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseRule(self, rule, tokl, sidx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vval = []
        for v in rule:
            idx, val = self.chkElem(tokl, sidx, v)
            if idx == -1: return -1, None
            vval.extend(val)
            sidx = idx + 1
        return sidx - 1, vval

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def func1(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.f is not None:
            return self.f(val)
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def func(self, idx, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return idx, val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, tokl, sidx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns on first rule match
        """
        for rule in self.lst:
            idx, val = self.parseRule(rule, tokl, sidx)
            if idx != -1:
                return self.func(idx, val)
        return -1, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def par(self, tokl, sidx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx, val = self.parse(tokl, sidx)
        if idx == -1:
            return idx, None
        return idx, self.func1(val)



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for l in self.lst:
            s.append('[')
            for ll in l:
                if ll is self:
                    s.append('self')
                else:
                    s.append(str(ll))
            s.append('], ')

        return ''.join(s)[:-2]

#-------------------------------------------------------------------------------
class ApplyAllParseObj(ParseObj):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, tokl, sidx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ trys all rules and returns the greediest (or first of the greediest)
        """

        print '\np:', self.lst

        br = None
        midx = -1
        for rule in self.lst:
            print 'rule:'
            idx, val = self.parseRule(rule, tokl, sidx)
            if idx > midx:
                br = val
                midx = idx

        return self.func(midx, br)

#-------------------------------------------------------------------------------
class RepeatParseObj(ParseObj):
#-------------------------------------------------------------------------------
    """ is always a rule with 2 items. if the second is present, then repeats
        symbol [[, symbol] ...]
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, tokl, sidx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print '\np:', self.lst

        l = self.lst[0]
        idx, val = self.chkElem(tokl, sidx, l[0])
        if idx == -1: return -1, None

        sidx = idx + 1

        if tokl[sidx][0] in l[1]:
            idx, vv = self.parse(tokl, sidx + 1)
            val.extend(vv)
            return self.func(idx, val)

        return sidx - 1, val

#-------------------------------------------------------------------------------
class Choice(ParseObj):
#-------------------------------------------------------------------------------
    """ initialized with a simple list of choices:
        ex: ['SYMBOL', 'INTEGER']
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Choice, self).__init__([[l] for l in args])

#-------------------------------------------------------------------------------
class WildCard(ParseObj):
#-------------------------------------------------------------------------------
    """ pulls all tokens until a terminator found, which can optionally be
        included
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, terminator, func = None, inclusive = True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(WildCard, self).__init__()
        if isinstance(terminator, list):
            self.term = set(terminator)
        else:
            self.term = set([terminator])
        ParseObj.__init__(self, func=func)

        if inclusive:
            self.adj = 0
        else:
            self.adj = -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, tokl, sidx=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        val = []
        for i in xrange(sidx, len(tokl)):
            if tokl[i][0] in self.term:
                return self.func(i + self.adj, val)
            val.append(tokl[i][1])
        return -1, None


#-------------------------------------------------------------------------------
class Parameters(ParseObj):
#-------------------------------------------------------------------------------
    """ parses parameter lists
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, st = '(', end = ')', sep=','):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Parameters, self).__init__()
        self.st = st
        self.end = end
        self.sep = sep

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, tokl, sidx=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print "Parameters:", tokl[sidx-2:sidx+5]
        if tokl[sidx][0] != self.st:
            return -1, None

        val = []
        p = []
        for i in xrange(sidx+1, len(tokl)):
            if tokl[i][0] == self.sep:
                val.append(p)
                p = []

            elif tokl[i][0] in self.end:
                val.append(p)
                #print "out", val
                return self.func(i, val)

            else:
                p.append(tokl[i][1])
        return -1, None



#----------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class rangeArgs(ApplyAllParseObj):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def func(self, idx, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = len(val)

        if l == 1:
            return idx, [0, val[0], '+=1', '<']
        if l == 3:
            return idx, [val[0], val[2], '+=1', '<']

        if val[4][0] == '-':
            return idx, [val[0], val[2], '+= ' + str(val[4]), '>']

        return idx, [val[0], val[2], '+= ' + str(val[4]), '<']


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])


    from lex import Lex, KWLex

    lx = KWLex(keyword, [Lex.CCOMMENT, Lex.HEX, Lex.FLOAT, Lex.SYMBOL, Lex.INTEGER, Lex.STRING, Lex.SSTRING, Lex.WHITESPACE])
    lx.add(["==", "<=", ">=", "!=", ':', '(', ')', ',', '=', '+=', '-=', '*=', '/='])

    lx.addRE(('nl', '\n'))
    lx.addRE(('op', "[*+-/]"))
    lx.addRE(('OTHER', '.'))
    lx.compile()

    si = Choice('SYMBOL', 'INTEGER')

    cvtfor = ParseObj(['for', 'SYMBOL', 'in', Choice('range', 'xrange'), '(', rangeArgs([[si], [si, ',', si], [si, ',', si, ',', si]]), ')', ':'])
    cvtfor.f = lambda val: 'for (%s = %s; %s %s %s; %s %s)' % (val[1], val[5], val[1], val[8], val[6], val[1], val[7])

    cvtif = ParseObj(['if', WildCard(':')], lambda val: 'if (' + ' '.join(val[1:]) + ') {')

    buf = """
    for i in xrange(l, -1, -1):
        cool += 3

    if d == 3:
        print
    else:
        cool = 1
"""

    tokl = lx.lex(buf)
    tokl = modify(tokl)
    print tokl


    i = 0
    t = []

    while i < len(tokl):
        ## convert for w/ range
        idx, val = cvtfor.par(tokl, i)
        if val is not None:
            t.append(val)
            i = idx + 1
            continue

        ## convert if
        idx, val = cvtif.par(tokl, i)
        if val is not None:
            t.append(val)
            i = idx + 1
            continue

        t.append(tokl[i][1])
        i += 1

    t.append('}')

    print ' '.join(t)

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


