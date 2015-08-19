#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.keys as keys

import string
import random
import hashlib

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: genpasswd [options] [additional text for hash]

        generates a random password

        Options:
           -l | --len <int> : length of passwd

           -a | --all        : use 'nearly' all printable characters
           -s | --simple     : use only letters and numbers
           -q | --quick      : use quickChars
           -m | --markov     : use a markov generator to make 'sensible' words
           -x | --hex        : make a hex passwd
           -h | --hp         : make an HP qualified password
           -n | --next <old> : create next password from old one

           -e | --extra      : add "extra"

           -c | --check      : check a passwd against validation rules
           -v | --verify     : validate against HP password rules
    """
    args, opts = oss.gopt(argv[1:], [('a', 'all'), ('s', 'simple'), ('v', 'verify'),
      ('c', 'check'), ('m', 'markov'), ('q', 'quick'), ('x', 'hex'), ('n', 'next')],
      [('l', 'len'), ('e', 'extra')], main.__doc__)

    ## check password
    if opts.check:
        passwd = raw_input("enter key: ") if not args else args[0]
        print(passwd)
        print("\nVerify:", HPVerify(passwd))
        oss.exit(0)

    ## set a default length
    length = 97 if opts.len is None else int(opts.len)

    ## get real random numbers
    if opts.next:
        rg = random.Random()
        seed = int(hashlib.sha256(args[0]).hexdigest(), 16) + 13
        rg.seed(seed)
    else:
        rg = random.SystemRandom()

    num = rg.getrandbits(8 * length)


    if opts.markov:
        import pylib.markov as mk
        #mw = mk.MarkovWord(seed=num, db=mk.BiGramSample, cls=mk.BiGram, rg=random.SystemRandom())
        mw = mk.MarkovWord(seed=num, db=mk.TriGramSample, cls=mk.TriGram, rg=random.SystemRandom())
        pwd = mw.genWord(length)

    elif opts.hex:
        pwd = "%x" % num

    elif opts.all:
        pwd = keys.cvtNum2AllChars(num)

    elif opts.simple:
        pwd = keys.cvtNum2SimpleChars(num)

    elif opts.quick:
        pwd = keys.cvtNum2QChars(num)

###    elif opts.hp:
###        while 1:
###            pwd = keys.cvtNum2ManyChars(num)
###            passwd = pwd[:length]
###            if HPVerify(passwd, verbose=False):
###                break

    else:
        pwd = keys.cvtNum2ManyChars(num)

    passwd = pwd[:length]

    if opts.extra:
        passwd += opts.extra

    print(passwd)

    if opts.verify:
        print("\nVerify:", HPVerify(passwd))

    oss.exit(0)


#-------------------------------------------------------------------------------
def GetRandomSHA(Path):
#-------------------------------------------------------------------------------
    return oss.SHASum(random.choice(oss.find(Path)))


#-------------------------------------------------------------------------------
def HPVerify(passwd, verbose=True):
#-------------------------------------------------------------------------------
    lc = uc = num = sp = 0

    if not (8 <= len(passwd) <= 32):
        return

    for ch in passwd:
        if ch in string.ascii_lowercase:
            lc += 1
        elif ch in string.ascii_uppercase:
            uc += 1
        elif ch in string.digits:
            num += 1
        elif ch in ",.?!@#$%^&*()-+":
            sp += 1

    val = sp != 0 and num != 0 and lc != 0 and uc != 0
    if not val and verbose:
        print(lc, uc, num, sp, len(passwd))
    return val



chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ23456789'

if __name__ == "__main__":
    main(oss.argv)





