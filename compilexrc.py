#!/usr/bin/env python
"""
usage: compilexrc [options] <xrc_file>

options:
    -a | --app     : generate application versus dialog code
    -m | --mixin   : import mixin file, name = <xrc_file>_mixin.py

"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import time
import pylib.osscripts as oss
import pylib.xmlparse as xp

VERSION = "2.2"

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: compilexrc [options] <xrc_file>
        options:
            -d | --dialog  : generate dialog code (default)
            -a | --app     : generate application code
            -f | --frame   : generate frame code
            -w | --wizard  : generate wizard code
            -p | --panel   : generate panel code

            -m | --mixin   : import mixin file, name = <xrc_file>_mixin.py
    """
    args, opts = oss.gopt(argv[1:], [('a', 'app'), ('w', 'wizard'), ('d', 'dialog'), ('m', 'mixin'), ('p', 'panel'), ('f', 'frame')], [], __doc__ + main.__doc__)
    if not args:
        oss._usage(1, "must supply xrc file(s)")

    if opts.app:
        tflag = 'APP'
    elif opts.wizard:
        tflag = 'WIZ'
    elif opts.dialog:
        tflag = 'DLG'
    elif opts.panel:
        tflag = 'PNL'
    elif opts.frame:
        tflag = 'APP'
    else:
        tflag = None

    for infn in oss.paths(args):
        fn = infn.name
        xrc = XRCParser(infn, fn)
        xrc.compileXrc(tflag, opts.mixin)

    oss.exit(0)


