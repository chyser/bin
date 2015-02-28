#!/usr/bin/env python
"""
usage:

"""

import math

#-------------------------------------------------------------------------------
class triple(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, xs, y=0, z=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        try:
            self.x = xs[0] + 0
            self.y = xs[1]
            self.z = xs[2]
        except TypeError:
            try:
                self.x = xs.x + 0
                self.y = xs.y
                self.z = xs.z
            except AttributeError:
                self.x = xs + 0
                self.y = y
                self.z = z

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if idx == 0: return self.x
        if idx == 1: return self.y
        if idx == 2: return self.z
        raise IndexError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, idx, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if idx == 0: self.x = v
        elif idx == 1: self.y = v
        elif idx == 2: self.z = v
        raise IndexError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in "xyz":
            yield(getattr(self, i))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "triple: " + str(self.x) + ' ' + str(self.y) + ' ' + str(self.z)

#-------------------------------------------------------------------------------
class point(triple):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, xs, y=0, z=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        triple.__init__(self, xs, y, z)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "point: " + str(self.x) + ' ' + str(self.y) + ' ' + str(self.z)


#-------------------------------------------------------------------------------
class vector(triple):
#-------------------------------------------------------------------------------
    ZERO = None
    ONE = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, xs, y=0, z=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        triple.__init__(self, xs, y, z)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def magnitude(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalize(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        m = self.magnitude()
        self.x /= m
        self.y /= m
        self.z /= m

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __neg__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self) * -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __nonzero__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self != vector.ZERO

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __len__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 3

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __eq__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.x == a.x and self.y == a.y and self.z == a.z

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __ne__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.x != a.x or self.y != a.y or self.z != a.z

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dotProduct(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.x * a.x + self.y * a.y + self.z * a.z

    dot = dotProduct

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def angle(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return math.degrees(math.acos(self.dot(a)/(self.magnitude() * a.magnitude())))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sign(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return cmp(self.dot(a), 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __add__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.x + a.x, self.y + a.y, self.z + a.z)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iadd__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.x += a.x; self.y += a.y; self.z += a.z

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __sub__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.x - a.x, self.y - a.y, self.z - a.z)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __isub__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.x -= a.x; self.y -= a.y; self.z -= a.z

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def crossProduct(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.y * a.z - self.z * a.y,
                      self.z * a.x - self.x * a.z,
                      self.x * a.y - self.y * a.x)

    cross = crossProduct

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __mul__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(a, vector):
            return self.crossProduct(a)
        return vector(self.x * a, self.y * a, self.z * a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __rmul__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.x * a, self.y * a, self.z * a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __imul__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.x *= a; self.y *= a; self.z *= a

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __div__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.x / a, self.y / a, self.z / a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __idiv__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.x /= a; self.y /= a; self.z /= a

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __floordiv__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return vector(self.x // a, self.y // a, self.z // a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __ifloordiv__(self, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.x //= a; self.y //= a; self.z //= a

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "vector: " + str(self.x) + ' ' + str(self.y) + ' ' + str(self.z)


vector.ZERO = vector(0, 0, 0)
vector.ONE = vector(1, 1, 1)

#-------------------------------------------------------------------------------
class matrix(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, row_l=None, col=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(matrix, self).__init__()
        self.name = ""

        if row_l is not None:
            self.__alloc(row_l, col)
        else:
            self.data = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __alloc(self, row_l, col):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(row_l, matrix):
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

        T = matrix(n, m)
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

        if isinstance(b, matrix):
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
            c = matrix(cm, cn)

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
class Identity(matrix):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, m):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Identity, self).__init__()
        self.diag([1.0]*m)
        self.name = "Identity"


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    import pylib.tester as tester

    v2 = vector(1.3, 2, 3.1)
    tester.Assert(v2.crossProduct(v2) == vector.ZERO)
    tester.Assert(v2 + v2 != 2.1 * v2)
    tester.Assert(v2 + v2 == 2 * v2)
    tester.Assert(v2 - v2 == vector.ZERO)
    tester.Assert(vector([1, 0, 0]) * vector(point((0, 1, 0))) == vector(vector(0, 0, 1)))
    tester.Assert(vector([v for v in vector.ONE]) == vector.ONE)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])

    v = vector(2, 0, 0)
    print v.magnitude()

    print v * 12.1

    v1 = vector(0, 2, 0)

    print v.angle(v1)

    v2 = vector(1.3, 2, 0)
    print v2.crossProduct(v2)

    print vector.ZERO

    __test__()
    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    main(oss.argv)

