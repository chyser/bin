"""

Usage:

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


#import Queue
#import threading

import processing as pc


#-------------------------------------------------------------------------------
class BaseThreadPool(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, numThreads):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.numth = numThreads
        self.jid = 0
        self.results = {}
        self.q = pc.Queue()
        self.cnt = 0

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
        return vals

#-------------------------------------------------------------------------------
class ThreadPool(BaseThreadPool):
#-------------------------------------------------------------------------------
    """ class for managing a bunch of worker threads
    """
    class iter:
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
        super(ThreadPool, self).__init__(numThreads)

        self.out = pc.Queue()
        for i in range(numThreads):
            self.__startWorker()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getSome(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.iter(self, self.cnt)

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
    def __startWorker(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.t = pc.Process(target=self._worker)
        self.t.setDaemon(True)
        self.t.start()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _worker(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            jid, func, args = self.q.get()
            res = func(*args)
            self.out.put((jid, res))


#-------------------------------------------------------------------------------
class SingleThreadPool(BaseThreadPool):
#-------------------------------------------------------------------------------
    """ Imitates ThreadPool without the threads
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def wait(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ wait for all jobs to complete
        """
        while not self.q.empty():
            jid, func, args = self.q.get()
            res = func(*args)
            self.results[jid] = res
            self.q.task_done()


import time
def tf(num):
    n = num
    for i in range(100000):
        time.sleep(0)
        num += 1
        #if i % 5000 == 0:
        #    print n
    return num

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------

    tp = ThreadPool(3)

    tp.addJob(tf, 1)
    tp.addJob(tf, 20)
    tp.addJob(tf, 300)
    tp.addJob(tf, 4000)
    tp.addJob(tf, 50000)
    tp.addJob(tf, 600000)
    tp.addJob(tf, 7000000)
    tp.addJob(tf, 7000000)
    tp.addJob(tf, 7000000)

    #tp.wait()

    for v in tp.getSome():
        print v


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import sys
    main(sys.argv)

