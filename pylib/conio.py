#!/usr/bin/env python
"""
Library:

"""

import WConio as wc

#-------------------------------------------------------------------------------
def put(x, y, s, fgc=None, bgc=None):
#-------------------------------------------------------------------------------
    wc.gotoxy(x, y)
    if bgc:
        wc.textbackground(bgc)
    if fgc:
        wc.textcolor(fgc)
    wc.cputs(s)


#-------------------------------------------------------------------------------
def getCursorPos():
#-------------------------------------------------------------------------------
    t = wc.gettextinfo()
    return t[9], t[10]

#-------------------------------------------------------------------------------
def initialize():
#-------------------------------------------------------------------------------
    wc.clrscr()
    return WindowBase()

#-------------------------------------------------------------------------------
class WindowBase(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.origCursor = 1
        self.curCursor = 1
        self.origState = wc.gettextinfo()[4] & 0x00FF
        t = wc.gettextinfo()

        self.sx = 0
        self.sy = 0
        self.ex = t[2]
        self.ey = t[3]
        self.wd = t[2]
        self.ht = t[3]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def status(self, y, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wc.gotoxy(0, y)
        wc.movetext(0, y, self.ex, self.ey -1, 0, y+1)
        wc.gotoxy(0, y)
        wc.textbackground(7)
        wc.textcolor(15)
        wc.clreol()
        wc.cputs(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wc.textattr(self.origState)
        print

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cursor(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        old = self.curCursor
        if val is None: val = self.origCursor
        self.curCursor = val
        wc.setcursortype(val)
        return old

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getCursor(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.curCursor

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getCursorPos(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getCursorPos()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvtCoords(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return x, y

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def goto(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wc.gotoxy(x, y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def put(self, x, y, s, fgc=None, bgc=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        put(x, y, s, fgc, bgc)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clr(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wc.clrscr()


#-------------------------------------------------------------------------------
class Window(WindowBase):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, sx, sy, wd, ht, bgc=None, save=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        WindowBase.__init__(self)
        self.sx = sx
        self.sy = sy
        self.ex = sx + wd
        self.ey = sy + ht
        self.wd = wd
        self.ht = ht
        self.bgc = bgc

        if save:
            self.buffer = wc.gettext(self.sx, self.sy, self.ex, self.ey)
        else:
            self.buffer = None

        if self.bgc:
            self.clr()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.buffer:
            wc.puttext(self.sx, self.sy, self.ex, self.ey, self.buffer)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvtCoords(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.sx <= x < self.ex and self.sy <= y < self.ey:
            return self.sx + x, self.sy + y
        return None, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def goto(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wc.gotoxy(x+self.sx, y+self.sy)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def put(self, x, y, s, fgc=None, bgc=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        put(x+self.sx, y+self.sy, s, fgc, bgc)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clr(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        old = self.cursor(0)
        for x in range(self.sx, self.ex):
            for y in range(self.sy, self.ey):
                put(x, y, ' ', None, self.bgc)
        self.cursor(old)


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    return 0

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)



    res = not __test__()
    oss.exit(res)


