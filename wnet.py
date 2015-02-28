#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.net.util as util
import netifaces as ni


IWLIST="/usr/sbin/iwlist"

NDIR = "/etc/sysconfig/network/"
KDIR = NDIR + "/wlcfg/"


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: wnet [options]

        options:
	    -s | --scan  : scan for wireless networks
    """

    args, opts = oss.gopt(argv[1:], [('s', 'scan')], [], main.__doc__)

    nets = scanNetworks()

    if opts.scan:
        for net in nets:
	     print('-'*40)
	     print('ESSID:', net.name)
	     print('    qual:', net.qual)
	     print('    encryption:', net.encrypt)

        oss.exit(0)

    knets = findKnownNetworks(nets)
    for net in knets:
        ch = raw_input('use "%s" on "%s" [y/n]: ' % (net.name, net.nic))
	if ch == 'y' or ch == '':
	    net.install()
            break

    else:
        print('Known Networks')
	for net in knets:
	    print('   ', net)

        print('\nAll Networks')
	for net in nets:
	    print('   ', net)

    oss.exit(0)


#-------------------------------------------------------------------------------
class WNet(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name='', nic='', addr='', mask=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.name = name
	self.nic = nic
	self.addr = addr
	self.mask = mask
	self.encrypt = 'off'
	self.qual = '0'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, nic, addr, mask):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	self.nic = nic
	self.addr = addr
	self.mask = mask

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getGW(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	mask = util.ConvertNetMaskToInt(self.mask)
	net = (util.ConvertNetMaskToInt(self.addr) & mask) | 0x1
	return util.ConvertIntToAddr(net)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def install(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	print('ifdwn %s' % self.nic)
	print('cp ' + KDIR + self.name, NDIR + 'ifcfg-' + self.nic)
	print('ifup %s' % self.nic)
	print('route add default gw %s %s' % (self.getGW(), self.nic))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isKnown(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return oss.exists(KDIR + self.name)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.name


#-------------------------------------------------------------------------------
def scanNetworks():
#-------------------------------------------------------------------------------
    nets = []
    for nic in ni.interfaces():
        if nic.startswith('wlan'):
            for net in getWNetworks(nic):
	        d = ni.ifaddresses(nic)[2][0]
	        net.add(nic, d['addr'], d['netmask'])
	        nets.append(net)
    return nets


#-------------------------------------------------------------------------------
def getWNetworks(nic):
#-------------------------------------------------------------------------------
    n = []
    s = oss.r("%s %s scan" % (IWLIST, nic), '|')

    state = 0
    net = None
    for line in s.split('\n'):
	line = line.strip()

        if state == 0:
            if line.find('Cell') == 0:
	        net = WNet()
	        state = 1

        elif state == 1:
            if line.find('Encryption') == 0:
	        net.encrypt = line.split(':')[1]

            elif line.find('Quality') == 0:
	        t = line.split()[0]
		net.qual = t.split('=')[1]

            elif line.find('ESSID') == 0:
	        name = line.split(':')[1][1:-1]
	        if name:
		    net.name = name
	            n.append(net)

            elif line.find('Mode') == 0:
	        state = 0

    return n


#-------------------------------------------------------------------------------
def findKnownNetworks(nets):
#-------------------------------------------------------------------------------
    return [net for net in nets if net.isKnown()]


if __name__ == "__main__":
    main(oss.argv)

