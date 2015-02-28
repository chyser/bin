import sys
import numpy

import pylib.statistics as stat

#-------------------------------------------------------------------------------
class MovingAverage(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, n):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(MovingAverage, self).__init__()
        self.n = n
        self.d = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self, sample):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.d.append(sample)
        return sum(self.d[-self.n:])/(1.0*self.n)

#-------------------------------------------------------------------------------
class MovingMax(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, n):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(MovingMax, self).__init__()
        self.n = n
        self.d = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self, sample):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.d.append(sample)
        return max(self.d[-self.n:])

#-------------------------------------------------------------------------------
class ExpMovingAverage(object):
#-------------------------------------------------------------------------------
    """ Exponential Weighted Moving Average

        Also called: Simple Exponential Smoothing, Brown's Simple Exponential Smoothing
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, alpha):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ExpMovingAverage, self).__init__()
        self.alpha = alpha
        self.avgk_1 = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self, sample):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.avgk_1 = self.alpha * self.avgk_1 + (1 - self.alpha) * sample
        return self.avgk_1

#-------------------------------------------------------------------------------
class LinearExpSmoothing(object):
#-------------------------------------------------------------------------------
    """ Linear Exponential Smoothing

        Also: Brown's Linear Exponential Smooting
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, alpha):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(LinearExpSmoothin, self).__init__()
        self.alpha = alpha
        self.avgk_1 = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         pass

#-------------------------------------------------------------------------------
def difference(sig, k=1):
#-------------------------------------------------------------------------------
    d = []
    for idx in xrange(len(sig)-1, k-1, -1):
        d.append(sig[idx] - sig[idx-k])
    d.reverse()
    return d

#-------------------------------------------------------------------------------
def add(sig, offset=0.0, k=1):
#-------------------------------------------------------------------------------
    d = [offset]*k
    for idx in xrange(k-1, len(sig)):
        d.append(sig[idx] + d[idx-k+1])
    return d

#-------------------------------------------------------------------------------
def autocov(series, lag, n_minus_k=False):
#-------------------------------------------------------------------------------
    """ Sample autocovariance function at specified lag. Use n - k as denominator
        if n_minus_k flag is true.

        series can be a numpy array or a list
    """

    n = len(series)

    try:
        zbar = series.mean()
    except AttributeError:
        series = numpy.array(series)
        zbar = series.mean()

    return sum([(series[i] - zbar) * (series[i + lag] - zbar) for i in range(n - lag)]) / ((n - lag) * n_minus_k or n)

#-------------------------------------------------------------------------------
def autocorr(series, lag):
#-------------------------------------------------------------------------------
    """ Sample autocorrelation function at specified lag, calculated as
        autocov(lag)/autocov(0)
    """

    return autocov(series, lag) / autocov(series, 0)

#-------------------------------------------------------------------------------
def autocorrelation(series, numLags = 30):
#-------------------------------------------------------------------------------
    d = [0]
    for idx in xrange(1, min(numLags, len(series))):
        d.append(autocorr(series, idx))
    return d

#-------------------------------------------------------------------------------
def partial_autocorr(series, lag):
#-------------------------------------------------------------------------------
    """Partial autocorrelation function, using Durbin (1960) recursive algorithm
    """

    # Initialize matrices of phi and rho
    phi = resize(0.0, (lag, lag))
    rho = resize(0.0, lag)

    if isinstance(series, list):
        series = numpy.array(series)

    # \phi_{1,1} = \rho_1
    phi[0, 0] = rho[0] = autocorr(series, 1)

    for k in range(1, lag):

        # Calculate autocorrelation for current lag
        rho[k] = autocorr(series, k + 1)

        for j in range(k - 1):

            # \phi_{k+1,j} = \phi_{k,j} - \phi_{k+1,k+1} * \phi_{k,k+1-j}
            phi[k - 1, j] = phi[k - 2, j] - phi[k - 1, k - 1] * phi[k - 2, k - 2 - j]

        # Numerator: \rho_{k+1} - \sum_{j=1}^k \phi_{k,j}\rho_j
        phi[k, k] = rho[k] - sum([phi[k - 1, j] * rho[k - 1 - j] for j in range(k)])

        # Denominator: 1 - \sum_{j=1}^k \phi_{k,j}\rho_j
        phi[k, k] /= 1 - sum([phi[k - 1, j] * rho[j] for j in range(k)])

    # Return partial autocorrelation value
    return phi[lag - 1, lag - 1]

