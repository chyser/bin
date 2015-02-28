#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import pylib.osscripts as oss


DIRS = [
    ('Downloads', 'downloads'),
    ('My Documents', 'docs'),
    ('RemoteDownloads', 'rdwnl'),
    ]

EXTS = ['pdf', 'txt', 'png', 'jpg', 'html', 'htm', '*']


HTML="""
<html>
<body>
%s
</body>
</html>
"""


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    t = ['<ul>\n']

    for name, d in DIRS:
        t.append('    <li><a href="%s.html">%s</a></li>\n' % (d, name))
        doPage(name, d)

    with open("links.html", "w") as otf:
        otf.write(HTML % ''.join(t))

    oss.exit(0)


#-------------------------------------------------------------------------------
def doPage(name, d):
#-------------------------------------------------------------------------------
    t = ["<h2>%s</h2>\n" % name]
    for ext in EXTS:
        t.append("<h3>%s</h3>\n<ul>\n" % ext)
        t.extend(get(d + '/*.' + ext))
        t.append("</ul>\n")

    with open(d + ".html", "w") as otf:
        otf.write(HTML % ''.join(t))


#-------------------------------------------------------------------------------
def get(pth):
#-------------------------------------------------------------------------------
    t = []
    for f in sorted(oss.ls(pth), key=lastMod):
        f = f.replace('\\', '/')
        t.append('    <li><a href="%s">%s</a></li>\n' % (f, oss.basename(f)))
    return t



#-------------------------------------------------------------------------------
def lastMod(a):
#-------------------------------------------------------------------------------
    return -os.stat(a).st_mtime

if __name__ == "__main__":
    main(oss.argv)
