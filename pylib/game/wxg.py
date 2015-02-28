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

import pylib.config as config
from . import util as game
from . import engine as ge
from . import board as gb
from . import wxdisp as wxd

import pylib.debug as dbg

import sys
import thread
import threading

gNodePixelSize = 78

#
# Colors
#

_gColorDB = None
#-------------------------------------------------------------------------------
def getColor(colorName):
#-------------------------------------------------------------------------------
    """ returns a wx.Colour of the specified color
    """
    c = _gColorDB.Find(colorName)
    assert c.Ok()
    return c

#-------------------------------------------------------------------------------
def ErrMsg(parent, Msg):
#-------------------------------------------------------------------------------
    print >> sys.stderr, "ERROR MSG:", Msg
    wx.MessageDialog(parent, Msg, "BDGame Error", wx.ICON_ERROR).ShowModal()

#-------------------------------------------------------------------------------
class Cfg(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Cfg, self).__init__()
        self.DefaultMapSizePixels = (2000, 2000)
        self.MainWindowSize = (700, 450)
        self.MainWindowFlags = 0
        self.DefaultBkgdColor = (245, 245, 225)
        self.DefaultNodeColor = (240, 240, 140)
        self.DefaultDirectory = '.'


## should be overridden
gConfig = config.DummyConfigObject(Cfg())


#-------------------------------------------------------------------------------
class InfoWin(wx.html.HtmlWindow):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.html.HtmlWindow.__init__(self, parent)
        #self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnLinkClicked)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnLinkClicked(self, info):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = info.GetHref()
        print("InfoWin::OnLinkClicked", url)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetPage(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.html.HtmlWindow.SetPage(self, s)


#-------------------------------------------------------------------------------
class UnitInfoWin(wx.html.HtmlWindow):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, units):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.html.HtmlWindow.__init__(self, parent)
        self.units = units

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnLinkClicked(self, info):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = info.GetHref()
        #print "InfoWin::OnLinkClicked", url
        id, cmd = url.split(':')

        try:
            id = int(id)
        except:
            wx.html.HtmlWindow.OnLinkClicked(self, info)
            return

        s = self.units.getUnit(id).InfoCall(cmd)
        if s is not None:
            self.SetPage(s)


