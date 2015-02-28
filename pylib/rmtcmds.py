#!/usr/local/bin/python

import time

#-------------------------------------------------------------------------------
def usage(err):
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


try:
    import pexpect

    #-------------------------------------------------------------------------------
    def hndlResponse(c, passwd):
    #-------------------------------------------------------------------------------
        while 1:
            i = c.expect([
                    ".*connecting.*\(yes/no\)\?",   # 0
                    "(?i)[Pp]assword:",             # 1
                    "port 22: No route to host",    # 2
                    "ssh: connect to host.*",       # 3
                    pexpect.EOF,                    # 4
                    pexpect.TIMEOUT                 # 5
                    ])

            if i == 0:
                c.sendline("yes")
            elif i == 1:
                c.sendline(passwd)
            elif i == 4:
                return c.before
            else:
                return None

    #-------------------------------------------------------------------------------
    def run(mach, cmd, user = "", passwd = "", timeout = 30):
    #-------------------------------------------------------------------------------
        if user: user += "@"

        c = pexpect.spawn("ssh %s%s %s" % (user, mach, cmd), timeout=timeout)
        return hndlResponse(c, passwd)

    #-------------------------------------------------------------------------------
    def cpt(mach, srcFiles, dest, options = "", user = "", passwd = "", timeout = 300):
    #-------------------------------------------------------------------------------
        if user: user += "@"

        c = pexpect.spawn("scp %s %s %s%s:%s" % (options, srcFiles, user, mach, dest), timeout=timeout)
        return hndlResponse(c, passwd)

    #-------------------------------------------------------------------------------
    def cpf(mach, srcFiles, dest, options = "", user = "", passwd = "", timeout = 300):
    #-------------------------------------------------------------------------------
        if user: user += "@"

        c = pexpect.spawn("scp %s %s%s:%s %s" % (options, user, mach, srcFiles, dest), timeout=timeout)
        return hndlResponse(c, passwd)

except ImportError:
    import pylib.osscripts as oss

    if oss.exists("C:/Program Files/OpenSSH/bin/scp.exe"):
        SCP = '"C:/Program Files/OpenSSH/bin/scp.exe"'
        SSH = '"C:/Program Files/OpenSSH/bin/ssh.exe"'
    else:
        SCP = "scp"
        SSH = "ssh"

    #-------------------------------------------------------------------------------
    def run(mach, cmd, user = "", passwd = "", timeout = 30):
    #-------------------------------------------------------------------------------
        if user: user += "@"
        print "here1"
        oss.r(SSH + " %s%s %s" % (user, mach, cmd))

    #-------------------------------------------------------------------------------
    def cpt(mach, srcFiles, dest, options = "", user = "", passwd = "", timeout = 300):
    #-------------------------------------------------------------------------------
        if user: user += "@"
        print "here"
        oss.r(SCP + " %s %s %s%s:%s" % (options, srcFiles, user, mach, dest))

    #-------------------------------------------------------------------------------
    def cpf(mach, srcFiles, dest, options = "", user = "", passwd = "", timeout = 300):
    #-------------------------------------------------------------------------------
        if user: user += "@"
        oss.r(SCP + " %s %s%s:%s %s" % (options, user, mach, srcFiles, dest))


#-------------------------------------------------------------------------------
class RmtMach(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, mach, user="", passwd="", timeout=30):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mach = mach
	self.user = user
	self.passwd = passwd
	self.timeout = timeout

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return run(self.mach, cmd, self.user, self.passwd, self.timeout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cpt(self, srcFiles, dest, options="", timeout=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if timeout is None:
	    timeout = self.timeout
        return cpt(self.mach, srcFiles, dest, options, self.user, self.passwd, timeout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cpf(self, srcFiles, dest, options="", timeout=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if timeout is None:
	    timeout = self.timeout
        return cpf(self.mach, srcFiles, dest, options, self.user, self.passwd, timeout)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import osscripts as oss


    args, opts = oss.gopt(oss.argv[1:], [], [('l', 'login'), ('p', 'passwd')], usage)

    if len(args) < 2:
        usage(1)

    if opts.login is None:
        opts.login = ""

    if opts.passwd is None:
        opts.passwd = ""

    s = cpt(args[0], " ".join(args[1:-1]), args[-1], opts.login, opts.passwd)
    print s
    oss.exit(0)

    res = run(args[0], " ".join(args[1:]), opts.login, opts.passwd)
    if res:
        print res
        oss.exit(0)

    print "Machine Down"
    oss.exit(1)


