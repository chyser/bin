#!/usr/bin/env python
"""
usage: httpcmd [OPTIONS] <URL>

Send an http command to the URL. Cmds include 'get', 'put', 'post' etc. The
default 'cmd' is 'GET'. Then dumps the returned status code, headers and body
data to stdout.

Options:
    -c | --cmd  : specifies the cmd, default is 'GET'
    -m | --msg  : specifies the body of a 'PUT' or 'POST' cmd. Use \n to represent
                  line breaks or specify each line with a -m.
    -h | --hdr  : specifies a single HTTP hdr. This option may be used more than
                  once

    -v | --verbose : prints lots of output

"""

import socket
import urllib
import shutil

import pylib.osscripts as oss
import pylib.net.util as pnet
import pylib.util as util
import pylib.net.psocket as psocket

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
class httpHdr(dict):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(httpHdr, self).__init__(*args)
        self.isBinary = False
        self.responseCode = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "binary: " + str(self.isBinary) + "\nresp: " + self.responseCode + "\n" + dict.__str__(self)

#-------------------------------------------------------------------------------
def getHdr(skt, verbose = False):
#-------------------------------------------------------------------------------
    """ gets an HTTP header
        returns, response, hdr dict, and additional data
    """
    data = ""

    wh = httpHdr()

    while 1:
        d = skt.recv(4096)

        if not d:
            wh.responseCode = data
            return wh, ''

        data += d
        idx = data.find('\r\n\r\n')

        if idx != -1:
            hdr = data[:idx+4].split('\r\n')
            data = data[idx+4:]

            for h in hdr[1:]:
                try:
                    k, v = h.split(': ', 1)
                    wh[k.lower()] = v
                except ValueError:
                    print >> oss.stderr, h

            try:
                wh.isBinary = wh['content-type'] != 'text/html'
            except KeyError:
                wh.isBinary = False

            wh.responseCode = hdr[0]
            return wh, data



#-------------------------------------------------------------------------------
def httpCmd(mach_ip, port, protocol, path, cmd = 'GET', hdrs = None, verbose = False):
#-------------------------------------------------------------------------------
    """ downloads from a URL

        URL: protocol + "://" + mach_ip + ":" + str(port) + path

        returns a httpHdr and a data string
    """
    assert protocol in ["http", "shttp"]
    assert cmd in ['GET', 'HEAD', 'TRACE', 'OPTIONS', 'DELETE']

    if verbose:
        print "URL: " + protocol + "://" + mach_ip + ":" + str(port) + path

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((mach_ip, port))

    ## see if SSL
    if protocol == "https":
        skt = psocket.SSLSocket(skt)

    if hdrs is None:
        hdrs = ''
    else:
        hdrs = '\r\n' + '\r\n'.join(hdrs)

    pkt = "%s %s HTTP/1.0%s\r\n\r\n" % (cmd, path, hdrs)
    if verbose:
        print pkt

    skt.send(pkt)

    return httpGetSkt(skt, verbose)

#-------------------------------------------------------------------------------
def httpGetSkt(skt, verbose=False):
#-------------------------------------------------------------------------------
    """ gets HTTP data from an open socket
    """

    #
    # get header
    #
    hdr, data = getHdr(skt, verbose)
    buf = []

    ln = len(data)
    if data:
        buf.append(data)

    #
    # get data
    #
    while 1:
        data = skt.recv(4096)
        if data:
            ln += len(data)
            buf.append(data)
            if not verbose: print '.',
        else:
            break

    if verbose:
        print "Bytes Transfered:", ln

    skt.close()
    return hdr, ''.join(buf)

#-------------------------------------------------------------------------------
def httpPutPost(mach_ip, port, protocol, path, cmd = 'PUT', data = None, hdrs = None, verbose = False):
#-------------------------------------------------------------------------------
    """ uploads to a URL using 'cmd' equal 'PUT' or 'POST'

        URL: protocol + "://" + mach_ip + ":" + str(port) + path

        returns
    """

    assert protocol in ["http", "shttp"]
    assert cmd in ['PUT', 'POST']

    if verbose:
        print "URL: " + protocol + "://" + mach_ip + ":" + str(port) + path

    if data is None:
        data = ''
    else:
        data = util.CvtNewLines(data, '\r\n')

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    skt.connect((mach_ip, port))

    ## see if SSL
    if protocol == "https":
        skt = psocket.SSLSocket(skt)

    if hdrs is None:
        hdrs = ''
    else:
        hdrs = '\r\n' + '\r\n'.join(hdrs)

    pkt = "%s %s HTTP/1.0\r\nContent-type: text/plain\r\nContent-length: %d%s\r\n\r\n%s\r\n" % (cmd, path, len(data), hdrs, data)
    if verbose:
        print pkt

    skt.send(pkt)

    return httpGetSkt(skt, verbose)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('v','verbose')], [('h', 'hdr'), ('m', 'msg'), ('c','cmd')], usage)

    sa, tp = pnet.ArgsToAddrPort(args)

    if opts.msg:
        if isinstance(opts.msg, list):
            opts.msg = '\r\n'.join(opts.msg)
        else:
            opts.msg = util.CvtNewLines(opts.msg, '\r\n')

    if opts.hdr:
        opts.hdr = list(opts.hdr)

    if opts.cmd is None:
        opts.cmd = 'GET'
    else:
        opts.cmd = opts.cmd.upper()


    if opts.cmd in ['PUT', 'POST']:
        hdr, s = httpPutPost(sa[0], sa[1], tp[0], tp[1], opts.cmd, opts.msg, opts.hdr, opts.verbose)
    else:
        hdr, s = httpCmd(sa[0], sa[1], tp[0], tp[1], opts.cmd, opts.hdr, opts.verbose)

    print hdr
    print s

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


