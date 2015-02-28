#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import cgi

import pylib.osscripts as oss
import pylib.html_utils as utils

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: mk_cmd_help.py [options] [<file_name> ...]

        options:
            -o | --output    : html file output <default: 'cmd_help.html'

        generate an html output file of the help strings from the specified
        commands

    """
    args, opts = oss.gopt(argv[1:], [], [('o', 'output')], main.__doc__ + __doc__)

    outfile = 'cmd_help.html' if opts.output is None else opts.output

    if len(args) == 0:
        args = oss.ls('*.py')

    title = oss.pwd()

    print("Writing to file: '%s'" % outfile)
    with open(outfile, 'w') as otf:
        otf.write(HTML_BEGIN % (title, title))

        ## make a table of links to prgms details
        links = ['<a href="#{0}">{0}</a>'.format(nm) for nm in args]
        otf.write('<a name="top"><h2>Contents</h2></a>\n')
        otf.write("<center>\n" + utils.makeTable(links, tattr='border="1" width="90%"') + "\n</center>\n\n")
        otf.flush()

        ## make an entry for each prgms details
        for prgm in args:
            print(prgm)
            otf.write('\n\n<hr/>\n')
            otf.write('<a name="{0}">'.format(prgm))
            otf.write('<h2>' + prgm + '</h2></a>\n')
            s = oss.r(prgm + ' --help', '$')
            otf.write('<font size="5"><pre>' + cgi.escape(s) + '</pre></font>\n')
            otf.write('<a href="#top">Top</a>\n')
            otf.flush()
        otf.write(HTML_END)
    oss.exit(0)


HTML_BEGIN = """
<html>
    <head>
        <title>
            %s
        </title>
    </head>

    <body>
    <h1>%s</h1>

"""

HTML_END = """
        <hr/>
    </body>
</html>
"""

if __name__ == "__main__":
    main(oss.argv)
