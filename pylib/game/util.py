#!/usr/bin/env python
"""
Library:

"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import sys
import math
import random
import itertools as it

import wx
import pylib.osscripts as oss
import pylib.util as util

class GameException(Exception): pass

#-------------------------------------------------------------------------------
def SatVal(v, minV=0, maxV=sys.maxint):
#-------------------------------------------------------------------------------
    return max(minV, min(v, maxV))


#-------------------------------------------------------------------------------
def SatVals(*args, **kwds):
#-------------------------------------------------------------------------------
    """ saturate all passed in values
    """
    minV = 0 if 'minV' not in kwds else kwds['minV']
    maxV = sys.maxint if 'maxV' not in kwds else kwds['maxV']
    return tuple([max(minV, min(a, maxV)) for a in args])


#-------------------------------------------------------------------------------
def validateRect(x, y, width, height, maxX, maxY, minX=0, minY=0):
#-------------------------------------------------------------------------------
    return max(x, minX), max(y, minY), min(max(x + width, 1), maxX), min(max(y + height, 1), maxY)


#-------------------------------------------------------------------------------
def validateMaxRect(x, y, width, height, maxX, maxY):
#-------------------------------------------------------------------------------
    return x, y, min(x + width, maxX), min(y + height, maxY)


gBITMAPDIR = "./bmp/"

#-------------------------------------------------------------------------------
def LoadBitmaps(Name):
#-------------------------------------------------------------------------------
    l = []
    for ch in "0123456789":
        l.append(LoadBitmap(Name + ch))

    if not any(l):
        raise GameException('No bitmaps loaded: ' + Name)

    return l


#-------------------------------------------------------------------------------
def LoadBitmap(Name, pth=None):
#-------------------------------------------------------------------------------
    if not pth:
        pth = gBITMAPDIR

    fn = "%s%s.bmp" % (pth, Name)
    if not oss.exists(fn):
        return None

    bmp = wx.Bitmap(fn, wx.BITMAP_TYPE_BMP)
    mdc = wx.MemoryDC()
    mdc.SelectObject(bmp)
    cc = mdc.GetPixel(0,0)
    mdc.SelectObject(wx.NullBitmap)

    mask = wx.Mask(bmp, cc)
    bmp.SetMask(mask)
    return bmp


#-------------------------------------------------------------------------------
def LoadMap(Name):
#-------------------------------------------------------------------------------
    bmp = wx.Bitmap(gBITMAPDIR + Name + '.bmp', wx.BITMAP_TYPE_BMP)

    map = wx.MemoryDC()
    mask = wx.Mask(bmp, "#000000")
    bmp.SetMask(mask)

    map.SelectObject(bmp)
    return map, mask


#-------------------------------------------------------------------------------
class Facing(object):
#-------------------------------------------------------------------------------
    seq = ['d1','d4','d7','d8','d9','d6','d3','d2']
    len = len(seq)
    d = {}
    for i, v in enumerate(seq):
        d[v] = i

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, facing):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        if isinstance(facing, int):
            facing = 'd%d' % facing
        elif isinstance(facing, Facing):
            facing = facing.facing

        self.facing = facing

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __sub__(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(v, Facing):
            v = Facing(v)
        t = abs(Facing.d[self.facing] - Facing.d[v.facing])
        if t > 4: t = 8 - t
        return t

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Clockwise(self, amt=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f = Facing.d[self.facing]
        idx = (f + amt) % Facing.len
        return Facing(Facing.seq[idx])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CounterClockwise(self, amt=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f = Facing.d[self.facing]
        idx = (f - amt) % Facing.len
        return Facing(Facing.seq[idx])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def opposite(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.Clockwise(4)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def i(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return int(self.facing[1])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.facing


#-------------------------------------------------------------------------------
class FacingCalc(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(FacingCalc, self).__init__()
        seq = [1,4,7,8,9,6,3,2]
        self.len = len(seq)
        self.d0 = {}; self.d1= {}
        for i, v in enumerate(seq):
            self.d0[i] = v
            self.d1[v] = i

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Clockwise(self, facing, amt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f = self.d1[facing]
        idx = (f + amt) % self.len
        return self.d0[idx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CounterClockwise(self, facing, amt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f = self.d1[facing]
        idx = (f - amt) % self.len
        return self.d0[idx]


__gFacingCalc = FacingCalc()

#-------------------------------------------------------------------------------
def AdjFacing(facing, dir, amt = 1):
#-------------------------------------------------------------------------------
    """ facing - [1,2,3,4,6,7,8,9]
        dir = ['l', 'r']
    """
    if dir == 'l':
        return __gFacingCalc.CounterClockwise(facing, amt)
    else:
        return __gFacingCalc.Clockwise(facing, amt)


_KEYS = {
    315 : 'd8',
    313 : 'd7',
    314 : 'd4',
    312 : 'd1',
    317 : 'd2',
    316 : 'd6',
    367 : 'd3',
    366 : 'd9',
    305 : 'd5',

    340 : "F1",
    341 : "F2",
    342 : "F3",
    343 : "F4",
    344 : "F5",
    345 : "F6",
    346 : "F7",
    347 : "F8",
    348 : "F9",
    349 : "F10",
    350 : "F11",
    351 : "F12",
    13  : "RET",
}


#-------------------------------------------------------------------------------
def CvtKeyToCmds(key):
#-------------------------------------------------------------------------------
    try:
        return _KEYS[key]
    except KeyError:
        return chr(key)


#-------------------------------------------------------------------------------
def CvtKeyToHexCoords(x, y, facing, cmd):
#-------------------------------------------------------------------------------
    cvt = True

    ## home (7)
    if cmd == 'd7':
        x -= 1
        if x & 0x1 == 0:
            y -= 1
        facing = 7

    ## up arrow (8)
    elif cmd == 'd8':
        y -=1
        facing = 8

    ## dwn arrow (2)
    elif cmd == 'd2':
        y += 1
        facing = 2

    ## end (1)
    elif cmd == 'd1':
        x -= 1
        if x & 0x1 != 0:
            y += 1
        facing = 1

    ## pgdn (3)
    elif cmd == 'd3':
        x += 1
        if x & 0x1 != 0:
            y += 1
        facing = 3

    ## pgup (9)
    elif cmd == 'd9':
        x += 1
        if x & 0x1 == 0:
            y -= 1
        facing = 9

    ## left arrow (4)
    elif cmd == 'd4':
        x -= 1
        facing = 4

    ## right arrow (6)
    elif cmd == 'd6':
        x += 1
        facing = 6

    else:
        cvt = False

    return x, y, facing, cvt


#-------------------------------------------------------------------------------
def CvtKeyToSqCoords(x, y, facing, cmd):
#-------------------------------------------------------------------------------
    cvt = True

    ## home (7)
    if cmd == 'd7':
        x -= 1
        y -= 1
        facing = 7

    ## up arrow (8)
    elif cmd == 'd8':
        y -=1
        facing = 8

    ## dwn arrow (2)
    elif cmd == 'd2':
        y += 1
        facing = 2

    ## end (1)
    elif cmd == 'd1':
        x -= 1
        y += 1
        facing = 1

    ## pgdn (3)
    elif cmd == 'd3':
        x += 1
        y += 1
        facing = 3

    ## pgup (9)
    elif cmd == 'd9':
        x += 1
        y -= 1
        facing = 9

    ## left arrow (4)
    elif cmd == 'd4':
        x -= 1
        facing = 4

    ## right arrow (6)
    elif cmd == 'd6':
        x += 1
        facing = 6

    else:
        cvt = False

    return x, y, facing, cvt


#-------------------------------------------------------------------------------
class IndexObj(util.KeyRefDict):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(IndexObj, self).__init__()
        self.idx = 0
        self[None] = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(val, (str, int)):
            idx = val
        else:
            idx = self.idx
            self.idx += 1

        self[idx] = val
        return idx

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getIdx(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if val in self:
            return self.getkey(val)

        return self.add(val)


#-------------------------------------------------------------------------------
def GetDirection(x0, y0, x1, y1):
#-------------------------------------------------------------------------------
    """ get the direction from point 0 to point 1
    """
    if x0 < x1:
        if y0 < y1:
            return 'd3'
        elif y0 == y1:
            return 'd6'
        else:
            return 'd9'
    elif x0 > x1:
        if y0 < y1:
            return 'd1'
        elif y0 == y1:
            return 'd4'
        else:
            return 'd7'
    else:
        if y0 < y1:
            return 'd2'
        else:
            return 'd8'


#-------------------------------------------------------------------------------
def OppositeDirection(dir):
#-------------------------------------------------------------------------------
    return Facing(dir).opposite()


#-------------------------------------------------------------------------------
def GetFacing(x0, y0, x1, y1):
#-------------------------------------------------------------------------------
    return int(GetDirection(x0, y0, x1, y1)[1])


#-------------------------------------------------------------------------------
def getPath(x0, y0, x1, y1):
#-------------------------------------------------------------------------------
    return [GetDirection(x0, y0, x1, y1)]


#-------------------------------------------------------------------------------
def CalcHexDistance(x0, y0, x1, y1):
#-------------------------------------------------------------------------------
    dx = x1 - x0
    sy0 = y0 - x0//2
    sy1 = y1 - x1//2
    dy = sy1 - sy0
    return max(abs(dx), abs(dy)) if dx * dy < 0  else abs(dx+dy)


#-------------------------------------------------------------------------------
def DrawHexPartial(dc, x, y, xx, a):
#-------------------------------------------------------------------------------
    xx2 = xx//2
    dc.DrawLine(   x-a, y+xx2,    x+a,     y)
    dc.DrawLine(   x+a,     y, x+xx-a,     y)
    dc.DrawLine(x+xx-a,     y, x+xx+a, y+xx2)


#-------------------------------------------------------------------------------
def DrawHex(dc, x, y, w, a):
#-------------------------------------------------------------------------------
    w2 = w//2

    dc.DrawLine(  x-a, y+w2,     x+a,    y)
    dc.DrawLine(  x+a,    y,   x+w-a,    y)
    dc.DrawLine(x+w-a,    y,   x+w+a, y+w2)
    dc.DrawLine(x+w-a,  y+w, x+w+a+1, y+w2)
    dc.DrawLine(  x-a, y+w2,     x+a,  y+w)
    dc.DrawLine(  x+a,  y+w,   x+w-a,  y+w)


#-------------------------------------------------------------------------------
def DrawFilledHex(dc, x, y, xx, a, brush=None, pen=None):
#-------------------------------------------------------------------------------
    xx2 = xx//2
    lst = [wx.Point(   x-a, y+xx2),
           wx.Point(   x+a,     y),
           wx.Point(x+xx-a,     y),
           wx.Point(x+xx+a, y+xx2),
           wx.Point(x+xx-a,  y+xx),
           wx.Point(   x+a,  y+xx)]

    if pen:
        dc.SetPen(pen)

    if brush:
        dc.SetBrush(brush)
        dc.DrawPolygon(lst)
        dc.SetBrush(wx.NullBrush)
    else:
        dc.DrawPolygon(lst)

    if pen:
        dc.SetPen(wx.NullPen)


#-------------------------------------------------------------------------------
def DrawIsoHex(dc, x, y, w, a):
#-------------------------------------------------------------------------------
    w2 = w//2
    w4 = w//4

    dc.DrawLine(  x-a, y+w4,   x  +a,    y)
    dc.DrawLine(  x-a, y+w4,     x+a, y+w2)
    dc.DrawLine(  x+a,    y,   x+w-a,    y)
    dc.DrawLine(  x+a, y+w2,   x+w-a, y+w2)
    dc.DrawLine(x+w-a,    y,   x+w+a, y+w4)
    dc.DrawLine(x+w-a, y+w2, x+w+a+1, y+w4)


#-------------------------------------------------------------------------------
def DrawFilledIsoHex(dc, x, y, xx, a, brush=None, pen=None):
#-------------------------------------------------------------------------------
    xx2 = xx//2
    xx4 = xx//4

    lst = [wx.Point(   x-a, y+xx4),
           wx.Point(   x+a,     y),
           wx.Point(x+xx-a,     y),
           wx.Point(x+xx+a, y+xx4),
           wx.Point(x+xx-a, y+xx2),
           wx.Point(   x+a, y+xx2)]

    if pen:
        dc.SetPen(pen)

    if brush:
        dc.SetBrush(brush)
        dc.DrawPolygon(lst)
        dc.SetBrush(wx.NullBrush)
    else:
        dc.DrawPolygon(lst)

    if pen:
        dc.SetPen(wx.NullPen)


#-------------------------------------------------------------------------------
def DrawFilledRect(dc, x, y, xx, brush, pen):
#-------------------------------------------------------------------------------
    if pen:
        dc.SetPen(pen)

    if brush:
        dc.SetBrush(brush)
        dc.DrawRectangle(x, y, xx, xx)
        dc.SetBrush(wx.NullBrush)
    else:
        dc.DrawRectangle(x, y, xx, xx)

    if pen:
        dc.SetPen(wx.NullPen)


#-------------------------------------------------------------------------------
class RangeObj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, rng):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.rng = rng
        self.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.l0 = self.calc(0)
        self.l1 = self.calc(1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calc(self, x):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lst = []
        rng = self.rng
        for i,j in it.product(xrange(x - rng, x + rng + 1), xrange(-rng, rng + 1)):
            d = CalcHexDistance(i, j, x, 0)
            if d <= rng:
                lst.append((i-x, j, d))

        random.shuffle(lst)
        lst.sort(key = lambda s: 1024*s[2] + abs(s[0]) + abs(s[1]))
        return lst[1:]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inRange(self, x, y, rng):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i, j, d in self.l0 if x & 0x1 == 0 else self.l1:
            if d > rng:
                break
            yield x+i, y+j

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inRange0(self, rng, x=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i, j, d in self.l0 if x & 0x1 == 0 else self.l1:
            if d > rng:
                break
            yield i, j, d


gRange = RangeObj(10)

#-------------------------------------------------------------------------------
def inRange(x, y, maxx, maxy, rng):
#-------------------------------------------------------------------------------
    bx = max(0, min(x - rng, maxx))
    ex = max(0, min(x + rng + 1, maxx))
    by = max(0, min(y - rng, maxy))
    ey = max(0, min(y + rng + 1, maxy))

    return [(i, j) for i, j in it.product(xrange(bx, ex), xrange(by, ey)) if CalcHexDistance(i, j, x, y) <= rng]

inRange = gRange.inRange


_OFFSETs = [(-1, -1), (1, -1), (0,-1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)]

#-------------------------------------------------------------------------------
def adjacentHexes(x, y):
#-------------------------------------------------------------------------------
    if x & 1 == 1:
        return [(x+i, y+j) for i, j in _OFFSETs[:-2]]
    return [(x+i, y+j) for i, j in _OFFSETs[2:]]


#-------------------------------------------------------------------------------
def adjacentHexes1(x0, y0, x1, y1):
#-------------------------------------------------------------------------------
    """ list of adjacent hexes to x0,y0 ordered by closeness to x1,y1
    """
    if x0 & 1 == 1:
        lst = [(x0+i, y0+j) for i, j in _OFFSETs[:-2]]
    else:
        lst = [(x0+i, y0+j) for i, j in _OFFSETs[2:]]

    ll = [(i, j, CalcHexDistance(i, j, x1, y1)) for i, j in lst]
    ll.sort(key = lambda s: s[2])
    return ll


#-------------------------------------------------------------------------------
class AStarLocation(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __hash__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ same actual location should hash same in same or different objects
        """
        return


