
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import wx
import wx.aui

import threading

import pylib.mx
import pylib.osscripts as oss
import pylib.config as cfg


from pylib.debug import *


## globals
gTITLE = "MDITemplate"
DEFAULT_CONFIG_NAME = gTITLE + ".cfg"
CHILD_EXTENSIONS = "*.*"

#
# Global Configuration
#
gConfig = None

#-------------------------------------------------------------------------------
class MDIConfigChild(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.Filename = ""
        self.WindowStyle = 0
        self.LineNumber = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class MDIConfig(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.childWindows = []
        self.MainWindowPos = (50, 50)
        self.MainWindowSize = (500,300)
        self.MainWindowFlags = 0
        self.currentWindow = ""


#-------------------------------------------------------------------------------
class CallUp(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.parent = parent

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def call(self, func, *args, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cf = getattr(self, func, None)
        if cf is not None:
            return cf(*args, **kw)

        if self.parent is None:
            raise NotImplementedError("No Function: " + func)

        return self.parent.call(func, *args, **kw)


#-------------------------------------------------------------------------------
class FileDb(object):
#-------------------------------------------------------------------------------
    """ Maintains information about opened files as well as a mapping between
        the hndl, filename and the window. The hndl must be unique.
    """

    #-------------------------------------------------------------------------------
    class FileObj(object):
    #-------------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, hndl=None, win=None, fpath=None, primary=True):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            object.__init__(self)
            self.hndl = hndl
            self.fpath = hndl if fpath is None else fpath

            self.win = win
            self.cxt = None
            self.order = -1
            self.update()
            self.props = set()
            self.primary = primary

            self.fpath = oss.canonicalPath(self.fpath)
            self.hndl = oss.canonicalPath(self.hndl)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def update(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #TODO: in cases where new file or changed name, sometimes doesn't exit
            try:
                self.filetime = oss.FileTimeInt(self.fpath)
            except WindowsError as we:
                print("EXCEPTION: FileObj.update:", we)
                self.filetime = 0

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def hasChanged(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            try:
                tm = oss.FileTimeInt(self.fpath)
                return tm > self.filetime
            except WindowsError as we:
                print("EXCEPTION: FileObj.hasChanged:", we)
                return False

        def setContext(self, cxt = None):
            self.cxt = cxt

        def getContext(self):
            return self.cxt

        def setProperty(self, prop):
            self.props.add(prop)

        def rmProperty(self, prop):
            self.props.discard(prop)

        def getProperty(self, prop):
            return prop in self.props

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __str__(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            s = ["\nfileDb.FileObj"]
            s.append(str(self.hndl))
            s.append(str(self.fpath))
            s.append(str(self.props))
            s.append(str(self.filetime))
            s.append(str(self.primary))
            return '\n    '.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(FileDb, self).__init__()

        ## tracking children windows
        self.cnt = 0
        self.fileObjHndls = {}
        self.dblock = threading.RLock()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getFO(self, cwin=None, hndl=None, fpath=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.dblock:
            if hndl is not None:
                hndl = oss.canonicalPath(hndl)
                if hndl in self.fileObjHndls:
                    return self.fileObjHndls[hndl]

            if fpath is not None:
                fpath = oss.canonicalPath(fpath)
                for fo in self.fileObjHndls.values():
                    if fo.primary and fpath == fo.fpath:
                        return fo

            if cwin is not None:
                for fo in self.fileObjHndls.values():
                    if cwin == fo.win:
                        return fo

###        print "-- db --"
###        print self.fileObjHndls
###        print "-- db --"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, cwin, hndl, fpath=None, primary=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add the window and its name to the database
        """

        with self.dblock:
            assert hndl not in self.fileObjHndls

            fo = FileDb.FileObj(hndl, cwin, fpath, primary)
            cwin.FileName = fo.fpath
            self.fileObjHndls[fo.hndl] = fo
            fo.order = self.cnt + 1
            self.cnt += 1
            return fo

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasChanged(self, fh = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns either a list of changed files or a boolean if a specific
            file was specified
        """

        with self.dblock:
            if fh is None:
                res = []
                for h in self.fileObjHndls.keys():
                    if self.fileObjHndls[h].hasChanged():
                       res.append(h)
                return res

            return self.getFO(hndl = fh).hasChanged()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, fh = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ updates any file change state such all or the specified file are now
            unchanged
        """

        with self.dblock:
            try:
                if fh is None:
                    for h in self.fileObjHndls.keys():
                        self.fileObjHndls[h].update()
                else:
                    self.getFO(hndl = fh).update()
            except KeyError:
                pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setContext(self, fh, cxt = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ allows storing any kind of context, cxt, with a file
        """
        with self.dblock:
            self.getFO(hndl = fh).setContext(cxt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getContext(self, fh):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ retrieves previously stored context
        """
        with self.dblock:
            return self.getFO(hndl = fh).getContext()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setProperty(self, fh, prop):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ adds a property (any string or object) to the set of properties
            associated with a file
        """
        with self.dblock:
            self.getFO(hndl = fh).setProperty(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmProperty(self, fh, prop):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ removes the specified property from a file
        """
        with self.dblock:
            self.getFO(hndl = fh).rmProperty(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getProperty(self, fh, prop):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a boolean indicating whether the property is present
        """
        with self.dblock:
            return self.getFO(hndl = fh).getProperty(prop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getChild(self, hndl, fpath=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ gets the child window associated with hndl
        """
        with self.dblock:
            hndl = oss.canonicalPath(hndl)
            fo = self.getFO(hndl = hndl)
            if fo is not None:
                return fo.win

    isin = getChild

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getFileName(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the fileName associated with this window
        """
        return self.getFO(cwin = c).fpath

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getHndl(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the hndl associated with this window
        """
        return self.getFO(cwin = c).hndl

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getFileTab(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the UI displayed name associated with this window
        """
        return oss.basename(self.getFO(cwin = c).fpath)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def itemsort(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ used to sort the list of (window, name) tuples return by items()
        """
        try:
            return self.fileObjHndls[s[1]].order
        except KeyError:
            return 10000

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def items(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns a list of (window, name) tuples of all entries
        """
        with self.dblock:
            l = [(fo.win, fo.hndl) for fo in self.fileObjHndls.values()]
            l.sort(key=self.itemsort)
            return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ remove the specified window from the database
        """
        with self.dblock:
            fo = self.getFO(cwin = c)
            try:
                del self.fileObjHndls[fo.hndl]
            except KeyError:
                print("Remove Failed", c.FileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ empty the database
        """
        with self.dblock:
            self.fileObjHndls.clear()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("\nfileDb Dump")
        print("\n    openfiles")
        for f, fo in self.fileObjHndls.items():
            print('--------------')
            print(f)
            print("           ", "            \n".join(str(fo).split('\n')))

            if fo.cxt is not None:
                print("           ", "            \n".join(str(fo.cxt).split('\n')))
            else:
                print("cxt == None")
        print("fileDb end")


#-------------------------------------------------------------------------------
def ErrMsg(parent, Msg):
#-------------------------------------------------------------------------------
    assert DbgPrint(Msg)
    wx.MessageDialog(parent, Msg, "%s Error" % gTITLE, wx.ICON_ERROR).ShowModal()


#-------------------------------------------------------------------------------
class DisplayPanel(pylib.mx.Panel, CallUp):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, style = wx.WANTS_CHARS | wx.CLIP_CHILDREN):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pylib.mx.Panel.__init__(self, parent, id = -1, style = style, name='display_panel')
        CallUp.__init__(self, parent)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self, FileName, force=False, askPerm=False, auto=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert DbgPrint("DisplayPanel: Save")
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Open(self, FileName, fdb):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert DbgPrint("DisplayPanel: Open")
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def closeWindow(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.Destroy()


#-------------------------------------------------------------------------------
class DisplayFrameBase(CallUp, pylib.mx.AutoEventBind):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, PanelClass, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        CallUp.__init__(self, parent)
        pylib.mx.AutoEventBind.__init__(self)

        self.fileName = FileName
        self.parent = parent
        self.win = PanelClass(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.win, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Open = self.win.Open
        self.Save = self.win.Save
        self.Reload = self.win.Reload

        self.SetFocus()
        wx.CallAfter(self.Layout)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def IsModified(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.IsModified1(self, *args, **kwds)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setReadOnlyIndicator(self, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.setReadOnlyIndicator(self, *args, **kwds)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def callDown(self, attr, *args, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        func = getattr(self.win, attr, None)
        if func is not None:
            return func(*args, **kw)
        return self.win.callDown(attr, *args, **kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetLineNum(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.win.GetLineNum()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GotoLine(self, ln):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.win.GotoLine(ln)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetPanel(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.win

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetChildAttr(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        setattr(self.win, attr, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtClose(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert DbgPrint("OnEvtClose")
        self.parent.OnCloseChild(e, self)


#-------------------------------------------------------------------------------
class DisplayFrameMDI(DisplayFrameBase, pylib.mx.MDIChildFrame):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, PanelClass, FileName = "", style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pylib.mx.MDIChildFrame.__init__(self, parent, -1, FileName, style = wx.DEFAULT_FRAME_STYLE | style)
        DisplayFrameBase.__init__(self, parent, PanelClass, FileName)


#-------------------------------------------------------------------------------
class DisplayFrameAui(DisplayFrameBase, wx.aui.AuiMDIChildFrame):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, PanelClass, FileName = "", style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.aui.AuiMDIChildFrame.__init__(self, parent, -1, FileName, style = wx.DEFAULT_FRAME_STYLE | style)
        DisplayFrameBase.__init__(self, parent, PanelClass, FileName)


#-------------------------------------------------------------------------------
class MainFrameBase(CallUp):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, context = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        CallUp.__init__(self, parent)

        self.fileDb = self.allocFileDb()

        self.sb = self.CreateStatusBar()
        self.context = context

        ## start a 1 minute timer
        self.timer = wx.Timer(self)
        self.timer.Start(20 * 1000)
        self.timerTicks = 0

        self.inCheck = 0
        self.OpenSaveDir = None
        self.Bind(wx.EVT_TIMER, self.OnEvtTimer)
        self.Bind(wx.EVT_SET_FOCUS, self.OnEvtSetFocus)

        self.ChildExts = '*.*'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def allocFileDb(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return FileDb()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setChildTitle(self, c, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bfn = oss.basename(FileName)
        c.SetTitle(bfn)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AdjustMenu(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CheckFilesTimes(self, autoReload=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.inCheck:
            return

        self.inCheck = 1

        for hndl in self.fileDb.hasChanged():
            ## some files are marked to reload whenever they are changed
            ## some actions should cause a reload
            if autoReload or self.fileDb.getProperty(hndl, 'auto-reload'):
                self.fileDb.getChild(hndl).Reload()

            else:
                ## other files may need approval
                if wx.MessageDialog(self, "File '%s' Changed\nReload?" % hndl, 'File Change Notification', wx.YES_NO|wx.ICON_QUESTION).ShowModal() == wx.ID_YES:
                    self.fileDb.getChild(hndl).Reload()

            self.fileDb.update(hndl)
        self.inCheck = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def syncFdb(self, FileName, fdb):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OpenFile(self, FileName, style = 0, lineNum = 0, hndl=None, readOnly=False, fo=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ Opens the file 'FileName' (path + file)
        """
        if hndl is None: hndl = FileName
        hndl = oss.canonicalPath(hndl)
        FileName = oss.canonicalPath(FileName)

        if self.fileDb.isin(hndl, FileName):
            ## BUG -- technically this shouldn't be allowed, lets see if it happens
            assert ptrace(3, "Open: FileName is already in database")
            pass

        c = self.CreateChild(FileName, style)
        fdb = self.fileDb.add(c, hndl, FileName)
        self.syncFdb(FileName, fdb)

        try:
            c.Open(FileName, fdb, fo=fo)
            c.GotoLine(lineNum)
            self.sb.SetStatusText("Loaded: " + FileName)
        except IOError:
            ErrMsg(self, "Can't Open: " + FileName)
            c.Destroy()
            self.fileDb.rm(c)
            return False

        self.setChildTitle(c, FileName)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnNew(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fd = wx.FileDialog(self, "New File", self.getHomeDir(), "", self.ChildExts, wx.SAVE | wx.OVERWRITE_PROMPT)

        if fd.ShowModal() == wx.ID_OK:
            sf = fd.GetPath()
            c = self.CreateChild()
            self.setChildTitle(c, sf)
            self.fileDb.add(c, sf)
            c.Save(c.FileName, askPerm=False)
            self.fileDb.update(c.FileName)

    OnNew.Help = "Create New"


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getOpenSaveDir(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.OpenSaveDir is None:
            self.OpenSaveDir = True
            return self.getHomeDir()
        return ""


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnOpen(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fd = wx.FileDialog(self, "Open", self.getOpenSaveDir(), "", self.ChildExts, wx.OPEN | wx.MULTIPLE | wx.FILE_MUST_EXIST)
        if fd.ShowModal() == wx.ID_OK:
            for fp in fd.GetPaths():
                self.FindOpenFile(fp)

    OnOpen.Help = "Open File(s)"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSave(self, e, Child = None, AskPerm = True, Auto = False, Closing=False, Force=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Child or self.GetActiveChild()
        if c is None: return

        if self.fileDb.getHndl(c) == str(c):
            return self.OnSaveAs(e, c)

        if c.Save(c.FileName, askPerm=AskPerm, auto=Auto, closing=Closing, force=Force):
            self.fileDb.update(c.FileName)
            self.sb.SetStatusText("Saved: " + c.FileName)

    OnSave.Help = "Save Current"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSaveAs(self, e, Child=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Child or self.GetActiveChild()

        fd = wx.FileDialog(self, "Save", self.getOpenSaveDir(), "", self.ChildExts, wx.SAVE | wx.OVERWRITE_PROMPT)

        if fd.ShowModal() == wx.ID_OK:
            sf = fd.GetPath()
            if self.fileDb.isin(sf):
                ErrMsg(self, "File Already Open")
                return

            self.fileDb.rm(c)
            self.fileDb.add(c, sf)
            self.setChildTitle(c, sf)
            c.reset()

            if c.Save(sf, force=True):
                self.fileDb.update(sf)
                self.sb.SetStatusText("Saved: " + sf)
                self.SaveAs1(sf)

    OnSaveAs.Help = "Save Current As"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SaveAs1(self, sf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtSetFocus(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert DbgPrint(3, "OnEvtSetFocus")
        self.CheckFilesTimes()
        e.Skip()

    OnEvtSetFocus.EVT_ID = -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtTimer(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.CheckFilesTimes()

        self.timerTicks += 1

        if self.timerTicks % 3 == 0:
            t = threading.Thread(None, self.SaveFiles, 'SaveFileThread')
            t.start()

        e.Skip()

    OnEvtTimer.EVT_ID = -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SaveFiles(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for c, hndl in self.fileDb.items():
            ## only sav named files
            if hndl != str(c):
                try:
                    c.Save(c.FileName, askPerm=False, auto=True)
                    self.fileDb.update(c.FileName)
                except wx.PyDeadObjectError as ex:
                    print(GetTraceback())
                    print("Bad File Window", hndl)
                    print(ex)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnCloseChild(self, e, Sender = None, AskPerm = True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = Sender or self.GetActiveChild()
        self.OnSave(e, c, AskPerm, Closing=True)
        self.fileDb.rm(c)
        c.Destroy()

    OnCloseChild.Help = "Close Current"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnReOpen(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = self.GetActiveChild()
        fileName = self.fileDb.getFileName(c)
        hndl = self.fileDb.getHndl(c)
        self.OnCloseChild(e, c, False)
        self.Open(fileName, hndl=hndl)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnAbout(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnHelp(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnEvtClose(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.Close()
        self.Destroy()
        assert DbgPrint("Finished")

        ## hack, some window won't close and I'm not sure why, but this kills it
        wx.Exit()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Close(self, all=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        c = self.GetSelectedWindow()
        if c is not None:
            if gConfig is not None:
                gConfig.currentWindow = self.fileDb.getFileName(c)

        cwins = []
        for c, fn in self.fileDb.items():
            self.OnSave(None, c, AskPerm = True, Closing=True)

        for c, fn in self.fileDb.items():
            mcc = MDIConfigChild()
            mcc.Filename = fn
            try:
                mcc.WindowStyle = cfg.GetFlags(c)
                mcc.LineNumber = c.GetLineNum()
                cwins.append(mcc)
            except wx.PyDeadObjectError as ex:
                print(GetTraceback())
                print("Bad File Window", fn)
                print(ex)

            if all:
                self.OnCloseChild(None, c)

        ###print "\nDumping file database:"
        ###self.fileDb.dump()

        self.fileDb.clear()

        ## save config
        if gConfig is not None:
            self.ShutdownNotification(gConfig)
            gConfig.MainWindowSize = self.GetSizeTuple()
            gConfig.MainWindowFlags = cfg.GetFlags(self)
            gConfig.MainWindowPos = self.GetPositionTuple()

            gConfig.childWindows = cwins
            assert DbgPrint(1, "Saving to:", gConfig._filename)
            gConfig.Save()

        assert DbgPrint("Finished")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShutdownNotification(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetActive(self, winName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass



#-------------------------------------------------------------------------------
class MainFrameMDI(MainFrameBase, pylib.mx.MDIParentFrame):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, ID, title, context, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.WS_EX_PROCESS_IDLE):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pylib.mx.MDIParentFrame.__init__(self, parent, ID, title, pos, size, style)
        MainFrameBase.__init__(self, parent, context)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateChild(self, FileName = "", style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return DisplayFrameMDI(self, DisplayPanel, FileName, style)


#-------------------------------------------------------------------------------
class MainFrameAui(MainFrameBase, wx.aui.AuiMDIParentFrame):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, ID, title, context, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.WS_EX_PROCESS_IDLE | wx.FRAME_NO_WINDOW_MENU):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.aui.AuiMDIParentFrame.__init__(self, parent, ID, title, pos, size, style)
        MainFrameBase.__init__(self, parent, context)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateChild(self, FileName = "", style = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return DisplayFrameAui(self, DisplayPanel, FileName, style)


#-------------------------------------------------------------------------------
def OpenConfig(co, win):
#-------------------------------------------------------------------------------
    global gConfig
    gConfig = co

    for c in co.childWindows:
        win.OpenFile(c.Filename, c.WindowStyle, c.LineNumber)

    win.SetActive(co.currentWindow)


#-------------------------------------------------------------------------------
def appmain(usage, MFrame, CFGNm, title, context=None):
#-------------------------------------------------------------------------------
    """ builds the application and main window
    """

    args, opt = oss.gopt(oss.argv[1:], [], [('c', 'config')], usage)

    ## get configuration
    if opt.config is None:
        gConfig.Open(CFGNm)
    else:
        gConfig.Open(opt.config)

    children = gConfig.Load()

    app = wx.PySimpleApp()
    win = MFrame(None, -1, title, context, pos = gConfig.MainWindowPos, size = gConfig.MainWindowSize,
              style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE | cfg.Flags2Style(gConfig.MainWindowFlags))


    app.SetTopWindow(win)

    ## open configured windows
    for c in children:
        win.Open(c[0], cfg.Flags2Style(c[1]))

    win.LoadConfig(gConfig)
    return app, win


#-------------------------------------------------------------------------------
def appmain1(MFrame, co, title, context=None):
#-------------------------------------------------------------------------------
    """ builds the application and main window
    """
    global gConfig

    gConfig = co
    app = wx.PySimpleApp()
    win = MFrame(None, -1, title, context, size = co.MainWindowSize,
              style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE | co.MainWindowFlags)
    app.SetTopWindow(win)
    return app, win


#-------------------------------------------------------------------------------
def appmain2(co):
#-------------------------------------------------------------------------------
    """ builds the application and main window
    """
    global gConfig

    gConfig = co
    app = wx.PySimpleApp()
    return app


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def usage(err):
    #---------------------------------------------------------------------------
        print >> oss.stderr, """
    usage: %s
       -c, --config : specify a configuration filename
    """ % (gTitle)
        oss.exit(err)

    app, win = appmain(usage, MainFrame, DEFAULT_CONFIG_NAME, gTITLE)
    win.Show(True)
    app.MainLoop()

