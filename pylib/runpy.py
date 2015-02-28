#!/usr/bin/env python
"""
Library:
    Support execution of python programs from other python program w/o new interpreter
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import sys
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def RunPrep(path, prgm, argv):
#-------------------------------------------------------------------------------
    fn = fileName = oss.splitnm(prgm)
    fileName += '.py'

    globd = {}
    exec('import sys', globd)

    ## enable local modules to be found
    wd = oss.abspath(path)
    globd['sys'].path[0] = wd
    oss.cd(wd)

    ## recreate argv
    globd['sys'].argv = [fileName] + argv

    ## change name
    globd["__name__"] = "__main__"
    globd["__debug__"] =  True

    sys.path = globd['sys'].path
    sys.argv = globd['sys'].argv
    sys.modules['__main__'] = __import__(fn)
    reload(oss)

    return fileName, globd


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


