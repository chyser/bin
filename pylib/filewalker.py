#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


#-------------------------------------------------------------------------------
class FileWalker(object):
#-------------------------------------------------------------------------------
    """ an 'file' iterator that keeps a stack of 'file' iterators, pooping each
        when it indicates done.
    """
    class IObj(object):
        def __init__(self, it, name=''):
            self.name = name
            self.it = iter(it)
            self.lineNum = 0

        def __iter__(self):
            return self

        def next(self):
            self.lineNum += 1
            return (self.name, self.lineNum, self.it.next())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, it=None, name=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ 'it' is an iterator, and 'name' is an optional "file name" associated
             with it.
        """
        object.__init__(self)
        self.lst = []
        if it is not None:
            self.add(it, name)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, it, name=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ push an iterator on to the current stack
        """
        self.lst.insert(0, self.IObj(it, name))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __iter__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def next(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return self.lst[0].next()
        except StopIteration:
            del self.lst[0]
            if self.lst:
                return self.next()
            raise


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    fw = FileWalker(['sara', 'boo', 'aidan', 'connor'], 'orig')

    results = []
    for idx, i in enumerate(fw):
        if idx == 2:
            fw.add(['amy', 'chris'], 'new')
        results.append(i)

    answer = [(u'orig', 1, u'sara'), (u'orig', 2, u'boo'), (u'orig', 3, u'aidan'), (u'new', 1, u'amy'),
        (u'new', 2, u'chris'), (u'orig', 4, u'connor')
        ]

    tester.Assert(results == answer)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

