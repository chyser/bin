#!/usr/local/bin/python
"""
A set of functions which make porting Korn/bash shell scripts to python easier.

- chrish@fc.hp.com

"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


_VERSION = "2.0"

import os
import re
import sys
import time
import glob
import shutil
import getopt
import string
import socket
import filecmp
import fnmatch
import os.path
import getpass
import difflib
import hashlib
import datetime
import warnings
import tempfile
import subprocess

#import pylib.lex as lex
import lex


try:
    argv = sys.argv
except:
    argv = ['embedded']

argc   = len(argv)
stderr = sys.stderr
stdout = sys.stdout
stdin  = sys.stdin
sleep  = time.sleep

class OSScriptsError(Exception): pass
class OSScriptsEx(Exception): pass


#-------------------------------------------------------------------------------
class ignoreException(object):
#-------------------------------------------------------------------------------
    """ context 'with (ignoreException(exceptions):' that ignores exceptions
        passed as arguments
    """
    def __init__(self, *exceptions):
        object.__init__(self)
        self.exceptions = set(exceptions)

    def __enter__(self):
        pass

    def __exit__(self, type, val, tb):
        return type in self.exceptions


#-------------------------------------------------------------------------------
class Environment(object):
#-------------------------------------------------------------------------------
    """ represents the environment
    """
    def __init__(self):
        object.__init__(self)
        self.env = os.environ

    def __setitem__(self, key, val):
        self.env[key] = val

    def __getitem__(self, key):
        if key in self.env:
            return self.env[key]
        return ""

    def items(self):
        return self.env.items()

    def keys(self):
        return self.env.keys()

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.env

    def __nonzero__(self):
        return self.__len__ != 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def export(self, key, val = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if val is None:
            if key not in self.env:
                raise OSScriptsError("exporting non-existent key")
            val = self.env[key]
        else:
            self.env[key] = val

        if sys.platform == 'win32':
            k = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Environment", 0, _winreg.KEY_SET_VALUE)
            _winreg.SetValueEx(k, key, 0, _winreg.REG_SZ, str(val))
            _winreg.CloseKey(k)
        else:
            raise NotImplementedError

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def exportAll(self, key, val = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if val is None:
            if key not in self.env:
                raise OSScriptsError("exporting non-existent key")
            val = self.env[key]
        else:
            self.env[key] = val

        if sys.platform == 'win32':
            rk = winreg.RegKey(winreg.RegKey.HKLM, "Software/SYSTEM/CurrentControlSet/Control/SessionManager/Environment", read=False)
            rk.setValue(key, str(val))
            rk.close()
        else:
            raise NotImplementedError

env = Environment()

HOME_DIR = env['HOME'] or env['HOMEPATH']

if sys.platform == 'win32':
    import _winreg
    with ignoreException(ImportError):
        import winreg

    def expanduser(dd):
        if not (dd and dd[0] == '~') or not HOME_DIR:
            return dd
        return abspath(HOME_DIR + '/' + dd[1:])

    DEV_NULL = "nul"
    PATH_ELEM_SEP = ';'
    DIR_ELEM_SEP = '\\'
else:
    expanduser = os.path.expanduser
    DEV_NULL = "/dev/null"
    PATH_ELEM_SEP = ':'
    DIR_ELEM_SEP = '/'


dirname = os.path.dirname


#-------------------------------------------------------------------------------
def ReInitOSScripts():
#-------------------------------------------------------------------------------
    global argv, argc, stderr
    argv = sys.argv
    argc = len(sys.argv)
    stderr = sys.stderr


#-------------------------------------------------------------------------------
class OptionClass(object):
#-------------------------------------------------------------------------------
    """ cmdline options are stored here """
    def __init__(self):
        object.__init__(self)
        self.__dict__['d'] = {}

    def __getitem__(self, x):
        return self.__dict__['d'][x]

    def __contains__(self, x):
        return x in self.__dict__['d']

    def __getattr__(self, x):
        return self.__dict__['d'][x]

    def __setattr__(self, x, v):
        self.__dict__['d'][x] = v

    def keys(self):
        return self.__dict__['d'].keys()

    def items(self):
        return self.__dict__['d'].items()

    def values(self):
        return self.__dict__['d'].values()

    def IsSet(self):
        return any(self.values())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getInt(self, attr, defVal=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return int(getattr(self, attr, defVal))
        except TypeError:
            return defVal

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, attr, defVal=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self, attr, defVal)


#-------------------------------------------------------------------------------
def addImportPath(path, idx=0):
#-------------------------------------------------------------------------------
    sys.path.insert(idx, path)


#-------------------------------------------------------------------------------
def write(*args):
#-------------------------------------------------------------------------------
    stdout.write(' '.join([str(v) for v in args]))


#-------------------------------------------------------------------------------
def writeln(*args):
#-------------------------------------------------------------------------------
    stdout.write(' '.join([str(v) for v in args]))
    stdout.write("\n")


#-------------------------------------------------------------------------------
def __gopti(CmdName, CmdLine, Options = None):
#-------------------------------------------------------------------------------
    ''' internal function checks options and expands shell wildcards

        (list)args, (OptionClass)opts = __gopti((str)CmdName, (str|list)CmdLine, (str)Options = None)

        CmdName - used for error messages only
        CmdLine - options and arguments
        Options - options to parse from CmdLine
    '''
    ropts = None

    if isinstance(CmdLine, (str, unicode)):
        CmdLine = lex.StringParse(CmdLine)
    elif len(CmdLine) == 1:
        CmdLine = lex.StringParse(CmdLine[0])

    if Options is not None:
        try:
            opts, args = getopt.getopt(CmdLine, Options, [])
        except getopt.GetoptError:
            raise OSScriptsError(CmdName + " -- option error")

        ropts = OptionClass()
        for o in Options:
            setattr(ropts, o, False)

        for o, a in opts:
            setattr(ropts, o[1], True)

        CmdLine = args

    lst = []
    for arg in CmdLine:
        if arg[0] == '"' and arg[-1] == '"':
            lst.append(arg[1:-1])
        else:
            tl = glob.glob(arg)
            if tl:
                lst.extend(tl)
            else:
                if not ('*' in arg or '?' in arg or '[' in arg or ']' in arg):
                    lst.append(arg)

    return map(expanduser, lst), ropts


#-------------------------------------------------------------------------------
def r(cmd, Options = "", shell=True, retRes=False):
#-------------------------------------------------------------------------------
    """ r - run. Runs the specified command(s) returning an error code or ...
         Options:
            < - returns file object for writing
            > - returns file object for reading
            | - return string generated by command
            $ - return string generated by command (both stdout and stderr)
            2 - returns tuple (fo_read, fo_write)
            3 - returns tuple (fo_read, fo_write, fo_stderr)
    """

    if isinstance(cmd, (str, unicode)):
        cmd = expanduser(cmd)

        if not Options:
            for c in cmd.splitlines():
                p = subprocess.Popen(c, shell=True)
                res = p.wait()
            return res

    if not Options:
        p = subprocess.Popen(cmd, shell=True)
        res = p.wait()
        return res

    elif Options == ">":
        return subprocess.Popen(cmd, universal_newlines=True, shell=shell, stdout=subprocess.PIPE).stdout

    elif Options == "|":
        p = subprocess.Popen(cmd, universal_newlines=True, shell=shell, stdout=subprocess.PIPE)
        f = p.stdout
        s = f.read()
        f.close()
        res = p.wait()

        if not retRes:
            return s
        return res, s

    elif Options == "$":
        p = subprocess.Popen(cmd, universal_newlines=True, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        f = p.stdout
        s = f.read()
        f.close()
        res = p.wait()

        if not retRes:
            return s
        return res, s

    elif Options == "<":
        return subprocess.Popen(cmd, shell=shell, stdin=subprocess.PIPE).stdin

    elif Options == "2":
        p = subprocess.Popen(cmd, universal_newlines=True, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.stdin, p.stdout

    elif Options == "3":
        p = subprocess.Popen(cmd, universal_newlines=True, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdin, p.stdout, p.stderr

    else:
        raise OSScriptsError("Bad Run Arguments")

## alias
run = r

#-------------------------------------------------------------------------------
def getuser():
#-------------------------------------------------------------------------------
    '''return current user'''
    return getpass.getuser()


#-------------------------------------------------------------------------------
def getpasswd():
#-------------------------------------------------------------------------------
    '''prompt and return a passwd'''
    return getpass.getpass()


#-------------------------------------------------------------------------------
def date(arg=None):
#-------------------------------------------------------------------------------
    """ print out the date and time. if arg == '|', return string instead """
    d = datetime.datetime.now()
    if arg == '|': return d.ctime()
    print(d.ctime())


#-------------------------------------------------------------------------------
def DateFileName(sec=False):
#-------------------------------------------------------------------------------
    """ returns a filename constructed from the current date and time:
        ex: 20070905_0634
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M" + ('%S' if sec else ''))


