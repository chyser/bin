#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import pylib.osscripts as oss
import sys, traceback
import time, thread


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    runit.py [-p] [-b] [-m] [-k] [-x] [-d <PathDir>] <script>
        -p | --pause    : pause after completion
        -b | --build    : generate build style output
        -m | --nomain   : disable calling main
        -k | --nomake   : disable running make
        -x | --nodebug  : disable debug flag
        -a | --absdir   : absolute path given, don't use for wkdir
        -d | --wkdir <PathDir> : directory where program is
        <script>: script to run or 'build'

    runit supports execution of python scripts from within Slickedit.  Since a
    window is created on execution (and is destroyed upon completion), console
    programs need to block on user input to allow execution results to be
    seen.  -p does this.  Also, exceptions often cause the blocking code to be
    bypassed, such that errors cannot be seen at all.  Even when visible, the
    default dump format is not easily parsed by editors.  -b does this.  Many
    forms of errors can be detected by 'importing' the program without running
    the main code.  -m does this.

    -d or providing the full path in the script names allows local directory
    modules to be found as if the script was run directly from the local
    directory.

    Version 1.0
    """
    args, opt = oss.gopt(argv[1:], [('p', 'pause'), ('b', 'build'), ('m', 'nomain'),
                   ('k', 'nomake'), ('x', 'nodebug'), ('a', 'absdir')], [('d', 'wkdir')], main.__doc__)

    oss.echo("die", "/tmp/runit_die")
    time.sleep(2)
    oss.rm("/tmp/runit_die")

    if not args:
        opt.usage(1, "Must supply a program to run")

    prgmName = oss.path(args[0])

    if opt.wkdir is None:
        pdir = prgmName.drive_path
        opt.wkdir = pdir if pdir and opt.absdir else '.'

    if 0:
        thread.start_new_thread(look_out, (1,))

    global moduleName, fileName, globd

    moduleName = prgmName.name
    fileName = prgmName.drive_path_name + '.py'

    globd = {}
    exec('import sys', globd)

    ## enable local modules to be found
    wd = oss.abspath(opt.wkdir)
    globd['sys'].path.insert(0, wd)

    ## if calling main is disabled, use build semantics
    if opt.nomain:
        opt.build = True

    try:
        ## recreate argv
        globd['sys'].argv = [fileName] + args[1:]

        ## if calling main is disabled, change name
        globd["__name__"] = "__main__" if opt.nomain is None else moduleName

        if opt.nodebug is not None:
            globd["__debug__"] =  True

        if opt.build is None:
            print("CmdLine: '%s'" % " ".join(globd['sys'].argv))

        ## run a makefile if it exists
        if opt.nomake is None:
            if oss.exists("make.pmk") or oss.exists("nmake.pmk"):
                oss.r('python C:\\bin\\pmake.py')
            elif oss.exists("makefile"):
                oss.r('make')

        sys.path = globd['sys'].path
        sys.argv = globd['sys'].argv
        reload(oss)

        sys.modules['runit'] = sys.modules['__main__']
        try:
            sys.modules['__main__'] = __import__(moduleName)
        except ImportError:
            print(sys.path, file=oss.stderr)

        try:
            execfile(sys.modules['runit'].fileName, sys.modules['runit'].globd)
        except SystemExit:
            pass

        if opt.pause and not opt.build:
            print("-- continue --")
            sys.stdin.readline()

    except Exception:
        if opt.build:
            ## print error message(s) in form many editors can parse
            t, v, tb = sys.exc_info()

            traceback.print_exc()

            print(traceback.extract_tb(tb))

            tbl = traceback.extract_tb(tb)[-1]
            s = traceback.format_exception_only(t,v)

            err = "".join(s)

            if s[0].find('File') != -1:
                l = s[0].split()
                print("%s(%s):\n" % (l[1].split('"')[1], l[3]), err)
            else:
                print("%s(%d):\n" % (tbl[0], tbl[1]), err)
        else:
            ## standard dump semantics
            traceback.print_exc()
            print("-- continue --")
            sys.stdin.readline()


#-------------------------------------------------------------------------------
def look_out(a):
#-------------------------------------------------------------------------------
    while 1:
        time.sleep(1)
        if oss.exists("/tmp/runit_die"):
            print("killing main")
            thread.interrupt_main()
            raise BaseException()


if __name__ == "__main__":
    main(oss.argv)

