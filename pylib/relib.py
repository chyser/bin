
import re
import pylib.tester as tester

#-------------------------------------------------------------------------------
class reCmp(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, rex, flags=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.rex = re.compile('^' + rex + '$', flags)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def eq(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rex.match(val) != None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rex.pattern


#-------------------------------------------------------------------------------
class reHas(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, rex, flags=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.rex = re.compile(rex, flags)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isIn(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rex.search(val) != None


#-------------------------------------------------------------------------------
def eq(s, rex, flags=0):
#-------------------------------------------------------------------------------
    """ return True if 's' matches the regular expression 'rex' using 'flags'
    """
    return re.match('^' + rex + '$', s, flags) != None


#-------------------------------------------------------------------------------
def split(pattern, s):
#-------------------------------------------------------------------------------
    return tuple([a.split() for a in re.split(pattern, s)])


#-------------------------------------------------------------------------------
def CvtFileWildCardToRE(filePath):
#-------------------------------------------------------------------------------
    """ file wildcards are *, ? and [...] and multiple paths separated by ';'
    """
    rr = []
    for ch in filePath:
        if ch == '*':
            rr.append('.*')
        elif ch == '.':
            rr.append('\.')
        elif ch == '?':
            rr.append('.')
        elif ch == '/' or ch == '\\':
            rr.append(r'[/\\]')
        elif ch == ';':
            rr.append('|')
        else:
            rr.append(ch)
    return ''.join(rr)


#-------------------------------------------------------------------------------
class scanf(object):
#-------------------------------------------------------------------------------
    """ perform C sscanf type line parsing

        There are two tokens that correspond to the % tags of C scanf, $$ and $!.
        $$ - return the string that occupies this space
        $! - ignoring the string that occupies this space

        all other characters must match identically
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, pattern):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(scanf, self).__init__()
        self.tx = re.compile(self.__cvt(pattern))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __cvt(self, pat):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        state = 0
        for ch in pat:
            if state == 1:
                if ch in [' ', '\t']:
                    continue
                else:
                    state = 0
            elif state == 2:
                state = 0
                if ch == '$':
                    s.append("(.*?)")
                    continue
                elif ch == '!':
                    s.append(".*?")
                    continue

            if ch in [' ', '\t']:
                s.append("[ ]+")
                state = 1
            elif ch == '$':
                state = 2
            elif eq(ch, "[_a-zA-Z0-9]"):
                s.append(ch)
            else:
                s.append("\\" + ch)

        s.append('$')
        #print ''.join(s)
        return ''.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def scan(self, line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ scan 'line' against the pattern this object was built with returning
            a tuple of all $$ matches in order of occurance in the pattern
        """

        m = self.tx.match(line)
        if m is None: return m
        return m.groups()


#-------------------------------------------------------------------------------
def splitPath(pth):
#-------------------------------------------------------------------------------
    """ os independent path splitter
    """
    return re.split(r'[\\/]', pth)


#-------------------------------------------------------------------------------
class MRE(object):
#-------------------------------------------------------------------------------
    SYM = '[_a-zA-Z][_a-zA-Z0-9]*'
    SPC = '[ \t]'
    SPC0 = '[ \t]*'
    SPC1 = '[ \t]+'
    NSPC = '[^ \t]'
    NSPC0 = '[^ \t]*'
    NSPC1 = '[^ \t]+'
    EMPTY = r'\b'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ary = []
        self.rx = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def spc(self, n=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ary.append('[ \t]+' if n != 0 else '[ \t]*')
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ary.append(self.cvt(val))
        return self

    choice = add

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addg(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ary.append('(' + self.cvt(val) + ')')
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addLookAhead(self, v, pos=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ary.append('(?%s%s)' % ('=' if pos else '!', self.cvt(v)))
        return self

    addLA = addLookAhead

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addSym(self, keywords=None, sym=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if keywords:
            for keyword in keywords:
                self.addLookAhead(keyword, False)
        self.add(sym if sym else self.SYM)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvt(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(val, MRE):
            return val.get()

        if isinstance(val, (str, unicode)):
            return val

        return '(?:' + '|'.join(['(?:' + self.cvt(v) + ')' for v in val]) + ')'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return ''.join(self.ary)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getRE(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.rx:
            self.rx = re.compile(self.get())
        return self.rx


STR_PARTITION = None

#-------------------------------------------------------------------------------
def strPartition(pattern, s):
#-------------------------------------------------------------------------------
    global STR_PARTITION
    if STR_PARTITION is None:
        STR_PARTITION = re.compile(r'("""|\'\'\'|"|\')(.*?)\1')

    def call(mo):
        return re.sub(' ', '\01', mo.group(2))

    return [[re.sub('\01', ' ', i) for i in ii.split()] for ii in re.split('(' + pattern + ')', STR_PARTITION.sub(call, s))]


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    tester.Assert(eq("bob", "[_a-zA-Z][_a-zA-Z0-9]+"))
    tester.Assert(not eq("bob ", "[_a-zA-Z][_a-zA-Z0-9]+"))
    tester.Assert(not eq(" bob ", "[_a-zA-Z][_a-zA-Z0-9]+"))
    tester.Assert(not eq("bib ", "[_a-zA-Z][_a-zA-Z0-9]+"))

    s = " cool $$% dogf$!d$!"

    sf = scanf(s)
    tester.Assert(not sf.scan("cool 100% dogfood") == ('100',))
    tester.Assert(sf.scan(" cool 100% dogfodfdfdod ") == ('100',))
    tester.Assert(sf.scan(" cool a% dogfodfdfod ") == ('a',))
    tester.Assert(sf.scan("             cool    1234 6%      dogfooddddddddddddddddddddddddddddd") == ('1234 6',))

    s = "warning: line $$, column $$"
    sf = scanf(s)
    tester.Assert(sf.scan("warning: line 31, column 42") == ('31', '42'))

    rex = CvtFileWildCardToRE('*.py;data?.dat')
    ee = reCmp(rex)

    rex = CvtFileWildCardToRE('*.py')
    tester.Assert(ee.eq('C:/bad/cool.py'))
    tester.Assert(ee.eq('C:\\bad\\cool.py'))
    tester.Assert(not ee.eq('da3ta5.dat'))
    tester.Assert(ee.eq('data5.dat'))
    tester.Assert(eq('C:/bad/cool.py', rex))
    tester.Assert(eq('C:\\bad\\cool.py', rex))

    tester.Assert(strPartition('==|-=', 'this is a "very cool" == test -= """more stuff"""') == [['this', 'is', 'a', 'very cool'], ['=='], ['test'], ['-='], ['more stuff']])

if __name__ == "__main__":
    import sys


    me = MRE()
    me.addLA('else', False).addLA('return', 0).add(me.SYM)
    rx = me.getRE()

    me = MRE()
    me.addSym(['else', 'return'])
    rx = me.getRE()

    print rx.match('cool')
    print rx.match('cool cool')
    print rx.match('else')
    print rx.match('ret')
    print rx.match('return')

    sys.exit(0)

    me = MRE()
    me.choice(('static', 'public', 'private', 'protected', '')).spc(0).choice(('static', 'public', 'private', 'protected', '')).spc(0).add(me.SYM).spc(1).addg(me.SYM).spc(0).add(r'\(')

    rx = me.getRE()
    print(rx.pattern)
    print rx.match('static int cool(d)').group(1)
    print rx.match('static public int cool(d)').group(1)
    print rx.match('public int cool(d)').group(1)
    print rx.match('public static int cool(d)').group(1)
    print rx.match(' int cool(d)').group(1)
    print rx.match('int cool(d)').group(1)

    me = MRE()
    me.choice(('public', 'private', 'abstract', 'final', 'protected', '')).spc(0).add('class').spc(1).addg(me.SYM).choice((me.SPC1 + 'extends' + me.SPC1 + '(' + me.SYM + ')', ''))

    rx = me.getRE()
    print(rx.pattern)
    print rx.match('public class sara').group(1)
    print rx.match('private class sara').group(1)
    print rx.match('private class sara').group(2)
    print rx.match('class sara').group(1)
    print rx.match(' class sara').group(1)
    print rx.match('private class sara extends boo').group(1)
    print rx.match('private class sara extends boo').group(2)


    sys.exit(0)


if __name__ == "__main__":
    import sys
    __test__()
    sys.exit(0)