#-------------------------------------------------------------------------------
def diff(*args):
#-------------------------------------------------------------------------------
    """perform a diff on two files
         -either "<options>, file, file"
         or string, list or tuples with - style options
    """

    if len(args) == 3:
        with ignoreException(AttributeError):
            l0 = args[1].readlines()
            l1 = args[2].readlines()
            a, o = __gopti('diff', args[0], 'cnu')

            if o.c: return difflib.context_diff(l0, l1)
            if o.n: return difflib.ndiff(l0, l1)
            return difflib.unified_diff(l0, l1)

    args, o = __gopti('diff', args, 'cnu')

    l0 = file(args[0]).readlines()
    l1 = file(args[1]).readlines()

    if o.c: return difflib.context_diff(l0, l1)
    if o.n: return difflib.ndiff(l0, l1)
    return difflib.unified_diff(l0, l1)


#-------------------------------------------------------------------------------
def ls(*Args):
#-------------------------------------------------------------------------------
    ''' ls - returns a list of files
        usage: ls(["." | ".."] | ["<filename>" | "*.<ext>" | "*"]+)
    '''
    if len(Args) == 0:
        Args = '.'

    args = []
    for a in Args:
        args.extend(glob.glob(a))

    lst = []
    for arg in args:
        if isDir(arg) and arg in Args:
            lst.extend(glob.glob(arg + '/*'))
        else:
            if exists(arg):
                lst.append(arg)
    return lst


