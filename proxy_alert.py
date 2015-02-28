#!/usr/bin/env python
import gobject
import gtk
from _winreg import *

class ProxyNotifier:
    def __init__(self):
        self.trayIcon = gtk.StatusIcon()
        self.updateIcon()

        #set callback on right click to on_right_click
        self.trayIcon.connect('popup-menu', self.on_right_click)
        gobject.timeout_add(1000, self.checkStatus)

    def isProxyEnabled(self):

        aReg = ConnectRegistry(None,HKEY_CURRENT_USER)

        aKey = OpenKey(aReg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        subCount, valueCount, lastModified = QueryInfoKey(aKey)

        for i in range(valueCount):
            try:
                n,v,t = EnumValue(aKey,i)
                if n == 'ProxyEnable':
                    return v and True or False
            except EnvironmentError:
                break
        CloseKey(aKey)

    def invertProxyEnableState(self):
        aReg = ConnectRegistry(None,HKEY_CURRENT_USER)
        aKey = OpenKey(aReg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, KEY_WRITE)
        if self.isProxyEnabled() :
            val = 0
        else:
            val = 1
        try:
            SetValueEx(aKey,"ProxyEnable",0, REG_DWORD, val)
        except EnvironmentError:
            print "Encountered problems writing into the Registry..."
        CloseKey(aKey)

    def updateIcon(self):
        if self.isProxyEnabled():
            icon=gtk.STOCK_YES
        else:
            icon=gtk.STOCK_NO
        self.trayIcon.set_from_stock(icon)

    def checkStatus(self):
        self.updateIcon()
        return True


    def on_right_click(self, data, event_button, event_time):
        self.invertProxyEnableState()
        self.updateIcon()


if __name__ == '__main__':
    proxyNotifier = ProxyNotifier()
