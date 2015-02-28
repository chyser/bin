#!/usr/bin/env python
"""
usage: This module contains a set of utilities and decorators

"""

import types

#
# decorators
#

#-------------------------------------------------------------------------------
def mkProperty(c):
#-------------------------------------------------------------------------------
    """ A decorator for creating properties

         Usage:
             @mkProperty
             def propname():
                 def fset(self, val):
                     ...
                 def fget(self):
                     ...
                 return locals()

         - creates a property propname acessed as self.propname
    """

    return property(**c())


#-------------------------------------------------------------------------------
class signature(object):
#-------------------------------------------------------------------------------
    """ A decorator for calling functions (same name) with different parameter
        signatures.
    """

    dd = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(val):
            self.val = val
        else:
            self.val = (None,)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __call__(self, *f):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if type(f[0]) not in [types.FunctionType, types.MethodType]:
            raise "crap"

        signature.dd[tuple([str(i) for i in self.val])] = f[0]

        def ff(self, *val):
            try:
                return signature.dd[tuple([str(type(i)) for i in val])](self, *val)
            except KeyError:
                try:
                    return signature.dd[('None',)](self, *val)
                except KeyError:
                    raise NotImplementedError("Type Not Supported")

        ff.__name__ = f[0].__name__
        ff.__doc__ = f[0].__doc__

        return ff

if __debug__:

    #-------------------------------------------------------------------------------
    class typecheck(object):
    #-------------------------------------------------------------------------------
        """ A decorator for calling functions (same name) with different parameter
            signatures.
        """

        dd = {}

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, *val):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if len(val):
                self.val = val
            else:
                self.val = (None,)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __call__(self, *f):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if type(f[0]) not in [types.FunctionType, types.MethodType]:
                raise "crap"

            typecheck.dd[tuple([str(i) for i in self.val])] = f[0]

            def ff(self, *val):
                try:
                    return typecheck.dd[tuple([str(type(i)) for i in val])](self, *val)
                except KeyError:
                    try:
                        return typecheck.dd[('None',)](self, *val)
                    except KeyError:
                        raise NotImplementedError("Type Check Error")

            ff.__name__ = f[0].__name__
            ff.__doc__ = f[0].__doc__

            return ff


else:
    class typecheck(object):
        def __init__(self, *args, **kw):
            pass

        def __call__(self, f):
            return f


#
# sanity checking
#

#-------------------------------------------------------------------------------
def implements(scls, cls):
#-------------------------------------------------------------------------------
    """ ensures class 'scls' implements all of the public methods of class 'cls'
        which therefore serves as an interface

        usage:
            assert implements(myclass, interfaceClass)

    """

    for i in cls.__dict__:
        if not i.startswith('__'):
            it = getattr(cls, i)

            if type(it) == types.MethodType:
                it = getattr(scls, i, None)
                if it is None:
                    raise NotImplementedError("class '%s' missing method: '%s'" % (scls.__name__, i))

                if type(it) != types.MethodType:
                    raise NotImplementedError("class '%s' missing method: '%s'" % (scls.__name__, i))
    return True


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    class fileLike(object):
        def read(buf): raise(NotImplementedError())

    class myfile(object):
        def read():
            pass

        @signature()
        def doit(self, val):
            print "any:", val

        @signature(str)
        def doit(self, val):
            print "str:", val

        @signature(int)
        def doit(self, val):
            print "int:", val

        @typecheck(int, int)
        def sum(self, a, b):
            return a + b


    assert implements(myfile, fileLike)


    mf = myfile()

    mf.doit("cool")
    mf.doit(3)
    mf.doit(34.5)

    mf.sum(3, 4)
    mf.sum(3, 3.5)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import sys
    main(sys.argv)




