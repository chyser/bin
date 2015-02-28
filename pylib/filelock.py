#!/usr/bin/env python
"""
Library:

"""

import sys
import time
import osscripts as oss

#-------------------------------------------------------------------------------
class FileLockWin(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lock(self, attr='r+'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.f = open(self.fname, attr)

        for _ in range(103):
            try:
                msvcrt.locking(self.f.fileno(), msvcrt.LK_LOCK, sys.maxint)
                return True
            except IOError:
                return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unlock(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.f is None:
            return

        self.f.flush()
        for _ in range(103):
            try:
                msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, sys.maxint)
                self.f.close()
                return
            except IOError:
                pass


#-------------------------------------------------------------------------------
class FileLockUnix(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def lock(self, attr='r+'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.f = open(self.fname, attr)
        try:
            fcntl.lockf(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)
	    self.f.read()
            return True
        except IOError:
	    pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unlock(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.f is None:
            return

        self.f.flush()
        fcntl.lockf(self.f, fcntl.LOCK_UN)
        self.f.close()


if sys.platform == 'win32':
    import msvcrt
    FileLockBase = FileLockWin
else:
    import fcntl
    FileLockBase = FileLockUnix


#-------------------------------------------------------------------------------
class FileLock(FileLockBase):
#-------------------------------------------------------------------------------
    """ represents a lock on a filesystem file
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName, val="0"):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        FileLockBase.__init__(self)

        self.fname = FileName
        if not oss.exists(FileName):
            otf = open(FileName, 'w')
            otf.write(val)
            otf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def exchange(self, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the prior value or None if couldn't get the lock while putting
            the new value 'val' into the file
        """
        if self.lock():
            self.f.seek(0, 0)
            nv = self.f.read()
            self.f.seek(0, 0)
            self.f.truncate(0)
            self.f.write(val)
            self.unlock()
            return nv

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, val=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ returns the current value and increments the value in the file
        """
        for _ in range(103):
            if self.lock():
                self.f.seek(0, 0)
                nv = self.f.read()
                try:
                    nv = int(nv)
                    self.f.seek(0, 0)
                    self.f.truncate(0)
                    self.f.write(str(nv + val))
                    self.unlock()
                    return nv
                except ValueError:
                    self.unlock()
                    return None
            else:
                time.sleep(0.01)


if __debug__:
    import threadpool as pool

    _LOCKFILE = '/tmp/locktest.lck'

    _NUM_PROCESSES = 531
    _THREAD_POOL_SIZE = 16

    def _doSomething(id, *args):
        fl = FileLock(_LOCKFILE)
        val = fl.add(1)
        return ["id: '%d' done" % id]

    def _test_increment():
        tp = pool.ProcessPool(_THREAD_POOL_SIZE)

        oss.echo(0, _LOCKFILE)

        for id in range(_NUM_PROCESSES):
            tp.addJob(_doSomething, id)

        tp.wait()

        res = []
        for r in tp.getAll():
            res.extend(r)

        val = oss.readf(_LOCKFILE, 0)
        return int(val) == _NUM_PROCESSES

    def _doExchange(id):
        fl = FileLock(_LOCKFILE)
        val = fl.exchange('taken')
        if val == 'init':
            return ["id: '%d' took lock" % id]
        return []

    def _test_exchange():
        tp = pool.ProcessPool(_THREAD_POOL_SIZE)

        oss.echo('init', _LOCKFILE, nl=False)

        for id in range(_NUM_PROCESSES):
            tp.addJob(_doExchange, id)

        tp.wait()

        res = []
        for r in tp.getAll():
            res.extend(r)

        return len(res) == 1


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import tester

    if __debug__:
        tester.Assert(_test_increment())
        tester.Assert(_test_exchange())

    return 0


if __name__ == "__main__":
    import osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)


    res = not __test__()
    oss.exit(res)



