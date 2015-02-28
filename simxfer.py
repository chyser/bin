#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.relib as reb

#SCP = 'C:\\Program~1\\putty\\pscp.exe'
SCP = 'C:\\bin\\pscp.bat'
SSH = 'C:\\bin\\plink.bat'

OPTIONS = ' -l chrish -p -r -pw kibsop) '
SSH_OPTIONS = ' -l chrish -pw kibsop) '


FLU01 = 'compflu-01.hpl.hp.com:work/sdc.hpl.hp.com/sim/'
FLU02 = 'compflu-02.hpl.hp.com:sdc.hpl.hp.com/sim/'

FLU = FLU01

SSHFLU  = 'compflu-01.hpl.hp.com'
SSHFLUN = 'work/sdc.hpl.hp.com/sim/'

machines = {
    'flu-01' : ('compflu-01.hpl.hp.com', 'work/sdc.hpl.hp.com/sim/'),
    'flu-02' : ('compflu-02.hpl.hp.com', 'sdc.hpl.hp.com/sim/'),
}


DBG = None

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: simxfer.py [options] <src_file> [<src_file> ...]

    src_file can be a file name(s) with or without wildcards or a directory. It
    cannot contain path elements

    options:
        -t | --to    : xfer the src file 'src_file' to 'dest_file' on remote system
        -f | --from  : xfer src file on remote system to local file dest_file
        -m | --mach  : spcify machine flu-01 or flu-02. default = flu-02
    """
    usage = oss.mkusage(main.__doc__)
    args, opts = oss.gopt(argv[1:], [('t', 'to'), ('f', 'from_'), ('l', 'list'), ('d', 'dbg')], [('m', 'mach')], usage, expandWildCards=False)

    if len(args) < 1:
        usage(1, 'must specify a target(s)')
        oss.exit(0)

    if opts.dbg:
        global DBG
        DBG = True

    l, a = getPath(oss.pwd(), 'sim', 0)
    a += '/'

    mach = 'flu-02' if opts.mach is None else opts.mach
    mp = machines[mach]

    if opts.list:
        r(SSH + SSH_OPTIONS + mp[0] + ' ls -xp "' + mp[1] + a + args[0] + '"')
        oss.exit(0)

    scpPath = mp[0] + ':' + mp[1]

    if '/' in args[0]:
        usage(2, "target cannot be a path")

    if opts.to:
        for arg in args:
            localFile = l + a + arg
            if oss.isDir(localFile):
                r(SCP + OPTIONS + localFile + ' "' + scpPath + a + arg + '"')
            else:
                r(SCP + OPTIONS + localFile + ' "' + scpPath + a + '"')

        oss.exit(0)

    if opts.from_:
        for arg in args:
            localFile = l + a + arg
            if oss.isDir(localFile):
                r(SCP + OPTIONS + ' "' + scpPath + a + arg + '" ' + localFile)
            else:
                r(SCP + OPTIONS + ' "' + scpPath + a + arg + '" ' + '.')

        oss.exit(0)


    r(SSH + SSH_OPTIONS + mp[0] + ' ls -xp "' + mp[1] + a + args[0] + '"')
    oss.exit(0)



#-------------------------------------------------------------------------------
def getPath(pth, dd, dropTail=0):
#-------------------------------------------------------------------------------
    p = reb.splitPath(pth)

    ln = len(p)
    idx = -1
    if p[idx] != dd:
        while idx != -ln and p[idx] != dd:
            idx -=1

    idx = ln if idx == -ln or idx == -1 else idx + 1

    if dropTail == 0:
        dropTail = ln
        after = ''
    else:
        after = '/'
    return '/'.join(p[:idx]) + '/', '/'.join(p[idx:dropTail]) + after


#-------------------------------------------------------------------------------
def expandWCs(arg):
#-------------------------------------------------------------------------------
    """ expand wildcards like "*.py", "c?c?.py", "tmp[1234].py"
        won't expand if surrounded  ' or "
    """
    if arg[0] in set(['"', "'"]) and arg[-1] in set(['"', "'"]):
        return [arg[1:-1]]

    if '*' in arg or '?' in arg or ('[' in arg and ']' in arg):
        return glob.glob(arg)

    return [arg]


#-------------------------------------------------------------------------------
def r(s):
#-------------------------------------------------------------------------------
    print(s)
    if not DBG:
        oss.r(s)



if __name__ == "__main__":
    main(oss.argv)


