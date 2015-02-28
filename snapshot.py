
from __future__ import print_function
from __future__ import division
##from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.win32 as w32
import pylib.struct2 as st

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: snapshot.py -f <path/filename>
        -f | --filename  : specify a path/filename prefix for numbered snapshots

    snapshot automatically saves images that are placed in the clipboard into
    numbered files specified by the prefix path/filename.

    """
    args, opts = oss.gopt(argv[1:], [], [('f', 'filename')], main.__doc__)

    if opts.filename is None:
        opts.usage(2, 'must provide a pth/filename')

    w = MyWindow(opts.filename)
    w32.RunLoop()

    oss.exit(0)


#-------------------------------------------------------------------------------
class MyWindow(w32.TaskBarApp):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, filename):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.filename = filename
        self.cnt = 0

        self.hdr = st.struct2([('c', 'B', 'B'), ('c', 'M', 'M'), ('b4', 'size'), ('a4', 'resv'), ('b4', 'offset')])

        super(MyWindow, self).__init__('snapshot', w32.LoadIcon(0, w32.IDI_APPLICATION), "snapshot")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def TaskBarMsg(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if lparam == w32.WM_LBUTTONDBLCLK:
            print("goodbye")
            w32.DestroyWindow(self.hwnd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def WndProcHndlr(self, hwnd, msg, wparam, lparam):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if msg == w32.WM_CREATE:
            self.NextViewer = None
            self.NextViewer = w32.SetClipboardViewer(self.hwnd)

        elif msg == w32.WM_CHANGECBCHAIN:
            print("WM_CHANGECBCHAIN")
            if wparam == self.NextViewer:
                self.NextViewer = lparam
            elif self.NextViewer:
                w32.SendMessage(self.NextViewer, msg, wparam, lparam)

        elif msg == w32.WM_DRAWCLIPBOARD:
            if self.NextViewer:
                w32.SendMessage(self.NextViewer, msg, wparam, lparam)

            w32.OpenClipboard(self.hwnd)
            try:
                try:
                    bmp = w32.GetClipboardData(w32.CF_DIB)

                    self.hdr.size = self.hdr.calcsize() + len(bmp)
                    self.hdr.offset = 0

                    fn = self.filename + str(self.cnt) + '.bmp'
                    print("Creating File:", fn)

                    with open(fn, "wb") as f:
                        f.write(self.hdr.getBin())
                        f.write(bmp)

                    self.cnt += 1

                except TypeError:
                    print("unsupported type")

                except IOError:
                    print("IOError")

            finally:
                w32.CloseClipboard()

        elif msg == w32.WM_DESTROY:
            w32.ChangeClipboardChain(self.hwnd, self.NextViewer)
            return super(MyWindow, self).WndProcHndlr(hwnd, msg, wparam, lparam)

        else:
            return super(MyWindow, self).WndProcHndlr(hwnd, msg, wparam, lparam)


if __name__ == "__main__":
    main(oss.argv)

