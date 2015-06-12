#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import glob

class MOptException(Exception): pass

#-------------------------------------------------------------------------------
class OptionClass(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, usageStr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self._usageStr_ = usageStr

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __contains__(self, x):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self[x] is not None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, x):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self, x)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, attr, default=None, cls=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        val = getattr(self, attr)
        if val is None:
            return default

        if cls is not None:
            try:
                val =  cls(val)
            except ValueError as ex:
                self.usage(101, "option: '%s' has '%s'" % (val, str(ex)))
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def usage(self, rc, s=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        """
        if self._usageStr_ is None:
            print('No help provided\n', file=sys.stderr)
            sys.exit(rc)

        if isinstance(self._usageStr_, (unicode, str)):
            print(self._usageStr_ + '\n' + str(s), file=sys.stderr)
            sys.exit(rc)
        else:
            self._usageStr_(rc, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logError(self, __d__, d, v=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #import pprint

        print('OptionClass.validate():')
        print('   ', self.__dict__, '\n')
        #pprint.pprint(self.__dict__)
        #pprint.pprint(d, '\n')
        if v is not None:
            print(v, '\n')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def validate(self, d):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        v = set(self.__dict__) - set(d)
        if v:
            return self.logError(self.__dict__, d, v)

        v = set(d) - set(self.__dict__)
        if v:
            return self.logError(self.__dict__, d, v)

        noFirstError = True
        for key, val in self.__dict__.items():
            if d[key] != val:
                if noFirstError:
                    noFirstError = self.logError(self.__dict__, d)
                print('    key:', key, ', d:', d[key], ', __dict__:', val)

        if not noFirstError: print()
        return noFirstError

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
def mopt(cmdLineArgs, oneOnlyFlags, oneOnlyParams, *args, **kwds):
#-------------------------------------------------------------------------------
    """ parses cmdLineArgs for options and arguments. options are normally
        identified by a leading '-'.

        mopt(cmdArgs, oneOnlyFlags, oneOnlyParams, usageStr="", **keyword)
        mopt(opt, oneOnlyFlags, oneOnlyParams, usageStr="", **keyword)

        mopt(cmdArgs, oneOnlyFlags, oneOnlyParams, multipleFlags, multipleParams, usageStr="", **keywords)
        mopt(opt, oneOnlyFlags, oneOnlyParams, multipleFlags, multipleParams, usageStr="", **keywords)

        Keyword arguments:
            addHelp         : automatically call usage for -? or --help', default: True
            nonOpStopOp     : '-'s are ignored after first non-option, default: True
            skipUnknownOps  : if True, put unknown options into arg list, else call usage with error. default: False
            allowMultiChar  : if False, '-abcd' means options a, b, c, and d, else it is option 'abcd'. default: False
            shortOpMarker   : marker when leading char used to identify short options. default: '-'
            longOpMarker    : marker when leading char used to identify long options. default: '--'
            expandWildCards : expand wildcards in arguments (assume they are files). default: True

        oneOnlyFlags, oneOnlyParams, multipleFlags and multipleParams are lists of:
            - tuples (<short form>, <long form>)
            - string
                if single char is short form, else long form

        usageStr may be either a string or a function to be used as to
        display a usage message to stderr.

        The long form value (or short if short form only) becomes an
        attribute of the option class and will be set to None or [] if not
        explicitely set. If an option is listed both as a flag and as a
        param, then it always tries to fill the param with the next command
        line arg unless it is last, in which case it does not generate a
        error (usage call).

        Arguments are checked for wildcards and expanded if expandWildCards
        is True. Expansion mimics unix shells {*.py, co??l.py, abc[123].py)
        and can be excaped by quotes ['"].

        If mopt() is called multiple times with a prior OptionClass 'opt'
        instead of a cmd line, further processing can occur on the remaining
        command line options. This usually implies the first call had
        skipUnknownOps = True.

        Returns tuple (list of arguments, OptionClass instance)
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cvt(options, opts, sopt, lopt, val=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        shortVals = {};  longVals = set()

        for opt in options:
            if isinstance(opt, unicode):
                shortV, longV = (opt, None) if sopt and len(opt) == 1 else (None, opt)
            else:
                shortV, longV = opt

            if shortV:
                name = shortV if longV is None else longV
                if not hasattr(opts, name):
                    name = shortV if longV is None else longV

                    ## note, each one should have a different list of not None
                    setattr(opts, name, None if val is None else [])
                shortVals[sopt + shortV] = name

            if longV:
                if not hasattr(opts, longV):
                    ## note, each one should have a different list of not None
                    setattr(opts, longV, None if val is None else [])
                longVals.add(lopt + longV)

        return shortVals, longVals

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expandWCs(arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ expand wildcards like "*.py", "c?c?.py", "tmp[1234].py"
            won't expand if surrounded  ' or "
        """
        if arg[0] in set(['"', "'"]) and arg[-1] in set(['"', "'"]):
            return [arg[1:-1]]

        if '*' in arg or '?' in arg or ('[' in arg and ']' in arg):
            return glob.glob(arg)

        return [arg]


    ## allow multiple calls by passing in the prior opt class
    if isinstance(cmdLineArgs, OptionClass):
        opts = cmdLineArgs
        cmdLineArgs = opts._args_
    else:
        opts = None

    ## parse out keyword arguments
    addHelp         = kwds.get('addHelp', True)
    nonOpStopOp     = kwds.get('nonOpStopOp', True)
    skipUnknownOps  = kwds.get('skipUnknownOps', False)
    allowMultiChar  = kwds.get('allowMultiChar', False)
    shortOpMarker   = kwds.get('shortOpMarker', '-')
    longOpMarker    = kwds.get('longOpMarker', '--')
    expandWildCards = kwds.get('expandWildCards', True)

    k = set(['addHelp', 'nonOpStopOp', 'skipUnknownOps', 'allowMultiChar', 'shortOpMarker', 'longOpMarker',  'expandWildCards'])

    if set(kwds) - k:
        raise MOptException("illegal keyword(s): " + str(set(kwds) - k))

    lopt = shortOpMarker if allowMultiChar else longOpMarker

    ## parse out arguments
    la = len(args)
    if la == 0 or la == 1:
        usageStr = '' if la == 0 else args[0]
        assert not isinstance(usageStr, list)
        if opts is None:
            opts = OptionClass(usageStr)
        shortMultipleFlags = longMultipleFlags = shortMultipleParams = longMultipleParams = set()

    elif la == 2 or la == 3:
        usageStr = '' if la == 2 else args[2]
        assert not isinstance(usageStr, list)
        if opts is None:
            opts = OptionClass(usageStr)

        if not (isinstance(args[0], (list, tuple)) and isinstance(args[1], (list, tuple))):
            raise TypeError('mopt() takes either 3-4 or 5-6 arguments (not counting keyword only args')

        shortMultipleFlags,  longMultipleFlags  = cvt(args[0], opts, shortOpMarker, lopt, 'list')
        shortMultipleParams, longMultipleParams = cvt(args[1], opts, shortOpMarker, lopt, 'list')

    else:
        raise TypeError('mopt() takes either 3-4 or 5-6 arguments (not counting keyword only args')

    shortSingleFlags,  longSingleFlags  = cvt(oneOnlyFlags,  opts, shortOpMarker, lopt)
    shortSingleParams, longSingleParams = cvt(oneOnlyParams, opts, shortOpMarker, lopt)

    opts._cmdline_ = cmdLineArgs
    opts._args_ = oargs = []

    if not allowMultiChar:
        ## convert ['-acbd'] to ['-a', '-c', '-b', '-d']
        cargs = []
        for arg in cmdLineArgs:
            if arg.startswith(lopt):
                cargs.append(arg)
            elif arg.startswith(shortOpMarker) and len(arg) > 2:
                for c in arg[1:]:
                    cargs.append(shortOpMarker + c)
            else:
                cargs.append(arg)
    else:
        cargs = cmdLineArgs

    #print('cargs:', cargs)

    idx = 0
    while idx < len(cargs):
        arg = cargs[idx]

        if addHelp:
            if arg == shortOpMarker + '?' or arg == lopt + 'help':
                opts.usage(0)

        if arg in shortSingleParams:
            idx += 1
            try:
                val = cargs[idx]
            except IndexError:
                ## allows the last option to also be a flag if no following parameter
                if arg not in shortSingleFlags:
                    opts.usage(10001, 'parameter "%s" has no parameter' % arg)
                val = True
            setattr(opts, shortSingleParams[arg], val)

        elif arg in longSingleParams:
            idx += 1
            try:
                val = cargs[idx]
            except IndexError:
                ## allows the last option to also be a flag if no following parameter
                if arg not in longSingleFlags:
                    opts.usage(10001, 'parameter "%s" has no parameter' % arg)
                val = True
            setattr(opts, arg[len(lopt):], val)

        elif arg in shortMultipleParams:
            idx += 1
            try:
                val = cargs[idx]
            except IndexError:
                ## allows the last option to also be a flag if no following parameter
                if arg not in shortMultipleFlags:
                    opts.usage(10001, 'parameter "%s" has no parameter' % arg)
                val = True
            getattr(opts, shortMultipleParams[arg]).append(val)

        elif arg in longMultipleParams:
            idx += 1
            try:
                val = cargs[idx]
            except IndexError:
                ## allows the last option to also be a flag if no following parameter
                if arg not in longMultipleFlags:
                    opts.usage(10001, 'parameter "%s" has no parameter' % arg)
                val = True
            getattr(opts, arg[len(lopt):]).append(val)

        elif arg in shortSingleFlags:
            setattr(opts, shortSingleFlags[arg], True)

        elif arg in longSingleFlags:
            setattr(opts, arg[len(lopt):], True)

        elif arg in shortMultipleFlags:
            getattr(opts, shortMultipleFlags[arg]).append(True)

        elif arg in longMultipleFlags:
            getattr(opts, arg[len(lopt):]).append(True)

        ## signal to stop option parsing is an 'empty' long option
        elif arg == lopt:
            if expandWildCards:
                for arg in cargs[idx+1:]:
                    oargs.extend(expandWCs(arg))
            else:
                oargs.extend(cargs[idx+1:])
            break

        ## must have found a negative number
        elif arg[0] == '-' and arg[1] in set('0123456789'):
            oargs.append(arg)

        ## must have found an unknown option
        elif arg.startswith(shortOpMarker):
            if not skipUnknownOps:
                opts.usage(10000, 'Unknown option: "%s"' % arg)

            oargs.append(arg)

        ## must be an argument
        else:
            if nonOpStopOp:
                if expandWildCards:
                    for arg in cargs[idx:]:
                        oargs.extend(expandWCs(arg))
                else:
                    oargs.extend(cargs[idx:])
                break

            if expandWildCards:
                oargs.extend(expandWCs(arg))
            else:
                oargs.append(arg)

        idx += 1

    return oargs, opts


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    class TException(Exception): pass

    def usage(rc, s=''):
        raise TException(s)

    t = ['-caa', '--sara', 'cool', 'filename', '--cool', '-5', '-a', '-a']

    args, opts = mopt(t, [('c', 'cat')], ['cool', 'sara'], ['a'], [], "cool")
    tester.Assert(opts.get('cool', 0, int) == 0)
    tester.Assert(len(opts.a) == 2)

    args, opts = mopt(t, [('c', 'cat')], ['cool', 'sara'], ['a'], [], 'this is the prgm', nonOpStopOp=False)
    tester.Assert(opts.get('cool', 0, int) == -5)
    tester.Assert(len(opts.a) == 4)

    args, opts = mopt(t, [('c', 'cat'), 'a'], ['cool', 'sara'], 'this is the prgm', nonOpStopOp=False)
    tester.Assert(opts.get('cool', 0, int) == -5)
    tester.AssertRecvException(AttributeError, opts.get, ('b', ))

    tester.AssertRecvException(TException, mopt, (t, [('c', 'cat')], ['cool', 'sara'], usage))

    tester.AssertRecvException(TException, mopt, (['--help'], [('c', 'cat')], ['cool', 'sara'], usage))
    tester.AssertRecvException(TException, mopt, (['-?'], [('c', 'cat')], ['cool', 'sara'], usage))

    args, opts = mopt(t, [('c', 'cat')], ['cool'], 'this is the prgm', nonOpStopOp=False, skipUnknownOps=True)
    tester.Assert(opts.get('cool', 0, int) == -5)
    tester.Assert(args == ['-a', '-a', '--sara', 'cool', 'filename', '-a', '-a'])

    # test opts as first param
    arg, opts = mopt(opts, [], [], ['a'], ['sara'], '', nonOpStopOp=False)
    tester.Assert(opts.validate({'a': [True, True, True, True], 'sara': ['cool'], 'cat': True, '_usageStr_': 'this is the prgm', 'cool': u'-5', '_args_': [u'filename'],
        '_cmdline_': ['-a', '-a', '--sara', 'cool', 'filename', '-a', '-a']}))

    arg, opts = mopt(opts, [], [], ['a'], ['sara'], nonOpStopOp=False)
    tester.Assert(opts.validate({'a': [True, True, True, True], 'sara': ['cool'],
        'cat': True, '_usageStr_': 'this is the prgm', '_args_': ['filename'], 'cool': '-5', '_cmdline_': ['filename']}))

    arg, opts = mopt(opts, [], [], ['a'], ['sara'], '', nonOpStopOp=False)
    tester.Assert(opts.validate({'a': [True, True, True, True], 'sara': ['cool'],
        'cat': True, '_usageStr_': 'this is the prgm', '_args_': ['filename'], 'cool': '-5', '_cmdline_': ['filename']}))

    arg, opts = mopt(opts, [], [], ['a'], ['sara'], nonOpStopOp=False)
    tester.Assert(opts.validate({'a': [True, True, True, True], 'sara': ['cool'],
        'cat': True, '_usageStr_': 'this is the prgm', '_args_': ['filename'], 'cool': '-5', '_cmdline_': ['filename']}))

    arg, opts = mopt(opts, ['c', 'cool'], [])
    tester.Assert(opts.validate({'a': [True, True, True, True], 'c': None, 'sara': ['cool'], 'cat': True,
        '_usageStr_': u'this is the prgm', '_args_': ['filename'],
        'cool': '-5', '_cmdline_': ['filename']}))
    tester.Assert('c' not in opts)
    tester.Assert('cat' in opts)
    tester.Assert(opts['cat'] is True)

    t = ['-cool', '-run', '5', 'stuff']
    args, opts = mopt(t, ['cool'], ['run'], 'this is the prgm', allowMultiChar=True)
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'run': '5',
        '_args_': ['stuff'], 'cool': True, '_cmdline_': ['-cool', '-run', '5', 'stuff']}))

    t = ['/cool', '/run', '5', 'stuff']
    args, opts = mopt(t, ['cool'], ['run'], 'this is the prgm', allowMultiChar=True, shortOpMarker='/')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'run': '5',
        '_args_': ['stuff'], 'cool': True, '_cmdline_': ['/cool', '/run', '5', 'stuff']}))

    t = ['--sara', 'boo']
    args, opts = mopt(t, ['sara'], ['sara'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'sara': 'boo',
        '_args_': [], '_cmdline_': ['--sara', 'boo']}))

    args, opts = mopt(t, ['sara'], ['sara'], usage)
    tester.AssertRecvException(TException, opts.get, ('sara', '', float))

    t = ['--sara']
    args, opts = mopt(t, ['sara'], ['sara'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'sara': True, '_args_': [], '_cmdline_': ['--sara']}))

    args, opts = mopt(['*.py'], ['sara'], ['sara'], 'this is the prgm')
    tester.AssertRecvException(TypeError, mopt, (['--help'], [('c', 'cat')]))

    args, opts = mopt(['*.py'], ['sara'], ['sara'], 'this is the prgm')
    tester.Assert('options.py' in args)

    args, opts = mopt(['"*.py"'], ['sara'], ['sara'], 'this is the prgm')
    tester.Assert('*.py' in args)

    args, opts = mopt(['coo[123].py'], ['sara'], ['sara'], 'this is the prgm')

    args, opts = mopt(['*.py'], ['sara'], ['sara'], 'this is the prgm', expandWildCards=False)
    tester.Assert('*.py' in args)

    args, opts = mopt(['*.py'], ['sara'], ['sara'], 'this is the prgm', expandWildCards=False, nonOpStopOp=False)
    tester.Assert('*.py' in args)

    t = ['-c', '-r', '5', 'stuff']
    args, opts = mopt(t, [('c', 'cool')], [('r','run')], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'run': '5',
        '_args_': ['stuff'], 'cool': True, '_cmdline_': ['-c', '-r', '5', 'stuff']}))

    t = ['-s']
    args, opts = mopt(t, ['s'], ['s'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 's': True, '_args_': [], '_cmdline_': ['-s']}))

    t = ['-s', 'boo']
    args, opts = mopt(t, ['s'], ['s'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 's': 'boo', '_args_': [], '_cmdline_': ['-s', 'boo']}))

    t = ['-s']
    args, opts = mopt(t, [], [], ['s'], ['s'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 's': [True], '_args_': [], '_cmdline_': ['-s']}))

    t = ['-s', 'boo']
    args, opts = mopt(t, [], [], ['s'], ['s'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 's': ['boo'], '_args_': [], '_cmdline_': ['-s', 'boo']}))

    t = ['--sara']
    args, opts = mopt(t, [], [], ['sara'], ['sara'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'sara': [True], '_args_': [], '_cmdline_': ['--sara']}))

    t = ['--sara', 'boo']
    args, opts = mopt(t, [], [], ['sara'], ['sara'], 'this is the prgm')
    tester.Assert(opts.validate({'_usageStr_': 'this is the prgm', 'sara': ['boo'], '_args_': [], '_cmdline_': ['--sara', 'boo']}))

    t = ['--sara', 'boo', '--', '--cool']
    args, opts = mopt(t, [], [], ['sara'], ['sara'])
    tester.Assert(opts.validate({'_usageStr_': '', 'sara': ['boo'], '_args_': ['--cool'],
        '_cmdline_': ['--sara', 'boo', '--', '--cool']}))

    t = ['--sara', 'boo', '--', '--cool']
    args, opts = mopt(t, [], [], ['sara'], ['sara'], expandWildCards=False)
    tester.Assert(opts.validate({'_usageStr_': '', 'sara': ['boo'], '_args_': ['--cool'],
        '_cmdline_': ['--sara', 'boo', '--', '--cool']}))

    t = ['--sara', '--', '--cool']
    args, opts = mopt(t, [], [], ['sara'], [], expandWildCards=False)
    tester.Assert(opts.validate({'_usageStr_': '', 'sara': [True], '_args_': ['--cool'],
        '_cmdline_': ['--sara', '--', '--cool']}))

    t = ['--sara']
    tester.AssertRecvException(TException, mopt, (t, [], [('s', 'sara')], usage))
    t = ['-s']
    tester.AssertRecvException(TException, mopt, (t, [], [('s', 'sara')], usage))
    t = ['--sara']
    tester.AssertRecvException(TException, mopt, (t, [], [], [], [('s', 'sara')], usage))
    t = ['-s']
    tester.AssertRecvException(TException, mopt, (t, [], [], [], [('s', 'sara')], usage))

    tester.AssertRecvException(TypeError, mopt, (t, [], [], [('s', 'sara')], usage))

    t = ['---sara', '---', '---cool']
    args, opts = mopt(t, [], [], ['sara'], [], expandWildCards=False, longOpMarker='---')
    tester.Assert(opts.validate({'_usageStr_': '', 'sara': [True], '_args_': ['---cool'],
        '_cmdline_': ['---sara', '---', '---cool']}))

    t = ['---sara', '-s', '-d']
    args, opts = mopt(t, [], [], ['sara'], [], expandWildCards=False, longOpMarker='---', shortOpMarker='---')
    tester.Assert(opts.validate({'_usageStr_': '', 'sara': [True], '_args_': ['-s', '-d'],
        '_cmdline_': ['---sara', '-s', '-d']}))

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = mopt(oss.argv[1:], [], [], __test__.__doc__)

    print(oss.argv[1:])
    print(args)
    print('-'*40)

    #mopt([], [], [], '', cool=5)
    t = ['---cc', 'cl9', '---lib', r'C:\libcpp\lib;C:\Program Files\Microsoft Visual Studio\VC98\lib', '-c', 'msh.cpp']
    args, opts = mopt(t, [], [('Z', 'cc'), ('L', 'lib')], [], [], expandWildCards=False, longOpMarker='---', shortOpMarker='---')

    print(args)
    print(opts)

    res = not __test__(verbose=True)
    oss.exit(res)


