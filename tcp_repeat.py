#!/usr/bin/env python
"""
usage: tcp_repeat.py [options] <dest:port>

options:
    -p | --port   : specify port to listen on (default: 50007)

listens on the specified port. displays and forwards incoming and outgoing
data to/from the destination addr/port

"""

import socket as s
import pylib.osscripts as oss

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
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('p', 'port')], usage)

    lport = 50007 if opts.port is None else int(opts.port)

    print 'listening on port:', lport

    addr, port = args[0].strip().split(':')
    port = int(port)

    print 'connecting to:', addr, port

    sout = s.socket(s.AF_INET, s.SOCK_STREAM)
    sin = s.socket(s.AF_INET, s.SOCK_STREAM)

    sin.bind(('', lport))
    sin.listen(1)

    while 1:
        conn, d = sin.accept()
        conn.settimeout(1.5)

        sout = s.socket(s.AF_INET, s.SOCK_STREAM)
        sout.connect((addr, port))
        sout.settimeout(1)

        while 1:

            try:
                print '>>'
                data = conn.recv(128*4096)
                if not data:
                    break
            except s.timeout:
                break

            print '>> ============================================================='
            print data

            sout.send(data)

            print '<<'
            try:
                data = sout.recv(128*4096)
                if not data:
                    break
            except s.timeout:
                break

            print '<< ---------------------------------------------'
            print data

            try:
                conn.send(data)
            except s.error:
                pass

        sout.close()
        conn.close()


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

