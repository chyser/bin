#!/usr/local/bin/python
"""
This module fires off a bunch of threads and then can wait for their conclusion
"""
import threading
import pylib.debug as dbg

assert dbg.SetDebugLevel(0)

#-------------------------------------------------------------------------------
class TraceLock(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, DbgPrint, name=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(TraceLock, self).__init__()
        self.DbgPrint = DbgPrint
        self.name = name or str(id(self))
        self.funcFilter = []
        self.lock = threading.Lock()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printStr(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = dbg.trace(2)
        ct = threading.currentThread()
        fl = oss.basename(d["file"])
        if d["func"] not in self.funcFilter:
            self.DbgPrint("lock(%s) %s: Thread: '%s' File: '%s', Line: '%s', Func: '%s'" % (self.name, s, ct.getName(), fl, d["line"], d["func"]))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def acquire(self, blocking=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.printStr("acquire(%d)" % blocking)
        self.lock.acquire(blocking)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def release(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.printStr("release(%d)" % blocking)
        self.lock.release()

#-------------------------------------------------------------------------------
class MThread(threading.Thread):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, id, target, name, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(MThread, self).__init__(None, target, name, args)
        self.res = None
        self.id = id
        self.target = target
        self.name = name
        self.args = args

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(MThread, self).__init__(None, self.target, self.name, self.args)
        self.res = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	assert dbg.DbgPrint("Started: %d" % self.id)
        self.res = self.target(*self.args)
	assert dbg.DbgPrint("Completed: %d" % self.id)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "Name: %s, id: %d, target: %s args: %s" % (self.name, self.id, self.target, self.args)


#-------------------------------------------------------------------------------
class MWorkThreadQueue(object):
#-------------------------------------------------------------------------------
    """ a queue of worker threads
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, isDaemon=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(MWorkThreadQueue, self).__init__()
        self.lst = []
        self.jobNum = 0
        self.exc = {}
	self.isDaemon = isDaemon
        self.__started = False

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for l in self.lst:
            l.Reset()
            self.exc[l.id] = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddJob(self, Func, Args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add 'Func(Args)' to the list of jobs to be executed returning an id
        """

        _id = self.jobNum
        self.exc[_id] = None

        self.jobNum += 1

        t = MThread(_id, target = Func, name = Args[0], args = Args)
	t.setDaemon(self.isDaemon)
        self.lst.append(t)
        return _id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def StartJobs(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ start the list of jobs
        """

        if self.__started: self.Reset()
        for l in self.lst:
            l.start()
        self.__started = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Wait(self, timeout=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ wait for the list of jobs to complete
        """

        if not self.__started: return False
        for l in self.lst:
	    assert dbg.DbgPrint("waiting: %d" % l.id, l)
            l.join(timeout)
            self.exc[l.id] = l.res
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def GetRes(self, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the result of the specifed job
        """

        return self.exc[id]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def IsAllRes(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ determine if all jobs completed with results == 'val'
        """

        res = True
        for l in self.lst:
            res = res and (l.res == val)
        return res

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return '\n'.join([str(l) for l in self.lst])



#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import random
    import time

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Test(Name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in range(random.randint(5, 30)):
            print "Thread:", Name
            time.sleep(1)
        return "%s Finished" % Name


    wq = MWorkThreadQueue()

    l = [wq.AddJob(Test, ("Aidan",))]
    l.append(wq.AddJob(Test, ("Connor",)))
    l.append(wq.AddJob(Test, ("Boo",)))

    wq.StartJobs()
    wq.Wait()

    for i in l:
        print i, wq.GetRes(i)

    wq.StartJobs()
    wq.Wait()

    for i in l:
        print i, wq.GetRes(i)


