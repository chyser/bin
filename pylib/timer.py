#!/usr/bin/env python
"""
Library:

"""

import thread
import time


#-------------------------------------------------------------------------------
class StopWatch(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.startTime = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def start(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.startTime = time.time()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def stop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.stopTime = time.time()
        return self.stopTime - self.startTime

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class Timer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
def setTimer(secs, func, args=None, kwds=None):
#-------------------------------------------------------------------------------
    def delay(arg=None):
        time.sleep(secs)
        args1 = tuple() if args is None else args
        kwds1 = dict() if kwds is None else kwds

        func(*args1, **kwds1)

    thread.start_new_thread(delay, (None,))

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

    def usage(rc, errmsg=""):
        print >> oss.stderr, __doc__
        if errmsg:
            print >> oss.stderr, """
Error:
""" + str(errmsg)
        oss.exit(rc)

    args, opts = oss.gopt(oss.argv[1:], [], [], usage)



    res += __test__()
    oss.exit(res)


