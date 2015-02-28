#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import random


#-------------------------------------------------------------------------------
def rand():
#-------------------------------------------------------------------------------
    return 2 * (random.random() - 0.5)


#-------------------------------------------------------------------------------
class Noise(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rand(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 2 * (random.random() - 0.5)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise NotImplemented


#-------------------------------------------------------------------------------
class PinkNoise(Noise):
#-------------------------------------------------------------------------------
    """  constants and algorithm from: http://home.earthlink.net/~ltrammell/tech/pinkalg.htm
    """
    AV = [4.6306e-003, 5.9961e-003, 8.3586e-003]
    PV = [3.1878e-001, 7.7686e-001, 9.7785e-001]

    AV = [[0.01089, 0.00899, 0.01359],
          [0.01,    0.00763, 0.00832, 0.01036],
          [0.00224, 0.00821, 0.00798, 0.00694, 0.00992]
         ]

    PV = [[0.3190,  0.7756,  0.9613],
          [0.303,   0.7417,  0.0168,  0.9782],
          [0.15571, 0.30194, 0.74115, 0.93003, 0.98035]
         ]

    W = [0.252, 0.672, 0.0001, 0.171, 0.190, 0.286, 0.175, 0.233, 0.021]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, stages=3):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Noise.__init__(self)
        self.stages = stages
        self.randreg = []

        idx = stages - 3
        for igen in range(stages):
            self.randreg.append(self.AV[idx][igen] * self.rand())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        idx = self.stages - 3
        for igen in range(self.stages):
            if random.random() > self.PV[idx][igen]:
                self.randreg[igen] = self.AV[idx][igen] * self.rand()
        return sum(self.randreg)


#-------------------------------------------------------------------------------
class PinkNoise(Noise):
#-------------------------------------------------------------------------------
    W0 = 0.252
    W = [0.672, 0.0001, 0.171, 0.190, 0.286, 0.175, 0.233, 0.021]
    P = [0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        output =  self.rand() * self.W0
        level = random.random()

        for i in range(8):
            if level > self.P[i]:
                break
            output += self.rand() * self.W[i]

        if output < -1: return -1
        if output > 1:  return 1
        return output


#-------------------------------------------------------------------------------
class WhiteNoise(Noise):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rand()


#-------------------------------------------------------------------------------
class BrownNoise(Noise):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, delta = 0.05):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Noise.__init__(self)
        self.delta = delta
        self.val = self.rand()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.val += self.rand() * self.delta
        if self.val < -1:
            self.val = -1
        elif self.val > 1:
            self.val = 1
        return self.val


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

    print('-'*40)

    pn = PinkNoise()
    for i in range(20):
        print(pn.get())

    print('-'*40)

    bn = BrownNoise(0.3)
    for i in range(20):
        print(bn.get())

    print('-'*40)

    wn = WhiteNoise()
    for i in range(20):
        print(wn.get())


    res = not __test__(verbose=True)
    oss.exit(res)


