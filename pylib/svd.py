"""

Pure Python SVD algorithm
    Input: 2-D list (m by n) with m >= n
    Output: U,W V so that A = U*W*VT
        Note this program returns V not VT (=transpose(V))
        On error, a ValueError is raised.
"""


import copy
import math

#-------------------------------------------------------------------------------
class Vector(list):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, sz_lst, init_val=0.0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(sz_lst, list):
            super(Vector, self).__init__(sz_lst)
        else:
            super(Vector, self).__init__([0.0 for i in xrange(sz_lst)])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clone(self, end=0, start=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if end == 0: end = len(self)
        return Vector(list(self[start:end]))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def assign(self, lst, idx=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self[idx:len(lst)] = lst

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resize(self, sz, val=0.0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ln = len(self)

        if sz > ln:
            self.extend([val]*(sz-ln))
        elif sz < ln:
            pass




#-------------------------------------------------------------------------------
class Matrix(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, row_l=None, col=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Matrix, self).__init__()
        self.name = ""

        if row_l is not None:
            self.__alloc(row_l, col)
        else:
            self.data = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __alloc(self, row_l, col):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(row_l, Matrix):
            self.data = copy.deeepcopy(row_l.data)

        elif isinstance(row_l, list):
            self.data = row_l

        else:
            self.data = [[0.0]*col for i in xrange(row_l)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self, A):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return copy.deepcopy(A)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def diag(self, w, reciprocal=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ diagonalize the vector w, with optional multiplicative reciprocal
        """
        l = len(w)

        self.__alloc(l, l)

        if reciprocal:
            for i in xrange(l):
                if w[i] < 1e-15:
                    self.data[i][i] = 0.0
                else:
                    self.data[i][i] = 1.0/w[i]
        else:
            for i in xrange(l):
                self.data[i][i] = w[i]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def transpose(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ''' Compute the transpose of a matrix.
        '''
        m, n = self.order()

        T = Matrix(n, m)
        T.name = self.name + "_T"

        for i in range(m):
            for j in range(n):
                T.data[j][i] = self.data[i][j]

        return T

    trans = transpose

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def order(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return len(self.data), len(self.data[0])


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __mul__(self, b):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ''' Multiply two matrices.
               a must be two dimensional
               b can be one or two dimensional.
        '''

        am, an = self.order()
        cm = am

        if isinstance(b, Matrix):
            bm, bn = b.order()
            cn = bn
        else:
            bm = len(b)
            cn = bn = 1

        if an != bm:
            raise ValueError('matrixmultiply error: array sizes do not match.')

        if bn == 1:
            c = [0.0]*cm
        else:
            c = Matrix(cm, cn)

        for i in range(cm):
            for j in range(cn):
                for k in range(an):
                    if bn == 1:
                        c[i] += self.data[i][k] * b[k]
                    else:
                        c[i][j] += self.data[i][k] * b[k][j]
        return c


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.data[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def toString(self, fmt="%6.2f"):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.name:
            s = [self.name]
        else:
            s = []

        for row in self.data:
            ss = []
            for col in row:
                ss.append(fmt % col)
            s.append(str(', '.join(ss)))
        return '\n'.join(s) + '\n'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.toString()

#-------------------------------------------------------------------------------
class Identity(Matrix):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, m):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Identity, self).__init__()
        self.diag([1.0]*m)
        self.name = "Identity"


#-------------------------------------------------------------------------------
def __svd(a):
#-------------------------------------------------------------------------------
    '''Compute the singular value decomposition of array.'''

    # Golub and Reinsch state that eps should not be smaller than the
    # machine precision, ie the smallest number
    # for which 1+e>1.  tol should be beta/e where beta is the smallest
    # positive number representable in the computer.

    eps = 1.e-15                           # assumes double precision

    tol = 1.e-64 / eps
    assert 1.0 + eps > 1.0                 # if this fails, make eps bigger

    assert tol > 0.0                       # if this fails, make tol bigger

    itmax = 50

    u = copy.deepcopy(a)
    m = len(a)
    n = len(a[0])
    #if __debug__: print 'a is ',m,' by ',n

    if m < n:
        if __debug__: print 'Error: m is less than n'
        raise ValueError('SVD Error: m is less than n.')

    e = [0.0] * n                          # allocate arrays
    q = [0.0] * n
    v = []

    for k in range(n):
        v.append([0.0] * n)

    # Householder's reduction to bidiagonal form
    g = 0.0
    x = 0.0

    for i in range(n):
        e[i] = g
        s = 0.0
        l = i + 1

        for j in range(i, m):
            s += (u[j][i] * u[j][i])

        if s <= tol:
            g = 0.0

        else:
            f = u[i][i]

            if f < 0.0:
                g = math.sqrt(s)
            else:
                g =  -math.sqrt(s)

            h = f * g -s
            u[i][i] = f -g

            for j in range(l, n):
                s = 0.0

                for k in range(i, m):
                    s += u[k][i] * u[k][j]
                f = s / h

                for k in range(i, m):
                    u[k][j] = u[k][j] + f * u[k][i]

        q[i] = g
        s = 0.0

        for j in range(l, n):
            s = s + u[i][j] * u[i][j]

        if s <= tol:
            g = 0.0

        else:
            f = u[i][i + 1]

            if f < 0.0:
                g = math.sqrt(s)
            else:
                g =  -math.sqrt(s)

            h = f * g -s
            u[i][i + 1] = f -g

            for j in range(l, n):
                e[j] = u[i][j] / h

            for j in range(l, m):
                s = 0.0

                for k in range(l, n):
                    s = s + (u[j][k] * u[i][k])

                for k in range(l, n):
                    u[j][k] = u[j][k] + (s * e[k])

        y = abs(q[i]) + abs(e[i])

        if y > x:
            x = y


    ## accumulation of right hand transformations
    for i in range(n -1, -1, -1):
        if g != 0.0:
            h = g * u[i][i + 1]

            for j in range(l, n):
                v[j][i] = u[i][j] / h

            for j in range(l, n):
                s = 0.0

                for k in range(l, n):
                    s += (u[i][k] * v[k][j])

                for k in range(l, n):
                    v[k][j] += (s * v[k][i])

        for j in range(l, n):
            v[i][j] = 0.0
            v[j][i] = 0.0

        v[i][i] = 1.0
        g = e[i]
        l = i

    ## accumulation of left hand transformations
    for i in range(n -1,  -1,  -1):
        l = i + 1
        g = q[i]

        for j in range(l, n):
            u[i][j] = 0.0

        if g != 0.0:
            h = u[i][i] * g

            for j in range(l, n):
                s = 0.0

                for k in range(l, m):
                    s += (u[k][i] * u[k][j])
                f = s / h

                for k in range(i, m):
                    u[k][j] += (f * u[k][i])

            for j in range(i, m):
                u[j][i] = u[j][i] / g

        else:
            for j in range(i, m):
                u[j][i] = 0.0

        u[i][i] += 1.0


    ##diagonalization of the bidiagonal form
    eps = eps * x

    for k in range(n -1,  -1,  -1):
        for iteration in range(itmax):

            ## test f splitting
            for l in range(k,  -1,  -1):
                goto_test_f_convergence = False

                if abs(e[l]) <= eps:
                    ## goto test f convergence
                    goto_test_f_convergence = True
                    break                  # break out of l loop

                if abs(q[l -1]) <= eps:
                    # goto cancellation
                    break                  # break out of l loop

            if not goto_test_f_convergence:
                ##cancellation of e[l] if l>0
                c = 0.0
                s = 1.0
                l1 = l -1

                for i in range(l, k + 1):
                    f = s * e[i]
                    e[i] = c * e[i]

                    if abs(f) <= eps:
                        #goto test f convergence
                        break

                    g = q[i]
                    h = __pythag(f, g)
                    q[i] = h
                    c = g / h
                    s =  -f / h

                    for j in range(m):
                        y = u[j][l1]
                        z = u[j][i]
                        u[j][l1] = y * c + z * s
                        u[j][i] =  -y * s + z * c

            ## test f convergence
            z = q[k]

            if l == k:
                ## convergence
                if z < 0.0:
                    ## q[k] is made non-negative
                    q[k] =  -z

                    for j in range(n):
                        v[j][k] =  -v[j][k]

                break     # break out of iteration loop and move on to next k value

            if iteration >= itmax -1:
                if __debug__: print 'Error: no convergence.'
                # should this move on the the next k or exit with error??
                # raise ValueError,'SVD Error: No convergence.'  # exit the program with error
                break        # break out of iteration loop and move on to next k

            ## shift from bottom 2x2 minor
            x = q[l]
            y = q[k -1]
            g = e[k -1]
            h = e[k]
            f = ((y -z) * (y + z) + (g -h) * (g + h)) / (2.0 * h * y)
            g = __pythag(f, 1.0)

            if f < 0:
                f = ((x -z) * (x + z) + h * (y / (f -g) -h)) / x
            else:
                f = ((x -z) * (x + z) + h * (y / (f + g) -h)) / x

            ## next QR transformation
            c = 1.0
            s = 1.0

            for i in range(l + 1, k + 1):
                g = e[i]
                y = q[i]
                h = s * g
                g = c * g

                z = __pythag(f, h)
                e[i -1] = z
                c = f / z
                s = h / z
                f = x * c + g * s

                g =  -x * s + g * c
                h = y * s
                y = y * c

                for j in range(n):
                    x = v[j][i -1]
                    z = v[j][i]
                    v[j][i -1] = x * c + z * s
                    v[j][i] =  -x * s + z * c

                z = __pythag(f, h)
                q[i -1] = z
                c = f / z
                s = h / z
                f = c * g + s * y
                x =  -s * g + c * y

                for j in range(m):
                    y = u[j][i -1]
                    z = u[j][i]
                    u[j][i -1] = y * c + z * s
                    u[j][i] =  -y * s + z * c

            e[l] = 0.0
            e[k] = f
            q[k] = x
            ## goto test f splitting

    #vt = transpose(v)
    #return (u,q,vt)
    return(u, q, v)

#-------------------------------------------------------------------------------
def svdcmp(A):
#-------------------------------------------------------------------------------
    u, w, v = __svd(A.data)
    return Matrix(u), w, Matrix(v)

#-------------------------------------------------------------------------------
def __pythag(a, b):
#-------------------------------------------------------------------------------
    absa = abs(a)
    absb = abs(b)

    if absa > absb: return absa * math.sqrt(1.0 + (absb / absa)**2)
    else:
        if absb == 0.0: return 0.0
        else: return absb * math.sqrt(1.0 + (absa / absb)**2)

#-------------------------------------------------------------------------------
def fleg(x, pl):
#-------------------------------------------------------------------------------
    nl = len(pl)
    pl[0] = 1.0
    pl[1] = x

    if nl > 2:
        twox = 2.0 * x
        f2 = x
        d = 1.0

        for j in xrange(2, nl):
            f1 = d
            d += 1
            f2 += twox
            pl[j] = (f2 * pl[j-1] - f1 * pl[j-2]) / d


#-------------------------------------------------------------------------------
def svbksb(U, w, V, b):
#-------------------------------------------------------------------------------
    """ 'U', 'w', 'V' come from svdcmp and 'b' is input vector
         returns
    """

    m, n = U.order()

    x = Vector(n)
    tmp = Vector(n)

    for j in xrange(n):
        s = 0.0
        if w[j]:
            for i in xrange(m):
                s += U[i][j] * b[i]
            s /= w[j]
        tmp[j] = s

    for j in xrange(n):
        s = 0.0
        for jj in xrange(n):
            s += V[j][jj] * tmp[jj]
        x[j] = s

    return x


TOL = 1.0e-5

#-------------------------------------------------------------------------------
def svdfit(x, y, ma, func = fleg, sig = None):
#-------------------------------------------------------------------------------
    """ x:float[] and y:float[] are input are sets of data points

        func = func(float, float[])
    """
    ndata = len(x)
    assert ndata > ma

    if sig is None:
        sig = [1.0]*ndata

    assert len(y) == len(sig) == ndata

    A = Matrix(ndata, ma)      ## design matrix

    b = [0.0]*ndata
    afunc = [0.0]*ma

    for i in xrange(ndata):
        func(x[i], afunc)

        tmp = 1.0/sig[i]
        for j in xrange(ma):
            A[i][j] = afunc[j]*tmp
        b[i] = y[i]*tmp

    U, w, V = svdcmp(A)
    wmax = max(w)

    thresh = TOL*wmax
    for j in xrange(ma):
        if w[j] < thresh: w[j] = 0.0

    a = svbksb(U, w, V, b)

    chisq = 0.0

    if sig is not None:
        for i in xrange(ndata):
            func(x[i], afunc)

            sum = 0.0
            for j in xrange(ma):
                sum += a[j]*afunc[j]

        tmp = (y[i]-sum)/sig[i]
        tmp = tmp*tmp
        chisq += tmp

    return a, chisq


#-------------------------------------------------------------------------------
class FuncClass(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(FuncClass, self).__init__()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def eval(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return



GOLD = 1.618034
GLIMIT = 100.0
TINY = 1.0e-20
ITMAX = 1000
CGOLD = 0.3819660
ZEPS = 1.0e-10

#-------------------------------------------------------------------------------
def SIGN(a, b):
#-------------------------------------------------------------------------------
    if b >= 0.0:
        return abs(a)
    else:
        return -1.0*abs(a)

#-------------------------------------------------------------------------------
def brent(ax, bx, cx, funcClass, tol):
#-------------------------------------------------------------------------------
    e = 0.0
    a = min(ax, cx)
    b = max(ax, cx)

    x = w = v = bx
    fw = fv = fx = funcClass.eval(x)

    for iter in xrange(ITMAX):
        xm = 0.5*(a+b)

        tol1 = tol * abs(x) + ZEPS
        tol2 = 2.0*tol1

        if abs(x - xm) <= tol2 - 0.5*(b-a):
            return fx, x

        if abs(e) > tol1:
            r = (x-w)*(fx-fv)
            q = (x-v)*(fx-fw)
            p = (x-v)*q - (x-w)*r

            q = 2.0*(q - r)
            if q > 0.0:
                p = -1 * p
            q = abs(q)

            etemp = e;  e = d
            if abs(p) >= abs(0.5*q*etemp) or p <= q*(a-x) or p >= q*(b-x):
                if x >= xm:
                    e = a-x
                else:
                    e = b-x

                d = CGOLD*e
            else:
                d = p/q
                u = x+d

                if u-a < tol2 or b-u < tol2:
                    d = SIGN(tol1, xm-x)

        else:
            if x >= xm:
                e = a-x
            else:
                e = b-x
            d = CGOLD*e

        if abs(d) >= tol1:
            u = x+d
        else:
            u = x + SIGN(tol1, d)
        fu = funcClass.eval(u)

        if fu <= fx:
            if u >= x:
                a = x
            else:
                b = u

            v, w, x = w, x, u
            fv, fw, fx =  fw, fx, fu

        else:
            if u < x:
                a = u
            else:
                b = u

            if fu <= fw or w == x:
                v=w; w=u; fv=fw; fw=fu

            elif fu <= fv or v == x or v == w:
                v = u; fv = fu
    else:
        raise "brent: Max iterations exceeded"

#-------------------------------------------------------------------------------
def mnbrak(ax, bx, funcClass):
#-------------------------------------------------------------------------------
    """ given two values 'ax' and 'bx' and a function of one variable, return
        a brakceting triplet (ax, bx, cx) such that the minimum and 'bx' are
        between 'ax' and 'cx'
    """
    fa = funcClass.eval(ax)
    fb = funcClass.eval(bx)

    if fb > fa:
        ax,bx = bx,ax
        fa,fb = fb,fa

    cx = bx + GOLD*(bx-ax)
    fc = funcClass.eval(cx)

    while fb > fc:
        r = (bx-ax)*(fb-fc)
        q = (bx-cx)*(fb-fa)
        u = bx - ((bx-cx)*q - (bx-ax)*r)/(2.0*SIGN(max(abs(q-r), TINY), q-r))

        ulim = bx + GLIMIT*(cx-bx)

        if (bx-u)*(u-cx) > 0.0:
            fu = funcClass.eval(u)
            if fu < fc:
                ax = bx; bx = u; fa = fb; fb = fu
                return ax, bx, cx, fa, fb, fc

            elif fu > fb:
                cx = u; fc = fu
                return ax, bx, cx, fa, fb, fc

            u = cx + GOLD*(cx-bx)
            fu = funcClass.eval(u)

        elif (cx-u)*(u-ulim) > 0.0:
            fu = funcClass.eval(u)
            if fu < fc:
                bx = cx; cx = u
                u = cx + GOLD*(cx-bx)

                fb = fc; fc = fu
                fu = funcClass.eval(u)

        elif (u-ulim)*(ulim-cx) >= 0.0:
            u = ulim
            fu = funcClass.eval(u)

        else:
            u = cx + GOLD*(cx-bx)
            fu = funcClass.eval(u)

        ax = bx; bx = cx; cx = u
        fa = fb; fb = fc; fc = fu

    return ax, bx, cx, fa, fb, fc


__ncom = None
__pcom = None
__xicom = None
__nrfunc = None

#-------------------------------------------------------------------------------
def f1dim(x):
#-------------------------------------------------------------------------------
    xt = Vector(__ncom)
    for j in xrange(__ncom):
        xt[j] = __pcom[j] + x*__xicom[j]
    return __nrfunc(xt)


#-------------------------------------------------------------------------------
class F1Dim(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ncom, pcom, xicom, funClass):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(F1Dim, self).__init__()
        self.ncom = ncom
        self.pcom = pcom
        self.xicom = xicom
        self.funClass = funClass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def eval(self, x):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xt = Vector(self.ncom)
        for j in xrange(self.ncom):
            xt[j] = self.pcom[j] + x*self.xicom[j]
        return self.funClass.eval(xt)

#-------------------------------------------------------------------------------
def linmin(p, xi, funcClass):
#-------------------------------------------------------------------------------
    """ modifies 'p' and 'xi'
    """
    n = len(p)

    ax = 0.0
    xx = 1.0

    f1dim = F1Dim(n, p.clone(), xi.clone(), funcClass)

    ax, xx, bx, fa, fx, fb = mnbrak(ax, xx, f1dim)
    fret, xmin = brent(ax, xx, bx, f1dim, TOL)

    for j in xrange(n):
        xi[j] *= xmin
        p[j] += xi[j]

    return fret

#-------------------------------------------------------------------------------
def SQR(x):
#-------------------------------------------------------------------------------
    return x*x

#-------------------------------------------------------------------------------
def powell(p, ftol, funcClass):
#-------------------------------------------------------------------------------
    """ Find the minimum of a function of n parameters

        inputs:
            p[0..n]  - an initial point
            funcClass - a funcClass.eval(pp[0..n])

        returns point at min, current direction set, value at min and num
        iterations
    """

    n = len(p)
    ptt = Vector(n)
    xit = Vector(n)

    xi = Matrix(n, n)
    xi.diag([1]*n)

    fret = funcClass.eval(p)
    pt = p.clone()

    for iter in xrange(ITMAX):
        fp = fret
        ibig = 0
        ddel = 0.0

        for i in xrange(n):
            for j in xrange(n):
                xit[j] = xi[j][i]

            fptt = fret

            fret = linmin(p, xit, funcClass)

            if abs(fptt-fret) > ddel:
                ddel = abs(fptt-fret)
                ibig = i

        if (2.0*abs(fp-fret)) <= ftol*(abs(fp) + abs(fret)):
            return p, xi, fret, iter

        for j in xrange(n):
            ptt[j] = 2.0*p[j] - pt[j]
            xit[j] = p[j] - pt[j]
            pt[j] = p[j]

        fptt = funcClass.eval(ptt)

        if fptt < fp:
            t = 2.0 * (fp - 2.0*fret + fptt) * SQR(fp - fret - ddel) - ddel * SQR(fp - fptt)

            if t < 0.0:
                fret = linmin(p, xit, funcClass)

                for j in xrange(n):
                    xi[j][ibig] = xi[j][n-1]
                    xi[j][n-1] = xit[j]

    else:
        raise "powell: Exceeded max iterations"

import sys
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    a = [[22., 10.,  2.,   3.,  7.],
         [14.,  7., 10.,   0.,  8.],
         [-1., 13., -1., -11.,  3.],
         [-3., -2., 13.,  -2.,  4.],
         [ 9.,  8.,  1.,  -2.,  4.],
         [ 9.,  1., -7.,   5., -1.],
         [ 2., -6.,  6.,   5.,  1.],
         [ 4.,  5.,  0.,  -2.,  2.]]

    u, w, v = svd(a)
    print w

    # [35.327043465311384, 1.2982256062667619e-15,
    #  19.999999999999996, 19.595917942265423, 0.0]

    print (math.sqrt(1248.), 20., math.sqrt(384.), 0., 0.)
    print
    # (35.327043465311391, 20.0, 19.595917942265423, 0.0, 0.0)

    A = Matrix(a)
    A.name = 'A'

    U = Matrix(u)
    U.name = 'U'

    V = Matrix(v)
    V.name = 'V'

    W1 = Matrix()

    m = max(w)
    print 'm', m
    for i in xrange(len(w)):
        if w[i] < m*1e-6:
            w[i] = 0

    print w
    W1.diag(w, reciprocal=True)

    print W1

    W = Matrix()
    W.diag(w)


    print U * W * V.trans()

    print U.trans() * U
    print V.trans() * V

    A1 = V * W1 * U.transpose()
    A1.name = 'A1'
    print A1

    print "A*A1"
    print A1 * A


    u, w, v = svd(a)
    print w


    C = Matrix([[1, 2, 3],
                [1, 3, 3],
                [1, 2, 4]])

    D = Matrix([[ 6,-2,-3],
                [-1, 1, 0],
                [-1, 0, 1]])

    U, w, V = svdcomp(C)
    print w


    print C*D
    print D*C

    W1.diag(w, reciprocal=True)
    print V * W1 * U.transpose()
    print D

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)

