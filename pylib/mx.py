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
import wx.wizard
import time
import wx.xrc as xrc


import pylib.osscripts as oss
import pylib.debug as dbg


#-------------------------------------------------------------------------------
def chgFontChildren(win, font):
#-------------------------------------------------------------------------------
    try:
        win.SetFont(font)
    except:
        pass
    for child in win.GetChildren():
        chgFontChildren(child, font)


#-------------------------------------------------------------------------------
def MsgBox(parent, caption, message, style = wx.OK | wx.CANCEL, font=None):
#-------------------------------------------------------------------------------
    mb = wx.MessageDialog(parent, str(message), caption, style)
    if font is not None:
        mb.SetFont(font)
        chgFontChildren(mb, font)
    return mb.ShowModal()


#-------------------------------------------------------------------------------
def ErrBox(message, caption="Error", parent=None, modal=True):
#-------------------------------------------------------------------------------
    if modal:
        return wx.MessageDialog(parent, str(message), caption, wx.ICON_ERROR).ShowModal()
    return wx.MessageDialog(parent, str(message), caption, wx.ICON_ERROR).Show()


#-------------------------------------------------------------------------------
def TxtBox(parent, title, msg, defval="", style=0):
#-------------------------------------------------------------------------------
    te = wx.TextEntryDialog(parent, msg, title, defval, style | wx.OK | wx.CANCEL)
    res = te.ShowModal()
    if res == wx.ID_OK:
        return te.GetValue()


#-------------------------------------------------------------------------------
def getFont(size, family, facename='', style=wx.NORMAL, weight=wx.NORMAL, underline=False):
#-------------------------------------------------------------------------------
    fnt = wx.Font(size, family, style, weight, underline, facename)
    assert fnt.IsOk()
    print('fnt:', fnt.IsOk())
    print('family:', fnt.GetFamily())
    print('fn:', fnt.GetFaceName())
    return fnt


#-------------------------------------------------------------------------------
class SimpleInit(wx.PySimpleApp):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def MainLoop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 0


