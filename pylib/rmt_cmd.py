#!/usr/local/bin/python

import osscripts

RMT_USER = 'root'
RMT_PASSWD = 'tuscany'

#-------------------------------------------------------------------------------
def __Usage(err):
#-------------------------------------------------------------------------------
    import sys
    print >> sys.stderr, """
usage: rmt_cmt [-l <login name>] [-p <passwd>] <machine> <command>
 - execute command on machine using default or provided login and passwd info
   -l | --login  : acct
   -p | --passwd : passwd
   -? | --help   : this message
"""
    sys.exit(err)

import pexpect

#-------------------------------------------------------------------------------
def RunRmtCmd(Mach, Cmd, Acct = None, Passwd = None):
#-------------------------------------------------------------------------------
    if Acct is None:
        Acct = RMT_USER
    if Passwd is None:
        Passwd = RMT_PASSWD

    c = pexpect.spawn("ssh -l %s %s %s" % (Acct, Mach, Cmd))
    while 1:
        try:
            i = c.expect(["%s@%s's password:" % (Acct, Mach), "connecting (yes/no)?", pexpect.EOF, "port 22: No route to host"])
        except:
            i = -1

        if i == 0:
            c.sendline(Passwd)
        elif i == 1:
            c.sendline("yes")
        elif i == 2:
            return(True, c.before)
        else:
            return(False, "")

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import osscripts

    args, opts = osscripts.gopt(osscripts.argv[1:], [('?', 'help')], [('l', 'login'), ('p', 'passwd')], __Usage)

    if opts.help or len(args) != 2:
        __Usage(1)

    stat, res = RunRmtCmd(args[0], args[1], opts.login, opts.passwd)
    if stat:
        print res
        osscripts.exit(0)

    print "Machine Down"
    osscripts.exit(1)

