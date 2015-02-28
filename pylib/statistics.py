import math, sys, operator, random

#-------------------------------------------------------------------------------
def Standardize_Z(x, mean, stddev):
#-------------------------------------------------------------------------------
    return (x - mean)/stddev


#-------------------------------------------------------------------------------
def MinMax(data):
#-------------------------------------------------------------------------------
    mn = sys.maxint
    mx = -sys.maxint
    for i in data:
        if i < mn: mn = i
        if i > mx: mx = i

    return mn, mx


#-------------------------------------------------------------------------------
def Summation(df, start=0, end=None):
#-------------------------------------------------------------------------------
    if isinstance(df, list):
        if end is None: end = len(df)
        return sum([df[i] for i in xrange(start, end)])

    if end is None: end = sys.maxint
    return sum(map(df, range(start, end)))


#-------------------------------------------------------------------------------
def Average(data):
#-------------------------------------------------------------------------------
    return float(sum(data))/len(data)


#-------------------------------------------------------------------------------
def Variance(data, avg=None, n1=1):
#-------------------------------------------------------------------------------
    if avg is None: avg = Average(data)
    l = len(data) - n1
    if l <= 0: l = 1
    return sum([math.pow(d - avg, 2) for d in data]) / (l)


#-------------------------------------------------------------------------------
def StdDev(data, avg=None, n1=1):
#-------------------------------------------------------------------------------
    return math.sqrt(Variance(data, avg, n1))


#-------------------------------------------------------------------------------
def stat(data, n1=1):
#-------------------------------------------------------------------------------
    avg = Average(data)
    return avg, StdDev(data, avg, n1), MinMax(data)


#-------------------------------------------------------------------------------
def factorial(n):
#-------------------------------------------------------------------------------
    if n == 0: return 1
    return reduce(operator.__mul__,  xrange(1, n+1))

permutations = factorial

#-------------------------------------------------------------------------------
def combinations(N, n=1):
#-------------------------------------------------------------------------------
    return factorial(N)/(factorial(N-n) * factorial(n))


#-------------------------------------------------------------------------------
def binomial(N, n, prob):
#-------------------------------------------------------------------------------
    return combinations(N, n) * math.pow(prob, n) * math.pow(1 - prob, N - n)


#-------------------------------------------------------------------------------
def poisson(n, a):
#-------------------------------------------------------------------------------
    return (math.pow(a, n) * math.exp(-a)) / factorial(n)


#-------------------------------------------------------------------------------
def Load(avg, var):
#-------------------------------------------------------------------------------
    ld = avg + ((var/2 - ((random.random() * var)) * 1.01))
    if ld < 0: ld = 0.0
    elif ld > 100: ld = 100.0
    return ld


PREC = 0.00005

#-------------------------------------------------------------------------------
def CDF_Norm(x):
#-------------------------------------------------------------------------------
    a = b = 1.0
    c = sum = term = float(x)

    if math.fabs(x) > 8:
        return 0.5 * x / math.fabs(x)

    i = 1
    while math.fabs(term) > PREC:
        a += 2;
        b *= -2 * i;
        c *= x * x;
        term = c / (a * b);
        sum += term;
        i += 1

    return sum / math.sqrt(2 * math.pi);


#-------------------------------------------------------------------------------
def histogram(inv, normalize=False):
#-------------------------------------------------------------------------------
    d = {}

    if normalize:
        ln = float(len(inv))

    for v in inv:
        d[v] = d.setdefault(v, 0) + 1

    mx = max(d.keys()) + 1
    mn = min(d.keys())

    l = []
    for idx in range(mn, mx):
        if idx in d:
            l.append((idx, d[idx]/ln if normalize else d[idx]))
        else:
            l.append((idx, 0))
    return l


#-------------------------------------------------------------------------------
class Histogram(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, numBins, low, high):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Histogram, self).__init__()
        self.numBins = numBins
        self.low = low
        self.offset = -self.low if self.low < 0 else 0
        self.high = high
        self.factor = (high - low)/(numBins - 1.0)
        self.ary = [0]*numBins
        self.scale = 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, vals):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for v in vals:
            idx = int(round((v + self.offset)/self.factor))
            if 0 <= idx < self.numBins:
                self.ary[idx] += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def show(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in xrange(self.numBins):
            print "%7.2f" % ((i+ 0.5)*self.factor - self.offset), '#'*(int(self.ary[i]*self.scale))


#-------------------------------------------------------------------------------
def GenNormal(mean, stddev):
#-------------------------------------------------------------------------------
    ## polar method
    r = 2
    while r > 1:
        a = 2*random.random()-1
        b = 2*random.random()-1
        r = a*a + b*b

    aval = a*math.sqrt((-2*math.log(r)/r))
    ## can also return a second val based on b
    return aval * stddev + mean


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if (__name__ == "__main__"):
    hist = Histogram(85, -400, 400)

    dist = [random.gauss(-50, 20) for i in xrange(500)]
    dist = [GenNormal(5, 50) for i in xrange(2000)]
    dist.extend([5.0 for i in xrange(400)])
    dist.extend([6.0 for i in xrange(100)])
    hist.add(dist)
    hist.scale = 0.15
    hist.show()

    print
    print stat(dist, n1=0)