#-------------------------------------------------------------------------------
def partial_autocorrelation(series, numLags=30):
#-------------------------------------------------------------------------------
    d = [0]
    for idx in xrange(1, min(numLags, len(series))):
        d.append(partial_autocorr(series, idx))
    return d


##-------- unconverted

from numpy import random
from numpy import arange, array, atleast_1d, concatenate, dot, resize
#from Matplot import PlotFactory
#import unittest, pdb

#_plotter = PlotFactory()





"""
def ar_process(length, params=[1.], mu=0., dist='normal', scale=1):
    # Generate AR(p) process of given length, where p=len(params).

    # Initialize series with mean value
    series = resize(float(mu), length)

    # Enforce array type for parameters
    params = atleast_1d(params)

    # Degree of process
    p = len(params)

    # Specify error distribution
    if dist is 'normal':
        a = random.normal(0, scale, length)
    elif dist is 'cauchy':
        a = random.standard_cauchy(length) * scale
    elif dist is 't':
        a = random.standard_t(scale, length)
    else:
        print 'Invalid error disitrbution'
        return

    # Generate autoregressive series
    for t in range(1, length):
        series[t] = dot(params[max(p-t, 0):], series[t - min(t, p):t] - mu) + a[t] + mu

    return series

def ma_process(length, params=[1.], mu=0., dist='normal', scale=1):
    # Generate MA(q) process of given length, where q=len(params).

    # Enforce array type for parameters
    params = concatenate(([1], -1 * atleast_1d(params))).tolist()
    # Reverse order of parameters for calculations below
    params.reverse()

    # Degree of process
    q = len(params) - 1

    # Specify error distribution
    if dist is 'normal':
        a = random.normal(0, scale, length)
    elif dist is 'cauchy':
        a = random.standard_cauchy(length) * scale
    elif dist is 't':
        a = random.standard_t(scale, length)
    else:
        print 'Invalid error disitrbution'
        return

    # Generate moving average series
    series = array([mu + dot(params[max(q - t + 1, 0):], a[t - min(t, q + 1):t]) for t in range(1, length)])

    return series
"""

#-------------------------------------------------------------------------------
def arma_process(length, ar_params=[1.], ma_params=[1.], mu=0., dist='normal', scale=1):
#-------------------------------------------------------------------------------
    """ Generate ARMA(p,q) process of given length, where p=len(ar_params) and q=len(ma_params).
    """

    # Initialize series with mean value
    series = resize(float(mu), length)

    # Enforce array type for parameters
    ar_params = atleast_1d(ar_params)
    ma_params = concatenate(([1], -1 * atleast_1d(ma_params))).tolist()

    # Reverse order of parameters for calculations below
    ma_params.reverse()

    # Degree of process
    p, q = len(ar_params), len(ma_params) - 1

    # Specify error distribution
    if dist is 'normal':
        a = random.normal(0, scale, length)
    elif dist is 'cauchy':
        a = random.standard_cauchy(length) * scale
    elif dist is 't':
        a = random.standard_t(scale, length)
    else:
        print 'Invalid error disitrbution'
        return

    # Generate autoregressive series
    for t in range(1, length):

        # Autoregressive piece
        series[t] += dot(ar_params[max(p-t, 0):], series[t - min(t, p):t] - mu)

        # Moving average piece
        series[t] += dot(ma_params[max(q - t + 1, 0):], a[t - min(t, q + 1):t])

    return series

#-------------------------------------------------------------------------------
def ar_process(length, params=[1.], mu=0., dist='normal', scale=1):
#-------------------------------------------------------------------------------
    """Generate AR(p) process of given length, where p=len(params)."""

    return arma_process(length, ar_params=params, ma_params=[], mu=mu, dist=dist, scale=scale)

#-------------------------------------------------------------------------------
def ma_process(length, params=[1.], mu=0., dist='normal', scale=1):
#-------------------------------------------------------------------------------
    """Generate MA(q) process of given length, where q=len(params)."""

    return arma_process(length, ar_params=[], ma_params=params, mu=mu, dist=dist, scale=scale)


'''
from numarray import *
'''

