#!/usr/bin/env python
"""
usage:

"""

import datetime

import pylib.osscripts as oss
import pylib.imapobj as imo
import pylib.emaillib as eml
import pylib.relib as relib
import pylib.net.util as nu

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main1(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    #mb = imo.IMAPServer('kirby.fc.hp.com', 'chrish', 'kibsop)')
    mb = imo.IMAPServer('mail.hp.com', 'chris_hyser@hp.com', 'kibsop)')
    print mb.version
    print mb.capability()

    print 'Num Messages', mb.numMsgs

    chk = relib.reHas('chrish@fc.hp.com|[hH]yser')
    for msgSeqNum in range(1, mb.numMsgs):
        hdr = mb.getMsgHdr(msgSeqNum)

        #if msgSeqNum >= 52:
        #    print hdr['to']

        tl = hdr.toList()
        if len(tl) != 1:
            continue

        #print msgSeqNum, tl[0]
        if chk.isIn(tl[0]):
            mb.store(msgSeqNum, '+FLAGS', '(\\Flagged)')
            #print "-----------------------------------------------------------"
            #print 'date:', hdr["date"]
            #print "subject:", hdr['subject']
            #print 'to:', hdr['to']
            #print hdr.flags
            print msgSeqNum

    mb.close()

    oss.exit(0)

#-------------------------------------------------------------------------------
def main1(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    mb = imo.IMAPServer('kirby.fc.hp.com', 'chrish', 'kibsop)')
    mb.store('1:*', '-FLAGS', '(\\Flagged)')


#-------------------------------------------------------------------------------
def HouseKeeping(mb):
#-------------------------------------------------------------------------------
    ## copy the deleted from INBOX
    print "cleaning up INBOX"
    mb.copy(mb.search('DELETED'), 'Trash')
    mb.expunge()

    for s in mb.listMailboxes():
        if s not in ['INBOX', 'Trash']:
            try:
                mb.select(s)
                print "cleaning up", s
                mb.copy(mb.search('DELETED'), 'Trash')
                mb.expunge()
            except:
                pass

    ## make them visible in Trash
    mb.select('Trash')
    mb.delFlags('\\Deleted')

    mb.select()


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    if nu.ping('kirby.fc.hp.com'):
        mb = eml.IMAPMailReceiver('kirby.fc.hp.com', 'chrish', 'kibsop)')
    else:
        mb = eml.IMAPMailReceiver('mail.hp.com', 'chris_hyser@hp.com', 'Olyprocodo(50)')

    today = datetime.date.today()

    cache = {}
    day = 0
    while 1:
        print
        idx = 0

        if day in cache:
            hdrs = cache[day]
        else:
            hdrs = cache[day] = mb.getDatedHdrs(today - datetime.timedelta(day))

        print today - datetime.timedelta(day)
        for hdr in hdrs:
            print ('%02d: "%s",  %s' % (idx, hdr['subject'], hdr['from']))[:110]
            idx += 1

        cmd = raw_input("msg # ")
        try:
            if '.' in cmd:
                mn, imb = cmd.split('.', 1)
                msg = hdrs[int(mn)].getMsg(imb)
            else:
                msg = hdrs[int(cmd)].getMsg()
            print msg.as_string()
            #print msg.get_content_type()

        except ValueError:
            pass

        if cmd == 'q':
            break
        elif cmd == 'n':
            day += 1
        elif cmd == 'p':
            if day > 0: day -= 1
        elif cmd == 'lmb':
            print mb.listMailboxes()
        elif cmd.startswith('cp '):
            cp, msg, mailbox = cmd.split(' ', 2)
            ml = []
            for m in msg.split(','):
                if ':' in m:
                    s, e = m.split(':')
                    ml.append(hdrs[int(s)] + ':' + hdrs[int(e)])
                else:
                    ml.append(hdrs[int(m)])

            print 'cp %s "%s"' % (ml, mailbox)

        elif cmd == "cleanup":
            HouseKeeping(mb)
        elif cmd == 'refresh':
            cache.clear()




#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

