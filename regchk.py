import sys
from _winreg import *
import pylib.osscripts as oss

KEYS = [
    r'Software\Microsoft\Windows\CurrentVersion\Run',
    r'Software\Microsoft\Windows\CurrentVersion\RunOnce',
    r'Software\Microsoft\Windows\CurrentVersion\RunOnceEx',
    r'Software\Microsoft\Windows\CurrentVersion\RunServices',
    r'Software\Microsoft\Windows\CurrentVersion\RunServicesOnce']

FILE = r'C:\bin\pylib\regkeys.txt'

#-------------------------------------------------------------------------------
def ChkRegKey(KeyStr):
#-------------------------------------------------------------------------------
    k = OpenKey(HKEY_LOCAL_MACHINE, KeyStr)
    sk, sv, d = QueryInfoKey(k)

    vals = []
    for i in range(0, sv):
        vals.append(EnumValue(k, i)[0])

    keys = []
    for i in range(0, sk):
        keys.append(EnumKey(k, i))

    vals.sort()
    keys.sort()
    return(keys, vals)

#-------------------------------------------------------------------------------
def ReadRegKeyFile(FileName):
#-------------------------------------------------------------------------------
    try:
        f = file(FileName)
    except IOError:
        print >> sys.stderr, "Can't open file:", FileName
        sys.exit(2)

    l = []
    for i in f:
        l.append(i[:-1])
    return l

#-------------------------------------------------------------------------------
def WriteRegKeyFile(FileName, lst):
#-------------------------------------------------------------------------------
    try:
        f = file(FileName, 'w')
    except IOError:
        print >> sys.stderr, "Can't open file:", FileName
        sys.exit(2)

    for i in lst:
        print >> f, i


#-------------------------------------------------------------------------------
def usage(err, s):
#-------------------------------------------------------------------------------
    print >> sys.stderr, """
usage: regchk
  -a | --add : add current values to check file
"""
    sys.exit(err)


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if (__name__ == "__main__"):
    args, opts = oss.gopt(oss.argv[1:], [("a", "add")], [], usage)

    l = []
    for KeyStr in KEYS:
        try:
            k, v = ChkRegKey(KeyStr)
            l.extend(k)
            l.extend(v)
        except:
            ## windows 2000 doesn't have all the keys
            pass

    ret = 0
    if opts.add:
        WriteRegKeyFile(FILE, l)
    else:
        Old = ReadRegKeyFile(FILE)
        for i in l:
            if i not in Old:
                print i
                ret = 1

    if ret: raw_input('registry "run" key changed')

    sys.exit(ret)
