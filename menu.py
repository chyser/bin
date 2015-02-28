#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk
    import tkMessageBox as tkm

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    a = []
    for i in range(13):
        if i == 3:
            a.append(None)
        else:
            a.append((i, i))


    m = Menu("Select Int", quit='Done', cols=3)
    while 1:
        v = m.run(a)

        MsgError('test', 'error')

        print("sel:", v)

        if v == 2:
            d = Menu("Select Letter")
            x = d.run("abcdef")
            print('x:', x)

        elif v == 1:
            d = Dialog("Boo")
            x = d.run({'s':'boo', 'b': True, '1' : None, 'c': 3.4})
            if x:
                print(x['s'], x['b'], x['c'])

        elif v == 4:

            d = Dialog1("cool")

            tp = [
                [tk.Button(d.root, text="press")],
                [tk.Entry(d.root, text=""), tk.Entry(d.root, text="cat")],
                [tk.Button(d.root, text="ok"), tk.Button(d.root, text="cancel")],
            ]

            d.run(tp)

            d = Dialog2("Test 2")

            def tp():
                print('here')

            d.mkButton('print', tp)
            d.nextRow()

            d.mkLabel("v1")
            d.mkValue("v1", "boo", ro=True)
            d.mkLabel("v2")
            d.mkValue("v2")

            d.nextRow()
            d.mkLabel("v3")
            d.mkValue("v3")
            d.mkLabel("v4")
            d.mkValue("v4")

            ans = d.run()

            if ans:
                print(ans['v1'])
                print(ans['v2'])
                print(ans['v3'])
                print(ans['v4'])

        elif v is None:
            break

    oss.exit(0)


