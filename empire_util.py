#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)


#-------------------------------------------------------------------------------
class Unit(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, id):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.id = id

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
def adjAttack(id, units, attacks):
#-------------------------------------------------------------------------------

    if attacks == 'NULL':
        return 'NULL'

    p = '{C@0|D@0|P@-8|N@0|r@5|R@10|s@10|S@0|f@-16|K@-16|h@-8|M@-16|I@0|}'

    u = units[id]
    print u.name, '--', u.id
    aa = attacks.split(']')

    aid = []
    atk = ''

    for a in aa:
        if a and a != 'NULL':
            #print a + ']'
            id = a[:2]
            r = a[2:]
            if r[-1] != '}':
                r += p
            else:
                r = r.split('{')[0]
                r += p

            try:
                aid.append(id)
                #print '   ', units[id].name, '(%s)' % id, r +']'
                #print '   ', id + '[' +r +']'
                atk += id + r +']'
            except KeyError:
                pass

    if atk:
        attacks = atk

    if atk and aid:
        ii = units.keys()
        for j in aid:
            try:
                ii.remove(j)
            except ValueError:
                pass

        #if ii:
        #    print ii

        for j in ii:
            attacks += j + '[D=0=' + p +']'

    return attacks

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    inf = file(args[0])

    lines = [ln[:-1] for ln in inf]

    idx = 0

    id = None
    units = {}
    while idx < len(lines):
        line = lines[idx]

        if line.startswith('#Type Id#'):
            idx += 1
            id = lines[idx]
            u = Unit(id)
            units[id] = u
            idx += 2
            u.name = lines[idx]

        elif line.startswith('# Attacks'):
            idx += 1
            units[id].attacks = lines[idx]

        elif line.startswith('# Range Attacks'):
            idx += 1
            units[id].rattacks = lines[idx]


        idx += 1

    inf.close()

    us = units.values()
    us.sort(key=lambda s: s.name)
    ids = [u.id for u in us]


    for id in ids:
        u = units[id]
        u.attacks = adjAttack(id, units, u.attacks)
        u.rattacks = adjAttack(id, units, u.rattacks)

    otf = file('newdb', 'w')

    idx = 0
    while idx < len(lines):
        line = lines[idx]

        if line.startswith('#Type Id#'):
            print >> otf, line
            idx += 1
            id = lines[idx]
            print >> otf, id

        elif line.startswith('# Attacks'):
            print >> otf, line
            print >> otf, units[id].attacks
            idx += 1

        elif line.startswith('# Range Attacks'):
            print >> otf, line
            print >> otf, units[id].rattacks
            idx += 1

        else:
            print >> otf, line

        idx += 1

    otf.close()
    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

