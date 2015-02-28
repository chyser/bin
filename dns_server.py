#!/usr/bin/env python
"""
usage:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

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


import pprint
import socket

import pylib.osscripts as oss
import pylib.bitfields as pbf

import dns

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])

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

    pprint.pprint(db)
    print()

    ## start server
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('', 53))

    try:
        while 1:
            data, addr = udps.recvfrom(1024)
            data = pbf.BitField(data)

            opcode, query = getQuery(data)
            query = unicode(query)

            print('---\nQuery: ', opcode, '-> "%s"' %  query)

            if opcode != 0:
                udps.sendto(genError(4, data), addr)
                continue

            if query in db:
                ip_name, ptr = db[query]
                resp = genResponse(ip_name, ptr, data)
                udps.sendto(resp, addr)
                print('Response: %s -> %s' % (query, ip_name))

            else:
                err, aa, addrs, aliases = dns.sendDNSQuery(query[:-1], '192.168.1.1')
                if err == 0:
                    resp = genResponse(addrs[0], 0, data)
                    udps.sendto(resp, addr)
                    print('Response: %s -> %s' % (query, addrs[0]))
                else:
                    udps.sendto(genError(3, data), addr)


    except KeyboardInterrupt:
        udps.close()

    oss.exit(0)



#-------------------------------------------------------------------------------
def getQuery(data):
#-------------------------------------------------------------------------------
    opcode = data.getBits(2, 3, 6)
    if opcode == 0:
        idx, name = dns.getCNAME(12, data)
    else:
        name = ''

    return opcode, name + '.'


#-------------------------------------------------------------------------------
def genResponse(ip_name, ptrRec, data):
#-------------------------------------------------------------------------------
    packet = pbf.BitField(12)

    aRec = not ptrRec

    ## generate header
    packet[:2] = data[:2]
    packet[2] = 0x84
    packet[3] = 0x80
    packet.setM(4, 2, 1)
    packet.setM(6, 2, 1)

    ## copy original question
    packet.extend(data[12:])

    ## create answer
    packet.append(0xc0)     # use pointer
    packet.append(0x0c)     # to domain name in question
    packet.append(0)        # root

    if aRec:
        packet.append(1)   # response type - A record
    else:
        packet.append(12)  # response type - PTR record

    packet.addM(2, 1)      # class (IN)
    packet.addM(4, 0xa5a5a5a5)  # ttl

    if aRec:
        packet.addM(2, 4)   # rdata_length
        packet.extend([int(x) for x in ip_name.split('.')])
    else:
        name = dns.genCNAME(ip_name)
        packet.addM(2, len(name))   # rdata_length
        packet.extend(dns.genCNAME(ip_name))

    return packet


#-------------------------------------------------------------------------------
def genError(rcode, data):
#-------------------------------------------------------------------------------
    ## generate header
    packet = pbf.BitField(12)
    packet[:2] = data[:2]
    packet[2] = 0x81
    packet[3] = 0x80 | rcode
    return packet


if __name__ == "__main__":
    main(oss.argv)

