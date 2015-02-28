#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import random
import socket

import pylib.osscripts as oss
import pylib.bitfields as pbf

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: dns <name to lookup> <ip addr of nameserver> [<ip addr of nameserver> ...]
    """
    args, opts = oss.gopt(argv[1:], [('d', 'dbgDump')], [], main.__doc__ + __doc__)

    for ns in args[1:]:
        err, authoritive, addrs, aliases = sendDNSQuery(args[0], ns, opts.dbgDump)

        print('NameServer:', ns)
        if err == 0:
            print(('Non-a' if not authoritive else 'A') + 'uthorative answer')
            print('IP Addresses:')
            print('   ', addrs)

            if aliases:
                print('Aliases:')
                print('   ', aliases)
        else:
            print('Error:', err)
        print()

    oss.exit(0)


#-------------------------------------------------------------------------------
def sendDNSQuery(name, nameServerIPAddr, dump=False):
#-------------------------------------------------------------------------------
    id = random.randint(0, 2**16-1)
    msg = pbf.BitField(12)

    msg.setM(0, 2, id)     ## set the id
    msg.setBit(2, 0, 1)    ## set recursion request
    msg.setM(4, 2, 1)      ## set query count to 1

    for lbl in name.split('.'):
        msg.append(len(lbl))        ## set length of this label
        msg.extend(bytes(lbl))      ## add the label
    msg.append(0)                   ## add the zero length root label

    msg.addM(2, 1)                  ## set qtype
    msg.addM(2, 1)                  ## set qclass

    if dump:
        print('Sent packet:')
        msg.hexDump()
        print()

    ## send packet
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.sendto(msg, (nameServerIPAddr, 53))

    ## get packet
    data = pbf.BitField(udps.recv(1024))

    ## ensure it is the correct request
    if id == data.getM(0, 2):
        if dump:
            print('Recved packet:')
            pbf.hexDump(data)
            print()

        #print('QR:', data.getBit(2, 7))
        AA = data.getBit(2, 2)
        #print('AA:', data.getBit(2, 2))
        #print('RD:', data.getBit(2, 0))
        #print('RA:', data.getBit(3, 7))
        #print('Opcode:', data.getBits(3, 3, 6))

        rcode = data.getBits(3, 0, 3)
        #print('RCODE:', rcode)

        if dump:
            print('Q records:', data.getM(4, 2))
            print('A records:', data.getM(6, 2))
            print('NS records:', data.getM(8, 2))
            print('Additional records:', data.getM(10, 2))

        if rcode != 0:
            return rcode, 0, [], []

        ## get question records
        for i in range(data.getM(4, 2)):
            idx, name = getCNAME(12, data)
            idx += 5

        ## get answers
        idx, ipaddrs, aliases = getAnswerRecords(idx, data)

        if dump:
            print()
            pbf.hexDump(data[idx:])
            print()

            for i in range(data.getM(8, 2)):
                idx, name = getCNAME(idx, data)
                print('NS:', name)

            print()
            pbf.hexDump(data[idx:])
            print()


        return 0, AA, ipaddrs, aliases


#-------------------------------------------------------------------------------
def getAnswerRecords(idx, data):
#-------------------------------------------------------------------------------
    ipaddrs = []
    aliases = []

    ## get answer records
    for i in range(data.getM(6, 2)):
        idx, name = getCNAME(idx, data)
        #print('answer name:', name)


        ansType = data.getM(idx, 2)
        #print('TYPE:', ansType)
        #print('CLASS:', data.getM(idx+2, 2))
        #print('TTL:', data.getM(idx+4, 4))

        rdatalen = data.getM(idx+8, 2)
        #print('RDATALEN:', rdatalen)

        idx += 10
        #pbf.hexDump(data[idx:idx + rdatalen])

        if ansType == 5:
            idx, cname = getCNAME(idx, data)
            aliases.append(cname)
        elif ansType == 12:
            idx, cname = getCNAME(idx, data)
            ipaddrs.append(cname)
        elif ansType == 1:
            ipaddrs.append(getIPAddr(idx, data))
            idx += rdatalen

    return idx, ipaddrs, aliases



#-------------------------------------------------------------------------------
def genCNAME(name):
#-------------------------------------------------------------------------------
    msg = pbf.BitField([])
    for lbl in name.split('.'):
        msg.append(len(lbl))        ## set length of this label
        msg.extend(bytes(lbl))      ## add the label
    msg.append(0)                   ## add the zero length root label
    return msg


#-------------------------------------------------------------------------------
def getCNAME(idx, data):
#-------------------------------------------------------------------------------
    name = []
    while data[idx] != 0:
        cnt = data[idx]
        if cnt == 0xc0:
            name.append(getCNAME(data[idx+1], data)[1])
            idx += 2
            break

        idx += 1
        name.append(str(data[idx:idx+cnt]))
        idx += cnt

    return idx, '.'.join(name)


#-------------------------------------------------------------------------------
def getIPAddr(idx, data):
#-------------------------------------------------------------------------------
    s = []
    for i in range(4):
        s.append('%d' % data[idx + i])

    return '.'.join(s)


if __name__ == "__main__":
    main(oss.argv)
