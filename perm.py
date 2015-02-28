#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss

import permutations

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
class PM(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(PM, self).__init__()
        self.name = name
        self.vms = []
        self.max = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addVm(self, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self.vms) >= self.max:
            return False
        self.vms.append('VM_%d' % id)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.vms = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def equal(self, pm):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self.vms) != len(pm.vms):
            return False

        return len(diffList(self.vms, pm.vms)) == 0


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.name + ': ' + str(self.max) + '  ' + str(self.vms)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def order(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vms = list(self.vms)
        vms.sort()
        return self.name + ': ' + str(vms)


#-------------------------------------------------------------------------------
class Collective(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, num):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Collective, self).__init__()
        self.pms = [PM("PM_%d" % i) for i in range(num)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCap(self, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for idx, m in enumerate(self.pms):
            m.max = lst[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addPM(self, pm):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.pms.append(pm)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for pm in self.pms:
            pm.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, vml):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = calcList(vml)

        pidx = 0
        for v in vml:
            #print "pidx:", pidx, "v:", v
            while not self.pms[pidx].addVm(v):
                pidx += 1
                #print "> pidx:", pidx, "v:", v

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def equal(self, co):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in range(len(self.pms)):
            if not self.pms[i].equal(co.pms[i]):
                return False
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def order(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for i in self.pms:
            s.append(i.order())
        return '\n'.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for i in self.pms:
            s.append(str(i))
        return '\n'.join(s)


#-------------------------------------------------------------------------------
def cool(v, lst):
#-------------------------------------------------------------------------------
    c = []
    for i in lst:
        if isinstance(v, list):
            vv = v[:]
        else:
            vv = [v]
        vv.append(i)
        c.append(vv)
    return c

#-------------------------------------------------------------------------------
def sumList(num, width):
#-------------------------------------------------------------------------------
    l = range(num + 1)

    g = l[:]

    for j in range(width-1):
        a = []
        for i in g:
            a.extend(cool(i, l))
        g = a

    b = []
    for i in a:
        if sum(i) == num:
            b.append(i)
    return b

#-------------------------------------------------------------------------------
def calcList(p):
#-------------------------------------------------------------------------------
    d = {}
    for i in range(len(p) + 1):
        for pp in p:
            try:
                d[tuple(pp[0:i])] = 1
            except: pass

    t = {}
    for k in d.keys():
        l = [i for i in k]
        l.sort()
        t[tuple(l)] = 1

    return t

#-------------------------------------------------------------------------------
def diffLists(a, b):
#-------------------------------------------------------------------------------
    """ return a - b
    """

    c = []
    for i in a:
        if i not in b:
            c.append(i)
    return c

#-------------------------------------------------------------------------------
def sum(lst):
#-------------------------------------------------------------------------------
    s = 0
    for i in lst:
        s += i
    return s


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)


    vn = 5
    pn = 5
    il = range(vn)
    p = permutations.Permutations(il)

    lll = sumList(vn, pn)
    cc = []

    print "creating lists"
    for cap in lll:
        for vml in p.ans:
            co = Collective(pn)
            co.addCap(cap)
            cc.append(co)
            co.create(vml)

    t = {}
    for c in cc:
        t[c.order()] = c

    print "pn:", pn, "vn:", vn
    print pow(pn, vn)
    print len(t.keys())
    #for tt in t.values():
    #    print "\n" + str(tt)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

