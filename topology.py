#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pprint
import pylib.osscripts as oss


#
# choose a path for real systems or for testing
#
TESTING = False
if oss.exists('/sys') and not TESTING:
    DIR_PATH = '/sys/devices/system'
else:
    DIR_PATH = '/tmp/topology/test1'
    print('Testing:', DIR_PATH)


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('d', 'disp')], [], main.__doc__ + __doc__)

    if opts.disp:
        displayNodes()
        displayCPUs()
        displayCaches()

    nodes, cpus = createHierachy()
    displayHierarchy(nodes, cpus)

    oss.exit(0)


#-------------------------------------------------------------------------------
def displayHierarchy(nodes, cpus):
#-------------------------------------------------------------------------------
    print()
    for node in sorted(nodes, key=lambda n: n.node):
        print('\nnode%d -- (%s):' % (node.id, node.memTotal))
        if node.cacheLvl == '3':
            d3 = 0
            for c3 in node.caches:
                if d3 != 0: print()
                d3 = 1
                print('   ', 'L3 -- (%s, %s):' % (c3.typ, c3.size))
                d2 = 0
                for c2 in c3.caches:
                    if d2 != 0: print()
                    d2 = 1
                    print('       ', 'L2 -- (%s, %s):' % (c2.typ, c2.size))

                    d1 = 0
                    for cpu in c2.cpus:
                        if d1 != 0: print()
                        d1 = 1
                        for c1 in cpus[cpu].caches:
                            print('           ', 'L1 -- (%s, %s):' % (c1.typ, c1.size))
                        print('                cpu%d' % cpu)
        else:
            d2 = 0
            for c2 in node.caches:
                if d2 != 0: print()
                d2 = 1
                print('   ', 'L2 -- (%s, %s):' % (c2.typ, c2.size))

                d1 = 0
                for cpu in c2.cpus:
                    if d1 != 0: print()
                    d1 = 1
                    for c1 in cpus[cpu].caches:
                        print('       ', 'L1 -- (%s, %s):' % (c1.typ, c1.size))
                    print('            cpu%d' % cpu)


#-------------------------------------------------------------------------------
def createHierachy():
#-------------------------------------------------------------------------------

    ## trick to only get unique values
    cd = {}
    for cc in getCaches().values():
        cd[(cc['level'], cc['type'], frozenset(cc['shared_cpu_list']))] = cc

    ## build caches structure
    caches = {
        '1' : [],
        '2' : [],
        '3' : [],
    }

    for cc, dd in cd.items():
        caches[cc[0]].append(Cache(cc[0], cc[1], cc[2], dd))

    ##give them all a uniue number for their level
    for cn in "123":
        cid = 0
        for cache in caches[cn]:
            cache.id = cid
            cid += 1

    ## build up cpus structure
    cpus = {}
    for cpu in getCPUs().values():
        c = cpus[cpu['cpu']] = CPU(cpu['cpu'], cpu)
        for cc in caches['1']:
            if c.id in cc.cpus:
                c.caches.append(cc)

    ## assign all level 1 caches to the corresponding level 2 cache
    for cache in caches['2']:
        for cc in caches['1']:
            if cache.cpus & cc.cpus:
                cache.caches.append(cc)

    ## assign all level 2 caches to the corresponding level 3 cache
    for cache in caches['3']:
        for cc in caches['2']:
            if cache.cpus & cc.cpus:
                cache.caches.append(cc)

    ## assign level 2 or level 3 caches to corresponding node
    nodes = []
    nc = '3' if caches['3'] else '2'
    for nd in getNodes().values():
        node = Node(nd['node'], nd['cpulist'], nc, nd)
        nodes.append(node)

        for cc in caches[nc]:
            if node.cpus & cc.cpus:
                node.caches.append(cc)

    return nodes, cpus


