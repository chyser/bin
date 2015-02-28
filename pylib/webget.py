#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import socket
import urllib
import shutil

import pylib.osscripts as oss
import pylib.net.util as pnet
import pylib.net.psocket as psocket


#-------------------------------------------------------------------------------
def GetHdr(skt, verbose=False):
#-------------------------------------------------------------------------------
    """ gets an HTTP header
        returns, response, hdr dict, and additional data
    """
    data = ""
    while 1:
        data += skt.recv(4096)

        if verbose:
            print(data, file=oss.stderr)

        idx = data.find('\r\n\r\n')
        if idx != -1:
            hdr = data[:idx+4].split('\r\n')
            data = data[idx+4:]

            hdrdict = {}
            for h in hdr[1:-2]:
                try:
                    k, v = h.split(': ', 1)
                except ValueError as ex:
                    print(ex, file=oss.stderr)
                hdrdict[k.lower()] = v

            return hdr[0], hdrdict, data


#-------------------------------------------------------------------------------
def GetPage(args, outFileName=None, binary=False, hdrs=None, verbose=0):
#-------------------------------------------------------------------------------
    print('getPage:', outFileName)

    sa, tp = pnet.ArgsToAddrPort(args)

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect(sa)

    ## see if SSL
    if tp[0] == "https":
        skt = psocket.SSLSocket(skt)

    if hdrs:
        hs = []
        for h, v in hdrs.items():
            hs.append('%s: %s' % (h, v))

        hs = '\r\n' + '\r\n'.join(hs)
    else:
        hs = ''

    if verbose:
        print("GET %s HTTP/1.0%s\r\n\r\n" % (tp[1], hs), file=oss.stderr)
    skt.send("GET %s HTTP/1.0%s\r\n\r\n" % (tp[1], hs))

    ## get header
    rsp, hdr, data = GetHdr(skt, verbose)

    if outFileName is not None:
        if binary or hdr['content-type'] != 'text/html':
            otf = open(outFileName, "wb")
        else:
            otf = open(outFileName, "w")
    else:
        otf = oss.stdout

    ln = len(data)
    if data:
        otf.write(data)

    ## get data
    while 1:
        data = skt.recv(4096)
        if data:
            ln += len(data)
            otf.write(data)
            if verbose > 1:
                print(data, file=oss.stderr)
            if not verbose: print('.', end='', file=oss.stderr)
        else:
            break

    if verbose: print(file=oss.stderr)
    skt.close()
    if otf != oss.stdout:
        otf.close()


#-------------------------------------------------------------------------------
def GetPageUrlLib(url, outFileName=None, binary=None, verbose=False):
#-------------------------------------------------------------------------------
    if verbose:
        print("opening:", url, outFileName)
    inf = urllib.urlopen(url)

    otf = oss.stdout if outFileName is None else open(outFileName, "w")
    shutil.copyfileobj(inf, otf)

    if otf != oss.stdout:
        otf.close()


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


if __name__ == "__main__":
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

