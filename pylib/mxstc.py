#!/usr/bin/env python
"""
library wrapped around wx.stc
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import keyword

import wx
import wx.html
import wx.stc as stc

import pylib.mx

if wx.Platform == '__WXMSW__':
    faces = {'times': 'Times New Roman',
             'mono' : 'Courier New',
             'helv' : 'Arial',
             'other': 'Comic Sans MS',
             'size' : 10,
             'size2': 8,
             }
else:
    faces = {'times': 'Times',
             'mono' : 'Courier',
             'helv' : 'Helvetica',
             'other': 'new century schoolbook',
             'size' : 12,
             'size2': 10,
             }

#-------------------------------------------------------------------------------
class mxStc(stc.StyledTextCtrl):
#-------------------------------------------------------------------------------
    fold_symbols = 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.parent = parent
        self.resourcePath = ""
        self.COMMENT_MARKER = '!!!'

        ## undo keys we don't like w/o undoing keys we do (see: http://www.yellowbrain.com/stc/keymap.html)
        for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.CmdKeyClear(ord(i), stc.STC_SCMOD_CTRL)
            self.CmdKeyClear(ord(i), stc.STC_SCMOD_CTRL | stc.STC_SCMOD_SHIFT)

        self.CmdKeyAssign(stc.STC_KEY_DOWN, stc.STC_SCMOD_CTRL, stc.STC_CMD_LINEDOWN)
        self.CmdKeyAssign(stc.STC_KEY_UP, stc.STC_SCMOD_CTRL, stc.STC_CMD_LINEUP)

        self.SetMargins(0,0)
        self.autoindentIgnoreChars = set()
        self.autoindentBlockStart = set()

        self.commentSpellCheckIgnore = set()
        self.commentSpellCheck = set()

        self.Properties = {
            'indent' : self.SetIndent,
            'indentationGuides' : self.SetIndentationGuides,
            'tabWidth' : self.SetTabWidth,
            'useTabs'  : self.SetUseTabs,
            'backspaceUnindents' : self.SetBackSpaceUnIndents,
            'edgeMode' : self.SetEdgeMode,
            'edgeColumn' : self.SetEdgeColumn,
            'viewWhiteSpace' : self.SetViewWhiteSpace,
            'setCaretLineBkgd' : self.SetCaretLineBack,
            'setCaretLineVisible' : self.SetCaretLineVisible,
            'setCaretWidth': self.SetCaretWidth,
            'setCaretColor': self.SetCaretForeground,
            'setCaretPeriod': self.SetCaretPeriod,
            'autoindentIgnoreChars' : lambda s: self.autoindentIgnoreChars.update(set(s.split())),
            'autoindentBlockStart' : lambda s: self.autoindentBlockStart.update(set(s.split())),
            'commentSpellCheckIgnore' : lambda s: self.commentSpellCheckIgnore.update(set(s.split())),
            'commentSpellCheck' : lambda s: self.commentSpellCheck.update(set(s.split())),
            'wrapMode' : lambda b: self.SetWrapMode(stc.STC_WRAP_WORD if b else stc.STC_WRAP_NODE),
        }

        self.SetViewWhiteSpace(stc.STC_WS_INVISIBLE)
        self.SetCaretLineBack('#f4f4f4')
        self.SetCaretLineVisible(0)
        self.SetCaretWidth(2)
        self.SetCaretForeground('#2f2f2f')
        self.SetCaretPeriod(1000)
        self.SetCodePage(stc.STC_CP_UTF8)
        ###self.SetBufferedDraw(False)

        self.SetUseAntiAliasing(True)
        ###self.SetYCaretPolicy(stc.STC_CARET_SLOP, 2)
        self.SetVisiblePolicy(stc.STC_VISIBLE_SLOP, 2)

        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#000000,back:#FFFFFF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,   "fore:#000000,back:#FF0000,bold")

        ## Setup a margin to hold fold markers
        self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)

        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)

        ## make this non 0 to see line numbers
        self.SetMarginWidth(0,  0)
        self.SetMarginWidth(1, 10)
        self.SetMarginWidth(2, 0)

        self.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT)
        ###self.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT | stc.STC_PERFORMED_USER | stc.STC_PERFORMED_UNDO | stc.STC_PERFORMED_REDO)

        if self.fold_symbols == 0:
            # Arrow pointing right for contracted folders, arrow pointing down for expanded
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_ARROWDOWN, "black", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_ARROW, "black", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "black", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "black", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black");

        elif self.fold_symbols == 1:
            # Plus for contracted folders, minus for expanded
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_MINUS, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_PLUS,  "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black");

        elif self.fold_symbols == 2:
            # Like a flattened tree control using circular headers and curved joins
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_CIRCLEMINUS,          "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_CIRCLEPLUS,           "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,                "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNERCURVE,         "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040");
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,         "white", "#404040");

        elif self.fold_symbols == 3:
            # Like a flattened tree control using square headers
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS,          "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,           "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,             "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,           "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,           "white", "#808080")


        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        self.lookup = {}

        self.SetFoldMarginColour(1,   '#c0ac84')
        self.SetFoldMarginHiColour(1, '#c0ac84')
        self.SetFoldMarginColour(2,   '#c0ac84')
        self.SetFoldMarginHiColour(2, '#c0ac84')

        self.SEL_BKGD0 = "#e0e0e0"
        self.SEL_BKGD1 = "#d0d0d0"

        self.SetSelBackground(1, self.SEL_BKGD0)
        self.SetMouseDwellTime(3000)
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))
        self.cursorHidden = False
        self.cursorOffLimits = True

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(stc.EVT_STC_STYLENEEDED, self.OnStyleNeeded)
        self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)
        self.Bind(stc.EVT_STC_DWELLSTART, self.OnMouseDwell)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def LoadFileConfiguration(self, fn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            inf = file(self.resourcePath + '/' + fn)
        except IOError:
            print("Can't load style file:", fn)
            return

        state = None
        errors = []

        pe = [];  alias = []; keywords = {0 : [], 1 : [], 2 : [], 3 : []}
        linenumber = 0
        for line in inf:
            linenumber += 1
            ln = line.strip()

            ## is it a section block identifier. ex: [cool]
            ## set state
            if len(ln) > 2 and ln[0] == '[' and ln[-1] == ']':
                state = ln[1:-1]
                continue

            ## handle aliases
            if state == 'aliases':
                ## aliases are handled verbatim

                if line.startswith('/#'):
                    continue
                alias.append(unicode(line))
                continue

            ## else load error parsing code
            elif state == 'parse_error':
                pe.append(line)

            line = ln
            if not line or line.startswith('/#'):
                continue

            ## load any keywords
            if state == 'keywords':
                ## @keywords[0-9]:
                try:
                    key, val = line.split(':')
                    s = int(key[-1])
                    keywords[s].append(val)
                except Exception, ex:
                    msg = "StyleFile Error: %s:%d (%s) -- '%s'" % (fn, linenumber, ex, line)
                    errors.append(msg)
                    print(msg)

            ## file type specific way of comment out large blocks
            elif state == 'comment_marker':
                self.COMMENT_MARKER = line.strip()

            ## load properties
            elif state == 'properties':
                try:
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    #print "Loading property: '%s' -> '%s'" % (key, val)

                    try:
                        val = int(val)

                        ## call the saved 'set property function' with passed value
                        if key in self.Properties:
                            self.Properties[key](val)
                            print(key + '(%d)' %val)
                        else:
                            self.SetProperty(key, val)
                    except ValueError:
                        #print 'properties set addition'
                        self.Properties[key](val)

                except Exception as ex:
                    msg = "StyleFile Error: %s:%d (%s) -- '%s'" % (fn, linenumber, ex, line)
                    errors.append(msg)
                    ###print msg

            ## load styles
            elif state == 'style':
                w = line.split(':', 1)
                sty = w[0].strip()
                val = w[1].strip()

                try:
                    val = val % faces
                except:
                    pass

                ###print "self.StyleSetSpec(" + sty + ',' + val + ')'
                self.StyleSetSpec(eval(sty), val)

        inf.close()

        ## parse errors
        if pe:
            ###print('\n%s\n' % ''.join(pe))
            self.call('SetBldWinParser', fn, ''.join(pe))

        ## handle keywords
        self.abbreviations = []
        for s in keywords:
            if keywords[s]:
                #print "Setting keywords", s, val
                self.SetKeyWords(s, ' '.join(keywords[s]))
                self.abbreviations.extend(keywords[s])

        ## if we have aliases, load them
        if alias:
            try:
                lookup = eval(''.join(alias))
                self.lookup = {}

                for k, v in lookup.items():
                    if isinstance(v, tuple):
                        self.lookup[k] = v
                    else:
                        self.lookup[k] = (None, v)

                #print self.lookup
            except Exception as ex:
                a = ''.join(['%3d: %s' % (idx+1, line) for idx, line in enumerate(alias)])
                msg = "StyleFile Error: %s: (%s) -- \n'%s'" % (fn, ex, a)
                errors.append(msg)
                print(msg)

        if errors:
            pylib.mx.MsgBox(self, "Configuration File Errors: '%s'" % (fn), '\n'.join(errors))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setLexer(self, lName, confFile):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.LoadFileConfiguration("all.conf")

        if lName == 'python':
            self.SetLexer(stc.STC_LEX_PYTHON)
            self.SetKeyWords(0, " ".join(keyword.kwlist) + ' cdef ctypedef struct enum')
            self.SetKeyWords(1, "self None True False assert")

            self.LoadFileConfiguration(confFile)

        elif lName == 'java':
            self.SetLexer(stc.STC_LEX_CPP)
            self.LoadFileConfiguration(confFile)

        elif lName == 'javascript':
            self.SetLexer(stc.STC_LEX_CPP)
            self.LoadFileConfiguration(confFile)

        elif lName in [wx.stc.STC_LEX_LATEX, "latex"]:
            self.SetWrapMode(stc.STC_WRAP_WORD)
            self.SetLexer(wx.stc.STC_LEX_LATEX)
            self.LoadFileConfiguration(confFile)

        else:
            assert lName is None or lName == 'None' or isinstance(lName, int)

            if lName is not None and lName != 'None':
                ###print "setting lexer", lName
                self.SetLexer(lName)

            else:
                self.SetLexer(wx.stc.STC_LEX_NULL)
                self.SetKeyWords(0, '')
                self.SetKeyWords(1, '')

            if confFile is not None:
                ###print("loading:", confFile)
                self.LoadFileConfiguration(confFile)

        self.SetStyleBits(self.GetStyleBitsNeeded())
        ###print "Bits:", self.GetStyleBits()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnUpdateUI(self, evt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ##print "mxStc.OnUpdateUI called"

        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

            if braceOpposite == -1:
                #print "Bad Braces"
                self.BraceBadLight(braceAtCaret)
            else:
                #print "Highlighting Braces"
                self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#000000,back:#FFFFFF,bold")
                self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,   "fore:#000000,back:#D0C0C0,bold")
                self.BraceHighlight(braceAtCaret, braceOpposite)

            ###pt = self.PointFromPosition(braceOpposite)
            ###self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            ###print pt
            ###self.Refresh(False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnMarginClick(self, evt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def FoldAll(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum -= 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lastChild = self.GetLastChild(line, level)
        line += 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1;

        return line

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnStyleNeeded(self, evt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnModified(self, evt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetLineTextFromPos(self, pos):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ln = self.LineFromPosition(pos)
        return self.GetLine(ln), ln

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnMouseDwell(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # set the cursor for the window
        if not self.cursorOffLimits:
            self.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))
            self.cursorHidden = True
        e.Skip()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnRightDown(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('OnRightDown()called')
        e.Skip()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnMouseEvents(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # set the cursor for the window
        if e.Entering():
            self.cursorOffLimits = False

        if e.Leaving():
            self.cursorOffLimits = True

        if self.cursorHidden:
            self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))
            self.cursorHidden = False
        e.Skip()



#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    def usage(rc, errmsg=""):
        print >> oss.stderr, __doc__
        if errmsg:
            print >> oss.stderr, """
Error:
""" + str(errmsg)
        oss.exit(rc)

    args, opts = oss.gopt(oss.argv[1:], [], [], usage)


    app = wx.PySimpleApp()
    #__test__()

    oss.exit(0)
