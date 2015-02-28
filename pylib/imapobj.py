#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss
import imaplib
import email.message
import email.parser
import pylib.lex as lex

#-------------------------------------------------------------------------------
class EmailMessage(email.message.Message):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        email.message.Message.__init__(self)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test(self, tl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lx = lex.SLex([lex.STRING, ',', "[_a-zA-Z0-9][-_a-zA-Z0-9]*", '\\(.*\\)', '<.*>'] )
        lx.add(['@', ':', ';', '.'])
        return lx.lex(tl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def toList(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tl = self['to']
        if tl is None:
            return []

        lx = lex.SLex([lex.STRING, ',', "[_@a-zA-Z0-9][-_@\\.a-zA-Z0-9]*", '\\(.*\\)', '<.*>'] )
        lx.add([':', ';'])

        lst = []
        l = []
        for tok in lx.lex(tl):
            if tok == ',':
                lst.append(' '.join(l))
                l = []
            else:
                l.append(tok)

        if l:
            lst.append(' '.join(l))
        return lst

#-------------------------------------------------------------------------------
class IMAPSpecific(EmailMessage):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        EmailMessage.__init__(self)
        self.flags = None
        self.msgid = None
        self.server = None

#-------------------------------------------------------------------------------
class IMAPMessage(IMAPSpecific):
#-------------------------------------------------------------------------------
    pass

#-------------------------------------------------------------------------------
class IMAPMsgHdr(IMAPSpecific):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getMsg(self, imb=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.server.getMsg(self.msgid, imb)

#-------------------------------------------------------------------------------
class IMAPServerException(Exception):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Exception.__init__(self, s)

#-------------------------------------------------------------------------------
class IMAPServer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, server, user, passwd, SSL=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        if SSL:
            self.mb = imaplib.IMAP4_SSL(server)
        else:
            self.mb = imaplib.IMAP4(server)

        self.mb.login(user, passwd)
        self.select()
        self.version = self.mb.PROTOCOL_VERSION

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def select(self, mailbox='INBOX'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = self.mb.select(mailbox)
        if d[0] == 'NO':
            raise IMAPServerException(d[1][0])
        self.numMsgs = int(d[1][0])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getMsgHdr(self, num):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        num = str(num)
        typ, data = self.mb.fetch(num, '(FLAGS RFC822.HEADER)')
        hdr = data[0][1]
        imh = email.parser.Parser(IMAPMsgHdr).parsestr(hdr, True)
        imh.msgid = num
        imh.flags = imaplib.ParseFlags(data[0][0])
        imh.server = self
        return imh


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseBody(self, bd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx = 0

        stack = []
        root = []
        cur = root
        stack.append(cur)
        for t in lex.Parse(bd, ['(', ')'], [lex.SLex.STRING, lex.SLex.SYMBOL, lex.SLex.INTEGER])[3:]:
            if t == '(':
                stack.append(cur)
                l = []
                cur.append(l)
                cur = l
            elif t == ')':
                cur = stack.pop(-1)
            else:
                cur.append(t)

        def disp(lst, idx = 0):
            simple = True
            for n in lst:
                if isinstance(n, list):
                    if not isinstance(n[-1], list) and n[-1] in ['"ALTERNATIVE"', '"MIXED"']:
                        print ">>", n[-1]
                        simple = False
                    simple = disp(n, idx + 1) and simple
                    print
                else:
                    print ('    '*idx) + n
            return simple

        print "---------"
        v = disp(root)
        print "---------"
        return v

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getMsg(self, num, mimeimb=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        num = str(num)
        typ, data = self.mb.fetch(num, '(BODY)')
        simple = self.parseBody(data[0])

        if simple:
            mimeimb = 1

        if mimeimb is not None:
            typ, data = self.mb.fetch(num, '(BODY[%s])' % mimeimb)
            #typ, data = self.mb.fetch(num, '(BODY[])')

            hdr = data[0][1]
            imh = email.parser.Parser(IMAPMessage).parsestr(hdr, True)
            imh.msgid = num
            imh.flags = imaplib.ParseFlags(data[0][0])
            imh.server = self
            return imh
        else:
            return IMAPMessage()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def msgSeqNum(self, n):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(n, (list, tuple)):
            return ','.join([str(i) for i in n])
        return str(n)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self, ms, mailbox):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mb.copy(self.msgSeqNum(ms), mailbox)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def search(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ search the mailbox with args
            returns a list of msgids

            Search Keys:
                'ALL'
                'SINCE "1-Oct-2007"'
        """
        a = ' '.join(args)
        typ, data = self.mb.search(None, '(' + a + ')')
        return data[0].split()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def capability(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ, data = self.mb.capability()
        return data

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def store(self, ms, cmd, fl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mb.store(self.msgSeqNum(ms), cmd, fl)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if attr in self.__dict__:
            return self.__dict__[attr]
        return getattr(self.mb, attr)



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mb.close()
        self.mb.logout()

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])

    em = EmailMessage()
    em.toList()

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

