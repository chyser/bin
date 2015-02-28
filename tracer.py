
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import sys


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    trc = Tracer()
    trc.on.append(("mindmap.py", 20))
    trc.run(args[0])
    oss.exit(0)


#-------------------------------------------------------------------------------
class Tracer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.name = ""
        self.actions = {}
        self.ffilters = {}
        self.doit = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddAction(self, t, action):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.actions[t] = action
        self.doit = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddFFilter(self, name, Print=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.ffilters[name] = Print
        self.doit = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runf(self, func, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ standard thread run method
        """
        self.name = str(func)
        sys.settrace(self.trace)
        func(*args)
        sys.settrace(None)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, prgm):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ standard thread run method
        """
        self.name = prgm
        sys.settrace(self.trace)
        execfile(prgm)
        sys.settrace(None)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def trace(self, frame, event, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ this method is called after every python byte-code is executed. this
            is the same hook used by the debugger. in this case, it provides a
            method within in the code itself to schedule VM's. In turn, the
            performance of the code run in this thread (see run method) is slow,
            but that code is the simulation code which after all is running in a
            virtual machine :-)
        """
        #self.printf(event, '    ', self.name, frame.f_code.co_filename, frame.f_lineno)

        t = (frame.f_code.co_filename, frame.f_lineno)

        if t in self.actions:
            action = self.actions[t]
            if action == 'ON':
                self.doit = True

            elif action == 'OFF':
                self.doit = False

            elif action == 'PRINT':
                self.printf(frame.f_code.co_filename, frame.f_lineno)

            elif action == 'PRINT_LOCALS':
                self.printf(frame.f_code.co_filename, frame.f_lineno, frame.f_locals)

        if frame.f_code.co_filename in self.ffilters:
            if self.ffilters[frame.f_code.co_filename]:
                self.printf(frame.f_code.co_filename, frame.f_lineno)
            else:
                pass

        elif self.doit:
            self.printf(frame.f_code.co_filename, frame.f_lineno)

        return self.trace

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printf(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for a in args:
            s.append(str(a))
        print(' '.join(s))


if __name__ == "__main__":
    main(oss.argv)

