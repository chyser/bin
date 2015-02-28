import sys

import wx
import mx

_BIG_FLOAT = float(sys.maxint)
_NBIG_FLOAT = -1 * _BIG_FLOAT

#-------------------------------------------------------------------------------
class GraphControl(mx.Panel):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphControl, self).__init__(parent, -1, style = wx.WANTS_CHARS | wx.SUNKEN_BORDER)
        self.__gp = GraphPanel(self, id)
        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(self.__gp, 1, wx.TOP | wx.LEFT | wx.RIGHT | wx.GROW)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self.__gp, attr)


#-------------------------------------------------------------------------------
class GraphControlFixed(mx.Panel):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphControlFixed, self).__init__(parent, -1, style = wx.WANTS_CHARS | wx.SUNKEN_BORDER)
        self.__gp = GraphPanelFixed(self, id)
        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(self.__gp, 1, wx.TOP | wx.LEFT | wx.RIGHT | wx.GROW)
        self.SetSizer(mainBox)
        self.SetAutoLayout(True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self.__gp, attr)


#-------------------------------------------------------------------------------
class GraphPanelBase(mx.Panel):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphPanelBase, self).__init__(parent, id, style = wx.WANTS_CHARS)

        self.id = id

        self.yscale = self.xscale = 1.0
        self.yoffset = self.xoffset = 0

        self.SetBackgroundColour(wx.WHITE)
        self.w, self.h = self.GetClientSizeTuple()
        self.Reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.graphs = [];  self.hlines = [];  self.vlines = []
        self.miny = self.minx = _BIG_FLOAT
        self.maxy = self.maxx = _NBIG_FLOAT

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _AdjScale(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.maxy == self.miny or self.maxx == self.minx:
            self.yscale = self.xscale = 1.0
        else:
            self.yscale = float(self.h) / (self.maxy - self.miny)
            self.xscale = float(self.w) / (self.maxx - self.minx)

        self.yoffset = -1.0 * self.miny * self.yscale
        self.xoffset = -1.0 * self.minx * self.xscale

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def RemoveData(self, Lbl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for g in self.graphs:
            if g[4] == Lbl:
                self.graphs.remove(g)
                return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def RemoveLine(self, Lbl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for l in self.vlines:
            if l[4] == Lbl:
                self.vlines.remove(l)

        for l in self.hlines:
            if l[4] == Lbl:
                self.hlines.remove(l)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def VertLine(self, X, Clr, PS=1, Style = wx.SOLID, Lbl=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.vlines.append((X, Clr, Style, PS, Lbl))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def HorzLine(self, Y, Clr, PS=1, Style = wx.SOLID, Lbl=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.hlines.append((Y, Clr, Style, PS, Lbl))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtSize(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.w, self.h = self.GetClientSizeTuple()
        self.SetDimensions(0, 0, self.w, self.h)
        self._AdjScale()
        self.Refresh()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtY(self, Y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.h - int((Y * self.yscale) + self.yoffset)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtX(self, X):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return int((X * self.xscale) + self.xoffset)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtPaint(self, evt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ draw the graph on paint event
              - draw all registered vertical lines
              - draw all registered data sets (a list of (x,y) tuples)
              - draw all registered horizontal lines
        """

        dc = wx.PaintDC(self)
        dc.BeginDrawing()

        mny = self.CvtY(self.miny)
        mxy = self.CvtY(self.maxy)
        mnx = self.CvtX(self.minx)
        mxx = self.CvtX(self.maxx)

        for g in self.vlines:
            X, clr, s, ps, lbl = g
            dc.SetPen(wx.Pen(clr, ps, style = s))
            x = self.CvtX(X)
            dc.DrawLine(x, mny, x, mxy)

        for g in self.graphs:
            data, clr, s, ps, lbl = g

            #print lbl, data
            if not data: continue

            dc.SetPen(wx.Pen(clr, ps, style = s))

            px0, py0 = data[0]
            px0 = self.CvtX(px0)
            py0 = self.CvtY(py0)

            if ps == 1: dc.DrawCircle(px0+1, py0, 2)

            ## walk data list in order pulling out (x,y) tuples
            for d in data:
                px, py = d
                px = self.CvtX(px)
                py = self.CvtY(py)

                dc.DrawLine(px0, py0, px, py)
                if ps == 1: dc.DrawCircle(px+1, py, 2)
                px0, py0 = px, py

        for g in self.hlines:
            Y, clr, s, ps, lbl = g
            dc.SetPen(wx.Pen(clr, ps, style = s))
            y = self.CvtY(Y)
            dc.DrawLine(mnx, y, mxx, y)

        dc.EndDrawing()


#-------------------------------------------------------------------------------
class GraphPanel(GraphPanelBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphPanel, self).__init__(parent, id)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetupData(self, data, Clr, PS = 1, Style = wx.SOLID, Lbl=None, MaxY = _BIG_FLOAT, MinY = _NBIG_FLOAT, MaxX = _BIG_FLOAT, MinX = _NBIG_FLOAT):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if Lbl is None:
            Lbl = id(data)
        self.graphs.append((data, Clr, Style, PS, Lbl))

        ## adjust mins and maxs to reflect data
        for d in data:
            if not d: continue

            x, y = d
            if y < self.miny: self.miny = y
            if y > self.maxy: self.maxy = y
            if x < self.minx: self.minx = x
            if x > self.maxx: self.maxx = x

        ## cap data
        if self.maxy > MaxY: self.maxy = MaxY
        if self.miny < MinY: self.miny = MinY
        if self.maxx > MaxX: self.maxx = MaxX
        if self.minx < MinX: self.minx = MinX

        self._AdjScale()
        return Lbl

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def VertLine(self, X, Clr, PS=1, Style = wx.SOLID, Lbl=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphPanel, self).VertLine(X, Clr, PS, Style, Lbl)
        if X < self.minx:   self.minx = X
        elif X > self.maxx: self.maxx = X
        else: return
        self._AdjScale()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def HorzLine(self, Y, Clr, PS=1, Style = wx.SOLID, Lbl=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphPanel, self).HorzLine(Y, Clr, PS, Style, Lbl)
        if Y < self.miny:   self.miny = Y
        elif Y > self.maxy: self.maxy = Y
        else: return
        self._AdjScale()


#-------------------------------------------------------------------------------
class GraphPanelFixed(GraphPanelBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(GraphPanelFixed, self).__init__(parent, id)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetDim(self, MinX, MinY, MaxX, MaxY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.miny = MinY;  self.maxy = MaxY
        self.minx = MinX;  self.maxx = MaxX
        self._AdjScale()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetXDim(self, MinX, MaxX):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.minx = MinX;  self.maxx = MaxX
        self._AdjScale()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetupData(self, data, Clr, PS = 1, Style = wx.SOLID, Lbl=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ register the data list with the control
               - note once list registered, can just change values in list, don't
                 need to reregister
        """

        if Lbl is None:
            Lbl = id(data)
        self.graphs.append((data, Clr, Style, PS, Lbl))
        return Lbl