#-------------------------------------------------------------------------------
class Node(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, nid, cpus, cacheLvl, cc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.__dict__.update(cc)
        self.id = nid
        self.cpus = set(cpus)
        self.cacheLvl = cacheLvl
        self.caches = []


#-------------------------------------------------------------------------------
class Cache(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, level, typ, cpus, cc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.__dict__.update(cc)
        self.id = -1
        self.level = level
        self.typ = typ
        self.cpus = cpus
        self.caches = []


#-------------------------------------------------------------------------------
class CPU(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, id, cc):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.__dict__.update(cc)
        self.id = id
        self.caches = []


#-------------------------------------------------------------------------------
def displayNodes():
#-------------------------------------------------------------------------------
    print("\nnode\tcpulist\ttotal memory")
    print('-'*80)
    dd = getNodes()
    for c in sorted(dd.keys()):
        cc = dd[c]
        print('%s\t%s\t%s' % (
            cc['node'],
            dispList(cc['cpulist']),
            cc['memTotal'],
            ))


#-------------------------------------------------------------------------------
def displayCPUs():
#-------------------------------------------------------------------------------
    print("\ncpu\tphysId\tcoreId\tcoreSib\tthread_sibs")
    print('-'*80)
    dd = getCPUs()

    for c in sorted(dd.keys()):
        cc = dd[c]
        print('%s\t%s\t%s\t%s\t%s' % (
            cc['cpu'],
            cc['phys_pkg_id'],
            cc['core_id'],
            dispList(cc['core_sibs']),
            dispList(cc['thread_sibs']),
            ))


#-------------------------------------------------------------------------------
def displayCaches():
#-------------------------------------------------------------------------------
    print("\ncpu\tcache\tlevel\tshared\tsize\t#sets\tassociativity")
    print('-'*80)
    dd = getCaches()
    for c in sorted(dd.keys()):
        cc = dd[c]
        print('%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
            cc['cpu'],
            cc['type'],
            cc['level'],
            dispList(cc['shared_cpu_list']),
            cc['size'],
            cc['num_sets'],
            cc['assoc'],
            ))


#-------------------------------------------------------------------------------
def getCaches():
#-------------------------------------------------------------------------------
    dd = {}
    for d in oss.ls(DIR_PATH + '/cpu/cpu*/cache/*'):
        c = oss.pathsplit(d)
        dd[d] = {
            'cpu'             : int(c[5][3:]),
            'type'            : rl(d + '/type')[:7],
            'level'           : rl(d + '/level'),
            'shared_cpu_list' : cvtToList(rl(d + '/shared_cpu_list')),
            'size'            : rl(d + '/size'),
            'num_sets'        : rl(d + '/number_of_sets'),
            'assoc'           : rl(d + '/ways_of_associativity'),
        }

    return dd


#-------------------------------------------------------------------------------
def getCPUs():
#-------------------------------------------------------------------------------
    dd = {}
    for d in oss.ls(DIR_PATH + '/cpu/cpu*/topology/'):
        c = oss.pathsplit(d)
        dd[c[5]] = {
            'cpu'         : int(c[5][3:]),
            'phys_pkg_id' : rl(d + '/physical_package_id'),
            'core_id'     : rl(d + '/core_id'),
            'core_sibs'   : cvtToList(rl(d + '/core_siblings_list')),
            'thread_sibs' : cvtToList(rl(d + '/thread_siblings_list')),
        }

    return dd


#-------------------------------------------------------------------------------
def getNodes():
#-------------------------------------------------------------------------------
    dd = {}
    for d in oss.ls(DIR_PATH + '/node/node*/'):
        c = oss.pathsplit(d)
        dd[c[5]] = {
            'node'     : int(c[5][4:]),
            'cpulist'  : cvtToList(rl(d + '/cpulist')),
            'memTotal' : rdMemInfo(d + '/meminfo', 'MemTotal'),
        }

    return dd


#-------------------------------------------------------------------------------
def rl(fileName):
#-------------------------------------------------------------------------------
    """ rl, readLine reads in a single line of text
    """
    with open(fileName) as inf:
        return inf.readline().strip()


#-------------------------------------------------------------------------------
def rdMemInfo(fileName, label):
#-------------------------------------------------------------------------------
    with open(fileName) as inf:
        for line in inf:
            if label in line:
                d = line.split()
                return d[3] + d[4]


#-------------------------------------------------------------------------------
def cvtToList(s):
#-------------------------------------------------------------------------------
    l = []

    for ch in s.split(','):
        if '-' in ch:
            a, _, b = ch.partition('-')
            l.extend(range(int(a), int(b)+1))
        else:
            l.append(int(ch))

    return l


#-------------------------------------------------------------------------------
def dispList(l):
#-------------------------------------------------------------------------------
    return ','.join([str(ll) for ll in l])


if __name__ == "__main__":
    main(oss.argv)


