#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.webget as wg


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: webget [options] <url>

    fetch a web page from a URL and save to a file

    options:
        -f | --file   : output file name; default is stdout
        -u | --urllib : use urllib to get file
        -b | --binary : force output file to binary mode

        -h | --hdr    : can be used multuple times to specify headers as h=v pairs
    """

    args, opts = oss.gopt(argv[1:], [('b', 'binary'), ('u', 'urllib')], [('f', 'file')], [('v', 'verbose')], [('h', 'hdr')], main.__doc__)

    if not args:
        opts.usage(1, "Must Specify a URL")

    if opts.file is None:
        verbose = 0
    else:
        print("using file:", opts.file)
        verbose = 1
        print

    hdr = {}
    if opts.hdr:
        for hd in opts.hdr:
            h, v = hd.split('=')
            hdr[h] = v

    if opts.verbose:
        verbose = max(verbose, len(opts.verbose))

    if opts.urllib is None:
        wg.GetPage(args, opts.file, opts.binary, hdr, verbose)
    else:
        wg.GetPageUrlLib(args[0], opts.file, opts.binary, verbose)

    print()
    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

