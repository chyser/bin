"""
    this module contains a simple python only dft

"""
import math

#-------------------------------------------------------------------------------
def genSine(N, freq, amp=1.0):
#-------------------------------------------------------------------------------
    d = []
    vv = 2*math.pi * freq/N
    for i in range(N):
        d.append(amp * math.sin(i * vv))
    return d

#-------------------------------------------------------------------------------
def dft(ts):
#-------------------------------------------------------------------------------
    """ simple dft calculation on an input timeseries, ts. returns equal len
        array of real and imaginary parts
    """

    n = len(ts)
    ddn = 2*math.pi/n
    sin = math.sin
    cos = math.cos

    awr = [];  awi = []

    for j in range(n):
        wr = wi = 0
        ddnj = ddn*j

        for k in range(n):
            dd = ddnj*k
            v = ts[k]
            wr += v * cos(dd)
            wi += v * sin(dd)

        awr.append(wr)
        awi.append(wi)

    return awr, awi

#-------------------------------------------------------------------------------
def powerSpectrum(real, imag):
#-------------------------------------------------------------------------------
    d = []
    ln = len(real)/2

    real[ln] = imag[0]
    imag[0] = imag[ln] = 0.0

    for idx in range(ln):
        r = real[idx]
        i = imag[idx]
        val = r*r + i*i
        if not (idx == 0 or idx == ln):
            val *= 2
        d.append(val)
    return d


#-------------------------------------------------------------------------------
def mi(i, n):
#-------------------------------------------------------------------------------
    """ Welch Window per index multiplier
    """
    return 1 - ((i - 0.5*(n - 1))/(0.5*(n+1)) ** 2)

#-------------------------------------------------------------------------------
def WelchWindow(ts):
#-------------------------------------------------------------------------------
    """ apply a Welch window to the timeseries, ts
    """

    o = []
    n = len(ts)

    nm = dm = 0
    for i in range(n):
        mmi = mi(i, n)
        nm += mmi * ts[i]
        dm += mmi

    xm = nm/dm

    for i, val in enumerate(ts):
        o.append((val - xm) * mi(i, n))
    return o

#-------------------------------------------------------------------------------
class signal(list):
#-------------------------------------------------------------------------------
    """ mathematical representation of a signal (ie all points not explicitely
        defined return 'default_val' (0))
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lstlen = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(signal, self).__init__()
        self.default_val = 0.0
        if isinstance(lstlen, list) or isinstance(lstlen, tuple) or isinstance(lstlen, signal):
            self.extend(list(lstlen))
        else:
            self.extend([0.0]*lstlen)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not (0 <= idx < len(self)):
            return self.default_val
        return super(signal, self).__getitem__(idx)

#-------------------------------------------------------------------------------
def convolution(x, h):
#-------------------------------------------------------------------------------
    """ the convolution operator
    """

    n = len(x) + len(h)
    x = signal(x);  h = signal(h); y = []

    for i in range(n):
        s = 0
        for k in range(n):
            s += x[k] * h[i - k]
        y.append(s)

    return y

#-------------------------------------------------------------------------------
def correlation(x, h):
#-------------------------------------------------------------------------------
    n = len(x) + len(h)
    x = signal(x);  h = signal(h); y = []

    for i in range(n):
        s = 0
        for k in range(n):
            s += x[k] * h[i + k]
        y.append(s)

    return y

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    d = [3.0, 1.0, 5.0, -2.0, 4.0, -1.0]
    awr, awi = dft(d)

    print awr, awr1
    print awi, awi1


    u = [0, 0, 1, 1, 1, 0]
    h = [1, 2, 3]

    print convolution(u, h)
    print correlation(u, h)
    print correlation(u, u)


import sys
#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)








