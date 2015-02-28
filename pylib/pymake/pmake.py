#!/usr/bin/env python
"""
pmake runs a python interpreter over marked areas of a makefile, then runs the
appropriate make command
"""

_HELP_MSG = """
File Format:
    The first line of the file can have a special format:

        PROJECT = <type> [<tool> [<revision>]]
        ex:
            PROJECT = CPP VC 9
            PROJECT = PYTHON
            PROJECT = CPP GCC

    Embedded Python Code:
        - surround code like: @@@<code>@@@
        - makefile variables are read and understood by python code
        - python variables are passed to makefile
        - examples:
                   makefile                       python code
            OBJS = a.obj b.obj c.obj  <--> OBJS = ['a.obj', 'b.obj', 'c.obj']
            FILES = $(OBJS)           <--> FILES = OBJS
            FILES += $(SOURCE)        <--> FILES.extend(list(SOURCE))

"""

import StringIO, re
import sys, traceback
import pylib.osscripts as oss
import platform
import os
import time

__version__ = 1.2

if sys.platform == 'win32':
    __IncPath = r"C:\bin\pylib\pylib\pymake\makefile.inc"
else:
    __IncPath = "~/makefile.inc"


#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    """ usage: pmake [Options] [<target> [<target> ...]]

    pmake runs a python interpreter over marked areas of a makefile, then runs the
    appropriate make command

    Options:
        -f | --file  <file>     : specify makefile
        -r | --recurse          : recurse into subdirectories (first)
        -C | --directory <dir>  : change to directory first
        -m | --make <cmd>       : specify make command to run (ex nmake)
        -p | --project          : build makefile only
        -D | --define           : define variables

        -P | --pause            : pause the window after execution

        -h | --help             : extended help
