#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import


import pylib.osscripts as oss
import pylib.net.util as pnet
import pylib.util as util
import pylib.httpcmd as httpcmd


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: httpcmd [OPTIONS] <URL>

    Send an http command to the URL. Cmds include 'get', 'put', 'post' etc. The
    default 'cmd' is 'GET'. Then dumps the returned status code, headers and body
    data to stdout.

    Options:
        -c | --cmd  : specifies the cmd, default is 'GET'
        -m | --msg  : specifies the body of a 'PUT' or 'POST' cmd. Use \\n to represent
                      line breaks or specify each line with a -m.
        -h | --hdr  : specifies a single HTTP hdr. This option may be used more than
                      once

        -v | --verbose : prints lots of output

    """
    args, opts = oss.gopt(argv[1:], [('v','verbose')], [('h', 'hdr'), ('m', 'msg'), ('c','cmd')], main.__doc__)

    if not args:
        opts.usage(1, "Must specify a URL")

    sa, tp = pnet.ArgsToAddrPort(args)

    if opts.msg:
        if isinstance(opts.msg, list):
            opts.msg = '\r\n'.join(opts.msg)
        else:
            opts.msg = util.CvtNewLines(opts.msg, '\r\n')

    if opts.hdr:
        opts.hdr = list(opts.hdr)

    if opts.cmd is None:
        opts.cmd = 'GET'
    else:
        opts.cmd = opts.cmd.upper()


    if opts.cmd in ['PUT', 'POST']:
        hdr, s = httpcmd.httpPutPost(sa[0], sa[1], tp[0], tp[1], opts.cmd, opts.msg, opts.hdr, opts.verbose)
    else:
        hdr, s = httpcmd.httpCmd(sa[0], sa[1], tp[0], tp[1], opts.cmd, opts.hdr, opts.verbose)

    print(hdr)
    print(s)

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

