#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss
import pylib.imapobj as imo

import smtplib
import socket
import datetime

#-------------------------------------------------------------------------------
class SMTPError(Exception):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Exception.__init__(self, s)

#-------------------------------------------------------------------------------
class MailReceiver(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)


#-------------------------------------------------------------------------------
class IMAPMailReceiver(MailReceiver):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, server, user, passwd, SSL=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.mb = imo.IMAPServer(server, user, passwd, SSL)
        print self.mb.version
        print self.mb.capability()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDatedHdrs(self, dateStr=None, cmd = 'ON', seeDeleted=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if dateStr is None:
            dateStr = datetime.date.today()

        if isinstance(dateStr, (datetime.datetime, datetime.date)):
            dateStr = "%2d-%s-%4d" % (dateStr.day, [None, "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][dateStr.month], dateStr.year)

        #print dateStr

        delstr = ('UNDELETED' if not seeDeleted else '')

        hdrs = []
        for msgSeqNum in self.mb.search('%s %s "%s"' % (delstr, cmd, dateStr)):
            hdr = self.mb.getMsgHdr(msgSeqNum)
            if seeDeleted:
                hdrs.append(hdr)
            else:
                if '\\Deleted' not in hdr.flags:
                    hdrs.append(hdr)
        return hdrs

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addFlags(self, flags, msn='1:*'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(flags, (str, unicode)):
            flags = ' '.join(flags)
        self.mb.store(msn, '+FLAGS', flags)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delFlags(self, flags, msn='1:*'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(flags, (str, unicode)):
            flags = ' '.join(flags)
        self.mb.store(msn, '-FLAGS', flags)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def replaceFlags(self, flags, msn='1:*'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(flags, (str, unicode)):
            flags = ' '.join(flags)
        self.mb.store(msn, 'FLAGS', flags)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def listMailboxes(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        m = []
        for t in self.mb.lsub()[1]:
            if t[-1] == '"':
                idx = t.rfind('"', 0, -1)
                m.append(t[idx+1:-1])
            else:
                m.append(t.split()[2])
        return m

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def select(self, mailbox='INBOX'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mb.select(mailbox)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self, msgids, mailbox):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert mailbox in self.listMailboxes()
        self.mb.copy(msgids, mailbox)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def search(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.mb.search(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expunge(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mb.expunge()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class SMTPClient(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, server="localhost", transport=None, login=None, port=None, debug=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        if transport == 'TLS' or transport == 'SSL':
            secure = True
            if port is None:
                port = 465
        elif transport is None:
            secure = False
            if port is None:
                port = 25
        else:
            raise SMTPError("Illegal Transport")

        self.server = smtplib.SMTP()
        if debug:
            self.server.set_debuglevel(debug)

        try:
            v = self.server.connect(server, port, secure)
            if debug: print v
        except socket.error, se:
            raise SMTPError(se)

        #if secure:
        #    v = self.server.starttls()
        #    if debug: print v

        if login is not None:
            v = self.server.login(*login)
            if debug: print v


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def debug(self, val=2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.server.set_debuglevel(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendMsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.server.sendmail(msg['From'], msg['To'], msg.as_string())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendmail(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.server.sendmail(*args, **kwds)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.server.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)



#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])




    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

