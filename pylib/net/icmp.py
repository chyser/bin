"""
This module assists with sending and receving icmp packets
"""

from socket import *

import struct, time, select

#-------------------------------------------------------------------------------
class ICMP(object):
#-------------------------------------------------------------------------------
    ECHO_REPLY     =  0
    DEST_UNREACH   =  3
    SRC_QUENCH     =  4
    REDIRECT       =  5
    ECHO_REQUEST   =  8
    ROUTER_ADVERT  =  9
    ROUTER_SOLICIT = 10
    TIME_EXCEEDED  = 11

    SType = {0 : "ECHO_REPLY",
             3 : "DEST_UNREACH",
             4 : "SRC_QUENCH",
             5 : "REDIRECT",
             8 : "ECHO_REQUEST",
             9 : "ROUTER_ADVERT",
            10 : "ROUTER_SOLICIT",
            11 : "TIME_EXCEEDED"}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ICMP, self).__init__()
        self.data = self.type = self.code = None
        self.skt = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def socket(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.skt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setsockopt(self, lvl, val, size):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.skt.setsockopt(lvl, val, size)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setPkt(self, recPacket):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sender = inet_ntoa(recPacket[12:16])
        self.data = recPacket[20:]
        self.type, self.code  = struct.unpack('!bb', self.data[:2])
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBin(self, recPacket):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.data = recPacket
        self.type, self.code  = struct.unpack('!bb', self.data[:2])
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
       return "Type: " + ICMP.SType[self.type] + "\nCode: " + str(self.code) + "\n\n" + self.__rawDump(self.data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checksum(self, str):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sum = 0
        countTo = (len(str) / 2) * 2
        count = 0

        while count < countTo:
            thisVal = ord(str[count + 1]) * 256 + ord(str[count])
            sum = sum + thisVal
            sum = sum & 0xffffffffL

            count = count + 2

        if countTo < len(str):
            sum = sum + ord(str[len(str) -1])
            sum = sum & 0xffffffffL

        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer =  ~sum
        answer = answer & 0xffff

        return answer >> 8 | (answer << 8 & 0xff00)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __rawDump(self, data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return " ".join(map(lambda s: ("%02x" % (s & 0xff)), struct.unpack("b" * len(data), data)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setVal(self, Type, Code, Format, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        hdr = struct.pack("!bbH", Type, Code, 0)
        self.type = Type
        self.code = Code

        if Format[-1] == '*':
            dd = args[-1]
            args = args[:-1]
            val = struct.pack("!bbH" + Format[:-1], Type, Code, 0, *args)
            val += dd
        else:
            val = struct.pack("!bbH" + Format, Type, Code, 0, *args)
        val = val [4:]

        chks = self.checksum(hdr + val)
        self.data = struct.pack("!bbH", Type, Code, chks) + val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendto(self, dest):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.skt.sendto(self.data, (dest, 1))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recvfrom(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        recPacket, self.sender = self.skt.recvfrom(1024)
        self.setPkt(recPacket)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getVal(self, Format = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if Format is None:
            return self.type, self.code

        if Format[-1] == '*':
            Format = "!bbH" + Format[:-1]
            size = struct.calcsize(Format)
            res = struct.unpack(Format, self.data[:size])
        else:
            res = struct.unpack('!' + Format, self.data)

        l = [self.type, self.code]; l.extend(list(res)[3:])
        return tuple(l)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.skt.close()


#-------------------------------------------------------------------------------
class Pinger(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self,  *dest):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.results = {}
        self.ID = 3
        self.icmp = ICMP();

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recvPkts(self, Hndlr, timeout=5, HndlCxt=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ gather all the replies
        """
        timeLeft = timeout

        while timeLeft > 0:
            startedSelect = time.time()

            ## wait for either results on the socket or the timeout
            whatReady = select.select([self.icmp.socket()], [], [], timeLeft)
            timeReceived = time.time()

            ## see if it was the timeout
            if not whatReady[0]: return

            timeLeft -= (timeReceived - startedSelect)

            self.icmp.recvfrom()

            ## handler can specifiy an early out
            if Hndlr(timeReceived, HndlCxt): return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recvPings(self, timeout, ErrFunc=None, ErrCxt=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.recvPkts(self.recvPingHndl, timeout, (ErrFunc, ErrCxt))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recvPingHndl(self, timeReceived, cxt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ErrFunc = cxt[0]
        if self.icmp.type != ICMP.ECHO_REPLY:
            if ErrFunc is None:
                #print self.icmp
                pass
            else:
                if ErrFunc(cxt[1]): return True
        else:
            type, code, packetID, sequence, timeSent = self.icmp.getVal("Hhd*")
            if packetID in self.destDict:
                self.results[self.destDict[packetID]] = timeReceived - timeSent

                ## track responses by eliminating from sending dict, if empty, done
                del self.destDict[packetID]
                if not self.destDict: return True
        return False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendPings(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ send pings to all destinations in destDict
        """
        for ID, dest in self.destDict.items():
            self.icmp.setVal(ICMP.ECHO_REQUEST, 0, 'Hhd*', ID, 1, time.time(), 'Q' * 128)
            self.icmp.sendto(dest)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ping(self, destAddr, timeout=10):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.destDict = {}

        for d in destAddr:
            self.destDict[self.ID] = d
            self.ID += 1

        self.sendPings()
        self.recvPings(timeout)
        self.icmp.close()
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tr_print(self, cnt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.icmp.type == ICMP.TIME_EXCEEDED:
            print "%3d:" % cnt, self.icmp.sender
            return True
        else:
            print self.icmp
            return False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def traceroute(self, destAddr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.destDict = {self.ID : destAddr}
        self.results = {}
        self.ID += 1

        for i in range(1, 256):
            self.icmp.setsockopt(IPPROTO_IP, IP_TTL, i)
            self.sendPings()
            self.recvPings(10, self.tr_print, i)

            if not self.destDict:
                break

        self.icmp.close()
        return self


#-------------------------------------------------------------------------------
class RouterDiscoveryProtocol(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(RouterDiscoveryProtocol, self).__init__()
        self.p = Pinger()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __solicitHndlr(self, timeRecved, cat):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print self.p.icmp

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Solicit(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.p.icmp.setVal(ICMP.ROUTER_SOLICIT, 0, "i", 0)
        self.p.icmp.sendto("224.0.0.2")
        self.p.recvPkts(self.__solicitHndlr)
        self.p.icmp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.p.icmp.sendto("255.255.255.255")
        self.p.recvPkts(self.__solicitHndlr)
        self.p.icmp.close()

