#!/usr/bin/env python

"""
    usage: http_proxy.py [options]

    options:
        -v | --verbose  : dump out headers and other info
        -a | --addr   <host:port>  : set address, default ':%d'
        -p | --proxy  <host:port>  : set proxy for this proxy
        -x | --xclude <regex>      : don't proxy addresses matchuing regex

    version: %s
"""

import BaseHTTPServer, select, socket, SocketServer, urlparse, re
import pylib.osscripts as oss
import pylib.relib as relib

VERSION = "1.0"
DEFAULT_PORT = 8080

__doc__ = __doc__ % (DEFAULT_PORT, VERSION)

socket.setdefaulttimeout(10.0)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    """
    args, opts = oss.gopt(argv[1:], [('v', 'verbose')], [('a', 'addr'), ('p', 'proxy'), ('x', 'xclude')], __doc__ + main.__doc__)

    try:
        host, port = opts.addr.split(':')
    except AttributeError:
        host = ''; port = DEFAULT_PORT

    ProxyHandler.proxy = opts.proxy
    ProxyHandler.verbose = opts.verbose
    ProxyHandler.excludes = relib.reCmp(opts.xclude) if opts.xclude else None

    print ProxyHandler.excludes

    addr = (host, int(port))
    print 'Proxy on addr', addr
    httpd = ThreadingHTTPServer(addr, ProxyHandler)
    httpd.serve_forever()

    oss.exit(0)


#-------------------------------------------------------------------------------
def getHostPort(netloc, defPort=80):
#-------------------------------------------------------------------------------
    try:
        host, port = netloc.split(':')
    except:
        host, port = netloc, defPort

    return host, int(port)


#-------------------------------------------------------------------------------
class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
#-------------------------------------------------------------------------------
    server_version = "HTTPProxy/" + VERSION

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def do_CONNECT(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:

            ## should we send this request through a proxy?
            if self.proxy and not (self.excludes and self.excludes.eq(host)):
                host, port = getHostPort(self.proxy, defPort=DEFAULT_PORT)
            else:
                host, port = getHostPort(self.path)

            try:
                sock.connect((host, port))
            except (socket.timeout, socket.error) as ex:
                self.send_error(504, "proxy has timed out")
                return

            self.log_request(200)

            self.wfile.write("%s %s %s\r\n" % (self.protocol_version, 200, "Connection established"))
            self.wfile.write("Proxy-agent: %s\r\n" % self.version_string())
            self.wfile.write("\r\n")
            self._read_write(sock, 300)

        finally:
            sock.close()
            self.connection.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def do_GET(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        scm, netloc, path, params, query, fragment = urlparse.urlparse(self.path, 'http')

        if scm != 'http' or fragment or not netloc:
            self.send_error(400, 'bad url %s' % self.path)
            return

        host, port = getHostPort(netloc)

        ## should we send this request through a proxy?
        if self.proxy and not (self.excludes and self.excludes.eq(host)):
            print '$$$ PROXYING "%s"' % host
            host, port = getHostPort(self.proxy, defPort=DEFAULT_PORT)
            cmdUri = '%s %s %s\r\n' % (self.command, self.path, self.request_version)
        else:
            cmdUri = '%s %s %s\r\n' % (self.command, urlparse.urlunparse(('', '', path, params, query, '')), self.request_version)
            del self.headers['Proxy-Connection']

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            try:
                sock.connect((host, port))
            except (socket.timeout, socket.error) as ex:
                self.send_error(504, "proxy has timed out for '%s:%d'" % (host, port))
                return

            self.log_request()

            ## send the command
            sock.send(cmdUri)

            ## send the headers
            self.headers['Connection'] = 'close'
            for h, v in self.headers.items():
                s = '%s: %s\r\n' % (h, v)
                self.printit(">>", s.strip())
                sock.send(s)
            sock.send('\r\n')

            ## send the payload
            self._read_write(sock)

        finally:
            sock.close()
            self.connection.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _read_write(self, sock, max_idling=20):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.headers.has_key('Content-Length'):
            data = self.rfile.read(int(self.headers['Content-Length']))
        else:
            self.connection.setblocking(0)
            try:
                data = self.rfile.read()
            except IOError:
                data = ''
            self.connection.setblocking(1)
        self.rfile.close()

        if data:
            sock.send(data)

        socketList = [self.connection, sock]
        self.headers_done = 0

        count = 0
        while 1:
            count += 1
            inList, _, exList = select.select(socketList, [], socketList, 3)

            if exList:
                break

            elif inList:
                for sockObj in inList:
                    data = sockObj.recv(8192)
                    if data:
                        out = self.connection if sockObj is sock else sock
                        self.dump_headers(data)
                        out.send(data)
                        count = 0

            else:
                self.printit("idle: %d" % count)

            if count > max_idling: break

    rx_hdr = re.compile("^([a-zA-Z\-0-9]+):\W+(.*)$")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump_headers(self, data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.headers_done:
            return

        for line in data.split("\n"):
            line = line.strip()

            if not line:
                self.headers_done = True
                self.printit()
                return

            m = self.rx_hdr.match(line)

            if m:
                k, v = m.groups()
                self.printit("<< %s: %s" % (k, v))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printit(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.verbose:
            for a in args:
                print a,
            print


    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass


if __name__ == "__main__":
    main(oss.argv)

