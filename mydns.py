#!/usr/bin/env python
"""
usage:

"""

DOMAIN = 'work'

DNS_DATABASE = {
    'littleboy' : '192.168.1.102',
    'bigboy'    : '192.168.1.100',
    'sles10'    : '192.168.1.93',
    'xen1'      : '192.168.1.92',
    'taopooh'   : '192.168.1.30',
    'vm001'     : '192.168.1.95',
    'vm002'     : '192.168.1.96',
    'vm003'     : '192.168.1.97',
}



import pylib.osscripts as oss
#import pylib.relib as relib

import pprint as pp

import socket

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
class DNSQuery:
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.data = data
        self.dominio = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        opcode = (ord(self.data[2]) >> 3) & 0xf  # Opcode bits

        if opcode == 0:   # Standard query

            idx = 12
            while 1:
                ## check label length
                ln = ord(self.data[idx])
                if ln == 0: break

                self.dominio += self.data[idx + 1:idx + ln + 1] + '.'
                idx += ln + 1

            return self.dominio
        else:
            print '\n$$$$ unhandled type:', opcode

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def response(self, ip_name, ptr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        packet = ''

        aRec = not ptr

        ## generate header
        packet += self.data[:2] + "\x84\x80"
        packet += self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'  # Questions and Answers Counts

        ## copy original question
        packet += self.data[12:]

        ## create answer
        packet += '\xc0\x0c'               # Pointer to domain name

        if aRec:
            packet += '\x00\x01'           # response type - A record
        else:
            packet += '\x00\x0c'           # response type - PTR record

        packet += '\x00\x01'               # class (IN)
        packet += '\x00\x00\xff\x3c'       # ttl

        if aRec:
            packet += '\x00\x04'
            packet += str.join('', map(lambda x: chr(int(x)), ip_name.split('.')))
        else:
            assert len(ip_name) <= 63

            packet += '\x00' + chr(len(ip_name) + 2)
            packet += chr(len(ip_name))
            packet += ip_name
            packet += '\x00'

        return packet

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def error(self, code):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## generate header
        packet = self.data[:2] + "\x81"
        packet += chr(0x80 | code)
        packet += '\x00\x00\x00\x00\x00\x00\x00\x00'   # Questions and Answers Counts

        return packet

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self, packet):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx = 0
        print
        for i in packet:
            if idx != 0 and idx % 16 == 0:
                print
            idx += 1
            print '%02x' %int(ord(i)),
        print '\n'


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    #
    # set up database creating reverse mappings and some aliases
    #
    db = dict(DNS_DATABASE)
    for name, addr in DNS_DATABASE.items():
        a, b, c, d = addr.split('.')
        db[d + '.' + c + '.' + b + '.' + a + '.in-addr.arpa.'] = (name + '.work.', 1)
        db[name + '.work.'] = (addr, 0)
        db['m' + d + '.work.'] = (addr, 0)
        db['h' + d + '.work.'] = (addr, 0)

    pp.pprint(db)
    print

    #
    # start server
    #
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('', 53))

    try:
        while 1:
            data, addr = udps.recvfrom(1024)
            p = DNSQuery(data)

            query = p.parse()
            print '---\nQuery: ' + query

            if query in db:
                ip_name, ptr = db[query]
                resp = p.response(ip_name, ptr)
                #p.dump(resp)
                udps.sendto(resp, addr)
                print 'Response: %s -> %s' % (query, ip_name)

            else:
                udps.sendto(p.error(3), addr)


    except KeyboardInterrupt:
        udps.close()

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

