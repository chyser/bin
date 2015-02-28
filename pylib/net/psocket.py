""" provide a wrapper for an SSL socket
"""

import socket

#-------------------------------------------------------------------------------
class SSLSocket(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, skt, keyfile=None, certfile=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(SSLSocket, self).__init__()
        self.skt = skt
        self.sslo = socket.ssl(skt, keyfile, certfile)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recv(self, bufsize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            try:
                buf = self.sslo.read(bufsize)
                return buf
            except socket.sslerror, err:
                if err[0] in [socket.SSL_ERROR_ZERO_RETURN, socket.SSL_ERROR_EOF]:
                    return ""
                if err[0] in [socket.SSL_ERROR_WANT_READ, socket.SSL_ERROR_WANT_WRITE]:
                    continue

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def send(self, output):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.sslo.write(output)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendall(self, output):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bw = 0
        while bw < len(output):
            bw += self.sslo.write(output[bw:])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self.skt, attr)


