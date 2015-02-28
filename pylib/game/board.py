#!/usr/bin/env python
"""
Library:

"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import wx
from . import util as game

import math

def sqr(x):
    return x * x

from . import engine as ge


#-------------------------------------------------------------------------------
class GObject(object):
#-------------------------------------------------------------------------------
    """ Base object for all things that can fit onto a GraphBoard
    """
    nextId = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, brd, coords=None, owner=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        assert isinstance(brd, GBoardBase)

        self.brd = brd                 # the board the gobj is on
        self.owner = owner             # owning player or None
        self.level = 0                 # painters algorithm drawing order
        self.coord = coords            # coordinates
        self.ox = self.oy = 0

        self.id = GObject.nextId       # assign a unique id
        GObject.nextId += 1

        self.visible = True
        self.color = None
        self.facing = 0
        ge.gObjects.add(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def completeInit(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.coord is not None:
            self.brd.set(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WriteInfo(self, htmlStr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ write 'htmlStr' to the info window
        """
        self.brd.WriteInfo(htmlStr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DisplayInfo(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ write object information to the info window
        """
        self.WriteInfo(self.getDispInfo(1))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDispInfo(self, detail=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the info to be displayed in the information window (takes html)
        """
        return ""

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def InfoCall(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ a call back for links clicked in the information window
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def beenObserved(self, observingPlyr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called when gobs are observed during the turn
        """
        self.brd.gobjObserved(self, observingPlyr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, coord, refreshNow=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.coord = self.brd.normalizeCoords(coord)
        self.brd.set(self, refreshNow)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, refreshNow=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.brd.rm(self, refreshNow)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def move(self, coord, refreshNow=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.rm(False)
        self.set(coord, refreshNow)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def changeBoard(self, brd, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ changes the current board to the new board
        """
        self.rm()
        self.brd = brd
        self.set(coord)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def changeLevel(self, level):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.level = level
        self.brd.reSort(self.coord)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def MakeVisible(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.brd.makeVisible(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # def draw(self, dc, coord, facing, nodeSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


#-------------------------------------------------------------------------------
class GTerrain(object):
#-------------------------------------------------------------------------------
    """ the base object for all terrain types
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, typ, brush=None, isHigh=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ 'typ' is the terrain typ objects can compare against
            'isHigh' is used to determine whether objects can hide behind terrain
        """
        object.__init__(self)
        self.typ = typ
        self.high = isHigh
        self.brush = brush

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isHigh(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.high

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getType(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.typ

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDispInfo(self, detail=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ displays information about this terrain. can use html formatting
        """
        return """
            <h2>%s</h2>
        """ % (self.typ)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def draw(self, dc, x, y, xx, a=None, pen=False, iso=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tp = wx.BLACK_PEN if pen or a else wx.TRANSPARENT_PEN
        if a is not None:
            if iso:
                game.DrawFilledIsoHex(dc, x, y, xx, a, self.brush, tp)
            else:
                game.DrawFilledHex(dc, x, y, xx, a, self.brush, tp)
        else:
            game.DrawFilledRect(dc, x, y, xx, self.brush, tp)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.typ

UnknownTerrain = GTerrain('UNKOWN', wx.BLACK_BRUSH)


#-------------------------------------------------------------------------------
class GBoards(object):
#-------------------------------------------------------------------------------
    """ keeps track of all the boards currently in use
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.boards = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return iter(self.boards)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, brd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.boards.append(brd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prepForNewTurn(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for brd in self.boards:
            brd.prepForNewTurn()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 'Boards:\n' + '\n'.join(["  %s" % (str(brd)) for brd in self.boards])


## keep track of all the boards in use
gBoards = GBoards()


#-------------------------------------------------------------------------------
class GBoardBase(object):
#-------------------------------------------------------------------------------
    """ the base object for graphics boards. this represents a 2-d array tied to
        an empire.MapDisplay display panel.
    """
    #---------------------------------------------------------------------------
    class BoardNode(object):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, terrIdx = None, explored = 0):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            self.__slot__ = ['gobj', 'terrIdx', 'height', 'explored', 'properties']
            self.gobj = None          # either None, a GUnit, or a list of GUnits
            self.terrIdx = terrIdx    # idetifies the terrain at the node
            self.height = 0           # identifies the height at the node
            self.explored = explored  # a bitmask representing whether explored for the various players
            self.properties = None    # can be a generic set of per node items to store

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        gBoards.add(self)

        self.display = None
        self.vis = set()
        self.oldvis = set()

        self.name = name
        self.bitmap = None           ## used for drawing the board

        self.observedObjs = set()
        self.prevObservedObjs = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setDisplay(self, display):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.display = display

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasInput(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.display is not None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getInput(self, x, y, ox=0, oy=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.display.queue.clear()
        self.display.ShowCursor(x, y, ox, oy)
        #print 'getting input'
        t = self.display.queue.get()
        print('getInput:', t)
        return t

        return self.display.queue.get()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inputDone(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print 'erasing cursor'
        self.display.EraseCursor()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WriteInfo(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.display.WriteInfo(s)
        except AttributeError:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prepForNewTurn(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ execute before the display owning player starts a new turn

            the implementation allows objects seen to remain visible for rest of
            turn even if movement would make them invisible at some point.
        """
        if self.display is None:
            return

        self.prevObservedObjs = self.observedObjs
        self.observedObjs = set()

        ## TODO[20091121_111802]: do we need this granularity or should it be done
        ## for all boards a single time

        ## perform all observations on this board. will set objs in observedObjs
        self.display.owner.performTurnObservations(self)

        ## gobjs that are no longer visible should be made invisible
        for gobj in self.prevObservedObjs - self.observedObjs:
            gobj.visible = False
            self.refresh(gobj, False)

            ## TODO[20091121_150830]: remove this if not needed
###        ## gobjs that are newly observed should be made visible
###        for gobj in self.observedObjs - self.prevObservedObjs:
###            gobj.visible = True
###            self.refresh(gobj, False)

        self.refreshNow()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def gobjObserved(self, gobj, obsPlyr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called when a new unit is observed. refreshNow() should be called
            after a sequence of these calls to update the display
        """
        if self.display is None or obsPlyr is not self.display.owner:
            return

        if gobj not in self.observedObjs:
            gobj.visible = True
            self.observedObjs.add(gobj)
            self.refresh(gobj, False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNode(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ gets the node at specified coordinates 'coord'
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DisplayNodeInfo(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        terr = self.getterr(coord)
        s = [terr.getDispInfo(1)]

        gobjs = self.get(coord)
        for go in gobjs:
            if go.visible:
                s.append(go.getDispInfo(2))

        self.WriteInfo(''.join(s))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getProperties(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the properties associated with coordinates 'coord'
        """
        bn = self.getNode(coord)
        if bn.properties is None:
            return set()
        return bn.properties

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addProperty(self, prop, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add a property to coordinates 'coord'
        """
        bn = self.getNode(coord)
        if bn.properties is None:
            bn.properties = set()
        bn.properties.add(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmProperty(self, prop, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ remove a property from coordinates 'coord'
        """
        bn = self.getNode(coord)
        if bn.properties is not None:
            bn.properties.discard(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasProperty(self, prop, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a boolean representing whether property 'prop' is associated with
            coordinates 'coord'
        """
        return prop in self.getProperties(coord)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setExplored(self, plyr, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ each player has a notion of what nodes are explored and what aren't
        """
        bn = self.getNode(coord)
        alreadyExplored = bn.explored & plyr.pid
        if 1 or not alreadyExplored:
            bn.explored |= plyr.pid
            self.refresh1(coord, plyr.pid, False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isExplored(self, plyr, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a boolean representing whether this terrain is explored by
            player 'plyr'
        """
        return plyr is None or self.getNode(coord).explored & plyr.pid

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of gobjects in node specified by coord
        """
        u = self.getNode(coord).gobj
        if u is None: return []

        if isinstance(u, list):
            return u
        return [u]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, gobj, refreshNow=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ place 'gobj' at it's or the specified coordinates 'coord'
        """
        bn = self.getNode(gobj.coord)

        b = bn.gobj
        if b is None:
            bn.gobj = gobj
        else:
            try:
                b.append(gobj)
            except:
                b = bn.gobj = [b, gobj]

            ## sort on level so that can just be painted in order
            b.sort(key=lambda x: x.level)

        if gobj.owner is not None:
            self.setExplored(gobj.owner, gobj.coord)
        self.refresh(gobj, refreshNow)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reSort(self, gobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        b = self.getNode(gobj.coord).gobj

        if isinstance(b, list):
            ## sort on level so that can just be painted in order
            b.sort(key=lambda x: x.level)
            self.refresh(gobj)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, gobj, refreshNow=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ remove 'gobj' from the board at it's coordinates
        """
        bn = self.getNode(gobj.coord)

        b = bn.gobj
        if b is gobj:
            bn.gobj = None
        else:
            b.remove(gobj)
            if len(b) == 1:
                bn.gobj = b[0]

        self.refresh(gobj, refreshNow)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getterr(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the terrain at specified coordinates
        """
        return self.terrainMap[self.getNode(coord).terrIdx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setterr(self, terr, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ set the terrain at specified coordinates
        """
        self.getNode(coord).terrIdx = self.terrainMap.getIdx(terr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def makeVisible(self, gobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ make the 'gobj' visible if hidden behind other objects
        """
        if self.display is None:
            return

        b = self.getNode(gobj.coord).gobj

        ## all cases where it is already visible
        if b is None or b is gobj or b[-1] is gobj:
            return

        ## put on top/end of list and refresh the node
        b.remove(gobj)
        b.append(gobj)
        self.refresh(gobj)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getAdjacentCoords(self, coord, rng=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inRangeAndExplore(self, coord, rng, plyr=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of tuples (gobj, distance) of gobjs within 'rng'
            distance of coordinates 'coord' that can be observed w.r.t. terrain
            and sets the seen nodes/squares/hexes as explored for 'plyr' if
            provided.
        """
        regions = {}

        ## place gobjs found and line of sight blocking terrain into appropriate
        ## region
        for coord1, l in self.getAdjacentCoords(coord, rng):
            idx = int(round(math.atan2(coord1[1]-coord[1],coord1[0]-coord[0])*16/math.pi))
            if idx not in regions: regions[idx] = []

            regions[idx].extend([(go, l) for go in self.get(coord1)])
            if self.get(coord1):
                self.display.dbg('idx: %d' % idx)

            if self.getterr(coord1).isHigh():
                regions[idx].append((None, l + 0.1))

            ## TODO[20091121_132102]: currently terrain doesn't block the visibility
            ## of other terrain. That is harder and there maybe some justification
            ## for the current behavior
            if plyr is not None:
                self.setExplored(plyr, coord1)

        gobjs = []

        ## sort on distance from observer. Assume nothing in this region is visble
        ## past any LOS blocker
        for v in regions.values():
            for go, l in sorted(v, key=lambda s: s[1]):
                if go is None:
                    break
                gobjs.append((go, l))

        if plyr is not None:
            self.refreshNow()

        return sorted(gobjs, key=lambda s: s[1])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inRange(self, coord, rng):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of tuples (gobj, distance) of gobjs within 'rng'
            distance of coordinates 'coord'. Note: These may not be observable.
        """
        gobjs = []
        for coord, l in self.getAdjacentCoords(coord, rng):
            gobjs.extend([(go, l) for go in self.get(coord)])
        return sorted(gobjs, key=lambda s: s[1])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refresh(self, gobj, now=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ conditionally refreshes the display
        """
        if self.display is None: return
        self.display.refreshNeeded(gobj.coord, now, (gobj.ox, gobj.oy, self.wrap))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refresh1(self, coord, mask, now=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ conditionally refreshes the display
        """
        if self.display is None: return
        self.display.refreshNeeded(coord, now=now)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNow(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ refresh display immediately (used after a number of delayed refreshes)
        """
        if self.display is None: return
        self.display.screenRefresh()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "%s: Display: %s, Type: %s" % (brd.name, str(brd.display), str(type(brd)))


#-------------------------------------------------------------------------------
class RectangularBoard(GBoardBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, wrap=True, BoardNodeType=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        GBoardBase.__init__(self, name)

        self.terrainMap = game.IndexObj()
        self.boardNodeType = GBoardBase.BoardNode if BoardNodeType is None else BoardNodeType

        self.wrap = wrap
        self.XSize = self.YSize = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalizeCoords(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ ensure coordinates 'coord' map to the board either by wrapping
            or saturation
        """
        x, y = coord

        if self.wrap:
            rx = (x + self.XSize) % self.XSize
            ry = (y + self.YSize) % self.YSize
        else:
            rx = game.SatVal(x, maxV=self.XSize-1)
            ry = game.SatVal(y, maxV=self.YSize-1)

        return rx, ry

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNode(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.normalizeCoords(coord)
        return self.brd[x][y]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, XSize, YSize, defaultTerr = None, Visible=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ create a board of a certain size with a default terrain. 'Visible'
            controls whether terrain is initially visible or unexplored
        """
        self.XSize = XSize
        self.YSize = YSize

        terrIdx = self.terrainMap.getIdx(defaultTerr)
        vis = 0xffffffff if Visible else 0

        self.brd = [[self.boardNodeType(terrIdx, vis) for j in range(self.YSize)] for i in range(self.XSize)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasProperty(self, prop, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a boolean representing whether property 'prop' is associated with
            coordinates 'coord'

            OVERRIDDEN for perf
        """
        x, y = coord
        try:
            return prop in self.brd[x][y].properties
        except TypeError:
            return False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isExplored(self, plyr, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a boolean representing whether this terrain is explored by
            player 'plyr'

            OVERRIDDEN for perf
        """
        try:
            x, y = coord
            return self.brd[x][y].explored & plyr.pid
        except IndexError:
            x, y = self.normalizeCoords(coord)
            return self.brd[x][y].explored & plyr.pid

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of gobjects in node specified by coord

            OVERRIDDEN for perf
        """
        try:
            x, y = coord
            u = self.brd[x][y].gobj
        except IndexError:
            x, y = self.normalizeCoords(coord)
            u = self.brd[x][y].gobj

        if u is None: return []

        if isinstance(u, list):
            return u
        return [u]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getterr(self, coord):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the terrain at specified coorinates

            OVERRIDDEN for perf
        """
        try:
            x, y = coord
            return self.terrainMap[self.brd[x][y].terrIdx]
        except IndexError:
            x, y = self.normalizeCoords(coord)
            return self.terrainMap[self.brd[x][y].terrIdx]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance(self, coord1, coord2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the distance between 2 sets of coordinates
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance2(self, c1, c2, rng, rng2=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ checks if dist beetwen coordinates is less than rng and returns
            actual distance if true else None

            rng2 should be rng*rng
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getAdjacentCoords(self, coord, rng=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of tuples (coord, distance) of coordinates within
            distance 'rng' of coordinates 'coord'
        """
        adjCoords = {}
        x, y = coord

        rng2 = rng*rng
        for i in xrange(x - rng, x + rng + 1):
            for j in xrange(y - rng, y + rng + 1):
                r = self.calculateDistance2((i, j), (x, y), rng, rng2)
                if r is not None:
                    adjCoords[((i, j), r)] = None

        return adjCoords.keys()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return GBoardBase.__str__(self) + ' Size: %d, %d' % (self.XSize, self.YSize)


#-------------------------------------------------------------------------------
class BoardOfSquares(RectangularBoard):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance(self, c1, c2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return math.sqrt(sqr(c1[0] - c2[0]) + sqr(c1[1] - c2[1]))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance2(self, c1, c2, rng, rng2=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ checks if dist beetwen coordinates is less than rng and returns
            actual distance if true else None

            rng2 should be rng*rng
        """
        assert rng2 == rng*rng

        v = sqr(c1[0] - c2[0]) + sqr(c1[1] - c2[1])
        if v <= rng2:
            return math.sqrt(v)


#-------------------------------------------------------------------------------
class BoardOfHexes(RectangularBoard):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, wrap=True, BoardNodeType=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        RectangularBoard.__init__(self, name, wrap, BoardNodeType)
        self.iso = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance(self, c1, c2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return game.CalcHexDistance(c1[0], c1[1], c2[0], c2[1])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calculateDistance2(self, c1, c2, rng, rng2=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ checks if dist beetwen coordinates is less than rng and returns
            actual distance if true else None

            rng2 should be rng*rng
        """
        v = sqr(c1[0] - c2[0]) + sqr(c1[1] - c2[1])
        if v <= rng2:
            return math.sqrt(v)


#-------------------------------------------------------------------------------
def __test__():
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

    sqb = BoardOfSquares('test board')

    for brd in gBoards:
        print(brd)

    print(gBoards)

    res = not __test__()
    oss.exit(res)