"""
    args, opts = oss.gopt(oss.argv[1:], [('p', 'project'), ('h', 'help'), ('v', 'verbose'), ('F', 'force'), ('P', 'pause'), ('r', 'recurse')],
        [('f', 'file'), ('D', 'define'), ('m', 'make'), ('C', 'directory'), ('j', 'jobs'), ('W', 'wait')], main.__doc__)

    if opts.help:
        print _HELP_MSG
        usage(0)

    jobs = '' if opts.jobs is None else ' -j ' + opts.jobs

    if opts.directory:
        print "Changing to directory:", opts.directory
        try:
            oss.cd(opts.directory)
        except WindowsError:
            usage(1, "Can't find directory")

    ret = 0
    if opts.recurse:
        for root, dirs, files in os.walk('.', topdown=False):
            for name in dirs:
                pth = os.path.join(root, name)
                oss.pushcd(pth)
                ret += doFile(pth, opts.file, opts.make, jobs, opts, args)
                oss.popcd()

    ret += doFile('.', opts.file, opts.make, jobs, opts, args)

    if opts.pause:
        raw_input('pausing ...')

    if opts.wait:
       print 'pausing ... (%s secs)' % opts.wait
       time.sleep(int(opts.wait))

    oss.exit(ret)


#-------------------------------------------------------------------------------
def doFile(ddir, mfile, make, jobs, opts, args):
#-------------------------------------------------------------------------------
    if mfile is not None:
        makefile = mfile
        make = "nmake"

        if not oss.exists(makefile):
            print "%s doesn't exist" % makefile
            return 0

    else:
        if oss.exists('make.pmk'):
            makefile = 'make.pmk'
            makeCmd = 'make --win32' + jobs
        elif oss.exists('nmake.pmk'):
            makefile = 'nmake.pmk'
            makeCmd  = 'nmake'
        elif oss.exists('makefile'):
            makefile = 'makefile'
            makeCmd  = 'make --win32' + jobs
        else:
            return 0

    print '\nmaking:', ddir
    if make:
        makeCmd = make

    outfile = '/tmp/' + makefile + ".mak"

    tgtfile = makefile + ".mak"

    ret = 0
    try:
        GenMakefile(makefile, tgtfile, makeCmd)

        ret = 0
        cmd = ["%s -f %s" % (makeCmd, tgtfile)]

        if opts.define is not None:
            cmd.extend(['-D' + opts.define] if isinstance(opts.define, str) else ['-D %s' % d for d in opts.define])

        cmd.extend(args)
        cmd = ' '.join(cmd)

        print cmd
        print '-----------------------------------'
        ret = os.system(cmd)

    except Exception:
        traceback.print_exc()
        oss.rm(outfile)
        return 11

    return ret


#-------------------------------------------------------------------------------
def formatIt(v):
#-------------------------------------------------------------------------------
    try:
        if isinstance(v, str):
            return v
        return " ".join(v)
    except:
        return str(v)


#-------------------------------------------------------------------------------
def ExecPythonCode(globals, pcode):
#-------------------------------------------------------------------------------
    """ execute python code embedded in  makefile

        - embedded code is replaced by stdout
        - all "new" uppercase variables become makefile vars assigned
          appropriate contents
    """

    ## printing to stdout in executed code will be placed into makefile
    out = StringIO.StringIO()
    sys.stdout = out

    try:
        exec pcode in globals
    except Exception:
        type, value, tb = sys.exc_info()
        print >> sys.stderr, "Python Exception"
        print >> sys.stderr, "-"*20
        for idx, line in enumerate(pcode.split('\n')):
            print >> sys.stderr, "%03d: %s" % (idx+1, line)
        print >> sys.stderr, "-"*20
        raise

    sys.stdout = sys.__stdout__
    s = out.getvalue() + ' '
    out.close()

    return s


#-------------------------------------------------------------------------------
def PrintVariables(globals, oldglobals):
#-------------------------------------------------------------------------------
    pb = []
    for nm in globals:
        if not nm.startswith('_') and nm.isupper() and (nm not in oldglobals or globals[nm] != oldglobals[nm]):
            s = "\n%s = %s" % (nm, formatIt(globals[nm]))
            if len(s) > 75:
                s += '\n'
            pb.append(s)
    return ''.join(pb)


asgn = re.compile(r"(\w+)\s*=(.*)")
apnd = re.compile(r"(\w+)\s*\+=(.*)")


#-------------------------------------------------------------------------------
def ParseMakefile(makefile, otf, globals, LineNum = sys.maxint):
#-------------------------------------------------------------------------------
    try:
        inf = file(makefile, 'rU')
    except IOError:
        usage(1, "Cannot open input file: " + makefile)

    state = linenum = 0
    for line in inf:
        if linenum == LineNum:
            break
        linenum += 1

        ## state == 0 is 'makefile syntax' mode
        if state == 0:

            #
            # let simple make variable assignments be available to python code
            #

            am = asgn.match(line)
            if am is not None:
                ## s = cool
                sym = am.group(1)
                if not sym.startswith('__'):
                    globals[sym] = am.group(2).split()

            else:
                ## s += cool
                am = apnd.match(line)
                if am is not None:
                    sym = am.group(1)
                    if not sym.startswith('__'):
                        if sym not in globals:
                            s = sym + " = " + str(am.group(2).split())
                        else:
                            if isinstance(globals[sym], (str, unicode)):
                                globals[sym] = globals[sym].split()
                            globals[sym].extend(am.group(2).split())

            if line.startswith('include '):
                fn = line.split()[1]


        #
        # walk line looking for python code substitutions
        #
        idx = 0; inline = False
        while idx < len(line):

            ## if in 'makefile syntax' mode
            if state == 0:
                ## should we switch to 'python code' mode
                if line[idx:idx+3] == '@@@':
                    ## yes
                    state = 1;  pcode = []

                    ## assume python code will be inserted into a line
                    inline = True
                    idx += 3
                    continue

                ## translate 8 spaces to tab as general cleanup for a pmake file
                if idx == 0 and line[idx:idx+8] == ' '*8:
                    otf.write('\t')
                    idx += 7
                else:
                    otf.write(line[idx])

            ## if in 'python code' mode
            elif state == 1:
                if line[idx:idx+3] == '@@@':
                    state = 0
                    idx += 3

                    og = dict(globals)
                    s = ExecPythonCode(globals, "".join(pcode))

                    ## did we encounter switch mode while on same line?
                    if inline:
                        otf.write(s)
                    else:
                        otf.write(PrintVariables(globals, og) + '\n')
                        otf.write(s + '\n')
                else:
                    pcode.append(line[idx])

            idx += 1

    ##  if end of input but still in 'python code' mode, execute the code now
    if state == 1:
        s = ExecPythonCode(globals, "".join(pcode))
        if inline:
            otf.write(s)
        else:
            otf.write(PrintVariables(globals, {}) + '\n')
            otf.write(s + '\n')

    inf.close()


#-------------------------------------------------------------------------------
def prepGlobals(globals):
#-------------------------------------------------------------------------------
    """ shove some useful stuff into globals
    """

    exec """
from osscripts import *
from pylib.pymake.pmakelib import *
import pylib.pymake.pmakelib
pylib.pymake.pmakelib.SetMakeFileName(MAKEFILE_NAME)
""" in globals


#-------------------------------------------------------------------------------
def GenMakefile(makefile, outfile, make):
#-------------------------------------------------------------------------------
    try:
        otf = file(outfile, 'w')
    except IOError:
        usage(1, "Cannot open output file: " + outfile)

    try:
        ## populate globals with some useful stuff
        globals = {
            "MAKEFILE_NAME" : outfile,
            "MAKE_EXE"      : make,
            "PMAKE_VERSION" : __version__,
            "OS"            : oss.env["OS"],
            "UNAME"         : ' '.join(platform.uname()),
        }

        prepGlobals(globals)

        ## parse first line of makefile to see if "PROJECT" is set
        ParseMakefile(makefile, otf, globals, 1)

        ## parse the automatic include file
        otf.write('\n\n#------------------------------------------------------\n')
        otf.write('# include ' + __IncPath + '\n')
        otf.write('#------------------------------------------------------\n')
        ParseMakefile(__IncPath, otf, globals)

        ## parse the rest of the file
        otf.write('\n\n#------------------------------------------------------\n')
        otf.write('# makefile \n')
        otf.write('#------------------------------------------------------\n')
        ParseMakefile(makefile, otf, globals)

    finally:
        otf.close()






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

