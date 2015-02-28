#!/usr/bin/env python
"""
Library:

"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import wx
import wx.html
import wx.aui
import pylib.mx as mx

from . import util as game
from . import engine as ge
from . import board as gb

import pylib.debug as dbg

import math


BACKGROUND = wx.Colour(245,245,225)
GAME_NOTIFY_CURSOR = wx.Colour(0xd0,0xd0,0)
REGULAR_CURSOR = wx.Colour(0,0xd0,0)

DEBUG_PAINT = False

#-------------------------------------------------------------------------------
class MapDisplayBase(mx.ScrolledCanvas, ge.GMapDisplay):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        mx.ScrolledCanvas.__init__(self, parent, id = -1, style = wx.WANTS_CHARS | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        ge.GMapDisplay.__init__(self, parent, board, owner)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.currentCursorColor = GAME_NOTIFY_CURSOR
        self.SetFocus()

        if DEBUG_PAINT:
            self.dbgFont = wx.Font(2, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
            self.oldUpdateRegion = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dbg(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert dbg.DbgPrint1(s + '\n')
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WriteInfo(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.WriteInfo(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawCursor(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ draw the cursor on the screen
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def screenRefresh(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.Update()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtEraseBackground(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass


#-------------------------------------------------------------------------------
class MapDisplayBufferDDDDDDDDDDDDDDDD(MapDisplayBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MapDisplayBase.__init__(self, parent, board, owner)

        self.CursorX = None
        self.CursorY = None
        self.CursorOX = 0
        self.CursorOY = 0

        self.nodePixelSizeX = nodePixelSize
        self.nodePixelSizeY = nodePixelSize

        self.MaxBrdSizeX = board.XSize
        self.MaxBrdSizeY = board.YSize

        self.buffer = wx.EmptyBitmap(self.MaxBrdSizeX, self.MaxBrdSizeY)
        self.nodesToUpdate = set()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def screenRefresh(self, coord=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if coord is None:
            return
        xs, ys, xe, ye = coord
        xs, ys = self.CalcScrolledPosition(xs, ys)
        xe, ye = self.CalcScrolledPosition(xe, ye)
        self.RefreshRect(wx.Rect(xs, ys, xe, ye))
        self.Update()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawCursor(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShowCursor(self, *a):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNeeded(self, coord, now=True, extra=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.refreshNode(coord, now, extra)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNode(self, coord, now=True, extra=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.nodesToUpdate.add(coord)

        if extra is not None:
            ox, oy, wrap = extra

            if wrap:
                if coord[0] == self.MaxBrdSizeX-1:
                    self.nodesToUpdate.add((0, coord[1]))
                    self.nodesToUpdate.add((0, coord[1]+1))
                if coord[1] == self.MaxBrdSizeY-1:
                    self.nodesToUpdate.add((coord[0], 0))
                    self.nodesToUpdate.add((coord[0]+1, 0))
            else:
                if ox > 0 or oy > 0:
                    self.nodesToUpdate.add((coord[0], coord[1]+1))
                    self.nodesToUpdate.add((coord[0]+1, coord[1]))
                    self.nodesToUpdate.add((coord[0]+1, coord[1]+1))

        if now:
            self.Draw()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Draw(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ this assumes that DrawBoard() will also draw terrain
        """
        dc = wx.BufferedDC(None, self.buffer)
        dc.BeginDrawing()

        ps = self.nodePixelSizeX

        print('1')
        for cx, cy in self.nodesToUpdate:
            print('2')
            px = cx * ps
            py = cy * ps

            ## handle unexplored and mormal terrain
            if not self.brd.isExplored(self.owner, (cx, cy)):
                gb.UnknownTerrainSquare.draw(dc, px, py, ps)
            else:
                self.brd.getterr((cx, cy)).draw(dc, px, py, ps)

            ## draw visible objects
            for go in self.brd.get((cx, cy)):
                if go.visible:
                    ox = ps / go.ox
                    oy = ps / go.oy
                    go.draw(dc, go.facing, px + ox, py + oy, ps)
                    print('visible: ', cx, cy)
                else:
                    print('not visible: ', cx, cy)


        ## draw cursor
        self.DrawCursor(dc)

        self.screenRefresh(dc.GetBoundingBox())
        dc.EndDrawing()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtPaint(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)


