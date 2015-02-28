#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import HTMLParser


#-------------------------------------------------------------------------------
class MyHTMLParser(HTMLParser.HTMLParser):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        HTMLParser.HTMLParser.__init__(self)
        self.l = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def handle_starttag(self, tag, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.l.append(('S', (tag, dict(attr))))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def handle_endtag(self, tag):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.l.append(('E', tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def handle_data(self, data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.l.append(('T', data))


#-------------------------------------------------------------------------------
def parse(*args):
#-------------------------------------------------------------------------------
    m = MyHTMLParser()
    for t in args:
        m.feed(t)
    m.close()

    for i in m.l:
        yield i

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

    for typ, val in parse('This <b>is</b> <font color="#ff0000">red</font>'):
        print(typ, val)

    for typ, val in parse('This is <font color="#ff0000" name="arial" style="bold" style="italic" size="10">red</font>\n cool stuff'):
        print(typ, val)


    res = not __test__(verbose=True)
    oss.exit(res)

