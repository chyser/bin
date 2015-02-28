#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import socket
import base64


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: sslprobe.py <host_name> <port>
    """

    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    if len(args) != 2:
        opts.usage(1, 'must specify a host and port')

    HOST = args[0]
    PORT = int(args[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s = socket.ssl(s)
    print('connected')

    #s.send('\n')

    while 1:
        data = s.read(1024)
        try:
            t = data.split()
            if len(t) > 1:
                val = base64.b64decode(t[1])
                print('S: ', data, val)
            else:
                print('S: ', data)

        except TypeError:
            print('S: ', data)

        ch = raw_input('C: ')
        if ch[0] == '\\':
            v = base64.b64encode(ch[1:])
            print('//', v, base64.b64decode(v))
            s.write(v + '\r\n')
        else:
            s.write(ch + '\r\n')

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
