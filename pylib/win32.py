import win32api as api
import win32gui as gui
import win32con as con
import win32clipboard as wcb

from win32con import *
from win32api import *
from win32gui import *
from win32clipboard import *

#-------------------------------------------------------------------------------
class AWindow(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, style = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(AWindow, self).__init__()

        wc = gui.WNDCLASS()
        self.hinst = wc.hInstance = api.GetModuleHandle(None)
        wc.lpszClassName = str(self) + '1'
        wc.style = con.CS_VREDRAW | con.CS_HREDRAW;
        wc.hCursor = gui.LoadCursor(0, con.IDC_ARROW )
        wc.hbrBackground = con.COLOR_WINDOW
        wc.lpfnWndProc = self.__WndProc

        self.wclass = gui.RegisterClass(wc)
        if style is None:
            style = con.WS_OVERLAPPED | con.WS_SYSMENU

        self.hwnd = gui.CreateWindow(self.wclass, title, style, 0, 0, 100, 100, 0, 0, self.hinst, None)

        ## simulate a WM_CREATE message
        self.WndProcHndlr(self.hwnd, con.WM_CREATE, 0, 0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ShowWindow(self, c=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        gui.ShowWindow(self.hwnd, c)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def UpdateWindow(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        gui.UpdateWindow(self.hwnd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WndProcHndlr(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __WndProc(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.WndProcHndlr(hwnd, msg, wparam, lparam) is None:
            return 0

        if msg == con.WM_DESTROY:
            #gui.UnregisterClass(self.wclass, self.hinst)
            gui.PostQuitMessage(0)
            return 0

        return gui.DefWindowProc(hwnd, msg, wparam, lparam)


#-------------------------------------------------------------------------------
class TaskBarApp(AWindow):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, hicon, tip):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(TaskBarApp, self).__init__(title)

        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = self.hwnd, 0, flags, con.WM_USER+20, hicon, tip
        Shell_NotifyIcon(NIM_ADD, nid)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def TaskBarMsg(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WndProcHndlr(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if msg == con.WM_USER+20:
            self.TaskBarMsg(hwnd, msg, wparam, lparam)

        elif msg == con.WM_DESTROY:
            Shell_NotifyIcon(NIM_DELETE, (self.hwnd, 0))
            return super(TaskBarApp, self).WndProcHndlr(hwnd, msg, wparam, lparam)

        else:
            return super(TaskBarApp, self).WndProcHndlr(hwnd, msg, wparam, lparam)


RunLoop = gui.PumpMessages


#-------------------------------------------------------------------------------
def GetClipboardViewer():
#-------------------------------------------------------------------------------
    try:
        return wcb.GetClipboardViewer()
    except:
        return 0


#-------------------------------------------------------------------------------
def SetClipboardViewer(hwnd):
#-------------------------------------------------------------------------------
    try:
        return wcb.SetClipboardViewer(hwnd)
    except:
        return 0


#-------------------------------------------------------------------------------
def copyToClipboard(data, type=CF_TEXT):
#-------------------------------------------------------------------------------
    """ copy data to clipboard, default type is text
    """
    OpenClipboard()
    EmptyClipboard()
    SetClipboardData(type, data)
    CloseClipboard()



