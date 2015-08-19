#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


#-------------------------------------------------------------------------------
class Cache(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, size):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.data = {}
        self.size = size
        self.id = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ts, val = self.data[key]
        self.id += 1
        self.data[key] = self.id, val
        return val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(self.data) >= self.size:
            l = self.data.items()
            l.sort(key=lambda s: s[1][0])
            del self.data[l[0][0]]

        self.id += 1
        self.data[key] = self.id, val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __contains__(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return key in self.data

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        del self.data[key]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.data)


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    c = Cache(3)
    c['a'] = 'a';  c['b'] = 'b';  c['c'] = 'c';  c['a'];  c['d'] = 'd'
    tester.Assert(str(c) == str({u'a': (4, u'a'), u'c': (3, u'c'), u'd': (5, u'd')}))

    c['d'] = 'd';  c['e'] = 'e'
    tester.Assert(str(c) == str({u'a': (4, u'a'), u'e': (7, u'e'), u'd': (6, u'd')}))

    return 0


if __name__ == "__main__":
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