#-------------------------------------------------------------------------------
def arma(P, RHO, ma_weights, T=None, epsilon=None):
#-------------------------------------------------------------------------------
    """Returns an ARMA(P, Q) process. (Q <- len(ma_weights))

    Returns $X$ such that, for $t \in {0, \ldots, T-1}$,

    \[
        X_t = \sum_{k=1}^P \rho_k X_{t-k} +
                \sum_{k=1}^Q \alpha_k \epsilon_{t-k} + \epsilon_t
    \]

    where $\rho_k = \rho^k$ (for now) and $\alpha_k = ma_weights[k-1]$. Of
    course, the summation is truncated whenever $t < P$.
    """

    if epsilon is None:
        epsilon = random_array.normal(0, 1, (T,))
    elif T is None:
        raise ValueError("You must provide T or epsilon.")

    if T is None:
        T = shape(epsilon)[0]
    else:
        assert T == shape(epsilon)[0], "T and shape(epsilon) are incoherent."

    u = array(type=Float32, shape=(T,))
    for t in range(T):
        u[t] = epsilon[t]

        for k in range(1, min(t, len(ma_weights))+1):
            alpha_k = ma_weights[k-1] # offset by 1 since lists start at 0 in Python
            u[t] += alpha_k * epsilon[t-k]

        for p in range(1, min(t, P)+1):
            u[t] += RHO**p * u[t-p]

    return u

#-------------------------------------------------------------------------------
def autoregressive(P, RHO, T=None, epsilon=None):
#-------------------------------------------------------------------------------
    """Returns an AR(P) process.

    Returns $X$ such that, for $t \in {0, \ldots, T-1}$,

    \[
        X_t = \sum_{k=1}^P \rho_k X_{t-k} + \epsilon_t
    \]

    where $\rho_k = \rho^k$ (for now). Of course, the summation is
    truncated whenever $t < P$.
    """
    return arma(P, RHO, T=T, epsilon=epsilon, ma_weights=[])

#-------------------------------------------------------------------------------
def moving_average(ma_weights, T=None, epsilon=None):
#-------------------------------------------------------------------------------
    """Returns a MA(Q) process (Q <- len(ma_weights)).

    Returns $X$ such that, for $t \in {0, \ldots, T-1}$,

    \[
        X_t = \epsilon_t + \sum_{k=1}^Q \alpha_k \epsilon_{t-k}
    \]

    where $Q = len(ma_length)$ and $\alpha_k = ma_weights[k-1]$. Of course,
    the summation is truncated whenever $t < Q$.
    """
    return arma(-1, float('NaN'), ma_weights, T, epsilon=epsilon)


#-------------------------------------------------------------------------------
class TimeSeriesTests(object):
#-------------------------------------------------------------------------------
    def setUp(self):

        # Sample iid normal time series
        self.ts = array(random.normal(size=20))

    def testAutocovariance(self):
        # Autocovariance tests

        n = len(self.ts)

        # Confirm that covariance at lag 0 equals variance
        self.assertAlmostEqual(autocov(self.ts, 0), (n-1.)/n * self.ts.var(), 10, "Covariance at lag 0 not equal to variance")

        self.failIf(sum([self.ts.var() < autocov(self.ts, k) for k in range(1, n)]), "All covariances not less than or equal to variance")

    def testARIMA(self):
        # Test ARIMA estimation

        pass



#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    d = [1, 1, 2, 1, 1, 3, 4, 2, 1, 1, 2, 1, 3, 3, 3, 3, 5, 2, 1, 1, 2, 1, 1, 3,
         4, 2, 1, 1, 2, 1, 3, 3, 3, 3, 5, 2, 2, 1, 1, 2, 1, 1, 3, 4, 2, 1, 1, 2,
         1, 3, 3, 3, 3, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


    print partial_autocorrelation(d)
    print
    print autocorrelation(d)

    da = numpy.array(d)
    print partial_autocorr(da, 3)

    sys.exit(0)

    for i in d:
        print "%4.2f" % i,
    print '\n'

    e = ExpMovingAverage(0.7)
    for i in d:
        print "%4.2f" % e.next(i),
    print '\n'

    m = MovingAverage(4)
    for i in d:
        print "%4.2f" % m.next(i),
    print '\n'

    m = MovingMax(4)
    for i in d:
        print "%4.2f" % m.next(i),
    print '\n'

    import wavelet

    print len(d)
    dd = list(d)
    print dd

    s = wavelet.HaarWaveletTransform(d)
    print s


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)

