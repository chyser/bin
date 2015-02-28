#!/usr/bin/env python
"""
usage: tester [files_to_test]

run the automated testing suite on specified files

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

try:
    import pylib.osscripts as oss
except ImportError:
    import osscripts as oss

import sys
import types
import traceback

class TesterException(Exception): pass
sys.path.insert(0, '.')

__package__ = 'pylib'

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: tester <files to test>

    run an automated test against the specified python files.

    The files must have one or more functions with '__test__' embedded somewhere
    in the function name.
    """

    args, opts = oss.gopt(argv[1:], [('v', 'verbose')], [('p', 'package')], main.__doc__)

    pkg = '' if opts.package is None else opts.package + '.'

    tried = failed = 0

    for a in oss.paths(args):
        try:
            print("%-20s" % a, end='')
            t = test_it(pkg + a.name, opts.verbose)
            print("  %d tests" % t)
            tried += t
        except TesterException:
            print("failed")
            failed += 1

    print("\nRan %d tests. %d Failed\n" % (tried, failed), file=oss.stderr)

    if failed:
        oss.exit(1)
    oss.exit(0)


#-------------------------------------------------------------------------------
def Assert(val, msg=''):
#-------------------------------------------------------------------------------
    """ Asserts 'val' is True, printing 'msg' and logging if not.

        @type  val: boolean
        @param val: any object or results of an expression that returns 'truth'
        @type  msg: str
        @param msg: optional messge to include in logged output
    """

    if not val:
        raise TesterException("Test Assert Failed " + msg)


#-------------------------------------------------------------------------------
def AssertRecvException(exc, func, args, msg=''):
#-------------------------------------------------------------------------------
    """ Asserts the exception 'exc' was received when running function 'func' with
        tuples 'args' as arguments. Failure to recieve the exception is logged
        with the optional 'msg'
    """
    try:
        func(*args)
        raise TesterException("Specified Exception not Recieved " + str(msg))
    except exc:
        pass


#-------------------------------------------------------------------------------
class expectException:
#-------------------------------------------------------------------------------
    def __init__(self, e):
        if isinstance(e, Exception):
            self._t, self._v = e.__class__, str(e)
        elif isinstance(e, type) and issubclass(e, Exception):
            self._t, self._v = e, None
        else:
            raise Exception("usage: with expected(Exception): or with expected(Exception(\"text\"))")

    def __enter__(self):
        try:
            pass
        except:
            pass # this is a Python 3000 way of saying sys.exc_clear()

    def __exit__(self, t, v, tb):
        assert t is not None, "expected {0:s} to have been thrown".format(self._t.__name__)
        return issubclass(t, self._t) and (self._v is None or str(v).startswith(self._v))


#-------------------------------------------------------------------------------
def test_it(moduleName, verbose=False, testName = '__test__', log=oss.stdout):
#-------------------------------------------------------------------------------
    """ runs a function named '__test__' in the specified module moduleName
    """

    if verbose:
        print("Running test_it:", moduleName, file=oss.stderr)

    try:
        __import__(moduleName)
    except ImportError as ex:
        print("Import Failed: '%s'" % str(ex), file=oss.stderr)
        return 0

    module = sys.modules[moduleName]

###    if verbose:
###        print(module.__doc__)

    tested = failed = 0

    for name in dir(module):
        if testName in name:
            testFunction = getattr(module, name)
            if isinstance(testFunction, types.FunctionType):
                try:
                    tested += 1
                    testFunction()
                except Exception:
                    failed += 1
                    traceback.print_exc()

    if failed > 0:
        print("Tests Failed:", failed, file=oss.stderr)
        raise TesterException("Tests Failed")

    return tested


#-------------------------------------------------------------------------------
def pretest(moduleName):
#-------------------------------------------------------------------------------
    print("Running Pretest:", moduleName, file=oss.stderr)
    module = __import__(moduleName)

    print(module.__file__)
    if module.__file__.endswith('.py'):

        if test_it(moduleName):
            pass
        else:
            fn = module.__file__
            oss.rm(fn + 'c')
            oss.rm(fn + 'o')


#-------------------------------------------------------------------------------
def GetFuncArgs(fn, fo):
#-------------------------------------------------------------------------------
    """ returns a string showing function declaration and doc
    """
    s = fn + '('
    args = fo.func_code.co_argcount

    varg = karg = -1
    if fo.func_code.co_flags & 4:
        varg = args
        args += 1

    if fo.func_code.co_flags & 8:
        #kargs = args
        args += 1

    lst = fo.func_code.co_varnames[0:args]
    f = True
    for i, item in enumerate(lst):
        if not f:
            s += ", "
        else:
            f = False

        if i == varg:
            s += '*'
        elif i == karg:
            s += '**'

        s += item
    s += ")\n\n"

    f = fo.__doc__
    if f is not None:
        s += f.strip()

    return s + '\n'




if __name__ == "__main__":
    main(oss.argv)

