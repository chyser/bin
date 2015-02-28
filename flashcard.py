#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import random
import time

import pylib.osscripts as oss


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], __doc__ + main.__doc__)

    choices = range(0, 11)

    ans = raw_input('Numbers to specialize in: ')
    print()

    if ans.strip():
        for a in ans.split():
            choices.extend([int(a)] * 3)

    while 1:
        x = random.choice(choices)
        y = random.choice(choices)

        dodiv = random.random() < 0.5
        rans = x * y

        start = time.time()
        if dodiv:
            ans = raw_input("%d / %d = " % (rans, y))
            if y == 0:
                continue
        else:
            ans = raw_input("%d x %d = " % (x, y))
        end = time.time()

        if ans == 'q':
            break

        try:
            if dodiv:
                if int(ans) != x:
                    print("Sorry. The correct answer is", x)
                else:
                    print("Correct! Good Job! took %5.2f seconds" % (end - start))
            else:
                if int(ans) != x * y:
                    print("Sorry. The correct answer is", x * y)
                else:
                    print("Correct! Good Job! took %5.2f seconds" % (end - start))
        except Exception as ex:
            print(ex)

        print()





    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)


