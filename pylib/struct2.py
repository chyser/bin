import struct

class Struct2Exception(Exception): pass

#-------------------------------------------------------------------------------
def chs(s, size = None):
#-------------------------------------------------------------------------------
    """ convert a hex string into a binary string
    """
    if not isinstance(s, str):
        s = '%x' % s
    elif s[1] in ['x', 'X']:
        s = s[2:]

    if size is None: size = len(s)
    size = (size + 1) & ~0x1

    ls = len(s)
    if ls < size:
        s += '0' * (size - ls)

    d = []
    for i in range(size//2):
        d.append(struct.pack('B', int(s[i*2:i*2+2], 16)))
    return "".join(d)


#-------------------------------------------------------------------------------
def ss(binStr):
#-------------------------------------------------------------------------------
    """ return a tuple of the hex values in binStr
    """
    return map(lambda s: "%02x" % s, struct.unpack('B'*len(binStr), binStr))


#-------------------------------------------------------------------------------
def mkBin(Fmt, *data):
#-------------------------------------------------------------------------------
    return struct.pack(Fmt, *data)


#-------------------------------------------------------------------------------
def dumpHex(data, RCnt = 16, Hdr = "%04x:", Disp = " %02s"):
#-------------------------------------------------------------------------------
    for i, item in enumerate(ss(data)):
        if i % RCnt == 0:
            nl = i != 0 and "\n" or ""
            print ("%s" + Hdr) % (nl, i),
        elif i % 4 == 0:
            print " ",
        print Disp % item,


#-------------------------------------------------------------------------------
class struct2(object):
#-------------------------------------------------------------------------------
    """
        supports all of I{structs} formats AND
        b[1,2,4,8] for bytes, i[1,2,4,8] for integers and
        a<num> is an array of num bytes
    """
    lud = {'b1' : 'B', 'b2' : 'H', 'b4' : 'I', 'b8' : 'Q', 'i1' : 'b', 'i2' : 'h', 'i4' : 'i', 'i8' : 'q'}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fields=None, data=None, byteOrder='!'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ Fields is a list of tuples of type, name, and optional initial value.
            data is data to be assigned
        """
        object.__init__(self)
        self._list = []
        self._type = []
        self.byteOrder = byteOrder
        self._lo = [byteOrder]

        if fields is not None:
            self.SetFields(fields, data)

        self.decode()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called prior to conversion in set bin
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetFields(self, fields, data=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for f in fields:
            try:
                typ, name, val = f
            except ValueError:
                typ, name = f; val = 0

            self._list.append(name)
            self.__dict__[name] = val

            t, lo = self.__cvtType(typ)
            self._type.append(t)
            self._lo.append(lo)

        self._lo = "".join(self._lo)
        self._size = struct.calcsize(self._lo)

        if data is not None:
            self.setBin(data)
        else:
            self._remain_data = ""
            self._orig_data = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __cvtType(self, typ):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ in self.lud:
            return 0, self.lud[typ]

        if typ[0] == 'a':
            num = int(typ[1:])
            return num, "%ds" % num

###        if typ[0].isdigit():
###            return 0, typ

        return 0, typ

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addField(self, typ, name, val=0, setbin=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t, lo = self.__cvtType(typ)
        self._lo += lo
        self._type.append(t)

        self._list.append(name)
        self.__dict__[name] = val
        self._size = struct.calcsize(self._lo)

        if setbin:
            try:
                self.setBin(self._orig_data)
            except: pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addFields(self, lst, setbin=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for l in lst:
            try:
                b, nm, v = l
            except ValueError:
                b, nm = l; v = 0
            self.addField(b, nm, v, setbin=False)

        if setbin:
            try:
                self.setBin(self._orig_data)
            except: pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calcsize(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self._size

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getBin(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ creates a binary version of the "struct" represented by the named
            fields
        """
        tpl = []
        #print self._lo
        for idx, fld in enumerate(self._list):
            #print fld, self.__dict__[fld], self._type[idx]

            if self._type[idx]:
                tpl.append(chs(self.__dict__[fld], 2*self._type[idx]))
                #print tpl[-1]
            else:
                tpl.append(self.__dict__[fld])

        self._orig_data = struct.pack(self._lo, *tpl)
        return self._orig_data

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBin(self, data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ accept binary data and set all of the "struct" fields
        """
        self._orig_data = data
        self._remain_data = data[self._size:]
        tpl = struct.unpack(self._lo, data[:self._size])

        for idx, fld in enumerate(self._list):
            self.__dict__[fld] = (self._type[idx] and "".join(ss(tpl[idx]))) or tpl[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Peek(self, idx, size=1, typ='b1'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t, lo = self.__cvtType(typ)
        if self._remain_data:
            v = struct.unpack(self.byteOrder + lo, self._remain_data[idx:idx+size])
            if len(v) == 1:
                return v[0]
            return v

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __cmp__(self, o):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return cmp(self.getBin(), o.getBin())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for i in self._list:
            l.append("%s : %s," % (i, self.__dict__[i]))

        if not self._remain_data:
            return " ".join(l)

        return " ".join(l) + '\n' + " ".join(ss(self._remain_data)) + "\n\n"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Disp(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for i in self._list:
            l.append("%s : %s\n" % (i, self.__dict__[i]))
        return "".join(l) + "\n"


#-------------------------------------------------------------------------------
class bin(object):
#-------------------------------------------------------------------------------
    BIG_ENDIAN = 0
    LITTLE_ENDIAN = 1
    NET_ENDIAN = 0
    NATIVE_ENDIAN = 2

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, data, size = None, endian = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(bin, self).__init__()
        if endian != None:
            endian = bin.NATIVE_ENDIAN
        self.SetEndian(endian)

        if isinstance(data, int):
            self.data = struct.pack(self.endian_char + 'I', data)
        elif isinstance(data, long):
            self.data = chs(str(data), size)
        elif isinstance(data, basestring):
            self.data = chs(data, size)
        elif isinstance(data, bin):
            self.data = data.data
        else:
            self.data = data

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetEndian(self, endian):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if endian == bin.NATIVE_ENDIAN:
            self.endian_char = '='
        elif endian == bin.BIG_ENDIAN:
            self.endian_char = '>'
        elif endian == bin.LITTLE_ENDIAN:
            self.endian_char = '<'
        elif endian == bin.NET_ENDIAN:
            self.endian_char = '!'
        else:
            raise Struct2Exception("Bad Endian Selection")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __len__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return len(self.data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.data[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, idx, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.data[idx] = val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __delitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        del self.data[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getslice__(self, i, j):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.data[i:j]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setslice__(self, i, j, seq):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.data[i:j] = seq

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __delslice__(self, i, j):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        del self.data[i,j]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __long__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return long("".join(ss(self.data)), 16)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "".join(ss(self.data))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __int__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return struct.unpack("I", self.data)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    s = struct2([
        ("char",    "a"),
        ("char",    "b"),
        ("char",    "c"),
        ("char",    "d"),
        ("int4",   "i1"),
        ("a16",    "addr"),
        ("double", "d1"),
        ("int4",   "i2")
        ])
    print s

    s.a = 'a'
    s.b = 'b'
    s.c = 'c'
    s.d = 'd'
    s.i1 = 1234
    s.d1 = 1.0456
    s.i2 = 0xfedcba98L



    print s
    data = s.getBin()


    s1 = struct2([
        ("char",    "a"),
        ("char",    "b"),
        ("char",    "c"),
        ("char",    "d"),
        ("int4",   "i1"),
        ("a16",    "addr"),
        ("double", "d1"),
        ("int4",   "i2")
        ])

    print s1

    print "Test: setBin"
    s1.setBin(data)
    print s1

    print "Compare"
    print s == s1

    print ss(chs("0102030405060708090a0b0c0d0e0f1"))


