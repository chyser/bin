#!/usr/bin/env python
"""
Library:

"""

import random

#-------------------------------------------------------------------------------
class Random(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return random.random()


#-------------------------------------------------------------------------------
def greatly(p):
#-------------------------------------------------------------------------------
    return Prob(p.prob + (1.0 - p.prob)/2.0)


#-------------------------------------------------------------------------------
def barely(p):
#-------------------------------------------------------------------------------
    return Prob(p.prob - p.prob/2.0)


#-------------------------------------------------------------------------------
class Prob(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, prob=0, rg=Random()):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.set(prob)
        self.rg = rg

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, prob):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.prob = prob if 0 <= prob <= 1.0 else 1.0 if prob > 1.0 else 0.0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __and__(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return Prob(reduce(lambda p1,p2: p1.prob * p2.prob, args, self))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __invert__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return Prob(1.0 - self.prob)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __or__(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return Prob(1.0 - reduce(lambda p1,p2: (1.0 - p1.prob) * (1.0 - p2.prob), args, self))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __nonzero__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rg.get() < self.prob

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.prob)


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    return 0


if __name__ == "__main__":
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    p1 = Prob(0.8)
    p2 = Prob(0.7)
    p3 = Prob(0.7)

    p = p1 & p2 & p3
    print p1 | p2
    print ~p1

    if p:
        print "p was true"
    else:
        print "p was false"

    q = Prob(1.0)
    if q:
        print "q was true"
    else:
        print "q was false"

    if ~q:
        print "~q was true"
    else:
        print "~q was false"

    res = not __test__()
    oss.exit(res)


