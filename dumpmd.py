#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss

nodes = {}

p = set(['cpu', 'cache', 'exec-unit'])

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__ + __doc__)

    inf = open("/workspace/shared/12_cpu.md")



    state = 0
    lines = inf.readlines()
    idx = 0
    while 1:
        try:
            line = lines[idx].strip()
        except IndexError:
            break

        if not line:
            idx += 1
            continue

        if state == 0:
            if line.endswith('MD_NODE'):
                n, _ = line.split()
                num = int(n)

                nd = nodes[num] = Node(num)
                state = 1

        elif state == 1:
            if line.startswith('name:'):
                nd.name = line.split()[1]
                state = 2

        elif state == 2:
            if line.find('MD_PROP_ARC') > 0:
                 _, _, typ, _, n = line.split()
                 if typ == '(fwd)':
                    nd.fwd.append(int(n))
                 else:
                    nd.bck.append(int(n))

            elif line.find('MD_PROP_VAL') > 0:
                state = 3

            elif line.find('MD_PROP_DATA') > 0:
                state = 4

            elif line.endswith('MD_NODE_END'):
                state = 0

            else:
                nd.desc.append(line)

        elif state == 3:
            if line.startswith('name:'):
                lname = line.split()[1].strip()
            elif line.startswith('val:'):
                setattr(nd, lname, line.split()[1].strip())
                state = 2

        elif state == 4:
            if line.startswith('name:'):
                lname = line.split()[1].strip()
                desc = []

            elif line[0] in set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                setattr(nd, lname, ' / '.join(desc))
                idx -=1
                state = 2
            else:
                desc.append(line)

        idx += 1


###    for k,v in nodes.items():
###        print(k, v)

    for v in nodes.values():
        if v.name == 'cpu':
            printIt(v.mid, '')



    oss.exit(0)


#-------------------------------------------------------------------------------
class Node(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, num):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mid = num
        self.name = ''
        self.fwd = []
        self.bck = []
        self.desc = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = [self.name + ' ' + str(self.mid)]
        s.extend([str(n) for n in self.fwd])

        return '\n'.join(s)



#-------------------------------------------------------------------------------
def printIt(nd, hdr, lvl=0):
#-------------------------------------------------------------------------------
    v = nodes[nd]
    s = '    '*lvl

    if v.name in p:
        if hasattr(v, 'id'):
            print(s, nd, v.name, "id:(%s)" % v.id)
        elif hasattr(v, 'level'):
            print(s, nd, v.name, "level:(%s)" % v.level, 'type:', v.type)
        elif hasattr(v, 'type'):
            print(s, nd, v.name, 'type:', v.type)
        else:
            print(s, nd, v.name)

    for n in v.fwd:
        printIt(n, 'fwd', lvl+1)





if __name__ == "__main__":
    main(oss.argv)


