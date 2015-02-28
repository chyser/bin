#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import yaml
import pylib.osscripts as oss

JAVAC = 'javac'
VCS_ADD = 'hg add'

BUILD_PATH = './class'
CLASS_PATH = BUILD_PATH

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('f', 'force'), ('r', 'readonly'), ('m', 'makecmd')], [('c', 'cmdfile')], main.__doc__ + __doc__)

    global BUILD_PATH, CLASS_PATH


    if opts.cmdfile:
        if opts.makecmd and not oss.exists(opts.cmdfile):
            oss.touch(opts.cmdfile)

        with open(opts.cmdfile) as inf:
            dd = yaml.load(inf.read())
            if dd is None:
                dd = {}

            slist = dd['files'] if 'files' in dd else []
            BUILD_PATH = dd['build_path'] if 'build_path' in dd else './class'
            CLASS_PATH = dd['class_path'] if 'class_path' in dd else BUILD_PATH

            if not slist:
                slist = oss.find('.', "*.java")

            if 'cmds' in dd:
                CMDS = dd['cmds']
            else:
                CMDS = ['compile']


        if opts.makecmd:
            oss.mv(opts.cmdfile, opts.cmdfile + '.bak')
            with open(opts.cmdfile, 'w') as otf:
                slist.extend(oss.find('.', "*.java"))

                ## ensure names are unique
                s = set(slist)
                slist = [a for a in s]

                dd['files'] = slist
                otf.write(yaml.safe_dump(dd))

    else:
        CMDS = ['compile']
        slist = oss.find('.', "*.java")

    if args:
        CMDS = args

    rc = 0
    for cmd in CMDS:
        if rc != 0:
            oss.exit(rc)

        if cmd == 'compile':
            rc = compile(JAVAC, slist, opts.force, opts.readonly)

        elif cmd.startswith('run '):
            c = cmd[4:].strip()
            print(c)
            rc = oss.r(c)

        elif cmd == 'vcs_add':
            addToVcs(VCS_ADD, slist)


    oss.exit(0)


#-------------------------------------------------------------------------------
def compile(javac, srcList, force=False, readOnly=False, stopFirst=True):
#-------------------------------------------------------------------------------
    rc = 0
    for sc in srcList:
        pth, fn = sc.rsplit('\\', 1)
        pth1 = pth.split('\\', 2)[2]

        cdir = BUILD_PATH + '/' + pth1
        oss.mkdirs(cdir)

        fd = fn.rsplit('.', 1)[0]
        nf = cdir + '/' + fd + '.class'
        if force or not oss.exists(nf) or oss.newerthan(sc, nf):
            cmd = javac + " -cp %s -d %s %s" % (CLASS_PATH, BUILD_PATH, sc)

            print(cmd)
            if not readOnly:
                rc = oss.r(cmd)

                if rc and stopFirst:
                    oss.exit(rc)

    return rc


#-------------------------------------------------------------------------------
def addToVcs(vcsAdd, srcList):
#-------------------------------------------------------------------------------
    for f in srcList:
        cmd = vcsAdd + ' ' + str(f)
        print(cmd)
        oss.r(cmd)


if __name__ == "__main__":
    main(oss.argv)