#-------------------------------------------------------------------------------
def ls1(*Args):
#-------------------------------------------------------------------------------
    ''' ls1 - returns a list of files
        usage: ls(["." | ".."] | ["<filename>" | "*.<ext>" | "*"]+)
    '''
    if len(Args) == 0:
        Args = '.'

    args, opts = __gopti('ls', Args)

    lst = []
    for arg in args:
        if isDir(arg) and arg in Args:
            lst.extend(glob.glob(arg + '/*'))
        else:
            if exists(arg):
                lst.append(arg)
    return lst

#-------------------------------------------------------------------------------
def hostname():
#-------------------------------------------------------------------------------
    """ return the hostname of the host running the script """
    return socket.gethostname()


#-------------------------------------------------------------------------------
def echo(msg, fileName, foOptions="w", nl=True):
#-------------------------------------------------------------------------------
    """ echo's message to file 'fileName', returns status
    """
    with ignoreException(IOError):
        with open(expanduser(fileName), foOptions) as otf:
            nl = '\n' if nl else ''
            otf.write(str(msg) + nl)
        return True


#-------------------------------------------------------------------------------
def echob(msg, fileName, foOptions="wb"):
#-------------------------------------------------------------------------------
    """ echo's message to binary file 'fileName', returns status
    """
    return echo(msg, fileName, foOptions, False)


#-------------------------------------------------------------------------------
def readf(fileName, lineNum=None):
#-------------------------------------------------------------------------------
    """ returns the lines or a specific line from a file """
    with ignoreException(IOError):
        with open(expanduser(fileName), 'rU') as inf:
            lines = inf.readlines()

        if lineNum is None:
            return lines
        return lines[lineNum].rstrip()


#-------------------------------------------------------------------------------
def readfile(fileName):
#-------------------------------------------------------------------------------
    """ returns the contents of a file """
    with ignoreException(IOError):
        with open(expanduser(fileName), 'rU') as inf:
            return inf.read()


#-------------------------------------------------------------------------------
def tr(msg, fltr):
#-------------------------------------------------------------------------------
    """ transform letters in msg by lookup in dictionary filter """
    return "".join([fltr.get(i, i) for i in msg])


#-------------------------------------------------------------------------------
def exit(exit_code=0):
#-------------------------------------------------------------------------------
    """ wrapper for exit """
    return(sys.exit(exit_code))


#-------------------------------------------------------------------------------
def newerthan(file1, file2, attr='st_mtime'):
#-------------------------------------------------------------------------------
    """ returns a boolean status indicating whether file1 is newerthan file2
        attr can be [st_mtime (modified), st_atime (accessed), st_ctime (creation)]
    """
    t1 = getattr(os.stat(expanduser(file1)), attr)
    t2 = getattr(os.stat(expanduser(file2)), attr)
    return t1 > t2


#-------------------------------------------------------------------------------
def filesize(fileName):
#-------------------------------------------------------------------------------
    """ filesize - returns the filesize in bytes. """
    return os.stat(expanduser(fileName))[6]


#-------------------------------------------------------------------------------
def pwd():
#-------------------------------------------------------------------------------
    """ print working directory - returns a string """
    return os.getcwd()


#-------------------------------------------------------------------------------
def pathsplit(filename):
#-------------------------------------------------------------------------------
    return normpath(expanduser(filename)).split('/')


#-------------------------------------------------------------------------------
def basename(filename_list):
#-------------------------------------------------------------------------------
    """ returns basename of a string or list of basenames of a list of names """
    if not isinstance(filename_list, (str, unicode)):
        return [os.path.basename(fn) for fn in filename_list]
    return os.path.basename(filename_list)


#-------------------------------------------------------------------------------
def basename2(prefix, filename_list):
#-------------------------------------------------------------------------------
    """ returns basename string or list of basenames of a list of names
        removing the prefix
    """
    warnings.warn("deprecated", DeprecationWarning)
    if not isinstance(filename_list, (str, unicode)):
        return [basename2(fn) for fn in filename_list]

    pp = pathsplit(prefix)
    ff = pathsplit(filename_list)

    i = 0; lp = len(pp)
    while i < lp and pp[i] == ff[i]:
        i += 1

    return '/'.join(ff[i:])


#-------------------------------------------------------------------------------
def replaceExt(filename_list, ext):
#-------------------------------------------------------------------------------
    """ returns filename or filenames in list with a new extension """
    if not isinstance(filename_list, (str, unicode)):
        return [replaceExt(fn, ext) for fn in filename_list]

    if not ext.startswith('.'): ext = '.' + ext
    return os.path.splitext(filename_list)[0] + ext


#-------------------------------------------------------------------------------
def cd(path):
#-------------------------------------------------------------------------------
    ''' change directory <path> returning old directory '''
    return not os.chdir(expanduser(path))


