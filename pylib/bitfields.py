#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import



#-------------------------------------------------------------------------------
class BitField(bytearray):
#-------------------------------------------------------------------------------
    TYPE_NET = 0
    TYPE_BE = 0
    TYPE_LE = 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, d, typ=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bytearray.__init__(self, d)
        self.typ = typ

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setM(self, idx, cnt, val, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ is None: typ = self.typ

        if typ == self.TYPE_BE:
            for i in range(cnt):
                shift = (cnt - i - 1) * 8
                self[i+idx] = ((0xff << shift) & val) >> shift
        else:
            for i in range(cnt):
                shift = i * 8
                self[i+idx] = ((0xff << shift) & val) >> shift

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getM(self, idx, cnt, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ is None: typ = self.typ

        ans = 0
        if typ == self.TYPE_BE:
            for i in range(cnt):
                ans = (ans << i * 8) | self[i+idx]
        else:
            for i in range(cnt):
                ans |= self[i+idx] << (i * 8)

        return ans

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addM(self, cnt, val, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ is None: typ = self.typ

        if typ == self.TYPE_BE:
            for i in range(cnt):
                shift = (cnt - i - 1) * 8
                self.append(((0xff << shift) & val) >> shift)
        else:
            for i in range(cnt):
                shift = i * 8
                self.append(((0xff << shift) & val) >> shift)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _createMask(self, start, stop):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        mask = 0
        for idx in range(start, stop+1):
            mask |= 1 << idx
        return mask

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getBit(self, idx, bit, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= bit < 8
        return (self[idx] & (1 << bit)) >> bit

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getBitM(self, idx, cnt, bit, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= bit < cnt * 8
        return (self.getM(idx, cnt, typ) & (1 << bit)) >> bit

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getBits(self, idx, start, stop, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= start and start <= stop and stop < 8
        mask = self._createMask(start, stop)
        return (self[idx] & mask) >> start

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getBitsM(self, idx, cnt, start, stop, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= start and start <= stop and stop < cnt * 8
        mask = self._createMask(start, stop)
        return (self.getM(idx, cnt, typ) & mask) >> start

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBit(self, idx, bit, val, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= bit < 8
        if val == 0:
            self[idx] &= ~(1 << bit)
        else:
            self[idx] |= (1 << bit)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBitM(self, idx, cnt, bit, val, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= bit < cnt * 8
        data = self.getM(idx, cnt, typ)
        if val == 0:
            self.setM(idx, cnt, data & ~(1 << bit), typ)
        else:
            self.setM(idx, cnt, data | (1 << bit), typ)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBits(self, idx, start, stop, val, cnt=1, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= start and start <= stop and stop < 8
        mask = self._createMask(start, stop)
        self[idx] = (self[idx] & ~mask) | (mask & (val << start))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBitsM(self, idx, cnt, start, stop, val, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert 0 <= start and start <= stop and stop < cnt * 8
        mask = self._createMask(start, stop)
        data = (self.getM(idx, cnt, typ) & ~mask) | (mask & (val << start))
        self.setM(idx, cnt, data, typ)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hexDump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        hexDump(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def binDump(self, start=0, end=None, disp=16):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if end is None: end = len(self)
        binDump(self[start:end], disp)


#-------------------------------------------------------------------------------
def reverseBits(num):
#-------------------------------------------------------------------------------
    ans = 0
    while 1:
        ans |= num & 1
        num >>= 1
        if num == 0:
            break
        ans <<= 1

    return ans



#-------------------------------------------------------------------------------
def binDump(data, disp=16):
#-------------------------------------------------------------------------------
    for i in range(disp):
        print('%d' % (i // 10), end='')
    print()

    for i in range(disp):
        print('%d' % (i % 10), end='')
    print()
    print('-'*disp)

    for i in range(len(data) * 8):
        idx, bit = divmod(i, 8)
        print('1' if data[idx] & (1 << bit) else '0', end='')
    print('\n')


#-------------------------------------------------------------------------------
def hexDump(data):
#-------------------------------------------------------------------------------
    assert isinstance(data, (bytes, str, bytearray))

    s = b''
    for idx, byte in enumerate(data):
        if idx % 16 == 0:
            if idx != 0:
                print(' ', s)
                s = ''
            print(('%07x' % idx) + ': ', end='')

        if idx % 2 == 0:
            print(' ', end='')
            s += ' '

        s += (chr(byte) if 32 <= byte <= 127 else '.')
        try:
            print('%02x' % byte, end='')
        except TypeError:
            print('%02x' % ord(byte), end='')

    idx += 1
    if idx % 16 != 0:
        d = 16 - (idx % 16)
        for i in range(d):
            print('  ', end='')

        print(' ' * (d//2), end='')
        print(' ', s)

    print()


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)


    ba = BitField(2, BitField.TYPE_LE)

    ba.setBit(0, 3, 1)
    ba.setBit(0, 6, 1)
    ba.setBitM(0, 2, 12, 1)
    ba.binDump()

    ba = BitField(2, BitField.TYPE_LE)
    ba.setBitsM(0, 2, 1, 6, 5)
    ba.binDump()
    print(ba)

    ba = BitField(2)
    ba.setBitsM(0, 2, 1, 6, 5)
    ba.binDump()
    print(ba)

    print(binDump([reverseBits(0x8000)]))

    res = not __test__(verbose=True)
    oss.exit(res)

