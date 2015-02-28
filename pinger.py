#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.net.icmp  as icmp
import pylib.net.util as util


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ pinger.py [options] [target]
    pinger <target>                  : pings target
    pinger -m <netmask> -n <network> : pings all addresses on network
    pinger -n <network CIDR format>  : pings all addresses on network
    pinger -r <target>               : raceroute w/ icmp packets
    pinger -s                        : run router discovery protocol
    """
    args, opts = oss.gopt(argv[1:], [('r', 'route'), ('s', 'srtr')], [("m", "mask"), ("n" , "net")], main.__doc__)

    if opts.srtr is not None:
        icmp.RouterDiscoveryProtocol().Solicit()
        oss.exit(0)

    if opts.route is not None:
        print(icmp.Pinger().traceroute(args[0]).results)
        oss.exit(0)

    if opts.mask is not None:
        if opts.net is None:
            opts.usage(1, "if option 'm' set, 'n' must be set")

    if opts.net is not None:
        if opts.mask is None:
            nn = opts.net
            if nn[0] == '/':
                nn = util.getIPAddr() +  nn
            a, m = util.ConvertCIDR(nn)
            if a is None:
                opts.usage(1, "options 'n' and 'm' must be set together")
            opts.net, opts.mask = a, m
            print("    using mask:", m)

        mask = util.ConvertNetMaskToInt(opts.mask)
        net = util.ConvertNetMaskToInt(opts.net) & mask

        args = []
        mask = 0xffffffffL - mask
        for i in range(1, mask):
            args.append(util.ConvertIntToAddr(net | i))

        print("\nSearching Addresses: %s -- %s, %d" % (args[0], args[-1], mask + 1))
    else:
        if not args:
            opts.usage(1, "must set an option")
        p = icmp.Pinger()
        for k, v in p.ping(args, 25).results.iteritems():
            print("%s\t%s" % (k, v))
        oss.exit(0)


    p = icmp.Pinger()

    print("%s\t---" % util.ConvertIntToAddr(net))
    for k, v in p.ping(args).results.iteritems():
        print("%s\t%s" % (k, v))
    print("%s\t---" % util.ConvertIntToAddr(net + mask))
    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

