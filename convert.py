#!/usr/bin/env python
"""
usage:

usage: convert <num> <units1> <units2>
    convert 'num' 'units1' into 'units2'
    units can be:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import types
import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('d', 'debug')], [], usage)

    if not args:
        usage(1)

    rules.debug = opts.debug

    du = args[-1]
    if args[-2] == '=':
        args = args[:-2]
    else:
        args = args[:-1]

    tdu = args[-1]
    val = 0.0

    i = 0
    while i < len(args):
        amt = float(args[i])
        tsu = args[i+1]
        i += 2

        num = convert(amt, tsu, tdu)
        if num is None:
            print("Conversion between '%s' and '%s' not found" % (tsu, tdu))
            oss.exit(2)

        val += num

    num = convert(val, tsu, du)
    if num is None:
        print("Conversion between '%s' and '%s' not found" % (tsu, du))
        oss.exit(2)

    print('\n'.join(rules.log))
    print("%s  ==  %f %s" % (' '.join(args), num, du))

    oss.exit(0)


#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print(__doc__, file=oss.stderr)
    if errmsg:
        print("\nError:\n" + str(errmsg), file=oss.stderr)

    for nm, doc in rules.units():
        if doc:
            print(nm + ' -- ' + doc, file=oss.stderr)
        else:
            print(nm, file=oss.stderr)
    print(file=oss.stderr)

    oss.exit(rc)


#-------------------------------------------------------------------------------
class Unit(object):
#-------------------------------------------------------------------------------

    @staticmethod
    def factory(s):
        if isinstance(s, Unit):
            return s

        if '*' in s or '/' in s:
            return Unit(s)
        else:
            return s


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, num, denom=None, doc=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Unit, self).__init__()

        self.doc = doc

        if '/' in num:
            num, denom = num.split('/')

        self.num = num.split('*')
        self.num.sort()

        if denom is not None:
            self.denom = denom.split('*')
            self.denom.sort()
        else:
            self.denom = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __cmp__(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(v, Unit):
            return cmp(v.canonical(), self.canonical())

        if isinstance(v, str) and len(self.num) == 1 and len(self.denom) == 0:
            print("Unit.__cmp__:", v, self)
            return cmp(v, self.num[0])

        return -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def canonical(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return '*'.join(self.num) + "/" + '*'.join(self.denom)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self.denom) == 1:
            return '*'.join(self.num) + "/" + self.denom[0] + "   {" + self.doc + '}'
        elif len(self.denom) == 0:
            return '*'.join(self.num)  + "   {" + self.doc  + '}'
        else:
            return '*'.join(self.num) + "/(" + '*'.join(self.denom) + ')'  + "   {" + self.doc  + '}'


#-------------------------------------------------------------------------------
class Rule(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, amt1, unit1, unit2, amt2 = 1.0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Rule, self).__init__()
        self.amt1  = amt1

        if isinstance(unit1, (str, unicode)) and ':' in unit1:
            self.unit1, self.doc1 = unit1.split(':')
        else:
            self.unit1 = unit1
            self.doc1 = ''

        if isinstance(unit2, (str, unicode)) and ':' in unit2:
            self.unit2, self.doc2 = unit2.split(':')
        else:
            self.unit2 = unit2
            self.doc2 = ''

        self.amt2  = amt2

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idxTup):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        a, b = idxTup
        if a == 0:
            if b == 0:
                return self.amt1
            return self.unit1
        else:
            if b == 0:
                return self.amt2
            return self.unit2

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def doesRuleApply(self, su):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if su == self.unit1:
            return 1
        if su == self.unit2:
            return 2
        return 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDest(self, tok):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.unit2 if tok == 1 else self.unit1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNum(self, tok):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.amt1 if tok == 1 else self.amt2

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDenom(self, tok):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.amt2 if tok == 1 else self.amt1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def apply(self, tok, amt = 1.0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        num_func = self.getNum(tok)

        if isinstance(num_func, types.FunctionType):
            return num_func(amt)
        return amt*self.getDenom(tok)/num_func

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d1 = '{' + self.doc1 + '}' if self.doc1 else ''
        d2 = '{' + self.doc2 + '}' if self.doc2 else ''
        return "%s %s %s == %s %s %s" % (str(self.amt1), self.unit1, d1, str(self.amt2), self.unit2, d2)


#-------------------------------------------------------------------------------
class Rules(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, rules):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Rules, self).__init__()
        self.rules = rules
        self.debug = False
        self.verbose = True
        self.visited = set([])
        self.log = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.visited = set([])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, rule):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.rules.append(rule)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def units(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = {}
        for e in self.rules:
            if e.unit1 not in d:
                d[e.unit1] = e.doc1
            elif e.doc1:
                d[e.unit1] = e.doc1
            if e.unit2 not in d:
                d[e.unit2] = e.doc2
            elif e.doc2:
                d[e.unit2] = e.doc2

        return d.items()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.rules[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def search(self, su, du):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ look for a direct conversion rule
        """

        for rule in self.rules:
            tok = rule.doesRuleApply(su)
            if tok and du == rule.getDest(tok):
                return rule, tok
        return None, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lookup(self, amt, su, du, times=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if su == du:
            return amt

        if isinstance(su, Unit):
            if isinstance(du, Unit):
                val = self.lookup(1.0, su.num[0], du.num[0], 0)
                if val is None:
                    return None

                if su.denom:
                    rules.clear()
                    val1 = self.lookup(1.0, su.denom[0], du.denom[0], 0)
                    if val1 is None:
                        return None

                    return val*val1*amt
                return val*amt

        self.visited.add((su, du))

        #
        # if this rule is found, calc and return
        #
        rule, tok = self.search(su, du)
        if rule is not None:
            val = rule.apply(tok, amt)
            if self.verbose: self.log.insert(0, str(rule))
            #if self.verbose: self.log.insert(1, "%7.6f  %s -- %s\n" % (val, su, du))

            return val

        #
        # rule not found, recursively look at possible intermediate rules
        #
        for rule in self.rules:
            tok = rule.doesRuleApply(su)
            if tok == 0:
                continue

            nsu = rule.getDest(tok)
            if (nsu, du) in self.visited:
                continue

            val = rules.lookup(rule.apply(tok, amt), nsu, du, times + 1)
            if not val: continue

            if self.verbose: self.log.insert(0, str(rule))
            #if self.verbose: self.log.insert(1, "%7.6f  %s -- %s\n" % (val, su, du))

            return val
        return None


rules = Rules([

    ## volume
    Rule(2.0, 'tbsp', 'fl_oz:fluid ounce'),
    Rule(3.0, 'tsp', 'tbsp:tablespoon'),
    Rule(5.0, 'ml:milliliter',  'tsp:teaspoon'),
    Rule(8.0, 'fl_oz', 'cup'),
    Rule(16.0, 'fl_oz', 'pint'),
    Rule(2.0, 'pint', 'quart'),
    Rule(4.0, 'quart', 'gal:gallon'),
    Rule(1000.0, 'ml', 'l:liter'),
    Rule(1.0, Unit('ft*ft*ft'), 'gal', 7.480519),
    Rule(8, 'gal', 'bushel'),


    ## mass
    Rule(28.348, 'g', 'oz:ounce'),
    Rule(1000.0, 'g:gram', 'kg:kilogram'),
    Rule(2.2047, 'lb:pound-mass', 'kg'),
    Rule(14, 'lb:pound-mass', 'stone'),
    Rule(2240, 'lb:pound-mass', 'ton'),

    ## distance
    Rule(2.54, 'cm:centimeter', 'in'),
    Rule(100.0, 'cm', 'm:meter'),
    Rule(10.0, 'mm:millimeter', 'cm'),
    Rule(1000.0, 'm', 'km:kilometer'),
    Rule(12.0, 'in:inch', 'ft:foot'),
    Rule(3.0, 'ft', 'yd:yard'),
    Rule(1.609, 'km', 'mi:statute mile'),
    Rule(1.151, 'mi', 'n_mi:nautical mile'),
    Rule(8.0, 'furlong', 'mi'),
    Rule(40.0, 'rod', 'furlong'),
    Rule(6.0, 'ft', 'fathom'),
    Rule(9.460e12, 'km', 'light-year'),
    Rule(3.262, 'light-year', 'parsec'),
    Rule(1.496e8, 'km', 'au:astronomical unit'),
    Rule(720, 'ft', 'cable'),
    Rule(3, 'mi', 'league'),
    Rule(16.5, 'ft', 'rod'),
    Rule(4, 'rod', 'chain'),
    Rule(4, 'in', 'hand'),

    ## area
    Rule(43560.0, Unit('ft*ft'), 'acre'),

    ## time
    Rule(60.0, 's:second', 'min:minute'),
    Rule(60.0, 'min', 'hr:hour'),
    Rule(24.0, 'hr', 'day'),

    ## physics
    Rule(1.0, Unit('kg*m', 's*s', 'F=ma'), 'N:newton, force'),
    Rule(1.0, Unit('N*m'), 'J:joule'),
    Rule(1.0, Unit('J', 's'), 'W:watt'),

    ## temperature
    Rule(lambda f: 5.0/9.0 * (f - 32.0), "F:fahrenheit", "C:celsius", lambda c: 9.0/5.0 * c + 32),
    Rule(lambda k: k - 273.16, 'K:kelvin', 'C', lambda c: c+273.16),
    Rule(lambda r: r - 459.69, 'R:rankin', 'F', lambda f: f + 459.69),

    ## pressure
    Rule(0.01450377, 'psi', 'millibar'),
    Rule(1, Unit('lbf', 'in*in'), 'psi'),
    Rule(9.67841e-4, 'atmosphere', 'millibar'),


    ])


#-------------------------------------------------------------------------------
def convert(amt, su, du):
#-------------------------------------------------------------------------------
    su = Unit.factory(su)
    du = Unit.factory(du)
    return rules.lookup(amt, su, du)


if __name__ == "__main__":
    main(oss.argv)

