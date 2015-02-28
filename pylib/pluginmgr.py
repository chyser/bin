"""

Provides functions to enable dynamic loading of modules and particular classes

"""


import imp
import inspect
import sys
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def LoadPlugin(name, path=sys.path, suffix=None, prefix=None):
#-------------------------------------------------------------------------------
    res = []

    fp, pn, desc = imp.find_module(name, path)
    m = imp.load_module(name, fp, pn, desc)
    d = m.__dict__

    for i in d.keys():
        if i[0] != '_' and isinstance(d[i], type):
            if ((suffix is not None and i.endswith(suffix)) or
                (prefix is not None and i.startswith(prefix)) or
                (prefix is None and suffix is None)):
                 res.append((i, d[i]))
    return res

#-------------------------------------------------------------------------------
def LoadPlugins(path, suffix=None, prefix=None):
#-------------------------------------------------------------------------------
    plugins = []
    if not isinstance(path, list):
        path = [path]

    for pth in path:
        for f in oss.ls(pth + '/*.py', pth + '/*.pyd'):
            plugins.extend(LoadPlugin(oss.splitnm(oss.basename(f)), path, suffix, prefix))
    return plugins

#-------------------------------------------------------------------------------
def LoadClasses(name, path=sys.path, cxt=None):
#-------------------------------------------------------------------------------
    res = []

    fp, pn, desc = imp.find_module(name, path)
    m = imp.load_module(name, fp, pn, desc)
    d = m.__dict__

    for i in d.keys():
        if i[0] != '_' and isinstance(d[i], type):
            res.append((i, d[i]))
    return res

#-------------------------------------------------------------------------------
def LoadDerivedClasses(name, path, base):
#-------------------------------------------------------------------------------
    """ pull non-private classes from module 'name' that are derived from one of
        the set of base classes 'base' provided.
        returns: list of tuples (name, class, intersection set of base with ancestors)
    """

    try:
        base = set([base]) if isinstance(base, (str, unicode)) else set(base)
    except TypeError:
        base = set([base])

    fp, pn, desc = imp.find_module(name, path)
    m = imp.load_module(name, fp, pn, desc)
    d = m.__dict__

    res = []
    for i in d.keys():
        if i[0] != '_' and isinstance(d[i], type):
            ins = base & set(inspect.getmro(d[i]))
            if ins:
                res.append((i, d[i], ins))
    return res

#-------------------------------------------------------------------------------
def LoadLibraries(path, func, cxt=None):
#-------------------------------------------------------------------------------
    if isinstance(path, (str, unicode)):
        path = [path]

    plugins = []
    for pth in path:
        for f in oss.ls(pth + '/*.py', pth + '/*.pyd'):
            plugins.extend(func(oss.splitnm(oss.basename(f)), path, cxt))
    return plugins

