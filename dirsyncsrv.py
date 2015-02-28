import thread
import time

import win32serviceutil
import win32service
import win32event

import pylib.xmlparse as xp
import pylib.osscripts as oss
import dirsync as ds

REVISION = "1.1"

#-------------------------------------------------------------------------------
class WinService(win32serviceutil.ServiceFramework):
#-------------------------------------------------------------------------------
    _svc_name_ = "WinService"
    _svc_display_name_ = 'WinService'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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



# config info
#-------------------------------------------------------------------------------
class CfgRoot(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(CfgRoot, self).__init__()
        self.log = ""
        self.items = []

#-------------------------------------------------------------------------------
class CfgItem(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(CfgItem, self).__init__()
        self.rule = ""
        self.src = ""
        self.dest = ""
        self.excludes = []
        self.filters = []
        self.verbose = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## handle optional arguments
        if attr == 'verbose':
            return True

#-------------------------------------------------------------------------------
class DirSyncService(WinService):
#-------------------------------------------------------------------------------
    _svc_name_ = "DirSyncService"
    _svc_display_name_ = "Directory Syncing Service"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        WinService.__init__(self, args)
        self.logfile = "C:/var/log/dirsync.log"
        try:
            oss.cp(self.logfile, self.logfile + ".old")
        except: pass

        self.cfgfile = "C:/var/cfgs/dirsyncdb.xml"
        self.log = file(self.logfile, "wU")
        self.tds = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcStop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        WinService.SvcStop(self)
        self.log.close()

        ## hack to attempt a stop w/o having to reboot if all else fails
        for t in self.tds:
            t.STOP = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logmsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            print >> self.log, msg
            self.log.flush()
        except:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PeriodicCheck(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dead = []
        ## see if they are alive
        for t in self.tds:
            if not t.isAlive():
                dead.append(t)

        ## restart any which are dead
        for t in dead:
            item = t.cxt
            self.tds.remove(t)
            t = ds.DirSyncThread(item.rule, item.src, item.dest, item.excludes, item.filters, item, item.verbose and self.log)
            self.tds.append(t)
            t.setDaemon(True);  t.setName(item.rule);  t.start();  time.sleep(0)
            self.logmsg("$$ RE-Started: '%s' thread. isAlive: %s" % (t.getName(), str(t.isAlive())))

        ## adjust next check period
        if dead:
            return 30*1000
        else:
            return 5*60*1000

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SvcDoRun(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xo = xp.XMLToObj()
        tag, cr = xo.unmarshal_str(file(self.cfgfile).read())

        ## set up log file
        self.logfile = cr.log
        try:
            oss.cp(self.logfile, self.logfile + ".old")
        except: pass
        self.log = file(self.logfile, "w")

        ## provide info as to what configuration and additional logging we are using
        self.LogInfoEvent("DirSyncServer Rev: '%s'" % REVISION)
        self.LogInfoEvent("Using Log File: '%s'" % self.logfile)
        self.LogInfoEvent("Using Config File: '%s'" % self.cfgfile)

        for item in cr.items:
            self.logmsg("$$ Inserting Rule: '%s'" % item.rule)
            t = ds.DirSyncThread(item.rule, item.src, item.dest, item.excludes, item.filters, item, item.verbose and self.log)
            self.tds.append(t)
            t.setDaemon(True);  t.setName(item.rule);  t.start();  time.sleep(0)
            self.logmsg("$$ Started: '%s' thread. isAlive: %s" % (t.getName(), str(t.isAlive())))

        self.WaitInterval = 30 * 1000
        WinService.SvcDoRun(self)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    win32serviceutil.HandleCommandLine(DirSyncService)




