#!/usr/bin/env python
"""
"""

import wmi
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [('p', 'ps'), ('s', 'startup'), ('c', 'cpu'), ('n', 'net')],
        [('P', 'passwd'), ('U', 'user')],
        __doc__ + main.__doc__)

    if len(args) > 0:
        c = wmi.WMI(args[0], user=opts.user, password=opts.passwd)
    else:
        c = wmi.WMI()

    if opts.ps:
        for p in sorted(c.Win32_Process(), key=lambda s: s.ProcessId) :
            print "%10s %10s %10s %-30s" % (str(p.ProcessId), str(p.ParentProcessId), str(p.Handle), p.Name)

    elif opts.startup:
        for s in c.Win32_StartupCommand():
            print s

    elif opts.cpu:
        for s in c.Win32_Processor():
            print s

    elif opts.net:
        nd = []
        nc = {}

        for s in c.Win32_NetworkAdapter():
            nd.append(s)

        for s in c.Win32_NetworkAdapterConfiguration():
            nc[s.Index] = s

        for n in nd:
            print '-'*80
            print n
            print nc[n.Index]

    else:
        oss._usage(0, __doc__ + main.__doc__)

    oss.exit(0)

if __name__ == "__main__":
    main(oss.argv)




