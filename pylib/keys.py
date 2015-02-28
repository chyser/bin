#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import string

__QuickChars = '0123456789abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ-_+$'

__sd = {}

for idx, ch in enumerate(__QuickChars):
    __sd[ch] = idx

#-------------------------------------------------------------------------------
def cvtNum2QChars(num, length=None):
#-------------------------------------------------------------------------------
    if num == 0:
        s = ['0']
    else:
        s = []
        while num > 0:
            s.insert(0, __QuickChars[num & 0b00111111])
            num >>= 6

    if length:
        l = length - len(s)
        if l > 0:
            s = (['0']*l) + s

    #s.reverse()
    return ''.join(s)


#-------------------------------------------------------------------------------
def cvtQChars2Num(s):
#-------------------------------------------------------------------------------
    num = 0
    for ch in s:
        num = num << 6 | __sd[ch]
    return num




__SimpleChars = string.digits + string.letters
__ManyChars = __SimpleChars + '_()[]+-@!~:;{}|'
__PrintableChars = string.printable[:94]


#-------------------------------------------------------------------------------
def cvtNum2Chars(num, srcChars):
#-------------------------------------------------------------------------------
    s = []
    mod = len(srcChars)
    while num > 0:
        num, idx = divmod(num, mod)
        s.append(srcChars[idx])
    return ''.join(s)


#-------------------------------------------------------------------------------
def cvtNum2AllChars(num):
#-------------------------------------------------------------------------------
    return cvtNum2Chars(num, __PrintableChars)


#-------------------------------------------------------------------------------
def cvtNum2SimpleChars(num):
#-------------------------------------------------------------------------------
    return cvtNum2Chars(num, __SimpleChars)


#-------------------------------------------------------------------------------
def cvtNum2ManyChars(num):
#-------------------------------------------------------------------------------
    return cvtNum2Chars(num, __ManyChars)


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    import random

    for i in range(100):
        n = random.randint(0, 9999999999999999999999999999999999999999999)
        s = cvtNum2QChars(n)
        a = cvtQChars2Num(s)
        print(s, a)
        tester.Assert(n == a)

    for i in range(100):
        n = random.randint(0, 9999999)
        s = cvtNum2QChars(n)
        a = cvtQChars2Num(s)
        print(s, a)
        tester.Assert(n == a)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    s = cvtNum2SChars(-123456789, 16)
    print(s)
    print(cvtSChars2Num(s))

    res = not __test__(verbose=True)
    #oss.exit(res)

