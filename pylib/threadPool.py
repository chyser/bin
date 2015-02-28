#!/usr/bin/env python
"""
Library: Thread and Process Pools


THREAD_POOL_SIZE = 16
tp = pool.ThreadPool(THREAD_POOL_SIZE)

def doWithFile(f, rx, val):
    results = []
    return results

for f in files:
    tp.addJob(doWithFile, f, rx, val)

tp.wait()

res = []
for r in tp.getAll():
    res.extend(r)

"""


import Queue
import threading
try:
    import multiprocessing as pc
except ImportError:
    try:
        import processing as pc
    except ImportError:
        pass

#-------------------------------------------------------------------------------
class BasePool(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class iter:
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, tp, cnt):
            self.tp = tp
            self.cnt = cnt

        def __iter__(self):
            return self

        def next(self):
            if self.cnt <= 0:
                raise StopIteration

            jid, res = self.tp.out.get()
            self.cnt -= 1
            return res

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, numThreads):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.numth = numThreads
        self.q = None
        self.out = None

        self.jid = self.cnt = 0
        self.results = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addJob(self, func, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ adds a function and args to list of jobs to be executed returning
            the job id
        """
        jid = self.jid
        self.q.put((jid, func, args))
        self.jid += 1
        self.cnt += 1
        return jid

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getSome(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        i = self.iter(self, self.cnt)
        self.cnt = 0
        return i

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getRes(self, jid):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the results of a particular job
        """
        res = self.results[jid]
        del self.results[jid]
        return res

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getAll(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the results of all jobs in list
        """
        vals = self.results.values()
        self.results = {}
        self.cnt = 0
        return vals

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def wait(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ wait for all jobs to complete
        """
        while self.cnt > 0:
            jid, res = self.out.get()
            self.results[jid] = res
            self.cnt -= 1

        self.cnt = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _worker(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            jid, func, args = self.q.get()
            res = func(*args)
            self.out.put((jid, res))


#-------------------------------------------------------------------------------
class ThreadPool(BasePool):
#-------------------------------------------------------------------------------
    """ class for managing a bunch of worker threads
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, numThreads):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ThreadPool, self).__init__(numThreads)
        self.out = Queue.Queue()
        self.q = Queue.Queue()

        for i in range(numThreads):
            self.__startWorker()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __startWorker(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = threading.Thread(target=self._worker)
        t.daemon = True
        t.start()


#-------------------------------------------------------------------------------
class ProcessPool(BasePool):
#-------------------------------------------------------------------------------
    """ class for managing a bunch of worker processes
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, numThreads):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ProcessPool, self).__init__(numThreads)

        self.q = pc.Queue()
        self.out = pc.Queue()

        for i in range(numThreads):
            self.__startWorker()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __startWorker(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = pc.Process(target=self._worker)
        t.daemon = True
        t.start()


#-------------------------------------------------------------------------------
class SingleThreadPool(BasePool):
#-------------------------------------------------------------------------------
    """ Imitates ThreadPool without the threads
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, nt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BasePool.__init__(self, nt)
        self.q = Queue.Queue()
        self.out = Queue.Queue()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ wait for all jobs to complete
        """
        while not self.q.empty():
            jid, func, args = self.q.get()
            self.out.put((jid, func(*args)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getSome(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__run()
        return BasePool.getSome(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def wait(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__run()
        return BasePool.wait(self)



import time
def __tf(num):
    n = num
    for i in range(100000):
        time.sleep(0)
        num += 1
    return num

#-------------------------------------------------------------------------------
def __test(tp, all, verbose):
#-------------------------------------------------------------------------------
    tp.addJob(__tf, 1)
    tp.addJob(__tf, 20)
    tp.addJob(__tf, 300)
    tp.addJob(__tf, 4000)
    tp.addJob(__tf, 50000)
    tp.addJob(__tf, 600000)
    tp.addJob(__tf, 7000000)

    ans = set([100001, 100020, 100300, 104000, 150000, 700000, 7100000])

    if all:
        tp.wait()
        for v in tp.getAll():
            ans.remove(v)
            if verbose:
                print'@1',  v
    else:
        for v in tp.getSome():
            ans.remove(v)
            if verbose:
                print '@0', v

    if verbose:
        print

    return len(ans) == 0

#-------------------------------------------------------------------------------
def __test__(verbose=None):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    tp = SingleThreadPool(3)
    tester.Assert(__test(tp, 0, verbose))
    tester.Assert(__test(tp, 1, verbose))

    tp = ThreadPool(3)
    tester.Assert(__test(tp, 0, verbose))
    tester.Assert(__test(tp, 1, verbose))

    tp = ProcessPool(3)
    tester.Assert(__test(tp, 0, verbose))
    tester.Assert(__test(tp, 1, verbose))

    return 1

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

    args, opts = oss.gopt(oss.argv[1:], [('v', 'verbose')], [], usage)

    res = not __test__(opts.verbose)
    oss.exit(res)



