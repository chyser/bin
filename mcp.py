#!/usr/bin/env python

import pylib.osscripts as oss
import hashlib

#-------------------------------------------------------------------------------
class McpDb(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, readonly=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.db = {}
        self.readonly = readonly
        self.read()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def read(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            for line in open('mcp.db'):
                k,v = line[:-1].split(':')
                self.db[k] = v
        except IOError:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        otf = open('mcp.db', 'w')
        for k,v in self.db.items():
            otf.write('%s:%s\n' % (k, v))
        otf.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checkAll(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.whatChanged(self.db.keys())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def whatChanged(self, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        out = []

        for f in lst:
            hash = hashlib.md5(open(f).read()).hexdigest()
            if f not in self.db or self.db[f] != hash:
                out.append(f)
                if not self.readonly:
                    self.db[f] = hash

        self.write()
        return out

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: mcp [options]
        copies files that have changed in monotone

        options:
            -d | --disp   : display only (no copy)
            -f | --force  : force copy of everything
            -u | --update : update from monotone
    """
    args, opts = oss.gopt(oss.argv[1:], [('d', 'disp'), ('f', 'force'), ('u', 'update')], [], None)

    db = McpDb(opts.disp)

    if opts.update:
        args = []
        v = oss.r('mtn status', '|')

        for line in v[:-1].split('\n'):
            if line.startswith('  patched') or line.startswith('  added'):
                d, fl = line.split()
                args.append(fl)

        if opts.force is None:
            args = db.whatChanged(args)
    else:
        args = db.checkAll()

    for a in args:
        if opts.disp is None:
            print "pscp -pw kibsop) %s chrish@compflu-01.hpl.hp.com:work/sdc.hpl.hp.com/eucalyptus/%s" % (a,a)
            oss.r("pscp -pw kibsop) %s chrish@compflu-01.hpl.hp.com:work/sdc.hpl.hp.com/eucalyptus/%s" % (a,a))
        else:
            print a

    oss.exit(0)

if __name__ == "__main__":
    main(oss.argv)

