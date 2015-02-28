#!/usr/bin/env python


from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.net.util as util
import pylib.osscripts as oss
import pylib.struct2 as struct2

import random
import socket


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: dhcpc.py [options] <mac address>

        options:
            -s | --server      : specify server to try (default: broadcast)
            -i | --interface   : specify network interface to send request
                                 through (default: all)
            -b | --bcast_reply : set broadcast reply flag

        dhcpc is a dhcp client. It will retrieve information for the specified
        mac address.
    """
    args, opts = oss.gopt(argv[1:], [('b', 'bcast_reply')], [('s', 'server'), ('i', 'interface')], main.__doc__)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(3)

    baddr = '255.255.255.255' if opts.server is None else opts.server
    haddr = opts.interface if opts.interface is not None else '0.0.0.0'
    bcastFlag = 0 if opts.bcast_reply is None else 0x80

    print('Server:', baddr, 'Interface:', haddr)

    s.bind((haddr, 68))

    reqid = random.randint(0, 0xffffffff)

    req = DHCPPacket()
    req.op = 1
    req.htype = 1
    req.hlen = 6
    req.flags = bcastFlag
    req.xid = reqid
    req.msgType = 3
    req.chaddr = util.ConvertMacToInt(args[0])
    req.addField('b1', 'END', 255)

    s.sendto(req.getBin(), (baddr, 67))

    while 1:
        try:
            data, addr = s.recvfrom(1024)
        except socket.timeout:
            break

        res = DHCPPacket(data)
        if res.xid == reqid:
            print('--------------------------')
            print('Response from:', addr[0], '\n')
            print('    addr   :', util.ConvertIntToAddr(res.yiaddr))
            print('    mask   :', util.ConvertIntToAddr(res.mask))
            print('    router :', util.ConvertIntToAddr(res.router0))
            print('    dns    :', util.ConvertIntToAddr(res.dns_server0))

    oss.exit(0)


#-------------------------------------------------------------------------------
class DHCPPacket(struct2.struct2):
#-------------------------------------------------------------------------------
    layout = [
        ('b1', 'op'), ('b1', 'htype'), ('b1', 'hlen'), ('b1', 'hops'),
        ('b4', 'xid'),
        ('b2', 'secs'), ('b2', 'flags'),
        ('b4', 'ciaddr'),
        ('b4', 'yiaddr'),
        ('b4', 'siaddr'),
        ('b4', 'giaddr'),
        ('a16', 'chaddr'),
        ('64s', 'sname', ''),
        ('128s', 'file', ''),
        ('b1', 'MAGIC1', 99),
        ('b1', 'MAGIC2', 130),
        ('b1', 'MAGIC3', 83),
        ('b1', 'MAGIC4', 99),
        ('b1', 'DHCP', 53),
        ('b1', 'DHCPLen', 1),
        ('b1', 'msgType'),
    ]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, data=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.nidx = 0
        struct2.struct2.__init__(self, self.layout, data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getList(self, field):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx = 0;  lst = []

        while 1:
            res = getattr(self, field + str(idx), None)
            if res is None:
                return lst

            lst.append(res)
            idx += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            code = self.Peek(0)

            if code == 1:
                self.addFields([('b1', 'MASK_OP'), ('b1', 'MASK_LEN'), ('b4', 'mask')])

            elif code == 3:
                self.addFields([('b1', 'ROUTER_OP'), ('b1', 'ROUTER_LEN'), ('b4', 'router0')])
                for i in range(1, self.ROUTER_LEN//4):
                    self.addField('b4', 'router%d' % i)

            elif code == 6:
                self.addFields([('b1', 'DNS_OP'), ('b1', 'DNS_LEN'), ('b4', 'dns_server0')])
                for i in range(1, self.DNS_LEN//4):
                    self.addField('b4', 'dns_server%d' % i)

            elif code == 42:
                self.addFields([('b1', 'NTP_OP'), ('b1', 'NTP_LEN'), ('b4', 'ntp0')])
                for i in range(1, self.NTP_LEN//4):
                    self.addField('b4', 'ntp%d' % i)

            elif code == 12:
                ln = self.Peek(1)
                self.addFields([('b1', 'HOSTNAME_OP'), ('b1', 'HOSTNAME_LEN'), ('%ds' % ln, 'hostname')])

            elif code == 15:
                ln = self.Peek(1)
                self.addFields([('b1', 'DOMAINNAME_OP'), ('b1', 'DOMAINNAME_LEN'), ('%ds' % ln, 'domain_name')])

            elif code == 81:
                ln = self.Peek(1)
                self.addFields([('b1', 'FQDN_OP'), ('b1', 'FQDN_LEN'), ('b1', 'fqdn_flags'), ('b1', 'rcode1'), ('b1', 'rcode2'), ('%ds' % (ln-3), 'fqdn')])

            elif code == 52:
                self.addFields([('b1', 'OVERLOAD_OP'), ('b1', 'OVERLOAD_LEN'), ('%ds' % ln, 'overload_option')])


            ## end of option data
            elif code == 255 or code is None:
                break

            ## skip fields we aren't decoding
            else:
                self.nidx += 1
                if code == 0:
                    self.addField('b1', 'PAD_%d' % self.nidx)
                else:
                    print("Ignoring code:", code)
                    ln = self.Peek(1)
                    self.addField('a%d' % (ln + 2), 'UNDECODED_%d' % self.nidx)


if __name__ == "__main__":
    main(oss.argv)

