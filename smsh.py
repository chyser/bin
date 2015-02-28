#!/usr/bin/env python
"""
usage:

"""

import win32api as w32
import win32console as w32con
import msvcrt
import os
import subprocess
import pylib.osscripts as oss
import pylib.wincursor as wc

gKnownMachines = {
    'm5' : 'm5.fc.sudc.hpl.hp.com',
    'kirby' : 'kirby.fc.hp.com'
}


SSH = "ssh.exe"
#SCP = "C:\\Program Files\\OpenSSH\\bin\\scp.exe"
SCP = "C:/workspace/cygwin/bin/scp.exe"

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
class Context(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, mach, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Context, self).__init__()
        self.parent = parent
        self.mach = mach
        self.nickname = mach.split('.')[0]
        self.name = name
        self.prompt = "%s> " % self.nickname
        self.cwd = None
        self.history = []

        self.aliases = {'ls' : 'ls -xp',
                        'll' : 'ls -l',
                        'cls' : 'clear',
                        'work' : 'cd /home/chrish/compflu/plugin/controller'
                       }

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def init(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cwd = self.parent.homeDir()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "cxt: " + self.mach + ", " + self.name + ", " + self.cwd + ", " + str(self.aliases)



#-------------------------------------------------------------------------------
class Console(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, mach):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Console, self).__init__()
        self.dbglvl = 0
        self.defName = "chrish"
        self.cxt = {}
        self.mach = None
        self.setContext(mach)
        self.wc = wc.Console("smsh")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setContext(self, mach):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## if already exists, just use it
        if mach in self.cxt:
            self.mach = self.cxt[mach]
        else:
            ## else look for shortcut name
            if mach in gKnownMachines:
                machine = gKnownMachines[mach]
            else:
                machine = mach

            #print "Creating new context:", mach, machine

            ## then create new one
            self.cxt[mach] = self.mach = Context(self, machine, self.defName)
            self.mach.init()
        print self.mach.cwd

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def homeDir(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.RmtCmd2Str('pwd')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def RmtCmd2Str(self, cmd, chdir=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return oss.r(self.mkRmtCmd(cmd, chdir), '|').strip()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rawRun(self, cmd, shell=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if cmd.startswith('cd '):
            oss.cd(cmd[3:])
            print oss.pwd()
            return

        l = []
        for ch in cmd:
            if ch == '*':
                l.append('\\*')
            else:
                l.append(ch)
        cmd = ''.join(l)
        if self.dbglvl > 3: print cmd
        #return os.system(cmd)
        return subprocess.call(cmd, shell=shell)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runCmd(self, cmd, chdir=True, shell=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cc = self.mkRmtCmd(cmd, chdir)
        if self.dbglvl > 2: print cc
        return self.rawRun(cc, shell)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mkRmtCmd(self, cmd, chdir=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if chdir:
            return ('"%s" ' % SSH) + self.mach.name + '@' + self.mach.mach + ('  cd %s; ' % self.mach.cwd) + cmd
        return ('"%s" ' % SSH) + self.mach.name + '@' + self.mach.mach + ' '+ cmd

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getCmd(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return getattr(self, "cmd_" + cmd)
        except:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def completer(self, cons, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        args = cmd.split()
        val = args[-1]
        vall = val.split('/')

        if len(vall) == 1:
            vv = val
            vvv = ''
            val = '.'
        else:
            vv = vall[-1]
            vvv = '/'.join(vall[:-1])
            val = vvv + '/'

        #cons.writeXY(0, 30, "vv = '%s', val = '%s', vvv = '%s'" % (vv, val, vvv), 1)

        l = self.RmtCmd2Str('ls -p ' + val, chdir=True).split('\n')
        #cons.writeXY(0, 40, l)

        ll = [cc for cc in l if cc.startswith(vv)]

        #cons.writeXY(0, 50, ll)

        if not ll:
            return l

        if len(ll) == 1:
            if vvv:
                vvv += '/' + ll[0]
            else:
                vvv = ll[0]
            #cons.writeXY(0, 60, 'vvv: ' + vvv, 1)
            args[-1] = vvv
            #cons.writeXY(0, 70, args)
            #cons.writeXY(0, 75, len(args))
            if len(args) > 1:
                res = ' '.join(args)
            else:
                res = args[0]

            #cons.writeXY(0, 78, res)
            return res
        else:
            return ll

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def read_input(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #return raw_input(self.mach.prompt)
        self.wc.prompt = self.mach.prompt
        return self.wc.read_input(self.completer)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while True:
            cmdstr = self.read_input()
            if not cmdstr:
                continue

            try:
                cmd = cmdstr.split()[0]
                args = cmdstr.split()[1:]
            except:
                cmd = cmdstr

            #
            # perform alias substitutions
            #
            if cmd in self.mach.aliases:
                cmd = self.mach.aliases[cmd]
                cmdstr = cmd + ' ' + ' '.join(args)
                try:
                    cmd = cmdstr.split()[0]
                    args = cmdstr.split()[1:]
                except:
                    cmd = cmdstr

                if self.dbglvl > 1:
                    print "alias: %s --> '%s'" % (cmd, cmdstr)

            #
            # interpret commands
            #
            cf = self.getCmd(cmd)
            if cf:
                cf(args)

            ## run local commands
            elif cmd[0] == '!':
                self.rawRun(cmdstr[1:])

            elif cmd == 'pwd':
                print self.mach.cwd

            elif cmd == 'clear':
                self.rawRun('clear')

            elif cmd == 'exit':
                self.wc.close()
                break

            ## run remote commands
            else:
                if self.dbglvl > 0:
                    print cmdstr
                self.runCmd(cmdstr, shell=True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd__mach(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ _mach [machine name] -- display or change the machine currently in use
        """
        if args:
            self.setContext(args[0])
        print "Current Machine:", self.mach.mach

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd__dbg(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''_dbg [level] -- display and/or set debug level
        '''
        if args:
            self.dbglvl = int(args[0])
        print self.dbglvl

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_less(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.rawRun(self.mkRmtCmd('cat ' + ' '.join(args)) + '| more')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_cd(self, dir=None, pp=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        olddir = self.mach.cwd

        if dir:
            dir = dir[0]

            if dir.startswith('..'):
                if dir == '..':
                    self.mach.cwd = '/'.join(self.mach.cwd.split('/')[:-1])
                else:
                    for d in dir.split('/'):
                        self.cmd_cd([d], False)

            elif dir == '.':
                pass
            elif dir.startswith('/'):
                self.mach.cwd = dir
            else:
                self.mach.cwd += '/' + dir
        else:
            self.mach.cwd = self.homeDir()

        res = self.runCmd('cd ' + self.mach.cwd, False)

        if res != 0:
            self.mach.cwd = olddir

        if pp:
            print self.mach.cwd

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_cpf(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''cpf [scp-options] <rmt_file> <local_file> -- perform scp of remote file to local file
        '''
        dest = args[-1]
        src = ' '.join(args[:-1])

        cmd = ('"%s" ' % SCP) + ("%s@%s:%s/" % (self.mach.name, self.mach.mach, self.mach.cwd)) + src + ' ' + dest
        print cmd
        self.rawRun(cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_cpt(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''cpt [scp-options] <local_file> <rmt_file> -- perform scp of local file to remote file
        '''
        dest = args[-1]
        src = ' '.join(args[:-1])

        cmd = ('"%s" ' % SCP) + src + (" %s@%s:%s/" % (self.mach.name, self.mach.mach, self.mach.cwd)) + dest
        print cmd
        self.rawRun(cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_prompt(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if args:
            self.mach.prompt = ' '.join(args) + ' '
        print self.mach.prompt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd__eval(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print "eval:"
        try:
            print eval(' '.join(args))
        except Exception, ex:
            print ex
            print "\n\n"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_alias(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''alias [<name> <val>]
        '''
        if args:
            self.mach.aliases[args[0]] = ' '.join(args[1:])
        print self.mach.aliases

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd_help(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''help [topic] -- display help
        '''
        for cf, f in Console.__dict__.items():
            if cf.startswith('cmd_'):
                if f.__doc__:
                    print f.__doc__



#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    if not args:
        usage(1, 'must specify machine')

    if args[0] in gKnownMachines:
        mach = gKnownMachines[args[0]]
    else:
        mach = args[0]

    print "Connecting to", mach

    Console(args[0]).run()

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