#-------------------------------------------------------------------------------
class MapDisplayFrame(wx.aui.AuiMDIChildFrame, mx.AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, board, owner, nodePixelSize, title="", style = 0, displayClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.aui.AuiMDIChildFrame.__init__(self, parent, -1, title, style = wx.DEFAULT_FRAME_STYLE | style)
        mx.AutoEventBind.__init__(self)

        self.parent = parent
        self.win = displayClass(self, board, owner, nodePixelSize)
        self.sb = parent.sb

        board.frame = self
        self.setSizer(self.win)
        self.SetFocus()
        wx.CallAfter(self.Layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setSizer(self, win):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(win, 1, wx.EXPAND)
        self.SetSizer(s)
        self.SetAutoLayout(True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def putChar(self, cc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.putChar(cc)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WriteInfo(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.WriteInfo(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        inf = file(FileName, "rU")
        self.win.Load(inf)
        inf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtClose(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert dbg.DbgPrint("MapDisplayFrame.OnEvtClose")
        self.parent.OnCloseChild(e, self)


#-------------------------------------------------------------------------------
class MainFrame(wx.aui.AuiMDIParentFrame, mx.AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, game, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.WS_EX_PROCESS_IDLE):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.aui.AuiMDIParentFrame.__init__(self, None, -1, title, pos, size, style)
        mx.AutoEventBind.__init__(self)

        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        self.cnt = 0
        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(4)
        self.sb.SetStatusWidths([-1, -1, -1, -1])
        self.dw = {}
        self.mainmap = None

        self.nodePixelSize = gNodePixelSize

        self.event = threading.Event()
        self.event.clear()

        self.game = game
        self.game.set(self.event, self)

        ## start a 1 minute timer
        self.timer = wx.Timer(self)
        self.timer.Start(60 * 1000)

        self.AdjustMenu()

        ## child windows
        self.windows = {}

        ## set up info window
        win = wx.Panel(self, size=(200,250))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(win, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.info_nb = mx.Notebook(win, -1, style = wx.NB_TOP)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.info_nb, 1, wx.EXPAND)
        win.SetSizer(sizer)

        self._mgr.AddPane(win, wx.aui.AuiPaneInfo().Name("Info").Caption("Info").Right().MaximizeButton(True))

        self.info = UnitInfoWin(self.info_nb, ge.gObjects)
        self.info_nb.AddPage(self.info, "Unit")

        self.turn_info = InfoWin(self.info_nb)
        self.info_nb.AddPage(self.turn_info, "Turn")

        self.game_info = InfoWin(self.info_nb)
        self.info_nb.AddPage(self.game_info, "Game")

        self._mgr.Update()
        wx.CallAfter(self.Layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WriteInfo(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.info.SetPage(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AdjustMenu(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fmenu = mx.Menu(self)
        fmenu.AddItem("New",    self.OnNewGame,  "Play a New Game")
        fmenu.AddItem("Open",   self.OnOpen, "Open an Existing Game")
        fmenu.AddItem("Save",   self.OnSave, "Save the Current Game")
        fmenu.AddItem("SaveAs", self.OnSaveAs, "Save the Current Game")
        fmenu.AddItem("Close",  self.OnCloseChild,  "Close the Current Game")
        fmenu.AddItem("Exit",   self.OnEvtClose)

        hmenu = mx.Menu(self)
        hmenu.AddItem("Help", self.OnAbout)
        hmenu.AddItem("About", self.OnAbout)

        menuBar = wx.MenuBar()
        menuBar.Append(fmenu, "&File")
        menuBar.Append(hmenu, "&Help")
        self.SetMenuBar(menuBar)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def putChar(self, char):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print "PutChar: '%s'" % char
        if char == 'F2':
            #print "Here"
            if self.event.isSet():
                print("Set")
                self.event.clear()
                self.sb.SetStatusText("Paused", 3)
            else:
                print("Clear")
                self.event.set()
                self.sb.SetStatusText("Run", 3)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSashDrag(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if e.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        self.infowin.SetDefaultSize((e.GetDragRect().width, 1000))
        wx.LayoutAlgorithm().LayoutMDIFrame(self)
        self.GetClientWindow().Refresh()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def O1nEvtSize(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.LayoutAlgorithm().LayoutMDIFrame(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnNewGame(self, e, fn = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fn is None:
            fd = wx.FileDialog(self, "Open Scenario", gConfig.DefaultDirectory, "", "*.scen", wx.OPEN | wx.FILE_MUST_EXIST)
            if fd.ShowModal() == wx.ID_OK:
                fn = fd.GetFilename()
            else:
                return

        if not self.game.newGame(fn):
            return

        ## create main display frame for main board
        self.mainmap = self.CreateMapDisplay(self.game.mainBoard, "Main Map")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DisplayBoard(self, brd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ selects the specified board 'brd' if already created
        """
        if brd.display and brd in self.windows:
            nb = self.GetNotebook()
            idx = nb.GetPageIndex(brd.frame)

            if idx != wx.NOT_FOUND:
                nb.SetSelection(idx)
                return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateMapDisplay(self, brd, title, displayOwner):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called to create a display of the board 'brd'
        """
        if self.DisplayBoard(brd):
            return

        if isinstance(brd, gb.BoardOfHexes):
            if brd.iso:
                displayClass = wxd.MapDisplayIsoHex
            else:
                displayClass = wxd.MapDisplayHex
        elif isinstance(brd, gb.BoardOfSquares):
            displayClass = wxd.MapDisplaySquare
        else:
            raise Exception('Unknown board type')

        c = self.windows[brd] = MapDisplayFrame(self, brd, displayOwner, self.nodePixelSize, title, displayClass=displayClass)
        return c

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnOpen(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #fd = wx.FileDialog(self, "Open Map", "", "", "*.mmp", wx.OPEN | wx.FILE_MUST_EXIST)
        #if fd.ShowModal() == wx.ID_OK:
        #    self.OpenMap(fd.GetFilename())
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnCloseChild(self, e, Sender = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Sender or self.GetActiveChild()
        if c != self.mainmap:
            c.win.brd.disp = None
            del self.windows[c.win.brd]
            c.Destroy()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSave(self, e, Child = None, AskPerm = False, Auto = False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Child or self.GetActiveChild()
        if c is None:
            return

        if self.dw[c] == "":
            self.OnSaveAs(e, c)
        else:
            if c.Save(self.dw[c], AskPerm = AskPerm, Auto = Auto):
                self.sb.SetStatusText("Saved: " + self.dw[c])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSaveAs(self, e, Child = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Child or self.GetActiveChild()
        fd = wx.FileDialog(self, "Save Map", "", "", "*.mmp", wx.SAVE | wx.OVERWRITE_PROMPT)

        if fd.ShowModal() == wx.ID_OK:
            sf = self.dw[c] = fd.GetFilename()
            c.SetTitle(sf)
            if c.Save(sf, Force = True):
                self.sb.SetStatusText("Saved: " + sf)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnAbout(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert dbg.DbgPrint("MainFrame.OnAbout")
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def O1nEvtTimer(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert dbg.DbgPrint("MainFrame.OnEvtTimer")
        for c, fn in self.dw.items():
            if fn != "":
                c.Save(fn, AskPerm = False, Auto = True)

    O1nEvtTimer.EVT_ID = -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtClose(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert dbg.DbgPrint("MainFrame.OnEvtClose")

        ## save config
        gConfig.MainWindowSize = self.GetSizeTuple()
        gConfig.MainWindowFlags = config.GetFlags(self)
        gConfig.Save()

        self.Destroy()
        self.game.Quit()

        assert dbg.DbgPrint("MainFrame.OnEvtClose --end")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OpenMap(self, FileName, style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = MapDisplayFrame(self, FileName, style)
        self.dw[c] = FileName
        try:
            c.Load(FileName)
            self.sb.SetStatusText("Loaded: " + FileName)

        except IOError:
            ErrMsg(self, "Can't open file: " + FileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def StartGame(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def _runThread(*a):
            self.game.run()
        thread.start_new_thread(_runThread, (None,))
        _gApp.MainLoop()


#-------------------------------------------------------------------------------
class GObjectBMPMixIn(object):
#-------------------------------------------------------------------------------
    """ This mixin handles additional methods for managing GOjects that require
        bitmaps
    """

    simpleMap = {0:0, 1:4, 2:2, 3:6, 4:4, 6:6, 7:4, 8:8, 9:6}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, bitmapName=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.bmpName = bitmapName

        if bitmapName is not None:
            self.loadBitmaps()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadBitmaps(self, bitmaps = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ load bitmaps for this gobj
        """
        self.bml = game.LoadBitmaps(self.bmpName if bitmaps is None else bitmaps)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def draw(self, dc, facing, px, py, nodeSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ draws a bmp onto the display 'dc' at the pixel coordinates (px, py)
            of 'nodeSize' with the specified 'facing' which due to display
            transformations may be different than a tunits notion of facing.
        """
        ## allows a bmp per facing, or simplified based on simpleMap conversion
        bmp = self.bml[facing] if self.bml[facing] is not None else self.bml[self.simpleMap[facing]]
        dc.DrawBitmap(bmp, px, py+1, True)


#-------------------------------------------------------------------------------
class GObjectBMPCountersMixIn(GObjectBMPMixIn):
#-------------------------------------------------------------------------------
    """ This mixin handles additional methods for managing GOjects that require
        bitmaps. Put's rounded rectangle around gobjs like board game counters
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def draw(self, dc, facing, px, py, nodeSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        b = wx.Brush(self.color)
        dc.SetBrush(b)

        dc.DrawRoundedRectangle(px+1, py+2, nodeSize-1, nodeSize-2, 5)

        ## allows a bmp per facing, or simplified based on simpleMap conversion
        bmp = self.bml[facing] if self.bml[facing] is not None else self.bml[self.simpleMap[facing]]
        dc.DrawBitmap(bmp, px, py+1, True)


#-------------------------------------------------------------------------------
class GTerrainBMPHexMixIn(object):
#-------------------------------------------------------------------------------
    """ This mixin handles drawing for simple terrain objects on a Hex map
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, brush):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.brush = brush

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def draw(self, dc, px, py, nodeSize, a, pen=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #tp = wx.BLACK_DASHED_PEN if pen else wx.TRANSPARENT_PEN
        tp = wx.BLACK_PEN if pen else wx.TRANSPARENT_PEN
        game.DrawFilledHex(dc, px, py, nodeSize, a, self.brush, tp)


_gMain = None
_gApp = None

#-------------------------------------------------------------------------------
def InitializeDisplay(title, game):
#-------------------------------------------------------------------------------
    global _gApp, _gMain, _gColorDB

    _gApp = wx.PySimpleApp()
    _gMain = MainFrame(title, game)

    _gColorDB = wx.ColourDatabase()

    _gApp.SetTopWindow(_gMain)
    _gMain.Show(True)

    return _gMain



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
    import time

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    InitializeDisplay()

    while 1:
        time.sleep(1)
        print('here')

    res = not __test__()
    oss.exit(res)

