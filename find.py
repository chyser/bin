#!/usr/bin/env python
"""
"""

import pylib.osscripts as oss
#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [('p', 'pat'), ('o', 'output')], __doc__ + main.__doc__)


    if len(args) == 0:
        args.append('.')

    if opts.output:
        otf = file(opts.output, 'w')
    else:
        otf = oss.stdout

    if opts.pat is None:
        opts.pat = '*'

    if ',' in opts.pat:
        opts.pat = opts.pat.split(',')

    a = Actions(otf)

    oss.find(args[0], opts.pat, a.action)

    if opts.output:
        otf.close()

    oss.exit(0)



#-------------------------------------------------------------------------------
class Actions(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, otf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.cnt = 0
        self.otf = otf

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def action(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.otf.write(s + '\n')
        self.cnt += 1

        if self.cnt % 1024 == 0:
            self.otf.flush()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


if __name__ == "__main__":
    main(oss.argv)
