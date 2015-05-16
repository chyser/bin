"""
"""
PARSE_ALL_CHARS = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""

PARSE_LC_LETTERS = 'abcdefghijklmnopqrstuvwxyz'
PARSE_UC_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
PARSE_LETTERS = PARSE_LC_LETTERS + PARSE_UC_LETTERS
PARSE_NUMBERS = '0123456789'

PARSE_SYM = '_' + PARSE_NUMBERS+ PARSE_LETTERS
PARSE_WS = "\t\n "

PARSE_TYPE_SYM  = 1001
PARSE_TYPE_WS   = 1002
PARSE_TYPE_OP   = 1003
PARSE_TYPE_STR  = 1004
PARSE_TYPE_CMNT = 1005
PARSE_TYPE_NUM  = 1006
PARSE_TYPE_UKWN = -1

#-------------------------------------------------------------------------------
def RmChars(BS, RS):
#-------------------------------------------------------------------------------
    s = ''
    for ch in BS:
        if ch not in RS: s += ch
    return s

#-------------------------------------------------------------------------------
def Parse(Str, Tokens, SaveUkwn = 0):
#-------------------------------------------------------------------------------
    res = [];  idx = 0;  sidx = -1;  type = None; CTokStr = ""

    while idx < len(Str):
        ch = Str[idx]

        if sidx == -1:
            for Type, TokStr in Tokens:
                if ch in TokStr:
                    CTokStr = TokStr; type = Type; sidx = idx
                    break

            if SaveUkwn and sidx == -1:  res.append((PARSE_TYPE_UKWN, ch))
            idx += 1
        else:
            if ch not in CTokStr:
                res.append((type, Str[sidx:idx]));  sidx = -1
            else:
                idx += 1

    if sidx != -1:
        res.append((type, Str[sidx:idx]))

    return res

#-------------------------------------------------------------------------------
class Parser:
#-------------------------------------------------------------------------------
    def __init__(self, *args):
        self.ps = []
        for i in args:
            if len(i) != 3:
                self.ps.append((i[0], i[1], i[1]))
            else:
                self.ps.append(i)

    def ParseT(self, line):
        res = [];  idx = 0;  sidx = -1

        while idx < len(line):
            ch = line[idx]

            if sidx == -1:
                for Type, TokStr, CTokStr in self.ps:
                    if ch in TokStr:
                        type = Type; sidx = idx
                        break
                idx += 1
            else:
                if ch not in CTokStr:
                    res.append((type, line[sidx:idx]));  sidx = -1
                else:
                    idx += 1

        if sidx != -1:
            res.append((type, line[sidx:idx]))

        return res

    def ParseUT(self, line):
        res = [];  idx = 0;  sidx = -1

        while idx < len(line):
            ch = line[idx]

            if sidx == -1:
                for Type, TokStr, CTokStr in self.ps:
                    if ch in TokStr:
                        type = Type; sidx = idx
                        break

                if sidx == -1:  res.append((PARSE_TYPE_UKWN, ch))
                idx += 1
            else:
                if ch not in CTokStr:
                    res.append((type, line[sidx:idx]));  sidx = -1
                else:
                    idx += 1

        if sidx != -1:
            res.append((type, line[sidx:idx]))

        return res

    def Parse(self, line):
        return map(lambda s: s[1], self.ParseT(line))

    def ParseU(self, line):
        return map(lambda s: s[1], self.ParseUT(line))

#-------------------------------------------------------------------------------
class ParserPython(Parser):
#-------------------------------------------------------------------------------
    def __init__(self, *args):
        Parser.__init__(self, (PARSE_TYPE_SYM, PARSE_SYM), (PARSE_TYPE_STR, '"\''),
                (PARSE_TYPE_OP, "<>=!*/+-%&|~"), (PARSE_TYPE_WS, PARSE_WS),
                (PARSE_TYPE_CMNT, "#"))

    def ParseT(self, line):
        lst = Parser.ParseUT(self, line)

        state = 0;  op = '';  s = '';  lst1 = []
        for t, i in lst:
            if state == 0:
                if t == PARSE_TYPE_WS:
                    continue

                elif t == PARSE_TYPE_STR:
                    state = 1; op = i; s = i

                elif t == PARSE_TYPE_CMNT:
                    state = 2; s = '#'

                elif t == PARSE_TYPE_UKWN:
                    lst1.append((i, i))

                elif t == PARSE_TYPE_SYM:
                    if i[0] in PARSE_NUMBERS:
                        lst1.append((PARSE_TYPE_NUM, i))
                    elif i in ['and', 'or', 'not', 'in']:
                        lst1.append((PARSE_TYPE_OP, i))
                    else:
                        lst1.append((PARSE_TYPE_SYM, i))

                else:
                    lst1.append((t, i))

            elif state == 1:
                s += i
                if i == op:
                    state = 0
                    lst1.append((PARSE_TYPE_STR, s))
                    s = ''

            else:
                s += i

        if s: lst1.append((PARSE_TYPE_CMNT, s))

        return lst1

#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    import sys,string

    Tokens = [(PARSE_TYPE_SYM, PARSE_SYM), (PARSE_TYPE_OP, "+="), (PARSE_TYPE_WS, PARSE_WS)]

    if len(sys.argv) > 1:
        print Parse(string.join(sys.argv[1:]), Tokens)

    print Parse("""
cool           =


5
""", Tokens)

if __name__ == "__main__":
    main()
