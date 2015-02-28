#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
from pyPdf import PdfFileWriter, PdfFileReader

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [('o', 'out')], main.__doc__ + __doc__)

    outfn = opts.out if opts.out else "document_output.pdf"

    output = PdfFileWriter()

    a = []
    for arg in args:
        print('copying "%s"' % arg)
        a.append(copyPdf(output, arg))

    with open(outfn, "wb") as outf:
        output.write(outf)

    oss.exit(0)


#-------------------------------------------------------------------------------
def copyPdf(output, name):
#-------------------------------------------------------------------------------
    inpf = open(name, "rb")
    inp = PdfFileReader(inpf)

    for i in range(inp.getNumPages()):
        output.addPage(inp.getPage(i))

    return inpf

if __name__ == "__main__":
    main(oss.argv)

