#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import fnmatch
import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: mycvs [cmd] [...]

        wrapper around cvs to make it work better to include some offline support

    cmd:
      online only:
        create [directory] - create a new archive from directory or current directory
        co <archive name>  - checkout the specified archive

        ci [dir_file [dir_file ...]] - checkin file or directories or current dir
        up [dir_file [dir_file ...]] - update file or directories or current dir

        cfd <file_name> - compare file to top of truck showing diffs
        cf [dir_file [dir_file ...]] - check for actions needed for file or directory

        sync  - sync the archive to the directory (cleanup deleted files etc)

      online or offline:
        add <file_name or directory name> - adds the file or directory to archive
                                            certain extensions are treated as binary

        rm <file_name> - removes the file both from the archive and directory

        cff [dir [dir ...] - recursively checks directories for files that aren't
                            part of the archive

        decvs - remove the CVS directories

"""
    args, opts = oss.gopt(argv[1:], [('F', 'force'), ('p', 'inPlace'), ('N', 'noIgnore'), ('b', 'binary')], [('d', 'dir'), ('m', 'msg')], main.__doc__)

    cmd = args[0]
    args = oss.paths(args[1:])

    cvs = CVS(opts.dir)
    cvs.Connect()

    if cmd == 'create':
        cvs.create(args, opts)
    elif cmd == 'check' or cmd == 'cf':
        cvs.check(args, opts)
    elif cmd == 'ci':
        cvs.ci(args, opts)
    elif cmd == 'up':
        cvs.update(args, opts)
    elif cmd == 'rm':
        cvs.rm(args, opts)
    elif cmd == 'add':
        cvs.add(args, opts)
    elif cmd == 'co':
        cvs.co(args, opts)
    elif cmd == 'cff':
        cvs.cff(args, opts)
    elif cmd == "cfd":
        cvs.fdiff(args, opts)
    elif cmd == 'decvs':
        cvs.decvs(args, opts)
    elif cmd == 'sync':
        cvs.sync(args, opts)

    oss.exit(0)

#-------------------------------------------------------------------------------
class BaseCVS(object):
#-------------------------------------------------------------------------------
    BinExts = set([
        '.exe', '.bmp', '.jpg', '.doc', '.dll', '.pyd', '.png', '.gif', '.db',
        '.zip', '.jar', '.lib', '.obj', '*.ico'
    ])

    IgnorePatterns = set([
        "*.vpb", "*.vtg", "*.chk", "*.vpwhist", "RCS", "SCCS", "CVS",
        "*.obj", "*.lib", "*.dll", "core", "*.ilk", "*.pdb", ".exe",
        "*.pmk.mak", "*.rsp", "*.pyo", "*.pyc", "MTN",
        '*.bak', 'bak', '*.bk1', 'tags', 'stags', '*.class', '*.psd',
    ])

    QuestionableExtensions = set(['.db', '.zip', '.jar', '.log'])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, root=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.root = root
        self.exe = 'cvs.exe '

        questionable = set([ '*' + ext for ext in self.QuestionableExtensions])
        binaries = set([ '*' + ext for ext in self.BinExts])

        self.IgnorePatterns = self.IgnorePatterns | questionable | binaries

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Connect(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cvsup = self.CvsRootCheck()
        self.updateOffline()
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CvsRootCheck(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.root is None:
            self.root = oss.readf('CVS/Root', 0)

        if self.root is None:
            self.root = oss.env['CVSROOT']

        return self.root.startswith(':pserver:') or oss.exists(self.root)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateOffline(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ if some offline operations were queued, execute them if online
        """
        if self.cvsup and oss.exists('CVS/offline'):
            inf = file('CVS/offline')
            for cmd in inf:
                oss.r(self.exe + cmd)
            inf.close()
            oss.rm('CVS/offline')
            return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _issueCmd(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ used for functions that can effectively work offline

            @type  cmd: string
            @param cmd: the command and command line to be passed to cvs
        """

        if self.cvsup:
            print(self.exe + cmd)
            oss.r(self.exe + cmd)
        else:
            try:
                otf = file('CVS/offline', 'a')
                otf.write(cmd + '\n')
                otf.close()
            except IOError:
                print("No project for offline", file=oss.stderr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ignoreFile(self, fn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for pat in self.IgnorePatterns:
            if fnmatch.fnmatch(fn, pat):
                return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, args, opts=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ removes the specified files or directories from CVS archive (possible
            offline)

            @type  args: sequence
            @param args: sequence of files or directories to remove
        """
        for fn in args:
            oss.rm(fn)
            self._issueCmd(' rm ' + fn)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ adds the specified files or directories to CVS archive (possible
            offline)

            @type  args: sequence
            @param args: sequence of files or directories to add
        """

        for fn in args:
            if opts.noIgnore is None:
                if self.ignoreFile(oss.basename(fn)):
                    continue

            ext = oss.splitext(fn).lower()
            if opts.binary:
                cvsopts = ' -kb '
            else:
                cvsopts = ' -kb ' if ext in self.BinExts else ''
            self._issueCmd(' add ' + cvsopts + fn)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ci(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ checks the files in. if directories are specified, goes there first

        @type  msg: string
        @param msg: check in message
        @type  args: sequence
        @param args: sequence of files or directories to check in
        @rtype: string
        @return: returns output of the cvs commands
        """

        if not self.cvsup:
            print('CVS Archive "%s" is down' % self.root, file=oss.stderr)
            return ""

        msg = opts.get('msg', '--')
        if not msg: msg = '--'

        if not args:
            #print(self.exe + ' ci -m "%s"' % msg)
            return oss.r(self.exe + ' ci -m "%s"' % msg, '|')
            #return oss.r(self.exe + ' ci -m "%s"' % msg)

        res = []
        for f in args:
            if oss.IsDir(f):
                oss.pushcd(f)
                res.append(oss.r(self.exe + ' ci -m "%s"' % msg, '|'))
                oss.popcd()
            else:
                res.append(oss.r(self.exe + ' ci -m "%s" %s' % (msg, f), '|'))
        return '\n'.join(res)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ updates file or directories

        @type  args: sequence
        @param args: sequence of files or directories to update
        @rtype: string
        @return: returns output of the cvs commands
        """

        if not self.cvsup:
            print('CVS Archive "%s" is down' % self.root, file=oss.stderr)
            return ""

        if not args:
            return oss.r(self.exe + ' up -d', '|')

        res = []
        for f in args:
            if oss.IsDir(f):
                oss.pushcd(f)
                res.append(oss.r(self.exe + ' up -d', '|'))
                oss.popcd()
            else:
                res.append(oss.r(self.exe + ' up ' + f, '|'))
        return '\n'.join(res)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self, args=None, opts=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ checks files or directories

        @type  args: sequence
        @param args: sequence of files or directories to check
        """
        if not self.cvsup:
            print('CVS Archive "%s" is down' % self.root, file=oss.stderr)
            return ''

        res = []
        if not args:
            for s in oss.r(self.exe + '-qn up -A ', '|').split('\n'):
                if not s.startswith('?'):
                    res.append(s)
            return '\n'.join(res)

        for f in args:
            if oss.IsDir(f):
                if oss.pushcd(f):
                    for s in oss.r(self.exe + '-qn up -A ', '|').split('\n'):
                        if not s.startswith('?'):
                            res.append(s)
                    oss.popcd()
            else:
                res.append(oss.r(self.exe + '-qn up -A ' + f, '|'))
        return '\n'.join(res)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.cvsup:
            print('CVS Archive "%s" is down' % self.root, file=oss.stderr)
            return

        name = args[0] if args else oss.basename(oss.pwd())

        if not self.root.startswith(':pserver:'):
            if oss.exists(self.root + '/' + name):
                if opts.force:
                    pass
                else:
                    print('CVS Archive "%s" exists' % name, file=oss.stderr)
                    return

        msg = opts.msg if opts is not None else 'Initial Checkin: ' + name

        questionable = set([ '*' + ext for ext in self.QuestionableExtensions])
        binaries = set([ '*' + ext for ext in self.BinExts])
        il = "-I! " + ' '.join([ '-I "%s"' % pat for pat in (self.IgnorePatterns | questionable | binaries)])
        oss.r(self.exe + ' import -m"%s" %s %s %s %s1' % (msg, il, name, name, name))

        self.co(None, opts)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def co(self, args=None, opts=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.cvsup:
            print('CVS Archive "%s" is down' % self.root, file=oss.stderr)
            return

        if args:
            name = args[0]
            oss.r(self.exe + ' co ' + name)
        else:
            name = oss.basename(oss.pushcd('..'))

            if opts.inPlace:
                print('inplace checkout')
                oss.r("cp -r %s /tmp/%s%s.bak" % (name, oss.DateFileName(), name))
                tn = '/tmp/cvs_inplace_' + name
                oss.mkdir(tn)
                oss.pushcd(tn)
                oss.r(self.exe + ' co ' + name)
                oss.popcd()
                oss.r("cp -r %s/%s/* %s" % (tn, name, name))
                oss.popcd()
            else:
                oss.r("mv %s /tmp/%s%s.bak" % (name, oss.DateFileName(), name))
                oss.r(self.exe + ' co ' + name)
                oss.popcd()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checkfor(self, dir = '.'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        lst = []

        if not oss.exists('CVS/Entries'):
            return

        ## get list of files
        inf = file('CVS/Entries')
        have = set()
        for line in inf:
            try:
                have.add(line.split('/')[1])
            except:
                pass

        inf.close()

        try:
            igf = file(".cffignore")
            for line in igf:
                line = line[:-1]
                have.add(line)
        except IOError:
            pass

        inf.close()

        for f in oss.ls():
            f = oss.basename(f)
            if self.ignoreFile(f):
                continue

            if oss.IsDir(f):
                if not oss.exists(f + '/CVS'):
                    if f not in have:
                        lst.append("%s/%s/" % (dir, f))
                else:
                    oss.pushcd(f)
                    lst.extend(self.checkfor(dir + '/' + f))
                    oss.popcd()
            elif f not in have:
                lst.append("%s/%s" % (dir, f))

        return lst

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decvs(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for f in oss.ls():
            bf = oss.basename(f)

            if bf.lower() == 'cvs':
                print('removing:', f)
                oss.r('rm -rf cvs')
                continue

            if self.ignoreFile(bf):
                continue

            if oss.IsDir(bf):
                oss.pushcd(bf)
                self.decvs(args, opts)
                oss.popcd()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def fdiff(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for fn in args:
            oss.r(self.exe + " diff %s" % fn)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sync(self, args=None, opts=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not oss.exists('./CVS/Entries'):
            print('must be in root cvs directory')
            return

        with open('./CVS/Entries', 'rU') as inf:
            files = set()

            for line in inf:
                d = line.split('/')
                files.add(d[1])

        rset = [f for f in files if not oss.exists(f)]

        print(rset)
        if self.validate():
            self.rm(rset)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def validate(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ch = raw_input('\nRemove files (y,n): ')
        return ch == 'y'


#-------------------------------------------------------------------------------
class CVS(BaseCVS):
#-------------------------------------------------------------------------------
    UpdateCodes = set(['U', 'P', 'A', 'R', 'M', 'C'])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = BaseCVS.update(self, args, opts)
        print(v)
        print('----------------------')
        for line in v.split('\n'):
            if line and line[0] in self.UpdateCodes:
                print(line)
        print('----------------------')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ci(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = BaseCVS.ci(self, args, opts)
        print(v)
        print('----------------------')
        for line in v.split('\n'):
            if line and line.startswith('Checking'):
                print('-', line[12:-1])
        print('----------------------')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for line in BaseCVS.check(self, args).split('\n'):
            if line:
                print(line)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cff(self, args, opts):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in self.checkfor():
            print(i)




if __name__ == "__main__":
    main(oss.argv)

