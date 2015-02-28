#!/usr/bin/env python
"""
usage: lnexe [options] <prgm name>

creates a bat file in C:/bin pointing to the specified program. If the program
is interpreted, specifies the correct interpreter.

options:
    -n : --nowin    | specifies that a console window shoudln't be created for gui apps
    -d : --debug    | specify the python debug flag
    -f : --filename | specifiy the name of the result link file (versus orig file
                       with .bat extension

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)

ArgLoop = '''@echo off
set ARGS=%1
if ""%1""=="""" goto l2
shift
:l1
if ""%1""=="""" goto l2
set ARGS=%ARGS% %1
shift
goto l1
:l2
rem echo %ARGS%
'''

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('n', 'nowin'), ('d', 'dbg')], [('f', 'filename')], usage)

    pn = oss.path(args[0])

    cmd = []
    if pn.ext == '.py':
        if opts.nowin:
            cmd.append('python.exe')
        else:
            cmd.append('pythonw.exe')

    if opts.dbg:
        cmd.append('-d')

    if opts.filename is None:
        opts.filename = pn.name + '.bat'
    else:
        if not opts.filename.endswith('.bat'):
            opts.filename += '.bat'

    cmd.append(oss.abspath(args[0]))
    cmd.append('%ARGS%')


    otf = file('C:/bin/' + opts.filename, 'w')

    print >> otf, ArgLoop
    print >> otf, ' '.join(cmd)

    otf.close()



    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)