#-------------------------------------------------------------------------------
class XRCResource(object):
#-------------------------------------------------------------------------------
    xr = None
    nmdx = 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.xr = xrc.EmptyXmlResource()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self.xr, attr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadFromFile(self, fileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.xr.Load(fileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadFromStr(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.FileSystem.AddHandler(wx.MemoryFSHandler())
        nm = 'XRCResource_' + str(self.nmdx + time.time())
        XRCResource.nmdx += 1
        wx.MemoryFSHandler.AddFile('XRC/app/' + nm, s)
        self.xr.Load('memory:XRC/app/' + nm)
        ###wx.MemoryFSHandler.RemoveFile('memory:XRC/app/' + nm)


#-------------------------------------------------------------------------------
class XRCMixin(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if attr not in self.__dict__:
            return xrc.XRCCTRL(self, attr)


#-------------------------------------------------------------------------------
class ADC(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, cntl, attr = None, func = None, proportion = 0, flag = wx.ALL, border = 5):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ADC, self).__init__()
        self.cntl = cntl
        if attr is None:
            self.attr = id(cntl)
        else:
            self.attr = attr
        self.func = func
        self.proportion = proportion
        self.flag = flag
        self.border = border


#-------------------------------------------------------------------------------
class ADL(list):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ADL, self).__init__()


#-------------------------------------------------------------------------------
class ADlg(object):
#-------------------------------------------------------------------------------
    class ADlgException(Exception): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title, Size, pos = wx.DefaultPosition, style = wx.DEFAULT_DIALOG_STYLE):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__dict__["win"] = wx.Dialog(parent, -1, title, pos, size = Size, style = style)
        self.__dict__["cntl"] = {}
        self.__dict__["cnvt"] = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, Attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            val = self.cntl[Attr].GetValue()
        except AttributeError:
            val = self.cntl[Attr].GetStringSelection()
        except AttributeError:
            val = self.cntl[Attr].GetSelections()
        except AttributeError:
            val = self.cntl[Attr].GetSelection()

        if Attr in self.cnvt:
            try:
                val = self.cnvt[Attr](*(val,))
            except:
                raise ADlg.ADlgException("Conversion Failure:" + val + ':' + str(self.cnvt[Attr]))

        return self.ChkVal(Attr, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setattr__(self, Attr, Val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__dict__["cntl"][Attr].SetValue(str(Val))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ChkVal(self, Attr, Val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return Val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddCtrl(self, Attr, Cntl, Func = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[Attr] = Cntl
        if Func is not None:
            self.cnvt[Attr] = Func

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddButton(self, Attr, Text, Pos, id = -1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[Attr] = wx.Button(self.win, id, Text, Pos)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addOk(self, pos, text='Ok'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[ID().ID()] = wx.Button(self.win, wx.ID_OK, text, pos)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCancel(self, pos, text='Cancel'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[ID().ID()] = wx.Button(self.win, wx.ID_CANCEL, text, pos)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddTextCtrl(self, Attr, Pos, Text = "", Size = wx.DefaultSize, Style = wx.TE_LEFT, id = -1, Func = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[Attr] = wx.TextCtrl(self.win, id, Text, Pos, Size, Style)
        if Func is not None:
            self.cnvt[Attr] = Func
        return self.cntl[Attr]

    addTC = AddTextCtrl

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addText(self, text, pos):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.StaticText(self.win, -1, text, pos)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def notOrientation(self, O):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if O == wx.HORIZONTAL:
            return wx.VERTICAL
        return wx.HORIZONTAL

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addSizers(self, List, Orientation):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sz = wx.BoxSizer(Orientation)
        for item in List:
            if isinstance(item, list):
                s = self.addSizers(item, self.notOrientation(Orientation))
                sz.Add(s, 0)
            else:
                sz.Add(item.cntl, item.proportion, item.flag, item.border)
                self.cntl[item.attr] = item.cntl

                if item.func is not None:
                    self.cnvt[item.attr] = item.func

        return sz

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddControlLists(self, HList):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sz = self.addSizers(HList, wx.HORIZONTAL)
        self.win.SetSizer(sz)
        sz.SetSizeHints(self.win)

    AddListH = AddControlLists

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddListV(self, VList):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sz = self.addSizers(VList, wx.VERTICAL)
        self.win.SetSizer(sz)
        sz.SetSizeHints(self.win)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.win.ShowModal() == wx.ID_OK

    run = Run


#-------------------------------------------------------------------------------
class Dlg(object):
#-------------------------------------------------------------------------------
    class DlgException(Exception): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__dict__["win"] = wx.Dialog(parent, -1, title, pos, style=style)
        self.__dict__["cntl"] = {}
        self.__dict__["cnvt"] = {}
        self.__dict__['prop'] = {}
        self.__dict__['rows'] = []
        self.__dict__['rowLen'] = 0
        self.__dict__['sid'] = 100

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            val = self.cntl[attr].GetValue()
        except AttributeError:
            val = self.cntl[attr].GetStringSelection()
        except AttributeError:
            val = self.cntl[attr].GetSelections()
        except AttributeError:
            val = self.cntl[attr].GetSelection()

        if self.cnvt[attr] is not None:
            try:
                val = self.cnvt[attr](*(val,))
            except:
                raise self.DlgException("Conversion Failure:" + val + ':' + str(self.cnvt[attr]))

        return self.chkVal(attr, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def chkVal(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setattr__(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__dict__["cntl"][attr].SetValue(str(val))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _addRow(self, row, cntl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if row >= self.rowLen:
            for i in range(self.rowLen, row + 1):
                self.rows.append([])
            self.__dict__['rowLen'] = row + 1

        self.rows[row].append(cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCtrl(self, row, attr, cntl, func=None, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[attr] = cntl
        self.cnvt[attr] = func
        self.prop[cntl] = kwds
        self._addRow(row, cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addButton(self, row, attr, text, id=-1, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[attr] = cntl = wx.Button(self.win, id, text)
        self.prop[cntl] = kwds
        self._addRow(row, cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addOk(self, row, text='Ok', **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[ID().ID()] = cntl = wx.Button(self.win, wx.ID_OK, text)
        self.prop[cntl] = kwds
        self._addRow(row, cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addSpacer(self, row, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sid = self.sid
        self.__dict__['sid'] += 1
        self.prop[sid] = kwds
        self._addRow(row, sid)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCancel(self, row, text='Cancel', **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[ID().ID()] = cntl = wx.Button(self.win, wx.ID_CANCEL, text)
        self.prop[cntl] = kwds
        self._addRow(row, cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addTC(self, row, attr, text="", style=wx.TE_LEFT, size=wx.DefaultSize, id=-1, func=None, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[attr] = cntl = wx.TextCtrl(self.win, id, text, size=size, style=style)
        self.cnvt[attr] = func
        self.prop[cntl] = kwds
        self._addRow(row, cntl)
        return self.cntl[attr]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addText(self, row, text, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cntl = wx.StaticText(self.win, -1, text)
        self.prop[cntl] = kwds
        self._addRow(row, cntl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        szv = wx.BoxSizer(wx.VERTICAL)
        self.win.SetSizer(szv)
        szv.SetSizeHints(self.win)

        for row in self.rows:
            ln = len(row)
            if ln == 0:
                szv.AddStretchSpacer()
            elif ln == 1:
                proportion = self.prop[row[0]].get('prop', 1)
                flag = self.prop[row[0]].get('flag', wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
                border = self.prop[row[0]].get('brdr', 2)
                if isinstance(row[0], int):
                    szv.AddStretchSpacer(proportion)
                else:
                    szv.Add(row[0], proportion, flag, border)
            else:
                szh = wx.BoxSizer(wx.HORIZONTAL)
                for cntl in row:
                    if cntl is not None:
                        proportion = self.prop[cntl].get('prop', 1)
                        flag = self.prop[cntl].get('flag', wx.EXPAND | wx.ALIGN_CENTER | wx.ALL)
                        border = self.prop[cntl].get('brdr', 2)
                        if isinstance(cntl, int):
                            szh.AddStretchSpacer(proportion)
                        else:
                            szh.Add(cntl, proportion, flag, border)
                    else:
                        szh.AddStretchSpacer()
                szv.Add(szh, 0)
        szv.Fit(self.win)

        print('here')
        return self.win.ShowModal() == wx.ID_OK


#-------------------------------------------------------------------------------
class Dlg1(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title, mvsLabel=None, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__dict__["win"] = wx.Dialog(parent, -1, title, pos, style=style)

        if mvsLabel is None:
            self.mvs = wx.BoxSizer(wx.VERTICAL)
        else:
            self.mvs = wx.StaticBoxSizer(wx.VERTICAL, self.win, mvsLabel)

        self.win.SetSizer(self.mvs)
        self.mvs.SetSizeHints(self.win)
        self.nextRow()

        self.cntl = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            val = self.cntl[attr].GetValue()
        except AttributeError:
            val = self.cntl[attr].GetStringSelection()
        except AttributeError:
            val = self.cntl[attr].GetSelections()
        except AttributeError:
            val = self.cntl[attr].GetSelection()
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextRow(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.curSizer = wx.BoxSize(wx.HORIZONTAL)
        self.mvs.Add(self.curSizer, 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, attr, cntl, prop=1, flags=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[attr] = cntl
        self.curSizer.Add(cntl, prop, flags, border)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addSpacer(self, prop):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.curSizer.AddStretchSpacer(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, success=wx.ID_OK):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mvs.Fit(self.win)
        return self.win.ShowModal() == success


#-------------------------------------------------------------------------------
class ID(object):
#-------------------------------------------------------------------------------
    gid = 5000

    def __init__(self):
        object.__init__(self)
        self.id = ID.gid
        ID.gid += 1

    def ID(self):
        return self.id

    def __int__(self):
        return self.id


#-------------------------------------------------------------------------------
def PasswdBox(parent, msg, title, defval="", style=0):
#-------------------------------------------------------------------------------
    return TxtBox(parent, msg, title, defval, wx.TE_PASSWORD)


#-------------------------------------------------------------------------------
class Menu(wx.Menu):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title='', style=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Menu.__init__(self, title, style)
        self.parent = parent
        self.children = {}
        self.ids = {}
        self.isReset = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddItem(self, Text, Func=None, HelpText=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if Text.endswith('---'):
            return self.AppendSeparator()

        id = ID().id
        self.Append(id, Text, HelpText)
        if Func is not None:
            self.children[Func] = id
            self.ids[id] = Text
            wx.EVT_MENU(self.parent, id, Func)
        return id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def InsertItem(self, pos, Text, Func=None, HelpText=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if Text.endswith('---'):
            return self.InsertSeparator(pos)

        id = ID().id
        self.Insert(pos, id, Text, HelpText)
        if Func is not None:
            self.children[Func] = id
            self.ids[id] = Text
            wx.EVT_MENU(self.parent, id, Func)
        return id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddSubMenu(self, Text, subMenu, HelpText=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        id = ID().id
        self.AppendMenu(id, Text, subMenu, HelpText)
        return id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddCheckItem(self, Text, Func=None, HelpText=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        id = ID().id
        self.AppendCheckItem(id, Text, HelpText)
        if Func is not None:
            self.children[Func] = id
            self.ids[id] = Text
            wx.EVT_MENU(self.parent, id, Func)
        return id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def RmItem(self, Func):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.DestroyId(self.children[Func])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for item in self.GetMenuItems():
            self.DestroyItem(item)
        self.isReset= True


#-------------------------------------------------------------------------------
class AutoEventBind(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class AutoEventBindException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ###super(AutoEventBind, self).__init__()
        self.AutoBind()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AutoBind(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ automatically make wx.EVT_* calls for methods named OnEvt*
        """

        for i in dir(self):
            if i.startswith("OnEvt"):
                nm = self.CvtName(i[2:])
                assert dbg.DbgPrint(3, "Binding:", i)
                func = getattr(self, i)
                evt_id = getattr(func, "EVT_ID", None)

                try:
                    if evt_id is None:
                        wx.__dict__[nm](self, func)
                    else:
                        wx.__dict__[nm](self, evt_id, func)
                except Exception, ex:
                    raise AutoEventBind.AutoEventBindException("OnEvt Exception: " + nm + " : " + i + ", " + str(evt_id) + "\n"+ str(ex))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtName(self, Name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for i, c in enumerate(Name):
            if c == '_': break
            if i > 0 and c.isupper() and not Name[i-1].isupper():
                s.append('_' + c)
            else:
                s.append(c.upper())
        return "".join(s)


#-------------------------------------------------------------------------------
class MDIParentFrame(wx.MDIParentFrame, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.MDIParentFrame.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)


#-------------------------------------------------------------------------------
class MDIChildFrame(wx.MDIChildFrame, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.MDIChildFrame.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)


#-------------------------------------------------------------------------------
class Frame(wx.Frame, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Frame.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)


#-------------------------------------------------------------------------------
class Panel(wx.Panel, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Panel.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)


import wx.lib.scrolledpanel as scrolled
#-------------------------------------------------------------------------------
class ScrolledPanel(scrolled.ScrolledPanel, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        scrolled.ScrolledPanel.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)


#-------------------------------------------------------------------------------
class Dialog(wx.Dialog, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Dialog.__init__(self, parent, *args, **kwargs)
        if parent is not None:
            dn = wx.Display.GetFromWindow(parent)
            disp = wx.Display(dn)
            rect = disp.GetClientArea()
            print(rect)
        print('mx.Dialog')

        AutoEventBind.__init__(self)


#-------------------------------------------------------------------------------
class Wizard(wx.wizard.Wizard, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.wizard.Wizard.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)

PreWizard = wx.wizard.PreWizard

## TODO[20091123_110600]: This can be removed if I'm happy with the replacement
#-------------------------------------------------------------------------------
class ScrolledCanvasOrig(wx.ScrolledWindow, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.ScrolledWindow.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)
        self.MaxX = self.MaxY = 0
        self.clientW = self.clientH = self.startX = self.startY = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetViewStart(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xx, yy = wx.ScrolledWindow.GetViewStart(self)
        sx = self.startX if self.startX else xx
        sy = self.startY if self.startY else yy
        return sx, sy

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtScreenToCanvas(self, SX, SY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return screen X and Y as canvas X and Y
        """
        xView, yView = wx.ScrolledWindow.GetViewStart(self)
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return SX + (xView * xDelta) - self.startX, SY + (yView * yDelta) - self.startY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtCanvasToScreen(self, CX, CY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return canvas X and Y as screen X and Y
        """
        xView, yView = wx.ScrolledWindow.GetViewStart(self)
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return CX - (xView * xDelta) + self.startX, CY - (yView * yDelta) + self.startY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetupScrolling(self, IncX, IncY, MaxX, MaxY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.SetScrollbars(IncX, IncY, MaxX/IncX, MaxY/IncY)
        self.MaxX = MaxX; self.MaxY = MaxY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBorders(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dc.SetBrush(wx.GREY_BRUSH)
        dc.SetPen(wx.GREY_PEN)
        dc.DrawRectangle(0, 0, self.startX, self.clientH)
        dc.DrawRectangle(self.startX, 0, self.startX + self.MaxX, self.startY)
        dc.DrawRectangle(self.startX, self.startY + self.MaxY, self.clientW, self.clientH)
        dc.DrawRectangle(self.startX + self.MaxX, 0, self.clientW, self.clientH)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtSize(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.clientW, self.clientH = self.GetClientSizeTuple()
        self.startX = (self.clientW - self.MaxX) / 2 if self.MaxX < self.clientW else 0
        self.startY = (self.clientH - self.MaxY) / 2 if self.MaxY < self.clientH else 0


#-------------------------------------------------------------------------------
class ScrolledCanvas(wx.ScrolledWindow, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwargs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.ScrolledWindow.__init__(self, *args, **kwargs)
        AutoEventBind.__init__(self)

###    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
###    def CvtScreenToCanvas(self, SX, SY):
###    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
###        """ return screen X and Y as canvas X and Y
###        """
###        return self.CalcUnscrolledPosition(SX, SY)

    CvtScreenToCanvas = wx.ScrolledWindow.CalcUnscrolledPosition

###    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
###    def CvtCanvasToScreen(self, CX, CY):
###    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
###        """ return canvas X and Y as screen X and Y
###        """
###        return self.CalcScrolledPosition(CX, CY)

    CvtCanvasToScreen = wx.ScrolledWindow.CalcScrolledPosition

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetupScrolling(self, IncX, IncY, MaxX, MaxY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.SetVirtualSize((MaxX, MaxY))
        self.SetScrollRate(IncX, IncY)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBorders(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return
        dc.SetBrush(wx.GREY_BRUSH)
        dc.SetPen(wx.GREY_PEN)
        dc.DrawRectangle(0, 0, self.startX, self.clientH)
        dc.DrawRectangle(self.startX, 0, self.startX + self.MaxX, self.startY)
        dc.DrawRectangle(self.startX, self.startY + self.MaxY, self.clientW, self.clientH)
        dc.DrawRectangle(self.startX + self.MaxX, 0, self.clientW, self.clientH)


#-------------------------------------------------------------------------------
class DisplayCanvas(ScrolledCanvas):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, width, height):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ScrolledCanvas.__init__(self, parent, id = -1, style = wx.WANTS_CHARS | wx.CLIP_CHILDREN)
        self.__buff = wx.EmptyBitmap(width, height)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.ModifyBuffer()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtEraseBackground(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtPaint(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.BufferedPaintDC(self, self.__buff, wx.BUFFER_VIRTUAL_AREA)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Draw(self, dc, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ModifyBuffer(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cdc = wx.ClientDC(self)
        self.DoPrepareDC(cdc)
        dc = wx.BufferedDC(cdc, self.__buff, wx.BUFFER_VIRTUAL_AREA)
        dc.BeginDrawing()
        self.Draw(*((dc,) + args))
        dc.EndDrawing()


#-------------------------------------------------------------------------------
class ScrolledWindow(wx.Window, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Window.__init__(self)
        AutoEventBind.__init__(self)
        self.MaxX = self.MaxY = 0
        self.clientW = self.clientH = self.startX = self.startY = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetViewStart(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xx, yy = wx.ScrolledWindow.GetViewStart(self)
        sx = self.startX if self.startX else xx
        sy = self.startY if self.startY else yy
        return sx, sy

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtScreenToCanvas(self, SX, SY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return screen X and Y as canvas X and Y
        """
        xView, yView = wx.ScrolledWindow.GetViewStart(self)
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return SX + (xView * xDelta) - self.startX, SY + (yView * yDelta) - self.startY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvtCanvasToScreen(self, CX, CY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return canvas X and Y as screen X and Y
        """
        xView, yView = wx.ScrolledWindow.GetViewStart(self)
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return CX - (xView * xDelta) + self.startX, CY - (yView * yDelta) + self.startY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetupScrolling(self, IncX, IncY, MaxX, MaxY):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.SetScrollbars(IncX, IncY, MaxX/IncX, MaxY/IncY)
        self.MaxX = MaxX; self.MaxY = MaxY

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DrawBorders(self, dc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dc.SetBrush(wx.GREY_BRUSH)
        dc.SetPen(wx.GREY_PEN)
        dc.DrawRectangle(0, 0, self.startX, self.clientH)
        dc.DrawRectangle(self.startX, 0, self.startX + self.MaxX, self.startY)
        dc.DrawRectangle(self.startX, self.startY + self.MaxY, self.clientW, self.clientH)
        dc.DrawRectangle(self.startX + self.MaxX, 0, self.clientW, self.clientH)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtSize(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.clientW, self.clientH = self.GetClientSizeTuple()
        self.startX = (self.clientW - self.MaxX) / 2 if self.MaxX < self.clientW else 0
        self.startY = (self.clientH - self.MaxY) / 2 if self.MaxY < self.clientH else 0


#-------------------------------------------------------------------------------
def RegionIterator(rgn):
#-------------------------------------------------------------------------------
    ri = wx.RegionIterator(rgn)
    while ri.HaveRects():
        rct = ri.GetRect()
        ri.Next()
        yield rct


#-------------------------------------------------------------------------------
def RegionIterator1(rgn):
#-------------------------------------------------------------------------------
    lst = []
    ri = wx.RegionIterator(rgn)
    while ri.HaveRects():
        lst.append(ri.GetRect())
        ri.Next()

    lst.sort(key=lambda rct: (rct.x, rct.y), reverse=True)
    return lst


#-------------------------------------------------------------------------------
class Notebook(wx.Notebook):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Notebook, self).__init__(*args, **kw)
        self.d = {}
        self.idx = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddPage(self, page, text, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.Notebook.AddPage(self, page, text, *args)
        self.d[page] = self.idx
        self.idx += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetPageIndex(self, page):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return self.d[page]
        except KeyError:
            return wx.NOT_FOUND

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def HidePage(self, page):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass


#-------------------------------------------------------------------------------
class WinUpdateMgr(object):
#-------------------------------------------------------------------------------
    """ a context manager for window Freeze()/Thaw() pairs
    """
    def __init__(self, win):
        object.__init__(self)
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, type, val, tb):
        self.win.Thaw()


#-------------------------------------------------------------------------------
class BusyCursorMgr(object):
#-------------------------------------------------------------------------------
    """ a context manager for window Busy/EndBusy cursor pairs
    """
    def __enter__(self):
        wx.BeginBusyCursor()

    def __exit__(self, type, val, tb):
        wx.EndBusyCursor()


#-------------------------------------------------------------------------------
def cvtStringToFlag(prefix, s):
#-------------------------------------------------------------------------------
    try:
        return eval(prefix + s.upper())
    except AttributeError:
        pass


#-------------------------------------------------------------------------------
class SimpleTestApp(object):
#-------------------------------------------------------------------------------
    class MyFrame(wx.Frame):
        def __init__(self, **kwds):
            wx.Frame.__init__(self, None, **kwds)
            self.arg = self.rfunc = None

            self.Bind(wx.EVT_TIMER, self.OnEvtTimer)
            self.timer = wx.Timer(self)
            self.timer.Start(2 * 100, True)

        def OnEvtTimer(self, e):
            print('timer tick')
            if self.rfunc:
                if not isinstance(self.arg, tuple):
                    self.arg = (self.arg,)

                if not self.rfunc(*self.arg) :
                    self.Destroy()

        def setTest(self, func, arg):
            self.rfunc = func
            self.arg = arg

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, frame=MyFrame, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        self.app = wx.PySimpleApp()

        kwds['title'] = title
        self.win = frame(**kwds)
        self.app.SetTopWindow(self.win)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setTest(self, func, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.win.setTest(func, arg)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.win.Show(True)
        self.app.MainLoop()


#-------------------------------------------------------------------------------
class App(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, frame, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.app = wx.PySimpleApp()

        kwds['title'] = title
        if "id" not in kwds:
            kwds["id"] = -1
        self.win = frame(None, **kwds)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, show=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.app.SetTopWindow(self.win)
        if show:
            self.win.Show(True)
        self.app.MainLoop()


#-------------------------------------------------------------------------------
class ListBox(wx.VListBox):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name="listBox"):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.VListBox.__init__(self, parent, id, pos, size, style, name)
        self.contents = []
        self.SetItemCount(0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetStringSelection(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.contents[self.GetSelection()][0]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetCount(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return len(self.contents)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetString(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.contents[idx][0]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetFirstItem(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ScrollToLine(idx)
        self.RefreshAll()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Append(self, txt, color='#000000'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if txt.startswith('COLOR:#'):
            # COLOR:#fffffftext
            color = txt[6:13]
            txt = txt[13:]
        self.contents.append((txt, color))
        self.SetItemCount(len(self.contents))
        self.RefreshAll()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.VListBox.Clear(self)
        self.SetItemCount(0)
        self.contents = []
        self.RefreshAll()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnMeasureItem(self, n):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.GetTextExtent(self.contents[n][0])[1] + 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnDrawItem(self, dc, rect, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        txt, color = self.contents[idx]
        dc.SetFont(self.GetFont())
        dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT) if self.IsSelected(idx) else wx.NamedColour(color))
        dc.DrawLabel(txt, rect, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)


#-------------------------------------------------------------------------------
class ListBox1(wx.SimpleHtmlListBox):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.SimpleHtmlListBox.__init__(self, *args, **kwds)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetFirstItem(self, idx):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ScrollLines(idx)


#-------------------------------------------------------------------------------
class MDlg(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title, mvsLabel=None, addRow=True, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        self.dlg = wx.Dialog(parent, -1, title, pos, size, style=style)
        self.dlg.CenterOnParent()

        if mvsLabel is None:
            self.mvs = wx.BoxSizer(wx.VERTICAL)
        else:
            sb = wx.StaticBox(self.dlg, -1, mvsLabel)
            self.mvs = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.dlg.SetSizer(self.mvs)
        self.mvs.SetSizeHints(self.dlg)
        if addRow:
            self.nextRow()

        self.cntl = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            val = self.cntl[attr].GetValue()
        except AttributeError:
            val = self.cntl[attr].GetStringSelection()
        except AttributeError:
            val = self.cntl[attr].GetSelections()
        except AttributeError:
            val = self.cntl[attr].GetSelection()
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cntl[attr].SetValue(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextRow(self, sLabel=None, prop=0, flags=wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, border=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if sLabel is None:
            self.curSizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            sb = wx.StaticBox(self.dlg, -1, sLabel)
            self.curSizer = wx.StaticBoxSizer(sb, wx.HORIZONTAL)

        self.mvs.Add(self.curSizer, prop, flags, border)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCntl(self, cntl, attr=None, prop=1, flags=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if attr is not None:
            self.cntl[attr] = cntl
        self.curSizer.Add(cntl, prop, flags, border)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addSpacer(self, prop_size=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(prop_size, tuple):
            self.curSizer.AddSpacer(prop_size)
        else:
            self.curSizer.AddStretchSpacer(prop_size)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addDlgButtons(self, style):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## TODO[20100925_111917]: remove this if all is well -- (Sat Sep 25 11:19:33 2010)
###        self.nextRow(prop=0, flags=wx.ALIGN_CENTER, border=10)
###        self.addSpacer(1)
###
###        if style & wx.OK:
###            self.addCntl(wx.Button(self.dlg, wx.ID_OK, 'Ok'), 0, flags=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5)
###
###        if (style & (wx.OK | wx.CANCEL)) == (wx.OK | wx.CANCEL):
###            self.addSpacer((30,30))
###
###        if style & wx.CANCEL:
###            self.addCntl(wx.Button(self.dlg, wx.ID_CANCEL, 'Cancel'), 0, flags=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5)
###
###        self.addSpacer(1)

        szr = self.dlg.CreateButtonSizer(style)
        self.mvs.Add(szr, flag=wx.CENTER)

        if style & wx.HELP:
            self.dlg.Bind(wx.EVT_BUTTON, self.OnHelp, id=wx.ID_HELP)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def endModal(self, val=wx.ID_OK):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.dlg.EndModal(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnHelp(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('OnHelp called')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dumpRow(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for v in self.curSizer.GetChildren():
            if v.IsSizer():
                l.append('sizer')
            else:
                l.append(v.GetWindow())
        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, modal=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mvs.Fit(self.dlg)
        if modal:
            return self.dlg.ShowModal()
        else:
            self.dlg.Show()


#-------------------------------------------------------------------------------
class HtmlBoxDialog(MDlg):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, caption, message,style=wx.OK | wx.CANCEL ,size=wx.DefaultSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MDlg.__init__(self, parent, caption, addRow=0)

        self.nextRow(prop=1)

        hwin = wx.html.HtmlWindow(self.dlg, -1, size=size, style=wx.BORDER_SUNKEN)
        hwin.AppendToPage(message)
        self.addCntl(hwin, 1, border=5)

        self.addDlgButtons(style)


#-------------------------------------------------------------------------------
def HtmlBox(parent, caption, message, style=wx.OK|wx.CANCEL, size=wx.DefaultSize, modal=True):
#-------------------------------------------------------------------------------
    hb = HtmlBoxDialog(parent, caption, message, style=style, size=size)
    return hb.run(modal)


#-------------------------------------------------------------------------------
class ListCtrlDialog(MDlg):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, caption,  size=wx.DefaultSize, style=wx.OK | wx.CANCEL):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MDlg.__init__(self, parent, caption, addRow=0)

        self.lc = None
        self.Create(size, style)
        assert self.lc is not None

        self.ClearAll()
        self.dlg.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivate)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, size, style):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.addListCntl(size)
        self.addDlgButtons(style)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addListCntl(self, size=wx.DefaultSize):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.nextRow(prop=1, flags=wx.EXPAND)
        self.lc = wx.ListCtrl(self.dlg, -1, size=size, style=wx.LC_LIST)
        self.addCntl(self.lc, None, prop=1, border=5)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ClearAll(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.lc.ClearAll()
        self.ary = []
        self.idx = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetValues(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        item = -1; items = []

        while 1:
            item = self.lc.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1: break
            items.append(self.ary[item])

        return items

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnActivate(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print(e.GetIndex())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addItem(self, s, imgidx=None, bgclr='#ffffff'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if imgidx is None:
            self.lc.InsertStringItem(self.idx, s)
        else:
            self.lc.InsertImageStringItem(self.idx, s, imgidx)

        self.lc.SetItemBackgroundColour(self.idx, wx.NamedColor(bgclr))
        self.ary.append(s)
        self.idx += 1


#-------------------------------------------------------------------------------
class FileDialog(ListCtrlDialog):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, caption, filter='*', state=None, size=wx.DefaultSize, style=wx.OK | wx.CANCEL):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.curDir = ''
        self.filter = ''
        self.state = state

        ListCtrlDialog.__init__(self, parent, caption, size, style)

        ## restore any previous state
        if state and 'curDir' in state:
            self.cd(state['curDir'])
        else:
            self.cd(oss.pwd())

        if state and 'filter' in state:
            self.filter = state['filter']
        else:
            self.filter = filter

        self.set('fltrcntl', self.filter)
        self.origDir = self.curDir


        self.CreateImageList()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Create(self, size, style):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## top line shows current directory
        self.nextRow(prop=0)
        self.dir = wx.TextCtrl(self.dlg, -1, self.curDir)
        self.addCntl(self.dir, 'curDir', prop=1, border=5)

        ## list control box
        self.addListCntl(size)

        ## show file filter and refresh button
        self.nextRow(prop=0)
        self.fltrcntl = wx.TextCtrl(self.dlg, -1, self.filter)
        ###self.fltrcntl = wx.ComboBox(self.dlg, -1, self.filter, style=wx.CB_DROPDOWN)
        self.addCntl(self.fltrcntl, 'fltrcntl', prop=1, flags=wx.EXPAND|wx.ALL|wx.ALIGN_LEFT, border=5)

        rb = wx.Button(self.dlg, 1001, 'Refresh')
        self.addCntl(rb, prop=0, flags=wx.ALIGN_RIGHT|wx.ALL, border=5)
        self.dlg.Bind(wx.EVT_BUTTON, self.fill, rb)

        b = wx.Button(self.dlg, 1002, 'Home')
        self.addCntl(b, prop=0, flags=wx.ALIGN_RIGHT|wx.ALL, border=5)
        self.dlg.Bind(wx.EVT_BUTTON, self.goHome, b)

        self.CustomizeDlg()

        ## show basic dialog buttons
        self.addDlgButtons(style)

        self.dlg.SetDefaultItem(rb)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CustomizeDlg(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateImageList(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        size = (16, 16)
        self.imageList = wx.ImageList(*size)
        for art in wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_NORMAL_FILE:
            self.imageList.Add(wx.ArtProvider.GetBitmap(art, wx.ART_OTHER, size))
        self.lc.AssignImageList(self.imageList, wx.IMAGE_LIST_SMALL)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def goHome(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cd(self.origDir)
        self.fill()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnActivate(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = self.ary[e.GetIndex()]

        if v.endswith('/'):
            self.cd(v)
            self.fill()
        else:
            self.endModal()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cd(self, d):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not d: return

        ## absolute path
        if oss.isAbsPath(d) :
            self.curDir = d
        elif d.startswith('..'):
            self.curDir = '/'.join(oss.pathsplit(self.curDir)[:-1])
        else:
            self.curDir += '/' + d

        self.curDir = oss.canonicalPath(self.curDir)
        print('"cd" curDir:', self.curDir)
        self.set('curDir', self.curDir)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def fill(self, e=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ClearAll()
        curDir = self.get('curDir')

        ## path was modified by user, go to new path
        if curDir != self.curDir:
            self.cd(curDir)

        l = len(self.curDir)
        if not (l == 1 or (l == 3 and self.curDir[1] == ':')):
            self.addDir('..')

        for d in self.getDirs():
            self.addDir(d)

        for f in self.getFiles(self.get('fltrcntl')):
            self.addFile(f)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addDir(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.addItem(s + '/', 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addFile(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.addItem(s, 2)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetValues(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [oss.canonicalPath(self.curDir + '/' + v) for v in ListCtrlDialog.GetValues(self)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDirs(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return sorted([oss.basename(f) for f in oss.ls(self.curDir + '/*') if oss.IsDir(f)])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getFiles(self, filter):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        files = []
        for ff in filter.split():
            files.extend([f for f in oss.ls(self.curDir + '/' + ff) if not oss.IsDir(f)])
        return sorted(oss.basename(files))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def saveState(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.fill()
        v = ListCtrlDialog.run(self)

        ## set state
        if self.state is not None:
            self.state['curDir'] = self.curDir
            self.state['filter'] = self.get('fltrcntl')
            self.saveState()

        oss.cd(self.origDir)
        return v


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    ###import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    print(cvtStringToFlag('wx.NB_', args[0]))
    oss.exit()

    app = SimpleTestApp('test app')


    dlg = MDlg(app.win, 'Test Dialog', addRow=0)
    dlg.nextRow('User Login')
    dlg.addCntl(wx.TextCtrl(dlg.dlg), 'login', border=2)

    dlg.nextRow('Directory')
    dlg.addCntl(wx.TextCtrl(dlg.dlg, -1, 'C:/cool'), 'path', border=2)

    dlg.addDlgButtons(wx.ID_OK|wx.ID_CANCEL)


    msg = '''
    <body bgcolor="#cccccc">
    <table>
       <tr><td>cool</td><td> is something</td></tr>
       <tr><td>cool is some</td><td> is something</td></tr>
       <tr><td>coollller</td><td> is something</td></tr>
       <tr><td>c</td><td> is something</td></tr>
    </table>
    </body>
    '''

    def test(dlg):
        print('running test ...')

        state = {}
        mb = FileDialog(app.win, 'Select Files to Add to Project', state=state, size=(600,400), style=wx.OK|wx.CANCEL|wx.HELP)
        if mb.run() == wx.ID_OK:
            print(mb.GetValues())

###        mb = FileDialog(app.win, 'Select Files to Add to Project', state=state, size=(600,400))
###        if mb.run() == wx.ID_OK:
###            print(mb.GetValues())


    def test1(dlg):
        print('running test ...')
        HtmlBox(app.win, 'Caption', 'msg', modal=False)
        return 1

    app.setTest(test, dlg)

    app.run(0)


    res = not __test__()
    oss.exit(res)

