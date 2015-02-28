#!/usr/bin/env python
"""
usage:

"""

import re
import socket
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    if len(args) != 2:
        usage(1, "Must supply file and host")

    if args[0] == '-':
        inf = oss.stdin
    else:
        inf = file(args[0], 'rb')

    buf = re.sub("\r\n", "\n", inf.read())
    inf.close()

    host = args[1]

    if buf:
        print "Sending:"
        print buf
        print
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 15153))
        s.sendall(buf)
        s.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 15154))

    buf = s.recv(4096)
    s.close()
    print "Received:"
    print buf


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

