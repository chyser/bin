#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import math

#-------------------------------------------------------------------------------
def makeTable(items, cls="table", rcls="row", tattr=''):
#-------------------------------------------------------------------------------
    """ make an HTML table from a list of strings
    """
    ln = len(items)

    s = ['<table class="%s" %s>' % (cls, tattr)]
    if ln < 6:
        for i in items:
            s.append('    <tr class="%s"><td>%s</td></tr>' % (rcls, i))

    elif ln < 13:
        col = int(math.floor((ln + 2) / 3))
        for i in range(col):
            s.append('    <tr class="%s">' % rcls)
            for idx in range(0, ln, col):
                try:
                    s.append('        <td>%s</td>' % (items[idx+i]))
                except IndexError:
                    s.append('        <td>&nbsp;</td>')
            s.append('    </tr>')

    else:
        col = int(math.floor((ln + 5) / 6))
        for i in range(col):
            s.append('    <tr class="%s">' % rcls)
            for idx in range(0, ln, col):
                try:
                    s.append('        <td>%s</td>' % items[idx+i])
                except IndexError:
                    s.append('        <td>&nbsp;</td>')
            s.append('    </tr>')

    s.append('</table>')
    return('\n'.join(s))


#-------------------------------------------------------------------------------
def mkListofListsH(items, empty=''):
#-------------------------------------------------------------------------------
    ln = len(items)
    if ln < 6:   mcol = 1
    elif ln < 7: mcol = 3
    else:        mcol = 6

    lst = []
    col = (ln + mcol - 1) / mcol
    for i in range(col):
        ll = []
        for idx in range(0, ln, col):
            try:
                ll.append(items[idx+i])
            except IndexError:
                ll.append(empty)
        lst.append(ll)
    return lst


#-------------------------------------------------------------------------------
def mkListofLists(items, empty='', max_col=10):
#-------------------------------------------------------------------------------
    ln = len(items)
    if ln < 7:    mcol = 1
    elif ln < 19: mcol = 3
    elif ln < 37: mcol = 6
    else:         mcol = 10

    if mcol > max_col:
        mcol = max_col

    lst = []
    col = (ln + mcol - 1) / mcol
    for idx in range(0, ln, col):
        ll = []
        for i in range(col):
            try:
                ll.append(items[idx+i])
            except IndexError:
                ll.append(empty)
        lst.append(ll)
    return lst


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
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

