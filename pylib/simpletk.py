#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from Tkinter import *
import tkSimpleDialog

import tkMessageBox


__gMsgFuncs = {
    'info'  : tkMessageBox.showinfo,
    'warn'  : tkMessageBox.showwarning,
    'err'   : tkMessageBox.showerror,
    'ques'  : tkMessageBox.askquestion,
    'ok'    : tkMessageBox.askokcancel,
    'yes'   : tkMessageBox.askyesno,
    'retry' : tkMessageBox.askretrycancel,
}

#-------------------------------------------------------------------------------
def MsgBox(title, msg, typ, **options):
#-------------------------------------------------------------------------------
    if options:
        return __gMsgFuncs[typ](title, msg, **options)
    return __gMsgFuncs[typ](title, msg)


#-------------------------------------------------------------------------------
class SimpleTK(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title, maxSize=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.root = Tk()
        self.root.title(title)
        if maxSize:
            self.root.maxsize(*maxSize)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def app(self, func=None, args=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if func:
            func(self.root, args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, func=None, args=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if func:
            self.app(func, args)
        else:
            self.app()
        self.root.mainloop()


#-------------------------------------------------------------------------------
class Dialog(Toplevel):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, title=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None
        self.retCode = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)
        return retCode

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def body(self, master):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def buttonbox(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("&lt;Return>", self.ok)
        self.bind("&lt;Escape>", self.cancel)

        box.pack()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ok(self, event=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
        self.retCode = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cancel(self, event=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.parent.focus_set()
        self.destroy()
        self.retCode = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def validate(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 1 # override

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def apply(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass # override


#-------------------------------------------------------------------------------
class FieldsDialog(tkSimpleDialog.Dialog):
#-------------------------------------------------------------------------------
    """ Creates a dialog that displaying and editing a list of fields.

        fields = [entry1, entry2, ...]
        entryN:
            (label, field)
            (label, field, initial_value)
            (label, field, initial_value, validation_function)

        first field receives initial focus
        values are obtained by FieldsDialog[field]
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, fields):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.fields = fields
        self.results = {}
        tkSimpleDialog.Dialog.__init__(self, parent)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, n):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.results[n]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def body(self, master):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.v = {}
        row = 0

        first = None
        for field in self.fields:
            l = len(field)
            if l == 4:
                lbl, name, iv, func = field
            elif l == 3:
                lbl, name, iv = field
                func = None
            else:
                lbl, name =  field
                iv = '';  func = None

            Label(master, text=lbl).grid(row=row, column=0, sticky=W)

            e = Entry(master)
            e.insert(0, str(iv))
            self.v[name] = (e, func)
            e.grid(row=row, column=1)
            if first is None:
                first = e
            row += 1

        return first

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def validate(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for name, d in self.v.items():
            field, func = d
            if func:
                try:
                    self.results[name] = func(field.get())
                except (ValueError, TypeError):
                    MsgBox('Field Entry Error', "Field: '%s' should be of type '%s'" % (name, func.__name__), 'err')
                    return

            else:
                self.results[name] = field.get()
        return 1


#-------------------------------------------------------------------------------
class ListBox(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        frame = Frame(parent)
        sb = Scrollbar(frame, orient=VERTICAL)
        self.lb = Listbox(frame, yscrollcomand=sb.set)
        sb.config(command.listbox.view)
        sb.pack(side=RIGHT, file=Y)
        self.lb.pack(side=LEFT, file=BOTH, expand=1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def insert(self, val, idx=END):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sb.insert(idx, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.lb.curselection()


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester

    def doit(root, args=None):
        w = Label(root, text="Hello World")
        w.pack()

        d = FieldsDialog(root, [('Sara:', 'sara'), ('Boo', 'boo', 3, int)])
        print(d.results)

        lb = ListBox(root)
        lb.insert('sara')
        lb.insert('boo')


    #---------------------------------------------------------------------------
    class Test(SimpleTK):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def app(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            doit(self.root)


    #Test('My Test App').run()

    SimpleTK('My Test App').run(doit)



    return 0


#-------------------------------------------------------------------------------
class Record(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        self.LBL_name
        self.name
        self.FUNC_name




#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

