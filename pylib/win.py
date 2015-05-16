from WConio import *

#-------------------------------------------------------------------------------
def DrawBox(x, y, w, h):
#-------------------------------------------------------------------------------

    for i in xrange(x, x+w):
        gotoxy(i, y);   putch(205)
        gotoxy(i, y+h); putch(205)

    for i in xrange(y, y+h):
        gotoxy(x, i);   putch(186)
        gotoxy(x+w, i); putch(186)

    gotoxy(x, y);     putch(201)
    gotoxy(x+w, y);   putch(187)
    gotoxy(x, y+h);   putch(200)
    gotoxy(x+w, y+h); putch(188)


#-------------------------------------------------------------------------------
class Win:
#-------------------------------------------------------------------------------
    def __init__(self, x = 0, y = 0, w = 0 , h = 0, TxClr = None, BgClr = None):
	if w == 0 or h == 0:
	    (self.x, self.y ,r,b, self.ta, na,vm, self.h,
	        self.w, self.cx, self.cy) = gettextinfo()
	    self.rootwin = 1
        else:
	    self.rootwin = 0
	    self.x = x; self.y = y
	    self.w = w; self.h = h
	    self.cx = 0; self.cy = 0;

	    if TxClr == None or BgClr == None:
		(a,a,r,b, self.ta, na,vm, a, a, a, a) = gettextinfo()
		if not TxClr: TxClr = self.ta & 0xf
		if not BgClr: BgClr = self.ta >> 4

	    self.ta = BgClr << 4 | TxClr
            textattr(self.ta)

	self.clrscr()

	if not self.rootwin:
	    DrawBox(x-1, y-1, w+1, h+1)

    def clrscr(self):
	self.cx = 0; self.cy = 0
        if self.rootwin:
	    clrscr()
        else:
	    for j in xrange(self.y, self.y + self.h):
		for i in xrange(self.x, self.x + self.w):
		    gotoxy(i,j); putch(" ")

    def gotoxy(self, x, y):
	self.cx = self.x + x; self.cy = self.y + y
        gotoxy(self.cx, self.cy)

    def printxy(self, x, y, str, Color = None):
	ta = self.ta
	if Color: textcolor(Color)
        self.gotoxy(x, y)
	cputs(str)
	self.ta = ta
	textattr(self.ta)

    def putchxy(self, x, y, str, Color = None):
	ta = self.ta
	if Color: textcolor(Color)
        self.gotoxy(x, y)
	putch(str)
	self.ta = ta
	textattr(self.ta)

    def done(self):
        if self.rootwin:
	    textmode()

    def __del__(self): done()


#-------------------------------------------------------------------------------
class PopUp(Win):
#-------------------------------------------------------------------------------
    def __init__(self, x, y, w, h, TxClr = None, BgClr = None):
	self.bsx = wherex(); self.bsy = wherey()
        self.bs = gettext(x-1, y-1, x+w, y+h)
	Win.__init__(self, x, y, w, h, TxClr, BgClr)

    def done(self):
        puttext(self.x-1, self.y-1, self.x+self.w, self.y+self.h, self.bs)
	gotoxy(self.bsx, self.bsy)


#-------------------------------------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------------------------------------
    w = Win()
    w.gotoxy(10, 10)

    x = Win(10, 10, 40, 10, RED, BLUE)
    x.printxy(3, 3, "Cool")
    x.printxy(3, 4, "Cool", WHITE)
    x.printxy(3, 5, "Cool")
    x.gotoxy(3, 3)
    getch()

    y = PopUp(15, 11, 20, 5, WHITE, GREEN)
    y.printxy(1, 1, "Popup")
    getch()
    y.done()

    getch()
    w.done()
