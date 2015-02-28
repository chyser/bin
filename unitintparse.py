#!/usr/bin/env python
"""
"""

import pylib.osscripts as oss

import pylib.util as util
import pprint


#-------------------------------------------------------------------------------
class Unit(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, typid):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._lead = '#Type Id#'
        self._leaders = {}
        self._order = []
        self._cvt = {}
        self.typid = typid

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, a, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        k = lst[0]
        self._leaders[k] = self._lead
        self._order.append(k)
        self._cvt[k] = (self.pListItems, a)

        for idx, attr in enumerate(lst):
            self.__dict__[attr] = a[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pListItems(self, v, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(a) == 0:
            return 'NULL'

        s = ''
        for v in a:
            s += '[' + str(v) + ']'
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pForList(self, v, a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(a) == 0:
            return 'F'

        if a[0] is None:
            return 'F'

        s = 'T'
        for v in a:
            s += '[' + str(v) + ']'
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pDict(self, d, *a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(d) == 0:
            return 'NULL'

        s = ''
        for k, v in d.items():
            s += k + '[' + str(v) + ']'
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pForVal(self, v, *a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if v is None:
            return 'F'
        return 'T[' + str(v) + ']'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pScanRange(self, d, *a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ''
        for k in d:
            s += '[%s][%s][%s]' % (k, str(d[k][0]), str(d[k][1]))
        return s


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, fr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        obj = self

        while 1:
            line = fr.get()
            if line is None:
                return

            if line.startswith('#Type Id#'):
                fr.back()
                return

            self._lead = line

            if line.startswith('# Names'):
                obj.lname = fr.get()
                obj.sname = fr.get()
                obj.abbrv = fr.get()

                d = []
                while 1:
                    line = fr.get()
                    if line.startswith('#END_DESC#'):
                        break
                    d.append(line)

                obj.desc = '\n'.join(d)

            elif line.startswith('#Mv Sound File#'):
                obj.mvsndfile = fr.get()
            elif line.startswith('#F Sound File#'):
                obj.fsndfile = fr.get()
            elif line.startswith('#D Sound File#'):
                obj.dsndfile = fr.get()

            elif line.startswith('#Class'):
                obj.classinfo = fr.get()

            elif line.startswith('#Producer'):
                obj.producer = fr.get()
                obj.prodInfo = ParseDict(fr.get())

            elif line.startswith('#Constructor'):
                obj.constructor = fr.get()
                obj.consInfo = ParseDict(fr.get())

            elif line.startswith('#Repair'):
                obj.repair = ParseDict(fr.get())

            elif line.startswith('#Icon Data#'):
                obj.icon = fr.get()

            elif line.startswith('#[Speed]'):
                a = ParseArray(fr.get())
                obj.add(a, ['speed', 'range', 'roaduse', 'nocrash'])

            elif line.startswith('#Movement A'):
                obj.mvallow = ParseDict(fr.get())

            elif line.startswith('# Scan while'):
                obj.scanWhileLoaded = fr.get()

            elif line.startswith('# Portage'):
                a = ParseArray(fr.get())
                obj.add(a, ['portageVal', 'portageCap'])

            elif line.startswith('# Load Not Moving'):
                obj.loadWhileStill = fr.get()

            elif line.startswith('# Unload While Hosted Only'):
                obj.unloadWhileHostedOnly = fr.get()

            elif line.startswith('# Can Only Drop Un-Hosted'):
                obj.dropUnhostedOnly = fr.get()
            elif line.startswith('# Sentry Loaded'):
                obj.sentryLoadedUnits = fr.get()
            elif line.startswith('# Override Terrain'):
                obj.overrideTerrain = fr.get()
            elif line.startswith('# Boarding Cost'):
                obj.boardingCost = fr.get()

            elif line.startswith('# [Can Land]'):
                a = ParseArray(fr.get())
                obj.add(a, ['canLand', 'combatFactor', 'moveLaunch', 'moveRentry'])

            elif line.startswith('# Land Terrain'):
                obj.landTerrain = ParseArray(fr.get())
                self._cvt['landTerrain'] = (self.pListItems, self.landTerrain)

            elif line.startswith('# CanCarry'):
                obj.transport = ParseArray(fr.get())
                self._cvt['transport'] = (self.pListItems, self.transport)

            elif line.startswith('# CanDisband'):
                obj.disband = fr.get()
            elif line.startswith('# IgnoreType'):
                obj.ignore = fr.get()

            elif line.startswith('# Move Combat'):
                a = ParseArray(fr.get())
                obj.add(a, ['mcDamage', 'maxStrength', 'notSiegeUnit'])

            elif line.startswith('# Ignore Terrain'):
                obj.ignTerr = fr.get()
            elif line.startswith('# Consumed on Attack'):
                obj.consumedOnAttack = fr.get()
            elif line.startswith('# Can Dig-In'):
                obj.canDigIn = fr.get()
            elif line.startswith('# Gives Dig-In'):
                obj.siegeDigInBonus = fr.get()
            elif line.startswith('# Siege Defenders'):
                obj.siegeDefenders = ParseDict(fr.get())
            elif line.startswith('# Attacks'):
                obj.attacks = ParseDict(fr.get())

            elif line.startswith('# Range Fire'):
                a = ParseArray(fr.get())
                obj.add(a, ['range', 'rangeDamage', 'stealth', 'noTire'])
            elif line.startswith('# Range Attacks'):
                obj.rangeAttacks = ParseDict(fr.get())

            elif line.startswith('# Allow Hosted Fire'):
                obj.allowHostedFire = fr.get()

            elif line.startswith('# Allow Hosted Bombard'):
                obj.allowHostedBombard = fr.get()

            elif line.startswith('# [Defensive Fire Capable'):
                a = ParseArray(fr.get())
                obj.add(a, ['defenseFire', 'defFireWithMove'])

            elif line.startswith('# Is a "City'):
                obj.isCity = fr.get()

            elif line.startswith('# Can Exploit'):
                obj.canExploit = fr.get()

            elif line.startswith('# Can Supply'):
                obj.canSupply = fr.get()

            elif line.startswith('# Supply Data'):
                a = ParseArray(fr.get())
                obj.add(a, ['sdUnitCost', 'sdNPVal', 'sdPVal', 'sdexplitVal', 'sdSupVal'])

            elif line.startswith('# Can Reenter'):
                obj.canReenter = fr.get()

            elif line.startswith('# Reentry'):
                a = ParseArray(fr.get())
                obj.add(a, ['reSpeed', 'reRange', 'reCost'])

            elif line.startswith('# Can Launch'):
                obj.canLaunch = fr.get()

            elif line.startswith('# Can Detonate'):
                obj.canDetonate = fr.get()

            elif line.startswith('# Is a Nuke'):
                obj.isNuke = fr.get()

            elif line.startswith('# Hits To Ex'):
                a = ParseArray(fr.get())
                obj.add(a, ['lvl2', 'lvl3'])

            elif line.startswith('# Can Dive #'):
                obj.canDive = fr.get()

            elif line.startswith('# Can Dive Crippled'):
                obj.canDiveCrip = fr.get()

            elif line.startswith('# Dive Change Type'):
                t = fr.get()
                obj.diveChgType = None if t[0] == 'F' else t[2:-1]
                self._cvt['diveChgType'] = (self.pForVal, None)

            elif line.startswith('# Can Rise #'):
                obj.canRise = fr.get()

            elif line.startswith('# Rise Change Type'):
                t = fr.get()
                obj.riseChgType = None if t[0] == 'F' else t[2:-1]
                self._cvt['riseChgType'] = (self.pForVal, None)

            elif line.startswith('# Allow Sub #'):
                obj.allowSubBelow = fr.get()

            elif line.startswith('# Move Attack Sub Level #'):
                obj.mvAttkSubLvl = fr.get()

            elif line.startswith('# Range Attack Sub Level #'):
                obj.rgAttkSubLvl = fr.get()


            elif line.startswith('# Can Morph'):
                t = fr.get()

                if t[0] == 'F':
                    a = [None, None, None, None, None]
                else:
                    a = ParseArray(t[1:])
                obj.add(a, ['morphHosted', 'morphType', 'morphLanguage', 'changeName', 'morphHostOnly'])
                self._cvt['morphHosted'] = (self.pForList, a)

            elif line.startswith('# Builds Roads'):
                obj.buildRoads= fr.get()

            elif line.startswith('# Destroys Roads'):
                obj.destRoads = fr.get()

            elif line.startswith('# Road Times'):
                obj.roadTimes = ParseDict(fr.get())

            elif line.startswith('# Unit Scan Ranges'):
                a = ParseArray(fr.get())
                m = len(a)//3
                d = {}
                for i in range(m):
                    idx = i * 3
                    d[a[idx]] = (a[idx+1], a[idx+2])

                obj.sighting = d
                self._cvt['sighting'] = (self.pScanRange, None)

            elif line.startswith('# Build Mines'):
                t = fr.get()
                obj.bldMineTime = None if t[0] == 'F' else t[2:-1]
                self._cvt['bldMineTime'] = (self.pForVal, None)

            elif line.startswith('# Scan Mines'):
                obj.scanMines = fr.get()

            elif line.startswith('# Disable Mines'):
                t = fr.get()
                obj.rmMineTime = None if t[0] == 'F' else t[2:-1]
                self._cvt['rmMineTime'] = (self.pForVal, None)

            elif line.startswith('# Buy Points Cost'):
                obj.buyCost = fr.get()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def diff(self, u, verbose=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dl = []
        for attr in self.__dict__:
            if attr == 'typid':
                continue

            try:
                if self.__dict__[attr] != u.__dict__[attr]:
                    if verbose:
                        dl.append((attr, self.__dict__[attr], u.__dict__[attr]))
                    else:
                        dl.append(attr)
            except KeyError:
                dl.append((attr, 'KeyError'))

        return dl


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for attr in self._order:
            if attr in self._leaders:
                l.append(self._leaders[attr])

            val = getattr(self, attr)
            if attr in self._cvt:
                func, arg = self._cvt[attr]
                l.append(func(val, arg))

            elif isinstance(val, dict):
                l.append(self.pDict(val, None))

            else:
                l.append(str(getattr(self, attr)))

        return '\n'.join(l)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setattr__(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not attr.startswith('_') and self._lead is not None:
            self._leaders[attr] = self._lead
            self._lead = None

        if not attr.startswith('_'):
            self._order.append(attr)
        self.__dict__[attr] = val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return pprint.pformat(self.__dict__)


#-------------------------------------------------------------------------------
class UnitDB(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.objs = {}

        fr = FileReader(fn)

        state = None
        while 1:
            line = fr.get()
            if line is None:
                break

            if state is None:
                if not line.startswith('#Type Id#'):
                    continue
                else:
                    state = 1

            if line.startswith('#Type Id#'):
                typid = fr.get()
                obj = self.objs[typid] = Unit(typid)
                obj.load(fr)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def diff(self, un1, un2, verbose):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        u1 = self.objs[un1]
        u2 = self.objs[un2]

        return u1.diff(u2, verbose)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def units(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []

        for k in sorted(self.objs):
            l.append((k, self.objs[k].lname))

        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, tid):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return self.objs[tid]
        except KeyError:
            return None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getAttrs(self, tid, attrs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(attrs, list):
            attrs = [attrs]

        u = self.get(tid)
        l = []
        for attr in attrs:
            l.append((attr, getattr(u, attr)))

        return l


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def same(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for o1 in self.objs.values():
            for o2 in self.objs.values():
                if o1.abbrv == o2.abbrv and o1 != o2:
                    l.append((o1.typid, o2.typid))

        return l



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)




#-------------------------------------------------------------------------------
class FileReader(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        inf = open(fileName, 'rU')
        self.lines = inf.readlines()
        inf.close()
        self.idx = 0
        self.max = len(self.lines)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def back(self, cnt=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.idx -= cnt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, idx=None, strip=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if idx is not None:
            self.idx = idx
        else:
            self.idx += 1

        if self.idx >= self.max:
            return None

        if strip:
            return self.lines[self.idx][:-1]
        return self.lines[self.idx]


#-------------------------------------------------------------------------------
def ParseArray(s):
#-------------------------------------------------------------------------------
    if s == 'NULL':
        return []

    a = []
    for i in s.split(']')[:-1]:
        a.append(i[1:])

    return a


#-------------------------------------------------------------------------------
def ParseDict(s):
#-------------------------------------------------------------------------------
    if s == 'NULL':
        return {}

    d = {}
    for i in s.split(']'):
        #print i
        try:
            k, v = i.split('[')
            d[k] = v
        except ValueError:
            pass

    return d

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('n', 'names'), ('s', 'same'), ('d', 'diff'), ('p', 'dump'), ('v', 'verbose')],
        [('a', 'attr')], __doc__ + main.__doc__)

    units = UnitDB('unitdb.ini')

    if opts.names:
        pprint.pprint(units.units())

    elif opts.diff:
        print units.diff(args[0], args[1], opts.verbose)

    elif opts.same:
        print units.same()

    elif opts.attr:
        pprint.pprint(units.getAttrs(args[0], opts.attr))

    elif opts.dump:
        print units.get(args[0]).dump()

    else:
        print units.get(args[0])


    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