#-------------------------------------------------------------------------------
class XRCParser(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, inputFileName, fn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.uid = 0
        self.uname = 0

        self.infn = inputFileName

        inf = file(inputFileName, "rU")
        self.xml = inf.read()
        self.root = xp.xmlNode(self.xml)
        inf.close()

        self.otf = file(fn + '.py', 'w')
        self.mixin = fn + '_mixin'

        self.panel = self.frame = None
        self.menuInit = ''
        self.menuFuncs = ''
        self.statusBar = ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseMenuBar(self, xnn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('    parsing menu')

        mbname = 'self.' + xnn['name'] if 'name' in xnn else 'menubar'

        funcs = []
        txt = ['\n        ## Create MenuBar\n        %s = wx.MenuBar()' % mbname]

        for xn in xnn.findChildren('object'):
            if xn['class'] != 'wxMenu':
                continue

            mname = 'self.' + xn['name'] if 'name' in xn else 'menu'
            lbl = xn.findChild('label')
            if not lbl:
                raise Exception('no label on wxMenu')

            txt.append('\n        %s = mx.Menu(self)' % mname)
            txt.append('        %s.Append(%s, "%s")' % (mbname, mname, lbl.text))

            for mi in xn.findChildren('object'):
                if mi['class'] == 'wxMenuItem':
                    lbl = mi.findChild('label')
                    if not lbl:
                        raise Exception('no label on wxMenuItem')

                    hlp = mi.findChild('help')
                    help = hlp.text if hlp else ''

                    if 'name' not in mi:
                        raise Exception('no "name" on MenuItem')

                    txt.append('        %s.AddItem("%s", self.%s, "%s")' % (mname, lbl.text, mi['name'], help))
                    funcs.append(mi['name'])

        txt.append('        self.SetMenuBar(%s)' % mbname)

        txt1 = []
        for f in funcs:
            txt1.append("""
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def %s(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("%s() called")
""" % (f, f))

        self.menuInit = '\n'.join(txt)
        self.menuFuncs = '\n'.join(txt1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseStatusBar(self, xnn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        flds = xnn.findChild('fields')
        self.statusBar = """self.sb = self.CreateStatusBar(%s)""" % flds.text

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseXrcObjects(self, xnn, iteration=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for xn in xnn.findChildren('object'):
            cls = xn['class']
            name = xn['name']

            print(('    '*iteration) + 'Class:', cls)

            typ = None
            if cls == 'wxMenuBar':
                self.parseMenuBar(xn)

            elif cls == 'wxStatusBar':
                self.parseStatusBar(xn)

            elif cls == 'wxFrame':
                typ = 'frame'
                self.frame = name
                self.parseXrcObjects(xn, iteration+1)
                aflag = 'APP'

            elif cls == 'wxDialog':
                typ = 'dialog'
                aflag = 'DLG'

            elif cls == 'wxWizard':
                typ = 'wizard'
                aflag = 'WIZ'

            elif cls == 'wxPanel':
                typ = 'panel'
                self.panel = name
                aflag = 'PNL'

            if typ:
                self.generateCode(typ, name)

        return typ, aflag, name

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def generateCode(self, typ, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ == 'frame':
            p = ('self.panel = xrc.XRCCTRL(self, "%s")' % self.panel) if self.panel else ''
            self.otf.write(FRAME_STR % (name, name, p, self.menuInit, self.menuFuncs))

        elif typ == 'dialog':
            self.otf.write(DIALOG_STR % (name, name))

        elif typ == 'wizard':
            self.otf.write(WIZARD_STR % (name, name))

        elif typ == 'panel':
            if not self.frame:
                self.otf.write(PANEL_STR % (name, name))

        else:
            raise Exception('Unknown Type: %s' % typ)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compileXrc(self, tflag, mixin=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.otf.write(INTRO_STR % (self.infn, time.ctime(), VERSION))

        if mixin:
            self.otf.write("import %s import\n\n" % self.mixin)

        typ, aflag, name = self.parseXrcObjects(self.root)
        if tflag is None:
            tflag = aflag

        self.otf.write(RESOURCE % self.xml)

        print(typ, tflag, aflag, name)
        self.otf.write(APP[tflag] % name)
        self.otf.close()


INTRO_STR = '''"""
    Autogenerated from %s on %s by compilexrc version "%s".

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import wx
import pylib.osscripts as oss
import pylib.mx as mx
import wx.xrc as xrc
'''

FRAME_STR = '''

#-------------------------------------------------------------------------------
class %s(mx.Frame, mx.XRCMixin):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PreCreate(self, pre):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ This function is called during the class's initialization.
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## Two stage creation
        pre = wx.PreFrame()
        self.PreCreate(pre)
        gXrcResource.LoadOnFrame(pre, parent, "%s")
        self.PostCreate(pre)
        self.CenterOnParent()

        %s

        %s
        %s


'''

DIALOG_STR = '''

#-------------------------------------------------------------------------------
class %s(mx.Dialog, mx.XRCMixin):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PreCreate(self, pre):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ This function is called during the class's initialization.
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent=None, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## Two stage creation
        pre = wx.PreDialog()
        self.PreCreate(pre)
        gXrcResource.LoadOnDialog(pre, parent, "%s")
        self.PostCreate(pre)
        self.CenterOnParent()


'''

PANEL_STR = '''

#-------------------------------------------------------------------------------
class %s(mx.Panel, mx.XRCMixin):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PreCreate(self, pre):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ This function is called during the class's initialization.
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent=None, *args, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## Two stage creation
        pre = wx.PrePanel()
        self.PreCreate(pre)
        gXrcResource.LoadOnPanel(pre, parent, "%s")
        self.PostCreate(pre)
        #self.CenterOnParent()


'''

WIZARD_STR = '''

#-------------------------------------------------------------------------------
class %s(mx.Wizard, mx.XRCMixin):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PreCreate(self, pre):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ This function is called during the class's initialization.
        Override it for custom setup before the window is created usually to
        set additional window styles using SetWindowStyle() and SetExtraStyle().
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## Two stage creation
        pre = mx.PreWizard()
        self.PreCreate(pre)
        gXrcResource.LoadOnObject(pre, parent, "%s", 'wxWizard')
        self.PostCreate(pre)
        self.CenterOnParent()


'''

RESOURCE = '''
gXrcResource = mx.XRCResource()
gXrcResource.loadFromStr("""\
%s""")

'''

MAIN_APP = """
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], "", "")

    app = wx.PySimpleApp(0)

    win = %s(None)
    app.SetTopWindow(win)
    win.Show()
    app.MainLoop()

if __name__ == "__main__":
    main(oss.argv)
"""

PANEL_APP = """
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], "", "")

    app = wx.PySimpleApp(0)

    win = wx.Frame(None, -1)
    panel = %s(win)
    app.SetTopWindow(win)
    v = win.Show()

    app.MainLoop()

if __name__ == "__main__":
    main(oss.argv)
"""

MAIN_DLG = """
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], "", "")

    app = wx.PySimpleApp(0)

    win = %s(None)
    app.SetTopWindow(win)
    v = win.ShowModal()
    print(v)

if __name__ == "__main__":
    main(oss.argv)
"""

MAIN_WIZARD = """
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], "", "")

    app = wx.PySimpleApp(0)

    win = %s(None)
    app.SetTopWindow(win)
    page1 = wx.xrc.XRCCTRL(win, 'Page1')
    v = win.RunWizard(page1)
    print(v)

if __name__ == "__main__":
    main(oss.argv)
"""

APP = {
    'APP' : MAIN_APP,
    'WIZ' : MAIN_WIZARD,
    'DLG' : MAIN_DLG,
    'PNL' : PANEL_APP
}


if __name__ == "__main__":
    main(oss.argv)


