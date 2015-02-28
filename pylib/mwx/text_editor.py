#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

def __cntl(k):
    return ord(k) - ord('A') + 1


MXK_CA = __cntl('A')
MXK_CB = __cntl('B')
MXK_CC = __cntl('C')
MXK_CD = __cntl('D')
MXK_CE = __cntl('E')
MXK_CF = __cntl('F')
MXK_CG = __cntl('G')
MXK_CH = __cntl('H')
MXK_CI = __cntl('I')
MXK_CJ = __cntl('J')
MXK_CK = __cntl('K')

MXK_CQ = __cntl('Q')

MXK_CS = __cntl('S')
MXK_CT = __cntl('T')

MXK_CV = __cntl('V')

MXK_CX = __cntl('X')
MXK_CY = __cntl('Y')


TE_SAVE = 1
TE_QUIT = 2

#-------------------------------------------------------------------------------
class TextEditor(wx.TextCtrl, AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent = None, id = -1, val = "", pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(TextEditor, self).__init__(parent, id, val, pos, size, style | wx.TE_RICH2 | wx.TE_PROCESS_TAB)
        AutoEventBind.__init__(self)
        self.parent = parent
        self.lastch = 32
        self.selStart = None
        self.selEnd = None
        self.SelAttr = wx.TextAttr(wx.Colour(0,0,0), wx.Colour(228,228,228))
        self.NormAttr = wx.TextAttr(wx.Colour(0,0,0), wx.Colour(255,255,255))
        #self.SetSelection(1,0)
        #self.SetInsertionPointEnd()
        self.SetStyle(0, 0, self.NormAttr)
        wx.CallAfter(self.SetInsertionPointEnd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetRelPos(self, h, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.PositionToXY(self.GetInsertionPoint())
        self.SetInsertionPoint(self.XYToPosition(x + h, y + v))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetBegLine(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.PositionToXY(self.GetInsertionPoint())
        return self.XYToPosition(0, y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetEndLine(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.PositionToXY(self.GetInsertionPoint())
        return self.XYToPosition(self.GetLineLength(y), y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetBegEndLine(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.PositionToXY(self.GetInsertionPoint())
        return self.XYToPosition(0, y), self.XYToPosition(0, y+1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtChar(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        kc = e.GetKeyCode()
        skip = False


        if self.lastch == MXK_CK:
            if kc == MXK_CS:
                assert dbg.DbgPrint("Saving")
                try:
                    self.parent.EditorHandler(self.GetId(), TE_SAVE)
                except:
                    pass
            elif kc == MXK_CQ:
                assert dbg.DbgPrint("Quit")
                try:
                    self.parent.EditorHandler(self.GetId(), TE_QUIT)
                except:
                    pass

            elif kc == MXK_CB:
                self.selStart = self.GetInsertionPoint()
                self.selEnd = None

            elif kc == MXK_CK:
                self.selEnd = self.GetInsertionPoint()
                self.SetStyle(self.selStart, self.selEnd, self.SelAttr)

            elif kc == MXK_CH:
                self.SetStyle(0, self.GetLastPosition(), self.NormAttr)
                self.selStart = None

            elif kc == MXK_CC:
                if self.selStart is not None and self.selEnd is not None:
                    self.WriteText(self.GetRange(self.selStart, self.selEnd))

            elif kc == MXK_CV:
                if self.selStart is not None and self.selEnd is not None:
                    pos = self.GetInsertionPoint()
                    txt = self.GetRange(self.selStart, self.selEnd)
                    if self.selStart < self.GetInsertionPoint():
                        self.WriteText(txt)
                        self.Remove(self.selStart, self.selEnd)
                    else:
                        self.Remove(self.selStart, self.selEnd)
                        self.SetInsertionPoint(pos)
                        self.WriteText(txt)

                    self.selStart = None

            elif kc == MXK_CY:
                if self.selStart is not None and self.selEnd is not None:
                    self.Remove(self.selStart, self.selEnd)
                    self.selStart = None

            kc = 32


        elif self.lastch == MXK_CQ:
            if kc == MXK_CS:
                self.SetInsertionPoint(self.GetBegLine())

            elif kc == MXK_CD:
                self.SetInsertionPoint(self.GetEndLine())

            elif kc == MXK_CY:
                self.Remove(self.GetInsertionPoint(), self.GetEndLine())

            kc = 32

        elif kc == MXK_CX:
            self.SetRelPos(0, 1)
        elif kc == MXK_CE:
            self.SetRelPos(0, -1)
        elif kc == MXK_CS:
            self.SetRelPos(-1, 0)
        elif kc == MXK_CD:
            self.SetRelPos(1, 0)
        elif kc == MXK_CA:
            self.SetRelPos(-1, 0)
        elif kc == MXK_CF:
            self.SetRelPos(1, 0)

        elif kc == MXK_CY:
            x, y = self.GetBegEndLine()
            self.Remove(x, y)

        elif kc == MXK_CB:
            pgh = self.GetValue().split('\n')
            o = []
            for p in pgh:
                o.append('\n' + textwrap.fill(p))

            self.SetValue('\n'.join(o))

        else:
            skip = True

        self.lastch = kc

        #if self.selStart is not None:
        #    pos = self.GetInsertionPoint()
        #    if self.selEnd is None:
        #        self.SetStyle(self.selStart, self.GetInsertionPoint(), self.SelAttr)
        #    else:
        #        self.SetStyle(self.selStart, self.selEnd, self.SelAttr)
        #    self.SetInsertionPoint(pos)

        if skip: e.Skip()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtKeyUp(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return
        if self.selStart is not None:
            pos = self.GetInsertionPoint()
            if self.selEnd is None:
                self.SetStyle(self.selStart, self.GetInsertionPoint(), self.SelAttr)
            else:
                self.SetStyle(self.selStart, self.selEnd, self.SelAttr)
            self.SetInsertionPoint(pos)


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

    usage = oss.mkusage(__test__.__doc__)
    args, opts = oss.gopt(oss.argv[1:], [], [], usage)

    res = not __test__(verbose=True)
    oss.exit(res)