#-------------------------------------------------------------------------------
class AStarAlgorithm(object):
#-------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------
    class Node(object):
    #-------------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, location, mCost, parent):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            self.location = location # where is this node located
            self.mCost = mCost       # total move cost to reach this node
            self.parent = parent     # parent node
            self.score = 0           # calculated score (measure of fitness)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __eq__(self, n):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            return self.location == n.location

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __str__(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            return str(self.location) + ' c:%d, s:%d ' % (self.mCost, self.score)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNode(self, loc, mCost, parent = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return AStarAlgorithm.Node(loc, mCost, parent)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getBestOpenNode(self, maxCost):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.open:
            return

        lst = [n for n in self.open.values() if n.mCost < maxCost]
        if not lst:
            return

        lst.sort(key=lambda s: s.score)
        return lst[0]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _tracePath(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        locs = [node.location]
        n = node.parent

        while n.parent is not None:
            locs.insert(0, n.location)
            n = n.parent

        return locs, node.mCost

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _handleNode(self, node, end):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        del self.open[node.location]
        self.checked.add(node.location)

        for n in self.getAdjacentNodes(node, end):
            if n.location == end:
                return n

            if n.location in self.checked:
                continue

            ## if already in open, then was prior nodes neighbor
            elif n.location in self.open:
                continue
                ## since heuristic part of score is time independent, this won't matter
                on = self.open[n.location]

                if n.score < on.score:
                    on.mCost = n.mCost
                    on.score = n.score

            else:
                self.open[n.location] = n

        return None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findPath(self, startLoc, endLoc, maxCost=sys.maxint, maxNodes=sys.maxint):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.open = {}
        self.checked = set()
        cnt = 0

        nextNode = self.getNode(startLoc, 0)
        self.open[nextNode.location] = nextNode

        while nextNode is not None and cnt < maxNodes:
            cnt += 1
            res = self._handleNode(nextNode, endLoc)
            if res:
                self.open = {}
                self.checked = set()
                return self._tracePath(res)
            nextNode = self._getBestOpenNode(maxCost)

        self.open = {}
        self.checked = set()
        return [], 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getAdjacentNodes(self, curNode, destLocation):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of adjacent nodes to current node each with
            an assigned cost
        """
        pass


#-------------------------------------------------------------------------------
class InfluenceMap(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, sx, sy, wrap=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.sx = sx
        self.sy = sy
        self.wrap = wrap
        self.map = [[0 for j in range(sy)] for i in range(sx)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addInfluence(self, x, y, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.map[x][y] += val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calcCell(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sum = 0
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                rx, ry = self.normalizeCoords(i, j)
                sum += self.map[rx][ry]
        return sum

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calcCell1(self, x, y, map):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sum = 0
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if i == x and j == y:
                    continue
                rx, ry = self.normalizeCoords(i, j)
                sum += self.map[rx][ry]
        return sum

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def propagate(self, rounds=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        map1 = [[0 for j in range(self.sy)] for i in range(self.sx)]
        for r in range(rounds):
            map2 = [[0 for j in range(self.sy)] for i in range(self.sx)]
            for i in range(self.sx):
                for j in range(self.sy):
                    map2[i][j] += self.calcCell1(i, j, map2)
                    map2[i][j] = SatVal(map2[i][j], -1, 1)
            map1 = map2

        for i in range(self.sx):
            for j in range(self.sy):
                self.map[i][j] += map1[i][j]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalizeCoords(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ ensure coordinates 'coord' map to the board either by wrapping
            or saturation
        """
        if self.wrap:
            rx = (x + self.sx) % self.sx
            ry = (y + self.sy) % self.sy
        else:
            rx = SatVal(x, maxV=self.sx-1)
            ry = SatVal(y, maxV=self.sy-1)

        return rx, ry

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ''
        for j in range(self.sy):
            for i in range(self.sx):
                s += ' %2d' % int(self.map[i][j])
            s += '\n'
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str1__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ''
        for j in range(self.sy):
            for i in range(self.sx):
                s += '0' if self.map[i][j] == 0 else '+' if self.map[i][j] > 0 else '-'
            s += '\n'
        return s


#-------------------------------------------------------------------------------
class ObservationMap(InfluenceMap):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, x, y, rng, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = 2*rng+1
        InfluenceMap.__init__(self, s, s)
        self.ox = x
        self.oy = y
        self.rng = rng

        for i in range(s):
            for j in range(s):
                self.map[i][j] = rng - max(abs(i - rng), abs(j - rng))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, x, y, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.addInfluence(x - self.ox + self.rng, y - self.oy + self.rng, val)


#-------------------------------------------------------------------------------
class RegionRange(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, rng):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.rng = rng
        self.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.l0 = self.calc(0)
        self.l1 = self.calc(1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calc(self, x):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        regions = {}
        for i, j, d in gRange.inRange0(self.rng, x):
            #idx = int(round(math.atan2(i, j)*6.4/math.pi))
            idx = int(round(math.atan2(i, j)*12/math.pi))
            if idx not in regions: regions[idx] = []
            regions[idx].append((i, j, d))
        return sorted(regions.values(), key=lambda s: 1024*s[0][2] + abs(s[0][0]) + abs(s[0][1]))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getRegions(self, x=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.l0 if x & 0x1 == 0 else self.l1


gRegions = RegionRange(10)

#-------------------------------------------------------------------------------
def regions(x, y, rng):
#-------------------------------------------------------------------------------
    for ll in gRegions.getRegions(x):
        for l in ll:
            if l[2] > rng:
                break
            print(l[0] + x, l[1] + y, ' ', l[2], end='       ')
        print()


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    tester.Assert(CalcHexDistance(3, 3, 4, 1), 3)
    tester.Assert(CalcHexDistance(2, 4, 4, 1), 4)
    tester.Assert(CalcHexDistance(1, 4, 4, 1), 5)
    tester.Assert(CalcHexDistance(0, 5, 4, 1), 6)

    tester.Assert(CalcHexDistance(3, 3, 5, 0), 4)
    tester.Assert(CalcHexDistance(2, 4, 5, 0), 5)
    tester.Assert(CalcHexDistance(1, 4, 5, 0), 6)
    tester.Assert(CalcHexDistance(0, 5, 5, 0), 7)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    #import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

###
###    im = InfluenceMap(4, 5, False)
###    im.addInfluence(20, 15, 1)
###    im.addInfluence(20, 25, -1)
###    im.addInfluence(5, 8, -1)
###    im.addInfluence(4, 8, -1)
###
###    print im
###
###    im.propagate(50)
###
###    print im

    om = ObservationMap(10, 10, 3, 2)
    om.add(8,8, -2)
    om.add(10,8, -2)
    om.add(12,12, -2)
    print(om)

    om.propagate(4*3)
    print(om)

###    import pylib.timer as tt
###
###    st = tt.StopWatch()
###
###    st.start()
###    for i in range(100000):
###        inRange(5, 5, 10, 10, 3)
###    print(st.stop())
###    print(inRange(5, 5, 10, 10, 3))
###
###    st.start()
###    for i in range(100000):
###        inRange1(5, 5, 3)
###    print(st.stop())
###    print(inRange1(5, 5, 3))
###
###    st.start()
###    for i in range(100000):
###        list(gRange.inRange(5, 5, 3))
###    print(st.stop())
###    print(list(gRange.inRange(5, 5, 3)))
###
###    print(gRange)

    regions(15, 15, 4)
    regions(16, 15, 4)

    res = not __test__()
    oss.exit(res)
