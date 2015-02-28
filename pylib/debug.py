import sys
import traceback
import time

if __debug__:
    _DEBUG_LVL = 1

    _OUTPUT_FILE = sys.stderr

    _FORMAT = "%s "
    _END_LINE = "\n"

    #-------------------------------------------------------------------------------
    def SetDebugVal(tag, val=None):
    #-------------------------------------------------------------------------------
        if tag == 'DebugLevel':
            global _DEBUG_LVL
            _DEBUG_LVL = val

        elif tag == 'OutputFile':
            OFile = val
            if not isinstance(OFile, file):
                OFile = file(OFile, 'w')

            global _OUTPUT_FILE
            _OUTPUT_FILE = OFile

        elif tag == 'Format':
            global _FORMAT
            _FORMAT = val

        elif tag == 'EndLine':
            global _END_LINE
            _END_LINE = val

        else:
            return False
        return True

    #-------------------------------------------------------------------------------
    def SetDebugLevel(dl):
    #-------------------------------------------------------------------------------
        global _DEBUG_LVL
        _DEBUG_LVL = dl
        return True

    #-------------------------------------------------------------------------------
    def SetOutputFile(OFile):
    #-------------------------------------------------------------------------------
        if not isinstance(OFile, file):
            OFile = file(OFile, 'w')

        global _OUTPUT_FILE
        _OUTPUT_FILE = OFile
        return True

    #-------------------------------------------------------------------------------
    def doPrint(arg):
    #-------------------------------------------------------------------------------
        if _DEBUG_LVL == 0: return None
        if not isinstance(arg[0], int): return arg
        if arg[0] <= _DEBUG_LVL: return arg[1:]
        return None

    #-------------------------------------------------------------------------------
    def DbgPrint(*arg):
    #-------------------------------------------------------------------------------
        frm = sys._getframe(1)
        a = doPrint(arg)
        if a is not None:
            dp(['\n' + time.ctime() + " -- [%s:%d] " % (frm.f_code.co_filename, frm.f_lineno)])
            dp(a)
        return True

    #-------------------------------------------------------------------------------
    def DbgPrint1(*arg):
    #-------------------------------------------------------------------------------
        a = doPrint(arg)
        if a is not None:
            dp(a)
        return True

    #-------------------------------------------------------------------------------
    def DbgPrintObj(*arg):
    #-------------------------------------------------------------------------------
        a = doPrint(arg)
        if a is not None:
            a = a[0]
            lst = []
            map(lambda i: lst.append("     %s = '%s'" % (i, str(getattr(a, i)))), [i for i in dir(a) if i not in dir(a.__class__)])
            dp(("\nClass: " + str(a.__class__),))
            dp(lst)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DbgPrintNestedDict(d, cnt = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for k,y in d.items():
            if isinstance(y, dict):
                DbgPrintNestedDict(y, cnt + 1)
            else:
                print >> _OUTPUT_FILE, "    "*cnt + k, y


    #-------------------------------------------------------------------------------
    def log():
    #-------------------------------------------------------------------------------
        frm = sys._getframe(1)
        return dp(("[%s:%d]" % (frm.f_code.co_filename, frm.f_lineno),))

    #-------------------------------------------------------------------------------
    def caller():
    #-------------------------------------------------------------------------------
        frm = sys._getframe(2)
        return dp(("[%s:%d]" % (frm.f_code.co_filename, frm.f_lineno),))

#-------------------------------------------------------------------------------
def delay(sec):
#-------------------------------------------------------------------------------
    time.sleep(sec)

#-------------------------------------------------------------------------------
def dp(arg):
#-------------------------------------------------------------------------------
    """ arg is a sequence
    """
    l = "".join([_FORMAT % str(a) for a in arg]) + _END_LINE
    if _OUTPUT_FILE is not sys.stderr:
        print >> sys.stderr, l,
    print >> _OUTPUT_FILE, l,
    _OUTPUT_FILE.flush()
    return True


#-------------------------------------------------------------------------------
def PrintObj(obj):
#-------------------------------------------------------------------------------
    a = obj
    if a is not None:
        lst = []
        map(lambda i: lst.append("     %s = '%s'" % (i, str(getattr(a, i)))), [i for i in dir(a) if i not in dir(a.__class__)])
        dp(("\nClass: " + str(a.__class__),))
        dp(lst)
    return True

#-------------------------------------------------------------------------------
def trace(lvl = 0, text=""):
#-------------------------------------------------------------------------------
    stack = traceback.extract_stack()[-(2 + lvl):][0]
    return dict(text=text, func=stack[2], line=stack[1], file=stack[0])

#-------------------------------------------------------------------------------
def ptrace(lvl=0, text=""):
#-------------------------------------------------------------------------------
    d = trace(lvl, text)
    dp((str(d),))
    return True

#-------------------------------------------------------------------------------
def pAssert(val, msg=""):
#-------------------------------------------------------------------------------
    if not val:
        ptrace(3, msg)
    return True


#-------------------------------------------------------------------------------
def printAssert(val, msg):
#-------------------------------------------------------------------------------
    if not val:
        dp((msg,))
    return True

#-------------------------------------------------------------------------------
def GetTraceback():
#-------------------------------------------------------------------------------
    """ wrapper to get a trace back
    """
    return traceback.format_exc()

#-------------------------------------------------------------------------------
def GetTracebackInfo():
#-------------------------------------------------------------------------------
    """ get a traceback at the point this function is called w/o disruption
    """
    class GetTracebackInfoException(Exception): pass
    try:
        raise GetTracebackInfoException('Here')
    except GetTracebackInfoException:
        return traceback.format_exc()
    return '\n'.join(traceback.format_stack()[:-1])

#-------------------------------------------------------------------------------
def showStackTrace(start=0):
#-------------------------------------------------------------------------------
    return '\n'.join(traceback.format_stack()[start:-1])

#-------------------------------------------------------------------------------
class ReloadModules(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, modlist):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import thread

        super(ReloadModules, self).__init__()
        self.modules = {}

        print "\npylib.debug.ReloadModules is monitoring:"
        for i in modlist:
            print "   ", i
            if i in sys.modules:
                mod = sys.modules[i]
                if mod.__file__.endswith('.py'):
                    fl = mod.__file__
                else:
                    fl = mod.__file__[:-1]

                self.modules[i] = (fl, mod)

        thread.start_new_thread(self.run, (1,))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import pylib.osscripts as oss
        import time

        while 1:
            time.sleep(2)
            for i, fl_mod in self.modules.items():
                fl, mod = fl_mod
                if oss.newerthan(fl, fl + 'c'):
                    DbgPrint("reloading module:", i)
                    reload(mod)










#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    assert DbgPrint(1, "1 - see")
    assert SetDebugLevel(2)
    assert DbgPrint(3, "3 - don't see")
    assert SetDebugLevel(3)
    assert DbgPrint(3, "3 - see")

    #---------------------------------------------------------------------------
    class Cool(object):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, a, b, c):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            super(Cool, self).__init__()
            self.a = a; self.b = b; self.c = c
            self.j = None

    c = Cool(5,6,7)
    assert DbgPrintObj(c)
    assert log()
    assert DbgPrintObj(4, c)
    assert log()
    assert DbgPrint("good")


    print sys.modules
    re = ReloadModules(['time', 'traceback'])

