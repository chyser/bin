#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pickle

DIR = "/home/chrish/repo/"
DBPATH = DIR + "repo.db"


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: repo [cmds] [<file> [<file>]]

        cmds:
            push <files>  : save a file(s)
            pull <files>  : put the file(s) into correct places
            pull-all      : get all saved files
            ls            : show the current files
            clean <files> : unsave the file
            clean-all     : unsave all files

    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    if not args:
        return opts.usage(1)

    oss.mkdir(DIR)
    db = DataBase(DBPATH)

    cmd = args[0]

    if cmd == 'push':
        push(db, args[1:])

    elif cmd == 'pull':
        pull(db, args[1:])

    elif cmd == 'pull-all':
        pull(db, db.ls())

    elif cmd == 'ls':
        ls(db)

    elif cmd == 'clean':
        clean(db, args[1:])

    elif cmd == 'clean-all':
        cleanAll(db)

    else:
        print('unknown cmd "%s"' % cmd)

    db.close()

    oss.exit(0)


#-------------------------------------------------------------------------------
def push(db, args):
#-------------------------------------------------------------------------------
    for a in oss.paths(args):
        print('pushing "%s"' % a)

        pth = a.fpath
        nm = a.name_ext

        if not oss.exists(a):
            print('"%s" does not exist' % a)
            continue

        dest = DIR + nm
        if oss.exists(dest):
            print("warning: saved %s exists" % nm)
            ch = raw_input("overwrite: (Y/n): ")
            if ch == 'n':
                continue
            else:
                print('overwritten')

        print(nm, pth)
        db.put(nm, pth)
        oss.cp(a, DIR)


#-------------------------------------------------------------------------------
def pull(db, args):
#-------------------------------------------------------------------------------
    for a in oss.paths(args):

        nm = a.name_ext
        pth = db.get(nm)

        fpath = pth + '/' + nm
        print('pulling "%s" -> "%s' % (a, fpath))

        src = DIR + nm

        if not oss.exists(src):
            print("%s does not exist" % src)
            continue

        if oss.exists(fpath):
            ch = raw_input('overwrite "%s": (Y/n): ' % fpath)
            if ch == 'n':
                continue
            else:
                print('overwritten')

        db.rm(nm)
        oss.cp(src, fpath)


#-------------------------------------------------------------------------------
def ls(db):
#-------------------------------------------------------------------------------
    print(db.ls())


#-------------------------------------------------------------------------------
def clean(db, args):
#-------------------------------------------------------------------------------
    for k in oss.paths(args):
        print('cleaning "%s"' % k)
        db.rm(k.name_ext)


#-------------------------------------------------------------------------------
def cleanAll(db):
#-------------------------------------------------------------------------------
    for k in db.ls():
        db.rm(k)


#-------------------------------------------------------------------------------
class DataBase(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.name = name
        try:
            with open(name) as inf:
                self.db = pickle.load(inf)
        except IOError:
            self.db = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def put(self, key, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.db[key] = val

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.db[key]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            del self.db[key]
        except KeyError:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ls(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.db.keys()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with open(self.name, 'w') as otf:
            pickle.dump(self.db, otf)


if __name__ == "__main__":
    main(oss.argv)
