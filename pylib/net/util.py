import socket

import pylib.struct2 as s2
import pylib.net.icmp as icmp


class NetUtilException(Exception): pass

#-------------------------------------------------------------------------------
def ping(dests):
#-------------------------------------------------------------------------------
    """ ping one or a list of destinations, returning None if not all reachable
        else a dict with key == dest and value equal time
    """
    if isinstance(dests, (str, unicode)):
        dests = [dests]

    res = icmp.Pinger().ping(dests).results
    for d in res:
        if d not in res:
            return
    return res

getfqdn = socket.getfqdn


#-------------------------------------------------------------------------------
def getIPAddr():
#-------------------------------------------------------------------------------
    """ gets the current IP adress
    """
    return socket.gethostbyname(socket.gethostname())


#-------------------------------------------------------------------------------
def getIPAddrAll():
#-------------------------------------------------------------------------------
    """ gets the current IP adress
    """
    return socket.gethostbyname_ex(socket.gethostname())


#-------------------------------------------------------------------------------
def gethostbyaddr(ipaddr = None):
#-------------------------------------------------------------------------------
    if ipaddr is not None:
        return socket.gethostbyaddr(ipaddr)
    return socket.gethostbyaddr(getIPAddr())


#-------------------------------------------------------------------------------
def ConvertAddrToInt(Addr):
#-------------------------------------------------------------------------------
    """ convert either a hex string or a dotted notation IP4 hex string to address
        0xNNNNNNN or a.b.c.d
    """
    try:
        if '.' not in Addr:
            return int(Addr, 0)

        a, b, c, d = Addr.split('.')
        a = int(a, 0)
        assert 0 <= a < 256

        b = int(b, 0)
        assert 0 <= b < 256

        c = int(c, 0)
        assert 0 <= c < 256

        d = int(d, 0)
        assert 0 <= d < 256

        return (a << 24) | (b << 16) | (c << 8) | d

    except TypeError as ex:
        raise NetUtilException(ex)


ConvertNetMaskToInt = ConvertAddrToInt


#-------------------------------------------------------------------------------
def ConvertCIDR(addr):
#-------------------------------------------------------------------------------
    """ return the addr and the mask
        dd.dd.dd.dd/N
    """
    try:
        a, m = addr.split('/')
    except ValueError:
        raise NetUtilException('Incorrect CIDR address format')

    m = ConvertIntToAddr(0xffffffffL - (pow(2, (32-int(m))) - 1))
    return a, m



#-------------------------------------------------------------------------------
def getGatewayBroadcast(a, m=None):
#-------------------------------------------------------------------------------
    """ calculate gateway and broadcast from an addr/mask pair, CIDR
    """
    if m is None:
        a, m = ConvertCIDR(a)

    ai = ConvertAddrToInt(a)
    mi = ConvertAddrToInt(m)

    d = ai & mi
    start = ConvertIntToAddr(d)
    gateway = ConvertIntToAddr(d + 1)
    broadcast = ConvertIntToAddr(d + ~mi)

    return start, gateway, broadcast


#-------------------------------------------------------------------------------
def ConvertIntToAddr(i):
#-------------------------------------------------------------------------------
    """ convert an address to a dotted notation string
    """
    return "%d.%d.%d.%d" % ((i >> 24) & 0xff, (i >> 16) & 0xff, (i >> 8) & 0xff, i & 0xff)


#-------------------------------------------------------------------------------
def ConvertIntToMacAddr(i, size=6):
#-------------------------------------------------------------------------------
    """ convert an address to a ':' notation MAC address
    """
    return ":".join(s2.ss(s2.chs(i))[:size])


#-------------------------------------------------------------------------------
def ConvertMacToInt(s):
#-------------------------------------------------------------------------------
    l = s.split(':')

    if len(l) != 6:
        raise NetUtilException('Incorrect MAC address format -- length')

    try:
        v = 0
        for m in s.split(':'):
            v = (v << 8) | int(m, 16)
        return v
    except ValueError:
        raise NetUtilException('Incorrect MAC address format -- non-hex')


#-------------------------------------------------------------------------------
def ParseURL(url):
#-------------------------------------------------------------------------------
    """ returns a list of type, host, port, path
    """
    type = "http"
    port = 80
    path = host = "/"

    if "http://" == url[:7]:
        url = url[7:]

    elif "https://" == url[:8]:
        url = url[8:]
        type = "https"
        port = 443

    if '/' in url:
        s = url.split('/')
        hp = s[0]
        path = '/' + '/'.join(s[1:])
    else:
        hp = url

    if ':' in hp:
        host, port = hp.split(':')
        port = int(port)
    else:
        host = hp

    return type, host, port, path


#-------------------------------------------------------------------------------
def ArgsToAddrPort(args):
#-------------------------------------------------------------------------------
    """ converts an argument string or list of strings into 2 tuples:
           - the first is the standard (host, port) needed by socket.connect()
           - the other: is the type of URL and path if present (typ, path)
    """

    if isinstance(args, list):
        if len(args) < 2:
            return ArgsToAddrPort(args[0])
        nmaddr = args[0]
        port = int(args[1])
        typ = None
        path = ""
    else:
        typ, nmaddr, port, path = ParseURL(args)

    if nmaddr[0] not in set('0123456789'):
        nmaddr = socket.gethostbyname(nmaddr)

    return (nmaddr, port), (typ, path)