#-------------------------------------------------------------------------------
class MapDisplayRectangular(MapDisplayBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MapDisplayBase.__init__(self, parent, board, owner)

        self.CursorX = self.CursorY = None
        self.CursorOX = self.CursorOY = 0
        self.a = None
        self.iso = False

        self.nodePixelSizeX = nodePixelSize
        self.nodePixelSizeY = nodePixelSize

        self.MaxBrdSizeX = board.XSize
        self.MaxBrdSizeY = board.YSize

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Point2Coords(self, sx, sy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts screen coordinates to map coordinates and canvas pixel offsets
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Coords2Point(self, cx, cy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts map coordinates to screen coordinates
        """
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvtCoords(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ helper for converting coords from an event 'e'
        """
        return self.Point2Coords(e.m_x, e.m_y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtKeyToCoords(self, cx, cy, facing, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetClientCoords(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return rectangle in board coordinates that is on screen
        """
        cx, cy = self.GetViewStart()
        w, h = self.GetClientSizeTuple()
        w //= self.nodePixelSizeX
        h //= self.nodePixelSizeY

        return cx, cy, cx + w, cy + h, w, h

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def MakeCoordVisible(self, cx, cy, center = False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ make sure coordinates are visible
        """
        left, top, right, bottom, width, height = self.GetClientCoords()
        #print 'm1:', cx, cy, 'l:', left, top, 'r:', right, bottom, width, height
        ## if already visible, no change
        if left <= cx < right and top <= cy < bottom:
            return

        ## otherwise, center the coodinate in the screen
        ## TODO[20091123_100739]: this looked like it was divided by 4
        #w = (cx1 - cx0)/2; h = (cy1 - cy0)/2
        scx = game.SatVal(cx - width//2, 0, self.MaxBrdSizeX)
        scy = game.SatVal(cy - height//2, 0, self.MaxBrdSizeY)

        #print 'make:', scx, scy
        self.Scroll(scx, scy)
        #self.RefreshRect(wx.Rect(0, 0, self.nodePixelSizeX * self.MaxBrdSizeX, self.nodePixelSizeY * self.MaxBrdSizeY))
        #self.Update()
        #print self.GetViewStart()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShowXY(self, brd, cx, cy, ox, oy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ make sure the coordinates 'cx','cy' on board 'brd' are visible
        """
        self.parent.parent.DisplayBoard(brd)
        self.MakeCoordVisible(cx, cy, center = True)
        self.ShowCursor(cx, cy, ox, oy)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def FixCursorCoords(self, cx, cy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return game.SatVal(cx, 0, self.MaxBrdSizeX-1), game.SatVal(cy, 0, self.MaxBrdSizeY-1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShowCursor(self, cx, cy, ox=0, oy=0, clr=GAME_NOTIFY_CURSOR):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ sets the cursor
        """
        ocx = self.CursorX; ocy = self.CursorY

        self.curCursorClr = clr
        self.CursorX, self.CursorY = self.FixCursorCoords(cx, cy)
        self.CursorOX = ox
        self.CursorOY = oy
        print('cursor:', ox, oy)
        self.MakeCoordVisible(self.CursorX, self.CursorY)

        if ocx is not None:
            assert ocy is not None
            self.refreshNeeded((ocx, ocy), now=False)

        self.refreshNeeded((self.CursorX, self.CursorY), now=True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def EraseCursor(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.CursorX:
            ocx = self.CursorX
            self.CursorX = None
            self.refreshNeeded((ocx, self.CursorY))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtLeftDclick(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cx, cy, mx, my = self.cvtCoords(e)
        self.ShowCursor(cx, cy, clr=REGULAR_CURSOR)
        self.queue.put(ge.Action('ml2', (cx, cy)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtLeftDown(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cx, cy, mx, my = self.cvtCoords(e)
        self.ShowCursor(cx, cy, clr=REGULAR_CURSOR)
        self.queue.put(ge.Action('mld', (cx, cy)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtLeftUp(self, e, Sender = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cx, cy, mx, my = self.cvtCoords(e)
        self.queue.put(ge.Action('mlu', (cx, cy)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtRightDown(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cx, cy, mx, my = self.cvtCoords(e)
        self.brd.DisplayNodeInfo((cx, cy))

        self.SetFocus()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtChar(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ch = e.GetKeyCode()
        cc = game.CvtKeyToCmds(ch)
        #cx, cy, mx, my = self.CvtKeyToCoords(self.CursorX, self.CursorY, 0, game.CvtKeyToCmds(ch))

        print('putting char', ch, cc)
        self.queue.put(ge.Action('k', cc))
        self.parent.putChar(cc)
        #self.ShowCursor(cx, cy, REGULAR_CURSOR)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShowUpdateRegions(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ used for debugging. shows update regions as rectangles
        """
        if not DEBUG_PAINT:
            return True

        dc.SetPen(wx.Pen(wx.RED, 1, wx.SOLID))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        for rct in mx.RegionIterator(self.GetUpdateRegion()):
            dc.DrawRectangle(rct.x, rct.y, rct.width, rct.height)

        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawRectangle(self, dc, xs, ys, w, h):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ used for debugging
        """
        if not DEBUG_PAINT:
            return True

        print("dr:", xs//self.nodePixelSize, ys//self.nodePixelSize)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getYExtra(self, cx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        raise NotImplementedError()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBoard(self, dc, brdStartX, brdStartY, brdEndX, brdEndY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        psx = self.nodePixelSizeX
        psy = self.nodePixelSizeY

        for cx in range(brdEndX, brdStartX-3, -1):
            px = cx * psx
            dd = self.getYExtra(cx)

            for cy in range(brdEndY, brdStartY-3, -1):
                for go in self.brd.get((cx, cy)):
                    if go.visible:
                        py = cy * psy + dd
                        sx, sy = self.CvtCanvasToScreen(px, py)

                        if go.ox > 0:
                            ox = psx // go.ox
                            oy = psy // go.oy
                            go.draw(dc, go.facing, sx + ox, sy + oy, psx)
                        else:
                            go.draw(dc, go.facing, sx, sy, psx)
                    else:
                        print('not visible:', cx, cy)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBackground(self, dc, sx, sy, w, h, px, py, bsx, bsy, bex, bey):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.brd.bitmap:
            dc.Blit(sx, sy, w, h, self.brd.bitmap, px, py, wx.COPY, False)
            return

        psx = self.nodePixelSizeX
        psy = self.nodePixelSizeY
        for cx in range(bsx, bex+1):
            px = cx * psx

            dd = self.getYExtra(cx)

            for cy in range(bsy, bey+1):
                py = cy * psy + dd
                sx, sy = self.CvtCanvasToScreen(px, py)

                ## handle unexplored terrain
                if not self.brd.isExplored(self.owner, (cx, cy)):
                    gb.UnknownTerrain.draw(dc, sx, sy, psx, self.a, iso=self.iso)
                else:
                    self.brd.getterr((cx, cy)).draw(dc, sx, sy, psx, self.a, iso=self.iso)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtPaint(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ this blits from a bitmap of the board instead of drawing terrain
        """
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
        dc.BeginDrawing()

        w = self.MaxBrdSizeX * self.nodePixelSizeX
        h = self.MaxBrdSizeY * self.nodePixelSizeY
        dc.SetClippingRegion(0, 0, w, h)

        ## draw that part of the board that needs updating
        for rct in mx.RegionIterator(self.GetUpdateRegion()):
            cx, cy, px, py = self.Point2Coords(rct.x, rct.y)
            brdStartX, brdStartY, brdEndX, brdEndY = game.validateRect(cx, cy, rct.width//self.nodePixelSizeX, rct.height//self.nodePixelSizeY, self.MaxBrdSizeX, self.MaxBrdSizeY)

            sx, sy = self.CvtCanvasToScreen(px, py)
            self.DrawBackground(dc, sx, sy, rct.width, rct.height, px, py, brdStartX, brdStartY, brdEndX, brdEndY)
            self.DrawBoard(dc, brdStartX, brdStartY, brdEndX, brdEndY)

        ## draw cursor
        self.DrawCursor(dc)

        ## show the update regions in debug mode
        assert self.ShowUpdateRegions(dc)

        dc.EndDrawing()


#-------------------------------------------------------------------------------
class MapDisplayHex(MapDisplayRectangular):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize, nodePixelSizeY=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MapDisplayRectangular.__init__(self, parent, board, owner, nodePixelSize)

        if nodePixelSizeY:
            self.nodePixelSizeY = nodePixelSizeY

        self.MaxXPixelSize = self.MaxBrdSizeX * self.nodePixelSizeX
        self.MaxYPixelSize = self.MaxBrdSizeY * self.nodePixelSizeY + self.nodePixelSizeY//2
        self.SetupScrolling(self.nodePixelSizeX, self.nodePixelSizeY, self.MaxXPixelSize, self.MaxYPixelSize)

        self.a = int(round(self.nodePixelSizeX * math.cos(math.degrees(60))/4.0))
        #self.a = 36

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Point2Coords(self, sx, sy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts screen coordinates to map coordinates and canvas pixel offsets
        """
        px, py = self.CvtScreenToCanvas(sx, sy)

        cx = int((px + self.nodePixelSizeX-1)/self.nodePixelSizeX) - 1
        if cx % 2 == 0:
            cy = int((py + self.nodePixelSizeY/2 -1)/self.nodePixelSizeY) - 1
        else:
            cy = int((py + self.nodePixelSizeY-1)/self.nodePixelSizeY) - 1

        if cx < 0: cx = 0
        if cy < 0: cy = 0
        return cx, cy, px, py

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Coords2Point(self, cx, cy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts map coordinates to screen coordinates
        """
        px = cx * self.nodePixelSizeX
        dd = self.nodePixelSizeY//2 if cx % 2 == 0 else 0
        py = cy * self.nodePixelSizeY + dd
        return self.CvtCanvasToScreen(px, py)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtKeyToCoords(self, cx, cy, facing, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return game.CvtKeyToHexCoords(cx, cy, facing, cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawCursor(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.CursorX is None:
            return

        hx = self.nodePixelSizeX
        hy = self.nodePixelSizeY

        py = self.CursorY * hy + (hy//2 if self.CursorX % 2 == 0 else 0)
        px = self.CursorX * hx

        dc.SetPen(wx.Pen(self.currentCursorColor, 3, wx.SOLID))
        sx, sy = self.CvtCanvasToScreen(px, py)
        game.DrawHex(dc, sx+1, sy+1, hx-2, self.a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawHexPart(self, dc, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ps = self.nodePixelSizeX
        game.DrawHexPartial(dc, x, y, ps, self.a)

        if DEBUG_PAINT:
            dc.SetFont(self.font)
            dc.DrawText("%d:%d" % (x//ps, y//ps), x+2, y+(ps//2)-4)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawHex(self, dc, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ps = self.nodePixelSizeX
        game.DrawHex(dc, x, y, ps, self.a)

        if DEBUG_PAINT:
            dc.SetFont(self.font)
            dc.DrawText("%d:%d" % (x//ps, y//ps), x+2, y+(ps//2)-4)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawSquare(self, dc, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xx = self.HexPixelSize
        xx2 = xx//2

        dc.SetPen(wx.Pen(wx.Colour(255,0,0), 1, wx.DOT))
        dc.DrawLine(x, y, x+xx,    y)
        dc.DrawLine(x, y,    x, y+xx)

        dc.SetPen(wx.Pen(wx.Colour(220,220,0), 1, wx.DOT))
        dc.DrawLine(x, y+xx2, x+xx, y+xx2)
        dc.SetPen(wx.Pen(wx.BLACK, 1, wx.SOLID))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNeeded(self, coord, now=True, extra=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sx, sy = self.Coords2Point(coord[0], coord[1])
        self.RefreshRect(wx.Rect(sx - self.a, sy, self.nodePixelSizeX + 2*self.a, 2*self.nodePixelSizeY))
        if now:
            self.Update()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getYExtra(self, cx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.nodePixelSizeY//2 if cx % 2 == 0 else 0


#-------------------------------------------------------------------------------
class MapDisplayIsoHex(MapDisplayHex):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MapDisplayHex.__init__(self, parent, board, owner, nodePixelSize, nodePixelSize//2)
        self.iso = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBoard(self, dc, brdStartX, brdStartY, brdEndX, brdEndY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        psx = self.nodePixelSizeX
        psy = self.nodePixelSizeY

        for cx in range(brdEndX, brdStartX-3, -1):
            px = cx * psx
            dd = self.getYExtra(cx)

            for cy in range(brdEndY, brdStartY-3, -1):
                for go in self.brd.get((cx, cy)):
                    if go.visible:
                        py = cy * psy + dd
                        sx, sy = self.CvtCanvasToScreen(px, py)

                        if go.ox > 0:
                            ox = psx // go.ox
                            oy = psy // go.oy
                            go.draw(dc, go.facing, sx + ox, sy + oy, psx)
                        else:
                            go.draw(dc, go.facing, sx, sy - psy, psx)
                    else:
                        print('not visible:', cx, cy)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawCursor(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.CursorX is None:
            return

        hx = self.nodePixelSizeX
        hy = self.nodePixelSizeY

        py = self.CursorY * hy + (hy//2 if self.CursorX % 2 == 0 else 0)
        px = self.CursorX * hx

        dc.SetPen(wx.Pen(self.currentCursorColor, 3, wx.SOLID))
        sx, sy = self.CvtCanvasToScreen(px, py)
        game.DrawIsoHex(dc, sx+1, sy+1, hx-2, self.a)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawHexPart(self, dc, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ps = self.nodePixelSizeX
        game.DrawIsoHexPartial(dc, x, y, ps, self.a)

        if DEBUG_PAINT:
            dc.SetFont(self.font)
            dc.DrawText("%d:%d" % (x//ps, y//ps), x+2, y+(ps//2)-4)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawHex(self, dc, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ps = self.nodePixelSizeX
        game.DrawIsoHex(dc, x, y, ps, self.a)

        if DEBUG_PAINT:
            dc.SetFont(self.font)
            dc.DrawText("%d:%d" % (x//ps, y//ps), x+2, y+(ps//2)-4)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNeeded(self, coord, now=True, extra=None, recurse=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if recurse:
            self.refreshNeeded((coord[0], coord[1]-1), False, recurse=False)
        sx, sy = self.Coords2Point(coord[0], coord[1])
        self.RefreshRect(wx.Rect(sx - self.a, sy, self.nodePixelSizeX + 2*self.a , 2*self.nodePixelSizeY))
        if now:
            self.Update()


#-------------------------------------------------------------------------------
class MapDisplaySquare(MapDisplayRectangular):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MapDisplayRectangular.__init__(self, parent, board, owner, nodePixelSize)

        self.MaxXPixelSize = self.MaxBrdSizeX * self.nodePixelSizeX
        self.MaxYPixelSize = self.MaxBrdSizeY * self.nodePixelSizeY
        self.SetupScrolling(self.nodePixelSizeX, self.nodePixelSizeY, self.MaxXPixelSize, self.MaxYPixelSize)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Point2Coords(self, sx, sy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts screen coordinates to map coordinates and canvas pixel offsets
        """
        px, py = self.CvtScreenToCanvas(sx, sy)
        cx = px // self.nodePixelSizeX
        cy = py // self.nodePixelSizeY
        return cx, cy, px, py

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Coords2Point(self, cx, cy):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ converts map coordinates to screen coordinates
        """
        return self.CvtCanvasToScreen(cx * self.nodePixelSizeX, cy * self.nodePixelSizeY)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtKeyToCoords(self, cx, cy, facing, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return game.CvtKeyToSquareCoords(cx, cy, facing, cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawCursor(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.CursorX is None:
            return

        ps = self.nodePixelSizeX
        if self.CursorOX > 0:
            px = self.CursorX * ps + ps/self.CursorOX
            py = self.CursorY * ps + ps/self.CursorOY
        else:
            px = self.CursorX * ps
            py = self.CursorY * ps

        dc.SetPen(wx.Pen(self.currentCursorColor, 2, wx.SOLID))
        sx, sy = self.CvtCanvasToScreen(px, py)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(sx+2, sy+2, ps-4, ps-4)
        dc.SetBrush(wx.NullBrush)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refreshNeeded(self, coord, now=True, extra=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sx, sy = self.Coords2Point(coord[0], coord[1])

        #print 'refresh:', coord[0], coord[1]

        width = height = self.nodePixelSizeX
        ## TODO[20091122_170802]: The +- 2 is due to "stacked" drawing. is it worth it?

        if extra is not None:
            ox, oy, wrap = extra

            if wrap:
                if coord[0] == self.MaxBrdSizeX-1:
                    self.refreshNeeded((0, coord[1]))
                    self.refreshNeeded((0, coord[1]+1))
                if coord[1] == self.MaxBrdSizeY-1:
                    self.refreshNeeded((coord[0], 0))
                    self.refreshNeeded((coord[0]+1, 0))

            if ox > 0: width *= 2
            if oy > 0: height *=2

        self.RefreshRect(wx.Rect(sx, sy, width, height))

        if now:
            self.Update()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getYExtra(self, cx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 0


