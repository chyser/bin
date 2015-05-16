#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.relib as rl
import pylib.util as util

import os
import re
import time
import pickle
import random
import socket
import urlparse
import threading
import xmlrpclib
import subprocess
import webbrowser
import collections
import SimpleXMLRPCServer

FPATH = "C:\\Documents and Settings\\me\\Local Settings\\Application Data\\Mozilla\\Firefox\\Profiles\\"

LFILE = FPATH + "downloadflv.csv"
DBFILE = FPATH + "aflv.db"
DOWNLOADER = "C:/bin/axel/axel.exe"
WD = 'C:/home/me/tmp'

BACKUP_TIME_SECS = 3*60
FAILED_FILE = "C:/tmp/af.txt"


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: autoflv [options]

        options:
            -p | --print       : print directory path
            -c | --count <n>   : num files for client to getf
            -l | --load        : show files the need to be loaded
            -Z | --connect     : client stay connected
            -P | --pause       : pause on errors before exit

            -F | --failed      : cleanup failed files
            -A | --admin <cmd> : execute admin 'cmd'

            -n | --num_connections <n>: number of simultaneous connections
            -s | --speed  <n>  : max speed in bytes per sec

    """
    args, opts = oss.gopt(argv[1:], [('r', 'run'), ('P', 'pause'), ('p', 'print'), ('F', 'failed'), ('l', 'load'), ('Z', 'connect'), ('R', 'readOnly')],
        [('n', 'num_connections'), ('s', 'speed'), ('c', 'count'), ('A', 'admin')], main.__doc__ + __doc__)

    #
    # dump the path
    #
    if opts.print:
        print(FPATH)
        print(LFILE)
        oss.exit(0)

    #
    # handle any prior failed files
    #
    if opts.failed:
        HandleFailedFiles()
        oss.exit(0)

    #
    # do admin
    #
    if opts.admin:
        admin(opts.admin, opts.readOnly, args)
        oss.exit(0)


    cnt = int(opts.count) if opts.count else None

    #
    # If a server running, start as a client
    #
    serveDB = xmlrpclib.ServerProxy('http://localhost:3783/')
    try:
        #
        # try to open as a client
        #
        fdb = None
        client = random.randint(1, 0xfffffff)
        print('client (0x%07x) -- version %s' % (client, serveDB.version()))
        serveDB.login(client)

    except socket.error:
        #
        # open as the master
        #
        client = 0
        fdb = FileDB(DBFILE, readOnly=opts.readOnly)
        checker = Checker(LFILE, fdb)

        util.startDaemonThread(checker.checkPeriodically)

        serveDB = ServeDB(fdb)
        util.startDaemonThread(ServerSetup, serveDB)

        ## fail inprogress
        for v in fdb.getItems(lambda v: v.inprog):
            print("'%s' was in-progress, now failed" % v.name)
            fdb.update(v.name, failed=True, inprog=False)

        fdb.save()

        ## check for failed
        failed = fdb.getItems(lambda v: v.failed)
        if failed:
            util.startDaemonThread(WriteFailedFiles, failed, argv[0])
            time.sleep(1)


    #
    # dump out the current load list
    #
    if opts.load:
        l = serveDB.getNeedLoaded()
        print('Not Loaded: %d' % len(l))
        for name in l:
            print('   - %s' % name)

        if client:
            serveDB.logout(client)
        oss.exit()

    if opts.num_connections is None:
        opts.num_connections = '4'

    if opts.speed is None:
        opts.speed = '400000'  # bytes per sec

    oss.cd(WD)
    ct = util.TimeElapsed()
    success = [];  failed = []

    try:
        while cnt is None or cnt > 0:
            v = serveDB.getNext()
            if v:
                name = v[0]
                print('\n>>> getting: "%s"\n' %  name)
                res = getFile(name, v[1], opts.num_connections, opts.speed)

                if res:
                    success.append(name)
                    serveDB.success(name)
                else:
                    failed.append(name)
                    serveDB.failed(name)

            elif client and opts.connect is None:
                break

            if ct.check(60):
                if client:
                    print('... waiting')
                else:
                    print('... waiting -- %d' % serveDB.getNumClients())

            if cnt:  cnt -= 1

            ch = util.delayKey(1)
            if ch == 'q':
                break


    finally:
        if fdb:
            fdb.close()

        if client:
            serveDB.logout(client)
            print('client 0x%07x exiting' % client)
        else:
            if serveDB.getNumClients() > 0:
                print('Still Running Clients: ')
                for c in serveDB.clients.keys():
                    print("    0x%07x" % c)
                print()


    print('\nSuccess:', len(success))
    print('    \n'.join(success))

    ff = len(failed)
    if ff:
        print('\nFailed:', ff)
        print('    \n'.join(failed))
        if opts.pause:
            raw_input('----- PAUSE ------')
        oss.exit(10)

    oss.exit(0)


#-------------------------------------------------------------------------------
def ServerSetup(serveDB):
#-------------------------------------------------------------------------------
    time.sleep(0.1)
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 3783), logRequests=False, allow_none=True)
    server.register_instance(serveDB)
    print('Running server on 3748\n')
    server.serve_forever()


#-------------------------------------------------------------------------------
class ServeDB(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fdb):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.fdb = fdb
        self.lock = threading.Lock()
        self.clients = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def version(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "1.0"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def login(self, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.lock:
            self.clients[id] = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logout(self, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.lock:
            try:
                del self.clients[id]
            except:
                pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNumClients(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.lock:
            return len(self.clients)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNext(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = self.fdb.getItem(lambda v: not(v.loaded or v.failed or v.inprog), inprog=True)
        if v:
            return v.name, v.url

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNeedLoaded(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [f.name for f in self.fdb.getItems(lambda v: not (v.loaded or v.failed or v.inprog))]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getFailed(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [f.name for f in self.fdb.getItems(lambda v: v.failed)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def success(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.fdb.update(name, loaded=True, inprog=False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def failed(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.fdb.update(name, failed=True, inprog=False)


#-------------------------------------------------------------------------------
class FileDBElement(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, url, page, loaded=False, failed=False, inprog=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.name = name
        self.url = url
        self.page = page
        self.loaded = loaded
        self.failed = failed
        self.inprog = inprog

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dumpS(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        s.append(self.name)
        s.append(self.url)
        s.append(self.page)
        s.append(str(self.loaded))
        s.append(str(self.failed))
        s.append(+ str(self.inprog))
        return ','.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadS(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = s.split(',')
        self.name = v[0]
        self.url = v[1]
        self.page = v[2]
        self.loaded = v[3] == 'True'
        self.failed = v[4] == 'True'
        self.inprog = v[5] == 'True'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        s.append('name: ' + self.name)
        s.append('url: ' + self.url)
        s.append('page: ' + self.page)
        s.append('loaded: ' + str(self.loaded))
        s.append('failed: ' + str(self.failed))
        s.append('in prog: ' + str(self.inprog))
        return '\n'.join(s)


#-------------------------------------------------------------------------------
class FileDB(object):
#-------------------------------------------------------------------------------
    class FileDBClosedException(Exception): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, dbname=None, verbose=False, readOnly=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.db = collections.OrderedDict()
        self.updateTime = util.TimeElapsed()
        self.dbname = dbname
        self.lock = threading.RLock()
        self.readOnly = readOnly

        if dbname:
            self.load(dbname, verbose)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, dbname, verbose=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.lock:
            try:
                with open(dbname, 'rb') as inf:
                    self.db = pickle.load(inf)
            except (IOError, ValueError) as ex:
                if verbose:
                    print(ex)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.readOnly:
            return

        util.mkBackups(self.dbname, 10)
        self.updateTime.update()

        with self.lock:
            with open(self.dbname, 'wb') as otf:
                pickle.dump(self.db, otf)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with self.lock:
            for v in self.db.values():
                if v.inprog:
                    v.failed = True
                v.inprog = False
        self.save()
        self.db = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, name, fde):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()
        name = self.gn(name)

        with self.lock:
            self.db[name] = fde

        if self.updateTime.check(BACKUP_TIME_SECS):
            self.save()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, name, **dct):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()
        name = self.gn(name)

        with self.lock:
            util.updateObjWDict(self.db[name], dct)

        if self.updateTime.check(BACKUP_TIME_SECS):
            self.save()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getItem(self, cmp=None, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get items that match 'cmp' func atomically setting any 'kw' members
        """
        self.check()

        with self.lock:
            for v in self.db.values():
                if cmp is None or cmp(v):
                    util.updateObjWDict(v, kw)
                    return v

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()
        name = self.gn(name)

        with self.lock:
            return self.db[name]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getItems(self, cmp=None, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()

        l = []
        with self.lock:
            for v in self.db.values():
                if cmp is None or cmp(v):
                    util.updateObjWDict(v, kw)
                    l.append(v)
        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isIn(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()
        name = self.gn(name)

        with self.lock:
            return name in self.db

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.check()
        name = self.gn(name)

        with self.lock:
            try:
                del self.db[name]
            except KeyError:
                pass
                assert False, 'Not in database: '+  name

        if self.updateTime.check(5*60):
            self.save()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.db)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.db is None:
            raise self.FileDBClosedException('DB closed')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def gn(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not name.endswith('.flv'):
            return name + '.flv'
        return name


#-------------------------------------------------------------------------------
class Checker(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, iFile, fdb):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.lastCheck = 0
        self.sf = rl.scanf('"$!","$$","$$"')
        self.fdb = fdb
        self.iFile = iFile

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checkForFile(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ft = os.stat(self.iFile).st_mtime
        if ft == self.lastCheck:
            return
        self.lastCheck = ft

        s = ['\n[Input File Changed]']

        with open(self.iFile) as inf:
            for line in inf:
                url, page = self.sf.scan(line)
                up = urlparse.urlparse(url).path

                if not isCorrectFile(up):
                    continue

                name = up.split('/')[-1] if '/' in up else up
                if not self.fdb.isIn(name):
                    s.append('   - %s' % name)
                    self.fdb.add(name, FileDBElement(name, url, page))
                else:
                    v = self.fdb.get(name.rsplit('.', 1)[0])
                    if v.failed and v.url != url:
                        s.append('   - %s -- readd' % name)
                        self.fdb.add(name, FileDBElement(name, url, page))

        s.append('[/Input File Changed]\n')
        if len(s) > 2:
            print('\n'.join(s))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checkPeriodically(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        time.sleep(0.1)
        while 1:
            try:
                self.checkForFile()
            except FileDB.FileDBClosedException:
                break

            time.sleep(13)


#-------------------------------------------------------------------------------
def WriteFailedFiles(failed, fn):
#-------------------------------------------------------------------------------
    if not failed:
        return

    l = ['Dumping Failed Files:']
    with open(FAILED_FILE, 'w') as otf:
        otf.write('d = [\n')
        for v in failed:
            l.append('   ' + v.name)
            l.append('        %s' % v.page)
            otf.write('    ("%s", "%s", "%s"),\n' % (v.name, v.url, v.page))
        otf.write(']\n\n')

    print('\n'.join(l))


#-------------------------------------------------------------------------------
def HandleFailedFiles():
#-------------------------------------------------------------------------------
    with open(FAILED_FILE) as inf:
        dd = inf.read()
        d = []
        exec(dd)

        for name, mv, html in d:
            print(html)
            ch = raw_input()
            if ch != 'n':
                webbrowser.open(html)


#-------------------------------------------------------------------------------
class Admin(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.fdb = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def execute(self, cmd, readOnly, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.init(cmd, readOnly)
        func = getattr(self, 'CMD_' + cmd, None)
        if func:
            try:
                return func(*args)
            except Exception as ex:
                print(type(ex))
                print(ex)
        else:
            print('Unknown command "%s"' % cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def init(self, cmd, readOnly):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('Admin:', cmd)
        self.fdb = FileDB(DBFILE, verbose=True, readOnly=readOnly)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def line(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('-'*40)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_help(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ show help
        """
        for f in sorted(dir(self)):
            if f.startswith('CMD_'):
                func = getattr(self, f)
                print('   ' + f[4:])
                if func.__doc__:
                    print('     ' + func.__doc__)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_list(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ list all entries in db
        """

        if args:
            for a in args:
                self.line()
                try:
                    print(str(self.fdb.get(a)))
                except KeyError:
                    print('unknown "%s"' % a)
        else:
            for v in self.fdb.getItems():
                self.line()
                print(v)
        self.line()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_search(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ list all entries in db
        """
        self.line()
        if args:
            pat = re.compile(args[0], re.I)
        else:
            v = raw_input("enter pattern: ")
            if not v.strip():
                return

            pat = re.compile(v, re.I)

        for v in self.fdb.getItems():
            if pat.search(v.page):
                print('-----------')
                print(v.page)
                print(v.name)

        self.line()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_failed(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ list failed entries
        """
        for v in self.fdb.getItems(lambda v: v.failed):
            self.line()
            print(v)
        self.line()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_inProg(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ list in progress entries
        """
        for v in self.fdb.getItems(lambda v: v.inprog):
            self.line()
            print(v)
        self.line()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_notLoaded(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ list not loaded entries
        """
        for v in self.fdb.getItems(lambda v: not v.loaded):
            self.line()
            print(v)
        self.line()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_rm(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ remove specified db entry
        """
        print('rm')
        name = args[0]
        try:
            self.fdb.rm(name)
            self.fdb.save()
        except KeyError:
            print("'%s' not in db")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CMD_edit(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ allow editing specified db entry
        """
        print('edit')
        name = args[0]

        while 1:
            v = self.fdb.get(name)
            self.line()
            print(str(v))
            cmdline = raw_input('\ncmd> ')

            try:
                cmd, val = cmdline.split(' ')
                val = self.cvt(val)
            except ValueError:
                cmd = cmdline
                val = None

            if cmd == 'help':
                print(EDIT_HELP)

            elif cmd.startswith('loaded'):
                print('loaded', val)
                self.fdb.update(name, loaded=val)

            elif cmd.startswith('failed'):
                self.fdb.update(name, failed=val)

            elif cmd.startswith('reload'):
                self.fdb.update(name, failed=True)
                self.fdb.update(name, loaded=False)

            elif cmd == 'edit':
                name = val

            elif cmd == 'save':
                self.fdb.save()

            elif cmd == 'remove':
                self.fdb.rm(name)

            elif cmd == 'quit':
                break

            else:
                print('unknown command:', cmd)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvt(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if v == 'true':
            return True
        if v == 'false':
            return False
        return v


EDIT_HELP= '''
   - help
   - quit
   - loaded <true | false>
   - failed <true | false>
   - reload

'''

gAdmin = Admin()
#-------------------------------------------------------------------------------
def admin(cmd, readOnly, args):
#-------------------------------------------------------------------------------
    gAdmin.execute(cmd, readOnly, args)


#-------------------------------------------------------------------------------
def getFile1(name, url, *args):
#-------------------------------------------------------------------------------
        nn = name + '.dwn'
        oss.r('wget.exe -t 91 -O %s  %s' % (nn, url))
        oss.mv(nn, name)
        return True


#-------------------------------------------------------------------------------
def getFile(name, url, num_connections='4', speed='300000'):
#-------------------------------------------------------------------------------
        nn = name + '.dwn'

        if oss.exists(name) or oss.exists(nn):
            print('File Exists:', name)
            return

        cl = '%s -n %s -s %s -o %s  %s' % (DOWNLOADER, num_connections, speed, nn, url)
        print(time.ctime())
        print('cmd: "%s"' % cl)
        st = util.TimeElapsed()

        p = subprocess.Popen(cl, shell=False, stdout=subprocess.PIPE)
        so = p.stdout

        for line in so:
            try:
                wd = line.split()[0]
                if wd in set(['Initializing', 'File', 'Downloaded', 'Starting', 'Connection']):
                    print(line[:-1])

                if st.check(60):
                    print(line[:-1])

            except IndexError:
                pass

        p.wait()

        if p.returncode == 0:
            oss.mv(nn, name)
            print()
            return True

        print('Error:', p.returncode)


#-------------------------------------------------------------------------------
def isCorrectFile(f):
#-------------------------------------------------------------------------------
    return f.endswith('.flv') or f.endswith('mp4')


#-------------------------------------------------------------------------------
def test():
#-------------------------------------------------------------------------------
    url = 'http://www.the-blueprints.com/blueprints-depot/ships/battleships-germany/dkm-admiral-graf-spee-pocket-battleship-2.gif'
    getFile('graf-spee', url)


if __name__ == "__main__":
    #test()
    main(oss.argv)
