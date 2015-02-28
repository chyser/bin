#!/usr/bin/env python

import sys
import time
import pexpect
import os
import signal


def getpid(name):
    import subprocess, signal
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    l = []
    for line in out.splitlines():
        if name in line:
            l.append(int(line.split(None, 1)[0]))

    return l


def sigHandler(signum, frame):
    print "handler %d" % signum

    pid = getpid("openconnect")[0]
    #os.kill(pid, signal.SIGKILL)
    os.system("sudo kill -9 %d" % pid)
    os.system("sudo ifdown p2p1")
    os.system("sudo ifup p2p1")


signal.signal(signal.SIGINT, sigHandler)

while 1:
    print "\n" + '-'*80
    print "Logging in: '%s'" % time.ctime()

    p = pexpect.spawn("sudo /usr/sbin/openconnect -u chyser_us https://myaccess.oraclevpn.com")
    i = p.expect(["chrish's password:", 'Password:'])
    sys.stdout.write(p.before)

    if i == 0:
        p.sendline('kibsop)')
        p.expect([ 'Password:'])
        sys.stdout.write(p.before)

    #p.sendline('3MC9QCYIcTprJBMx')
    #p.sendline('2D+SW4TBjifkDFeK')
    #p.sendline('5M+9W7YBcifrDKg3')
    #p.sendline('EdG5Om85BNtsJ')
    #p.sendline('T2uthodc')
    p.sendline('yTVFWvkCFcaJZ1Nh')

    while 1:
        try:
            s = p.read_nonblocking(1, None)
            sys.stdout.write(s)
        except pexpect.EOF:
            break
        except AttributeError:
            break

    try:
        p.wait()
    except pexpect.ExceptionPexpect:
        pass


