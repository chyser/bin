#!/usr/bin/env python
"""
usage:

"""

import thread
import threading
import time

import win32serviceutil
import win32service
import win32event

import pylib.osscripts as oss
import pylib.config as cfg

REVISION = "1.1"

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

STANDALONE_DEBUGGING = 0

#-------------------------------------------------------------------------------
class WinService(win32serviceutil.ServiceFramework):
#-------------------------------------------------------------------------------
    _svc_name_ = "WinService"
    _svc_display_name_ = 'WinService'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not STANDALONE_DEBUGGING:
            win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.WaitInterval = win32event.INFINITE

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def LogInfoEvent(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import servicemanager as sm
        sm.LogInfoMsg('INFO:' + msg)
        self.logmsg('INFO:' + msg)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logmsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass ## override if additional logging is used

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PeriodicCheck(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.WaitInterval

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcStop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import servicemanager as sm
        sm.LogMsg(sm.EVENTLOG_INFORMATION_TYPE, sm.PYS_SERVICE_STOPPED, (self._svc_name_, ''))
        self.logmsg("$$ %s STOPPING" % self._svc_name_)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcDoRun(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import servicemanager as sm
        sm.LogMsg(sm.EVENTLOG_INFORMATION_TYPE, sm.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.logmsg("$$ %s STARTED" % self._svc_name_)

        while True:
            r = win32event.WaitForSingleObject(self.hWaitStop, self.WaitInterval)
            if r == win32event.WAIT_TIMEOUT:
                self.WaitInterval = self.PeriodicCheck()
            else:
                break

#-------------------------------------------------------------------------------
class CfgItem(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(CfgItem, self).__init__()
        self.uid = 0
        self.TaskName = ""
        self.ExeName = ""
        self.FreqInMinutes = 0
        self.TimeSpec = ""
        self.DateSpec = ""

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.TimeSpec + " " + self.ExeName + " " + str(self.FreqInMinutes)


#-------------------------------------------------------------------------------
class CfgObj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, c = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(CfgObj, self).__init__()
        self.cfgs = []

        if c is not None:
            self.cfgs.append(c)


#-------------------------------------------------------------------------------
class RunThread(threading.Thread):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(RunThread, self).__init__()
        self.cmd = cmd

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        oss.r(self.cmd)

#-------------------------------------------------------------------------------
class PythonTimerExecutionService(WinService):
#-------------------------------------------------------------------------------
    _svc_name_ = "PythonTimerExecutionService"
    _svc_display_name_ = "Python Timer Execution Service"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        WinService.__init__(self, args)
        self.logfile = "C:/var/log/ptes.log"
        try:
            oss.cp(self.logfile, self.logfile + ".old")
        except: pass

        self.tasks = {}
        self.logmsg("Initializing")
        self.cfgobj = cfg.ConfigObject(CfgObj(), "ptes.xml", "C:/var/cfgs")
        self.default = 5 * 60 * 1000
        self.trigger = time.time() + self.default
        self.tds = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcStop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.logmsg("Stopping Service")
        WinService.SvcStop(self)

        ## hack to attempt a stop w/o having to reboot if all else fails
        for t in self.tds:
            t.STOP = True
        self.logmsg("Stopped Service")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logmsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            m = time.ctime() + ": " + msg
            lf = file(self.logfile, "a")
            print >> lf, m
            lf.close()

            if STANDALONE_DEBUGGING:
                print m

        except:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parseCfgFile(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cfgobj.Load()
        d = {}

        for c in self.cfgobj.cfgs:
            if c.uid not in self.tasks:
                self.tasks[c.uid] = c
                c.trigger = time.time() + c.FreqInMinutes * 60
            d[c.uid] = None

        for u in self.tasks.keys():
            if u not in d:
                del self.tasks[u]

        self.setTrigger()

        if STANDALONE_DEBUGGING:
            self.printTasks()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setTrigger(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for u in self.tasks.keys():
            if self.tasks[u].trigger < self.trigger:
                print "setting trigger to", self.tasks[u].trigger
                self.trigger = self.tasks[u].trigger

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runcmd(self, cfg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = RunThread(cfg.ExeName)
        self.logmsg("Running '%s'" % cfg.TaskName)
        self.tds.append((t, time.time()))
        t.start()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printTasks(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for k in self.tasks.keys():
            print self.tasks[k]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PeriodicCheck(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.cfgobj.hasChanged():
            self.logmsg("Config File Changed")
            self.parseCfgFile()

        li = 0
        while 1:
            tm = time.time()
            if tm >= self.trigger:
                for u in self.tasks.keys():
                    c = self.tasks[u]
                    if c.trigger <= tm:
                        self.runcmd(c)
                        self.trigger = c.trigger = time.time() + c.FreqInMinutes * 60
                        print "set:", self.trigger, tm

                self.setTrigger()

            ## wait time is in millisecs
            next = int((self.trigger - tm)* 1000)

            if next < 500:
                print "next less 500"
                print "next", next, self.trigger, tm

            if next > 500 or li > 100:
                break
            time.sleep(0)
            li += 1

        if next > self.default:
            next = self.default

        if STANDALONE_DEBUGGING:
            self.printTasks()
            print next/1000.0

        self.logmsg("Setting Timer (secs): %d" % (next/1000))
        return next

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcDoRun(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.logmsg("Starting Service")
        self.parseCfgFile()
        self.PeriodicCheck()
        self.WaitInterval = 30 * 1000
        WinService.SvcDoRun(self)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('z', 'init_cfg'), ('s', 'standalone')], [], usage)


    if opts.init_cfg:
        cfg.ConfigObject(CfgObj(CfgItem()), "ptes.xml", "C:/var/cfgs").Save()
        oss.exit(0)

    if opts.standalone:
        global STANDALONE_DEBUGGING
        STANDALONE_DEBUGGING = 1
        PythonTimerExecutionService(args).SvcDoRun()
        oss.exit(0)

    win32serviceutil.HandleCommandLine(PythonTimerExecutionService)


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)
