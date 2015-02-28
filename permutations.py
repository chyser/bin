#!/usr/bin/env python
"""
usage: permutations [-c val] [[[[[a] b] c] d] ...]
    -c | --count <val> : permutation list of numbers up to count

prints all permutations of the argument list or numbers up to count if -c given

"""

import copy
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)


#-------------------------------------------------------------------------------
class Permutations(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Permutations, self).__init__()
        self.ans = []
        part = []

        self.__doit(lst, part)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __doit(self, lst, part):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in range(len(lst)):
            _lst = copy.deepcopy(lst)
            _part = copy.deepcopy(part)

            _part.append(lst[i])
            del _lst[i]
            if not _lst:
                self.ans.append(_part)
            else:
                self.__doit(_lst, _part)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [('c', 'count')], usage)

    if opts.count:
        p = Permutations(range(int(opts.count)))
        print len(p.ans), p.ans
    else:
        p = Permutations(args)
        print len(p.ans), p.ans


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