#------------------------------------------------------------------------------
class Menu(object):
#------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, geo=None, quit='', cols=1, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ans = None
        self.title = title
        self.geo = geo if geo else "+200+200"
        self.cols = cols
        self.quit = quit

        self.goptions = {
            'padx'   : 4,
            'pady'   : 0,
            'ipadx'  : 0,
            'ipady'  : 0,
            'sticky' : tk.E + tk.W,
        }
        self.goptions.update(kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def syncGeo(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.geo = self.root.geometry()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getGeo(self, location=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if location:
            l = self.geo.index('+')
            return self.geo[l:]
        return self.geo

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, a, func=str):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.root = tk.Tk()
        self.root.geometry(self.geo)
        self.root.title(self.title)

        la, ex = divmod(len(a), self.cols)
        if ex:
            self.cols += 1

        for idx, i in enumerate(a):
            col, row = divmod(idx, la)
            if i:
                text, command = (func(i[0]), self.__callback(i[1])) if isinstance(i, tuple) else (func(i), self.__callback(i))
                ttk.Button(self.root, text=text, command=command).grid(column=col, row=row, **self.goptions)


        if self.quit:
            ttk.Button(self.root, text=self.quit, command=self.__callback(None)).grid(column=0, columnspan=self.cols, row=la, sticky=tk.N+tk.S+tk.E+tk.W)

        self.root.mainloop()
        return self.ans

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __callback(self, ans):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def cb():
            self.ans = ans
            self.geo = self.root.geometry()
            self.root.destroy()
        return cb


#------------------------------------------------------------------------------
class BaseDialog(object):
#------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, ok='Ok', cancel='Cancel', geo=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.root = tk.Tk()
        self.root.title(title)
        self.ans = None
        self.ok = ok
        self.cancel = cancel

        self.geo = geo if geo else "+200+200"
        self.root.geometry(self.geo)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def syncGeo(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.geo = self.root.geometry()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getGeo(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.geo


#------------------------------------------------------------------------------
class Dialog(BaseDialog):
#------------------------------------------------------------------------------
    """ Simple TK dialog that takes a dictionary, uses keys as labels and
        returns either None or dictionary with new values. Uses the type of
        the values. A key beggining with '_' is readOnly.
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, ok='Ok', cancel='Cancel', geo=None, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseDialog.__init__(self, title, ok, cancel, geo)
        self.goptions = {
            'padx'   : 4,
            'pady'   : 4,
            'ipadx'  : 0,
            'ipady'  : 0,
            'sticky' : tk.E + tk.W,
        }
        self.goptions.update(kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, dct):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.dct = dct
        self.l = []

        row = 0
        for f in dct:
            if dct[f] is None:
                ttk.Separator().grid(column=0, columnspan=2, row=row, **self.goptions)
            elif isinstance(dct[f], bool):
                bv = tk.BooleanVar()
                bv.set(dct[f])
                ttk.Label(self.root, text=f).grid(column=0, row=row, **self.goptions)
                ttk.Checkbutton(self.root, variable=bv).grid(column=1, row=row, **self.goptions)
                self.l.append(self.__callback(f, bv))
            elif isinstance(dct[f], int):
                self.__mkEntry(f, tk.IntVar(), row)
            elif isinstance(dct[f], float):
                self.__mkEntry(f, tk.DoubleVar(), row)
            else:
                self.__mkEntry(f, tk.StringVar(), row)

            row += 1

        ttk.Button(self.root, text=self.ok, command=self.__finish).grid(column=0, row=row, sticky=tk.N+tk.S+tk.E+tk.W)
        ttk.Button(self.root, text=self.cancel, command=self.root.destroy).grid(column=1, row=row, sticky=tk.N+tk.S+tk.E+tk.W)

        self.root.mainloop()
        return self.ans

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def kill(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ans = v
        self.root.destroy()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __mkEntry(self, f, sv, row):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        txt, readonly = (f[1:], True) if f[0] == '_' else (f, False)

        ttk.Label(self.root, text=txt).grid(column=0, row=row, **self.goptions)
        sv.set(self.dct[f])

        width = len(str(self.dct[f]))
        state = 'readonly' if readonly else 'normal'
        tk.Entry(self.root, width=width, textvariable=sv, relief=tk.SUNKEN, state=state).grid(column=1, row=row, **self.goptions)

        self.l.append(self.__callback(f, sv))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __finish(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in self.l:
            i()
        self.ans = self.dct
        self.syncGeo()
        self.root.destroy()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __callback(self, f, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def cb():
            self.dct[f] = v.get()
        return cb


#------------------------------------------------------------------------------
class Dialog1(BaseDialog):
#------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, tp):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        row = 0

        for r in tp:
            col = 0
            for c in r:
                c.grid(column=col, row=row)
                col += 1
            row += 1

        self.root.mainloop()


#------------------------------------------------------------------------------
class Dialog2(BaseDialog):
#------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, ok="Ok", cancel="Cancel", geo=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseDialog.__init__(self, title, ok, cancel, geo)
        self.row = self.col = self.maxc = 0
        self.dct = {}
        self.l = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextRow(self, c=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.row += c
        if self.col > self.maxc:
            self.maxc = self.col

        self.col = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextCol(self, c=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.col += c

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mkLabel(self, f):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ttk.Label(self.root, text=f).grid(column=self.col, row=self.row, padx=4, pady=4)
        self.col += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mkValue(self, name, default="", ro=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sv = tk.StringVar()
        sv.set(str(default))

        state = 'readonly' if ro else 'normal'
        tk.Entry(self.root, textvariable=sv, relief=tk.SUNKEN, state=state).grid(column=self.col, row=self.row, padx=4, pady=4)

        self.l.append(self.__callback(name, sv))
        self.col += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mkButton(self, f, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ttk.Button(self.root, text=f, command=cmd).grid(column=self.col, row=self.row, padx=4, pady=4)
        self.col += 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.nextRow()
        ok, cancel = (0, self.maxc - 1) if self.maxc % 2 == 0 else (1, self.maxc - 2)

        if self.ok:
            ttk.Button(self.root, text=self.ok, command=self.__finish).grid(column=ok, row=self.row, sticky=tk.N+tk.S+tk.E+tk.W)

        if self.cancel:
            ttk.Button(self.root, text=self.cancel, command=self.root.destroy).grid(column=cancel, row=self.row, sticky=tk.N+tk.S+tk.E+tk.W)

        self.root.mainloop()
        return self.ans

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __finish(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in self.l:
            i()
        self.ans = self.dct
        self.syncGeo()
        self.root.destroy()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __callback(self, f, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def cb():
            self.dct[f] = v.get()
        return cb


#-------------------------------------------------------------------------------
def MsgError(title, msg):
#-------------------------------------------------------------------------------
    root = tk.Tk()
    root.withdraw()
    a = tkm.showerror(title, msg)
    root.destroy()
    return a


#-------------------------------------------------------------------------------
def MsgWarning(title, msg):
#-------------------------------------------------------------------------------
    root = tk.Tk()
    root.withdraw()
    a = tkm.showwarning(title, msg)
    root.destroy()
    return a


#-------------------------------------------------------------------------------
def MsgInfo(title, msg):
#-------------------------------------------------------------------------------
    root = tk.Tk()
    root.withdraw()
    a = tkm.showInfo(title, msg)
    root.destroy()
    return a




if __name__ == "__main__":
    main(oss.argv)