#-------------------------------------------------------------------------------
class CDStack(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.startDir = pwd()
        self.stack = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pushcd(self, path):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ''' change directory <path> returning old directory '''
        cur = abspath(pwd())
        if cd(path):
            self.stack.append(cur)
            return cur

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def popcd(self, v=1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in range(v):
            d = self.stack.pop()
            cd(d)
            return d

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def startcd(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cd(self.startDir)



__cdStack = CDStack()
pushcd = __cdStack.pushcd
popcd = __cdStack.popcd
startcd = __cdStack.startcd


#-------------------------------------------------------------------------------
def rm(*Args):
#-------------------------------------------------------------------------------
    ''' rm - removes files or directories
        usage: rm(["-rfv"], "<filename>" | "*.<ext>" | "*")
            -r - recursive removal
            -f - force
            -v - return list of removed files
        return:
            True   : all were deleted
            False  : one or more was not deleted
            [list] : -v returns list of deleted
    '''
    args, opts = __gopti("rm", Args, "rfv")

    vl = []
    for p in args:
        if isDir(p):
            if opts.r:
                try:
                    shutil.rmtree(p, opts.f)
                    vl.append(p)
                except:
                    vl.append(False)
            else:
                vl.append(False)

        elif exists(p):
            os.remove(p)
            vl.append(p)

    if opts.v:
        return filter(None, vl)
    return all(vl)


#-------------------------------------------------------------------------------
def exists(path):
#-------------------------------------------------------------------------------
    """ exists - returns boolean indicating whether the file exists """
    return os.path.exists(expanduser(path))


#-------------------------------------------------------------------------------
def mv(*Args):
#-------------------------------------------------------------------------------
    ''' mv - moves file(s) to a directory or a file
         usage: mv(["-f | -v"], "<filename>" | "*.<ext>", "<dest file or dir>")
            -f force overwrites
            -v return list of moved files instead of success val
         returns:
             True  : all files moved
             False : one or more files not moved
             [list]: -v retuns list of files moved
    '''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __mv(src, dest, force):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """internal function"""
        if not exists(src): return
        if force:  rm(dest)
        elif exists(dest): return

        shutil.move(src, dest)
        return True

    lst, opts = __gopti('mv', Args, "fv")

    if len(lst) < 2: raise OSScriptsError("mv: need at least two parameters")

    dest = lst[-1]
    if isDir(dest):
        l = [p if __mv(p, dest + "\\" + basename(p), opts.f) else False for p in lst[:-1]]
        if opts.v: return filter(None, l)
        return all(l)

    if len(lst) != 2:
        raise OSScriptsError("mv: > 2 params, last not dir")

    l = [lst[0] if __mv(lst[0], dest, opts.f) else False]
    if opts.v:  return filter(None, l)
    return all(l)


#-------------------------------------------------------------------------------
def mkdir(path):
#-------------------------------------------------------------------------------
    """ makes a directory """
    if not path:  return
    path = expanduser(path)
    if not exists(path):
        return not os.mkdir(path)
    if not isDir(path):
        raise OSError("mkdir: file of name exists")


#-------------------------------------------------------------------------------
def mkdirs(path):
#-------------------------------------------------------------------------------
    """ makes intermediate directories for path if non-existent """
    paths = pathsplit(expanduser(path))
    for idx in xrange(len(paths)+1):
        mkdir('/'.join(paths[:idx]))
    return True


#-------------------------------------------------------------------------------
def rmdir(path):
#-------------------------------------------------------------------------------
    """ removes a directory """
    with ignoreException(WindowsError):
        return not os.rmdir(expanduser(path))


#-------------------------------------------------------------------------------
def chmod(path, attr):
#-------------------------------------------------------------------------------
    """ changes the attributes of path """
    return not os.chmod(expanduser(path), attr)


#-------------------------------------------------------------------------------
def ln(*Args):
#-------------------------------------------------------------------------------
    """ ln [-s] <src> <dest>
        creates a hard (default) or symbolic link from src to dest
        -s - symbolic link
    """
    args, opts = __gopti("ln", Args, "s")

    if len(args) != 2:
        raise OSScriptsError("ln - needs 2 arguments")

    if sys.platform == 'win32':
        ## gets correct operation, just bigger files :-)
        return cp('-r', args[0], args[1])

    if opts.s:
        return os.symlink(args[0], args[1])
    os.link(args[0], args[1])


#-------------------------------------------------------------------------------
def cp(*Args):
#-------------------------------------------------------------------------------
    """ cp - just like unix cp. One or more files are copied to last specified arg

        usage: cp(['-rv'] | '<path>', '<file or path>')
           -v = verfiy
           -r = recursive
    """
    def __cp(src, dest, recurse, verify):
        if not recurse:
            shutil.copyfile(src, dest)
            if verify and not cmp(src, dest):
                raise OSScriptsError("cp: verify failed '%s' != '%s'\n" % (src, dest))
        else:
            if IsDir(src):
                shutil.copytree(src, dest)
            else:
                __cp(src, dest, False, verify)
        return True

    list, opts = __gopti('cp', Args, 'vr')

    if len(list) < 2:
        raise OSScriptsError("cp: need at least two parameters")

    if len(list) > 2 and not IsDir(list[-1]):
        return

    pfx = list[-1] + "/" if IsDir(list[-1]) else ""
    return all([__cp(p, list[-1], opts.r, opts.v) if pfx == "" else __cp(p, pfx + basename(p), opts.r, opts.v) for p in list[:-1]])


#-------------------------------------------------------------------------------
def cat(cmdLine):
#-------------------------------------------------------------------------------
    """ dumps file(s) to stdout

        usage: cat <filename1> [[<filename2>] ...]
    """
    def __cat(fileName):
        with ignoreException(IOError):
            with open(fileName, "rU") as inf:
                stdout.write(inf.read())
            return True

    args, opts = __gopti("cat", cmdLine)
    return all([__cat(fn) for fn in args])


#-------------------------------------------------------------------------------
def find(directory='.', filePattern='*.*', action=None, actionArg=None):
#-------------------------------------------------------------------------------
    """ Recursively walks directory <dir> looking for files that match
        FilePattern and calls the function Action (if not None) passing each
        filename and ActionArgs.
        It returns a list of all files found.
    """
    find_list = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _find1((pat, act, aarg), directory, files):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(pat, (str, unicode)):
            lst0 = fnmatch.filter(files, pat)
        else:
            lst0 = []
            for i in pat:
                lst0.extend(fnmatch.filter(files, i))

        lst = [os.path.join(directory, s) for s in lst0]
        find_list.extend(lst)
        return lst

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _find2((pat, act, aarg), directory, files):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for s in _find1((pat, act, aarg), directory, files):
            res = act(s, aarg) if aarg else act(s)
            if res is not None:
                print(s + '\n' + str(res))

    directory = expanduser(directory)
    func = _find2 if action else _find1
    os.path.walk(directory, func, (filePattern, action, actionArg))
    return find_list


#-------------------------------------------------------------------------------
def cmp(file1, file2, shallow=None):
#-------------------------------------------------------------------------------
    """ Compares two files. return true if files are the same. """
    return filecmp.cmp(expanduser(file1), expanduser(file2), shallow)


#-------------------------------------------------------------------------------
def splitFilename(fileName):
#-------------------------------------------------------------------------------
    """ returns the (path, name, ext) of 'fileName' """
    path, fnm = os.path.split(expanduser(fileName))
    nm, ext = os.path.splitext(fnm)
    return path, nm, ext


#-------------------------------------------------------------------------------
def splitext(fileName):
#-------------------------------------------------------------------------------
    """ returns the extension of a file name where:
        fileName = path + name + ext
    """
    return os.path.splitext(fileName)[1]


#-------------------------------------------------------------------------------
def splitnm(fileName):
#-------------------------------------------------------------------------------
    """ returns the name of the file where:
        fileName = path + name + ext
    """
    return os.path.splitext(basename(fileName))[0]


#-------------------------------------------------------------------------------
def getpath(fileName):
#-------------------------------------------------------------------------------
    """ returns the path of the file
        fileName = path + name + ext
    """
    return os.path.split(expanduser(fileName))[0]


#-------------------------------------------------------------------------------
def splitPath(fileName):
#-------------------------------------------------------------------------------
    """ returns the path and base filename as a tuple """
    path, fn = os.path.split(expanduser(fileName))
    if not path:  return './', fn
    return path, fn


#-------------------------------------------------------------------------------
def abspath(fileName):
#-------------------------------------------------------------------------------
    """ returns the absolute path in unix/python usage """
    return '/'.join(os.path.abspath(fileName).split('\\'))


#-------------------------------------------------------------------------------
def normpath(fileName):
#-------------------------------------------------------------------------------
    """ Normalize a pathname. This collapses redundant separators and
        up-level references so that A//B, A/./B and A/foo/../B all become A/B.
        It does not normalize the case (use os.path.normcase() for that).
    """
    return '/'.join(os.path.normpath(fileName).split('\\'))


#-------------------------------------------------------------------------------
def canonicalPath(fileName):
#-------------------------------------------------------------------------------
    """ returns a normalized path with extra directories removed and case converted
    """
    return os.path.normcase(os.path.abspath(expanduser(fileName)))

commonprefix = os.path.commonprefix


#-------------------------------------------------------------------------------
def relativePath(basePath, pth):
#-------------------------------------------------------------------------------
    """ returns the relative path of pth from basePath """
    bp = canonicalPath(basePath).split(os.sep)
    pt = canonicalPath(pth).split(os.sep)

    idx = 0; mx = len(bp)
    while idx < mx:
        if bp[idx] != pt[idx]:
            break
        idx += 1

    rp = [os.pardir] * (mx - idx)
    for i in range(idx, len(pt)):
        rp.append(pt[i])

    return os.sep.join(rp)


#-------------------------------------------------------------------------------
def findFilePathUp(fileName):
#-------------------------------------------------------------------------------
    """ search for file or directory above current working dir """
    ap = abspath(pwd())

    pth = ap  + '/'
    if exists(pth + fileName):
        return pth

    ap = abspath(pwd()).split('/')
    for idx in range(-1, -1 * len(ap), -1):
        pth = '/'.join(ap[:idx]) + '/'
        if exists(pth  + fileName):
            return pth


#-------------------------------------------------------------------------------
def commonPath(basePath, pth):
#-------------------------------------------------------------------------------
    """ removes the common 'basePath' from path 'pth' else return 'pth' """
    pt = canonicalPath(pth).split(os.sep)
    for idx, bb in enumerate(canonicalPath(basePath).split(os.sep)):
        if bb != pt[idx]:
            return pth
    return os.sep.join(pt[idx+1:])


#-------------------------------------------------------------------------------
def isAbsPath(fileName):
#-------------------------------------------------------------------------------
    return fileName and (os.path.isabs(fileName) or fileName[0] == '~')


#-------------------------------------------------------------------------------
def needsCompiled(fileName):
#-------------------------------------------------------------------------------
    """ determines if a '.py' file is newer then either a '.pyc' or '.pyo'
    """
    fname = splitnm(fileName)
    cfile = fname + '.pyc' if exists(fname + '.pyc') else None
    ofile = fname + '.pyo' if exists(fname + '.pyo') else None

    if cfile and ofile:
        bfile = cfile if newerthan(cfile, ofile) else ofile
    elif cfile:
        bfile = cfile
    elif ofile:
        bfile = ofile
    else:
        return True

    return newerthan(fname + '.py', bfile)


#-------------------------------------------------------------------------------
def touch(fileName, yr_time_none=None, mo=1, day=1, hr=0, Min=0, sec=0, APM=""):
#-------------------------------------------------------------------------------
    """ touch
        Sets a file's access time to either indicated time or current time
        - yr  : a time.time() value or an ASCII year value
        - mo  : month
        - day
        - hr
        - Min
        - sec
        - APM  : (AM | PM | "")
    """

    if yr_time_none is not None:
        ## float, than a time value
        if not isinstance(yr_time_none, float):
            h = int(hr)

            if APM == "PM":
                if h != 12: h = h + 12
            elif APM == "AM":
                if h == 12: h = 0

            t = time.mktime(int(yr_time_none), int(mo), int(day), h, int(Min), int(sec),0,0,0)
        else:
            ## time value
            t = yr_time_none
    else:
        t = time.time()

    fileName = expanduser(fileName)
    if not exists(fileName):
        with open(fileName, "w") as otf:
            pass

    os.utime(fileName, (t, t))


#-------------------------------------------------------------------------------
def fgrep(file_fileName, cmpStr, ignoreCase=None, lineNums=None):
#-------------------------------------------------------------------------------
    """ fgrep

        returns a list of strings that have a case sensitive or insentive match
          - file_fileName : open file or a filename
          - cmpStr         : string to grep for
          - ignoreCase     : case sensitive or not
          - lineNums       : include line numbers in output
    """
    lst = []
    try:
        f = file_fileName if isinstance(file_fileName, file) else open(expanduser(file_fileName))
        s = cmpStr.lower() if ignoreCase else cmpStr

        lineNum = 0;

        for line in f:
            lineNum += 1

            ln = string.lower(line) if ignoreCase else line
            try:
                if ln.find(s) >= 0:
                    lst.append((lineNum, line) if lineNums else line)
            except UnicodeDecodeError:
                pass
    finally:
        ## dont close what we didn't open
        if not isinstance(file_fileName, file):
            f.close()
    return lst


#-------------------------------------------------------------------------------
def SHASum(FileName):
#-------------------------------------------------------------------------------
    """ return SHA sum for 'FileName' or None
    """
    with ignoreException(IOError):
        with open(expanduser(FileName)) as inf:
            return hashlib.sha256(inf.read()).hexdigest()


#-------------------------------------------------------------------------------
def tmpfile(suffix = "", prefix = "", dir="/tmp"):
#-------------------------------------------------------------------------------
    """ Returns a temporary file name
    """
    f, name = tempfile.mkstemp(suffix, prefix)
    os.close(f)
    return name


#-------------------------------------------------------------------------------
def getmode(FileName):
#-------------------------------------------------------------------------------
    """ Returns the mode (permission) of the specified file
    """
    return os.stat(expanduser(FileName))[0]


#-------------------------------------------------------------------------------
def which(fileName):
#-------------------------------------------------------------------------------
    """ find the first executable file in the path
    """
    fileName = expanduser(fileName)
    if isExe(fileName):
        return fileName

    for p in env['PATH'].split(PATH_ELEM_SEP):
        tp = p + DIR_ELEM_SEP + fileName
        if isExe(tp):
            return tp


#-------------------------------------------------------------------------------
def deQuote(s):
#-------------------------------------------------------------------------------
    """ deQuote a string (typically fileName) returning a tuple of
        (True/False, 's' minus quotes)
    """
    if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return True, s[1:-1]
    return False, s


#-------------------------------------------------------------------------------
def FindExe(fileName, first=False, chkLocal=True):
#-------------------------------------------------------------------------------
    """ find the executable file 'fileName' in the system path and return a list
        of all occurances or if 'first' return first else None. 'chkLocal'
        specifies whether to check '.' (first if so)
    """
    quote, fileName = deQuote(fileName)
    fileName = expanduser(fileName)

    ## if has an actual path, just check that
    if ('/' in fileName or '\\' in fileName):
        if isExe(fileName):
            if quote:  fileName = '"' + fileName + '"'
            if first:  return fileName
            return [fileName]
        else:
            if first:  return
            return []

    ## check system paths
    pth = ['.'] + env['PATH'].split(PATH_ELEM_SEP) if chkLocal else env['PATH'].split(PATH_ELEM_SEP)

    lst = []
    for p in pth:
        tp = p + DIR_ELEM_SEP + fileName
        if isExe(tp):
            if quote:  tp = '"' + tp + '"'
            if first:  return tp
            lst.append(tp)

    if first:  return
    return lst


#-------------------------------------------------------------------------------
def FindExeExt(fileName, first=False, chkLocal=True):
#-------------------------------------------------------------------------------
    """ return a list (or first) of executable(s) for 'fileName' trying various
    known file extensions (msh, py, bat, exe)
    """
    quote, fileName = deQuote(fileName)

    if len(fileName.rsplit('.', 1)) == 2:
        v = FindExe(fileName, first, chkLocal)
        return v if v is None or not quote else '"' + v + '"'

    lst = []
    for ext in ['.msh', '.py', '.bat', '.exe']:
        v = FindExe(fileName + ext, chkLocal)
        if v is not None:
            if quote:  v = '"' + v + '"'
            if first:  return v
            lst.extend(v)

    if first:  return None
    return lst


__extensionCommands = {
    'py'  : 'python.exe ',
    'msh' : 'msh.exe -c ',
    'bat' : 'cmd.exe /c ',
    }

#-------------------------------------------------------------------------------
def getExe(fileName, chkLocal=True):
#-------------------------------------------------------------------------------
    """ search for an executable 'fileName' trying known extensions and adding
    corresponding interpreters if necessary.
    """
    v = FindExeExt(fileName, True, chkLocal)
    if v is None:  return

    print(v)
    ext = v.rsplit('.', 1)[-1]
    for e, c in __extensionCommands.items():
        if ext.startswith(e):   return c + v
    return v


#-------------------------------------------------------------------------------
def isExe(fileName):
#-------------------------------------------------------------------------------
    """ Returns a boolean indicating if the file has execute permission """
    fileName = expanduser(fileName)
    for e in __extensionCommands:
        if fileName.endswith('.' + e): return exists(fileName)
    return exists(fileName) and getmode(fileName) & 0111 != 0

IsExe = IsExecutable = isExe


#-------------------------------------------------------------------------------
def isWritable(fileName):
#-------------------------------------------------------------------------------
    """ Returns a boolean indicating if the file has write permission """
    return getmode(expanduser(fileName)) & 0222 != 0

IsWritable = isWritable

#-------------------------------------------------------------------------------
def isDir(name):
#-------------------------------------------------------------------------------
    """ Returns a boolean indicating if the name is a directory """
    return os.path.isdir(expanduser(name))

IsDir = isDir


#-------------------------------------------------------------------------------
def FileTime(fileName, attr="st_mtime"):
#-------------------------------------------------------------------------------
    """ Returns the filetime of a file 'fileName' as a printable string """
    return time.ctime(FileTimeInt(fileName, attr))


#-------------------------------------------------------------------------------
def FileTimeInt(fileName, attr="st_mtime"):
#-------------------------------------------------------------------------------
    """Returns the file time of 'filename' as an integer"""
    return getattr(os.stat(expanduser(fileName)), attr)


#-------------------------------------------------------------------------------
class path(str):
#-------------------------------------------------------------------------------
    """ path - special string type with properties returning useful elements """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getExt(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the extension """
        return splitext(self)

    ext = property(_getExt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getName(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the name """
        return splitnm(self)

    name = property(_getName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getFName(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the base name """
        return os.path.basename(self)

    basename = property(_getFName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getFPath(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the path (with drive letter) """
        return getpath(self)

    fpath = property(_getFPath)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getPath(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ path minus the drive letter if present """
        p = getpath(self)

        if len(p) > 1 and p[1] == ':':
            return p[2:]
        return p

    path = property(_getPath)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getDrive(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ the drive letter if present """
        if self[1] == ':':
            return self[0]
        return ''

    drive = property(_getDrive)

    drive_path = fpath

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getDrivePathName(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ full path and name minus extension """
        pth, nm, e = splitFilename(self)
        if pth:
            return pth + '/' + nm
        else:
            return nm

    drive_path_name = property(_getDrivePathName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getNameExt(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ name and extension minus any path """
        pth, nm, e = splitFilename(self)
        return nm + e

    name_ext = property(_getNameExt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def elems(self, beg = 0, end = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if end is None:
            end = len(self)
        lst = re.split("/|\\\\", self)
        return '/'.join(lst[beg:end])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        s.append('orig: ' + str(self))
        s.append('ext: ' + self.ext)
        s.append('name: ' + self.name)
        s.append('basename: ' + self.basename)
        s.append('fpath: ' + self.fpath)
        s.append('path: ' + self.path)
        s.append('drive: ' + self.drive)
        s.append('drive_path: ' + self.drive_path)
        s.append('drive_path_name: ' + self.drive_path_name)
        s.append('name_ext: ' +  self.name_ext)
        return '\n'.join(s)


#-------------------------------------------------------------------------------
def paths(lst):
#-------------------------------------------------------------------------------
    """ convert a list of strings into a list of paths
    """
    return [path(p) for p in lst]


#-------------------------------------------------------------------------------
def StartFile(fileName, err=None):
#-------------------------------------------------------------------------------
    ''' performs a Windows "OPEN/EXECUTE" on fileName '''
    try:
        os.startfile(expanduser(fileName))
        return True
    except WindowsError as ex:
        if err is not None: err.set(ex)


#-------------------------------------------------------------------------------
def mkusage(doc):
#-------------------------------------------------------------------------------
    class d(object):
        def __init__(self, doc):
            object.__init__(self)
            self.doc = doc

        def usage(self, rc, errmsg=""):
            _usage(rc, self.doc, errmsg)

    warnings.warn("deprecated", DeprecationWarning)
    return d(doc).usage


#-------------------------------------------------------------------------------
def _usage(rc, doc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information """
    warnings.warn("deprecated", DeprecationWarning)
    stderr.write(doc + '\n')
    if errmsg:
        stderr.write("\nError:\n" + str(errmsg) + '\n')
    exit(rc)

usage = _usage


#from pylib.options import mopt as gopt
from options import mopt as gopt


#
# Test functions
#

#-------------------------------------------------------------------------------
def __TestEnv():
#-------------------------------------------------------------------------------
    ''' test environment handler
    '''
    print('Home:', env['HOME'])
    print('UGGG:', env['UGGG'])
    env['AidanConnor'] = 'boo'
    env.export('AidanConnor')


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    import tester

    ## test cd, pwd, pushcd and popcd
    c = pwd()
    pushcd('/tmp')
    tester.Assert(abspath(pwd()) == abspath('/tmp'))
    popcd()
    tester.Assert(pwd() == c)

    dd = '/tmp/__osscripts__/test/'
    rm('-rf /tmp/__osscripts__')
    mkdirs(dd)

    echo('cool stuff\nmore cool stuff\n\nthen some\n', dd + 'osstest.txt')
    tester.Assert(fgrep(dd + 'osstest.txt', 'more') == ['more cool stuff\n'])
    tester.Assert(fgrep(dd + 'osstest.txt', 'MORE', ignoreCase=True) == ['more cool stuff\n'])
    tester.Assert(fgrep(dd + 'osstest.txt', 'More', ignoreCase=True, lineNums=True) == [(2, 'more cool stuff\n')])
    tester.Assert(SHASum(dd + 'osstest.txt') == '19d712bef35d3bc5eeed169ea9eb03278e3b7ba9fa143aee0bcb3a84510c254b')

    tester.Assert(replaceExt(['cool.txt', 'aidan.t', 'bob.exe'], 'py') == ['cool.py', 'aidan.py', 'bob.py'])

    f = r('ls.exe %s' % dd, '>'); s = f.read(); f.close()
    tester.Assert(s == 'osstest.txt\n')
    s = r('ls.exe %s' % dd, '$')
    tester.Assert(s == 'osstest.txt\n')
    s = r('ls.exe %s' % dd, '|')
    tester.Assert(s == 'osstest.txt\n')

    touch(dd + 'sara.py')
    r('ls.exe %s > /tmp/t' % dd)
    s = readf('/tmp/t', 1)
    tester.Assert(s == 'sara.py')



if __name__ == "__main__":
    import tester

    #---------------------------------------------------------------------------
    def RunCmd():
    #---------------------------------------------------------------------------
        """ runs cmd tests
            usage: osscripts [-h | --help | --help_cmd <cmd>] <cmd> <args ...>
        """
        args, opts = gopt(argv[1:], [('?', 'help')], [(None, 'help_cmd')], RunCmd.__doc__)

        #print "args:", args
        #print "opts:", opts

        import inspect
        m = __import__(__name__, globals())
        funcs = {}
        for fn, fo in inspect.getmembers(m, inspect.isfunction):
            funcs[fn] = fo

            if opts.help or opts.help_cmd == fn:
                print('-'*80)
                print(tester.GetFuncArgs(fn, fo))

        if opts.help or opts.help_cmd or not args:
            usage(1)

        print("RunCmd:", args)

        if args[0] in funcs:
            if len(args) > 1:
                print(funcs[args[0]](*args[1:]))
            else:
                print(funcs[args[0]]())
        else:
            print("Illegal Test Command", file=stderr)
            usage(2)

        exit()

    RunCmd()


