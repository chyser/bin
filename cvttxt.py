#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.win32 as w32


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: cvttxt [options]

        reads txt from stdin (remember to use Ctrl-Z/D) and copies to stdout or
        to the clipboard (on windows).

        options:
            -r | --rmnl  : removes newlines on all but empty strings
            -s | --strip : extra whitespace
            -c | --clip  : copies to clipboard

    """
    args, opts = oss.gopt(argv[1:], [('c', 'clip'), ('r', 'rmnl'), ('s', 'strip')], [], main.__doc__)

    txt = []
    for line in oss.stdin:
        if line[0] == '.':
            break

        if opts.rmnl:
            line = line[:-1]

            if line:
                txt.append(line + ' ')
            else:
                txt.append('\n')
        elif opts.strip:
            txt.append(strip(line) + ' ')
        else:
            txt.append(line)

    txt.append('\n')

    txt = ''.join(txt)

    if opts.clip:
        print('\nText placed in clipboard')
        w32.copyToClipboard(txt)
    else:
        oss.stdout.write(txt)

    oss.exit(0)


#-------------------------------------------------------------------------------
def strip(s):
#-------------------------------------------------------------------------------
    r = []
    state = 0
    for ch in s.strip():
        if state == 0:
            r.append(ch)
            if ch == ' ':
                state = 1
        elif state == 1:
            if ch != ' ':
                r.append(ch)
                state = 0

    return ''.join(r)


if __name__ == "__main__":
    main(oss.argv)
