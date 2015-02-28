#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import threading

#-------------------------------------------------------------------------------
class LatestMessage(object):
#-------------------------------------------------------------------------------
    """ Used when a worker thread is told to do lengthy things to a shared
        resource (say a gui window) and only the last (whenever that may arrive)
        one matters. Like a 1 deep queue which only contains the last added
        entry.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, msg=None, lock=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ 'msg' is an initial value. 'lock' is an optional lock to be used else
            a new one is allocated.
        """
        object.__init__(self)
        self.stateLock = threading.Condition() if lock is None else lock
        self.msg = msg

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setMsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ place the message and ensure the worker thread is notified is waiting
        """
        self.stateLock.acquire()
        try:
            self.msg = msg
        finally:
            self.stateLock.notify()
            self.stateLock.release()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getMsg(self, timeOut=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the latest message else wait for one
        """
        self.stateLock.acquire()
        while self.msg is None:
            self.stateLock.wait(timeOut)
        msg = self.msg
        self.msg = None
        self.stateLock.release()

        return msg


#-------------------------------------------------------------------------------
class LastMessageWorkerThread(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, target, threadName=None, args=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.lMsg = LatestMessage()
        args = tuple() if args is None else args
        self.thread = threading.Thread(None, target=target, name=threadName, args=args)
        self.thread.daemon = True

        LastMessageWorkerThread.start = self.thread.start
        LastMessageWorkerThread.setMsg = self.lMsg.setMsg
        LastMessageWorkerThread.getMsg = self.lMsg.getMsg


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import time
    import random

    import pylib.tester as tester

    class TestObj(object):
        def __init__(self):
            self.lmwt = None
            self.count = 0
            self.seen = set()

    def work(arg):
        while 1:
            delay = random.randint(0, 5)
            msg = arg.lmwt.getMsg()
            tester.Assert(msg not in arg.seen)
            arg.seen.add(msg)

            if verbose:
                print(msg, 'delaying: ', delay)

            arg.count += 1
            time.sleep(delay)

    arg = TestObj()
    lmwt = LastMessageWorkerThread(work, 'work', (arg,))
    arg.lmwt = lmwt

    lmwt.start()

    for i in range(100):
        lmwt.setMsg(i)
        time.sleep(0.5)

    time.sleep(10)

    if verbose:
        print('Count:', arg.count)

    tester.Assert(arg.count > 8)
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)
    res = __test__(verbose=True)
    print('results:', not res)
    oss.exit(res)


