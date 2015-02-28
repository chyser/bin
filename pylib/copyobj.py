"""
This module is much like copy, however, only the fields of the specfied source
class are copied to the destination. Thus src and dest don't have to be the same
type of object. In fact no hierarchical relationship is assumed.
"""

#-------------------------------------------------------------------------------
def copyobj(dest, src, Class = None):
#-------------------------------------------------------------------------------
    """ copy only fields from 'Class' or 'src'
    """

    if Class is None: Class = src.__class__
    map(lambda l: setattr(dest, l, getattr(src, l, None)), [i for i in dir(src) if i not in dir(Class)])

#-------------------------------------------------------------------------------
def CopyObjList(dest, src, fields):
#-------------------------------------------------------------------------------
    """ copy fields specified in 'fields'
    """

    map(lambda l: setattr(dest, l, getattr(src, l, None)), fields)

#-------------------------------------------------------------------------------
def CopyObjTup(dest, src, fields):
#-------------------------------------------------------------------------------
    """ copy fields specified in 'fields'. each element must be a tuple, element
        0 the new name in 'dest' and element 1 the name in 'src'
    """

    map(lambda l: setattr(dest, l[0], getattr(src, l[1], None)), fields)

#-------------------------------------------------------------------------------
def copyobjf(dest, src, Class, func):
#-------------------------------------------------------------------------------
    """ copy only fields from 'Class' or 'src' having first been passed to
        function 'func'
    """

    map(lambda l: setattr(dest, l, func(getattr(src, l, None))), [i for i in dir(src) if i not in dir(Class)])

#-------------------------------------------------------------------------------
def CopyObjListF(dest, src, fields, func):
#-------------------------------------------------------------------------------
    map(lambda l: setattr(dest, l, func(getattr(src, l, None))), fields)

#-------------------------------------------------------------------------------
def CopyObjTupF(dest, src, fields, func):
#-------------------------------------------------------------------------------
    map(lambda l: setattr(dest, l[0], func(getattr(src, l[1], None))), fields)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class c(object):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
            self.s = s

        def __str__(self):
            return 'c: ' + str(self.s)

        __repr__ = __str__

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class d(c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s, j):
            c.__init__(self, s)
    	    self.j = j

        def __str__(self):
            return "d: " + str(self.j) + ' ' + c.__str__(self)

        _repr__ = __str__

    l = c('l'); print l

    f = d('f', 'g'); print f

    copyobj(f, l, c); print f

    f = d('f', 'g'); print f

    print l;  copyobj(l, f, c); print l

