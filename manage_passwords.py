#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import pylib.encryptedstorage as es

try:
    import pylib.wincursor as wc
except ImportError:
    pass

DBFile = '/tmp/pdb2'
DBFile = '/home/chrish/admin/pwd.db'

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: manage_passwords.py [options] [<args> ...]

        options:
            -a | --add               : add records
            -e | --edit <arg>        : edit specified record
            -d | --delete <args> ... : delete specified record(s)

            -A | --all               : display all records
            -k | --key               : specify the key
    """
    args, opts = oss.gopt(argv[1:], [('a', 'add'), ('A', 'all'), ('e', 'edit'), ('d', 'delete'), ('G', 'gui')], [('k', 'key'), ('D', 'db')], main.__doc__ + __doc__)

    if opts.edit and not len(args) == 1:
        opts.usage(1, 'must specify record to edit')

    if opts.delete and not args:
        opts.usage(1, 'must specify record(s) to delete')

    dbf = opts.db if opts.db else DBFile

    key = opts.key if opts.key else raw_input('\nEnter Password: ')

    ## create the database
    db = DB(dbf, key)

    if opts.gui:
        gui = GUI(db)
        gui.run()
        oss.exit(0)

    cmd = CmdLineUI(db)

    if opts.edit:
        if not cmd.edit(args[0]):
            opts.usage(2, 'could not find record to edit')

    elif opts.delete:
        cmd.delete(args)

    elif opts.add:
        cmd.add()

    else:
        cmd.display(args, opts.all)

    oss.exit(0)


#-------------------------------------------------------------------------------
class CmdLineUI(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, db):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.db = db

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def edit(self, rec):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        e = self.db.find(rec)
        if not e:
            return

        e = e[0]
        print(e)
        print()

        e.name   = getEntryOrDefault('Name: ', e.name)
        e.url    = getEntryOrDefault('URL: ', e.url)
        e.login  = getEntryOrDefault('login: ', e.login)
        e.passwd = getEntryOrDefault('passwd: ', e.passwd)
        e.desc   = getEntryOrDefault('description: ', e.desc, True)

        self.db.save()
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delete(self, args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for a in args:
            self.db.rm(a)
        self.db.save()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            e = Entry()

            e.name   = getEntryOrDefault('Name: ', e.name)

            if self.db.isIn(e.name):
                print('Name "%s" is already in database\n' % e.name)
                continue

            e.url    = getEntryOrDefault('URL: ', e.url)
            e.login  = getEntryOrDefault('login: ', e.login)
            e.passwd = getEntryOrDefault('passwd: ', e.passwd)
            e.desc   = getEntryOrDefault('description: ', e.desc, True)
            self.db.add(e)

            ch = raw_input('\nAnother Entry: (y/n)')

            if ch != 'y':
                self.db.save()
                return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def display(self, args, all=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## if args, dump their records
        if args:
            for e in self.db.find(*args):
                print(e)

        ## dump all records
        elif all:
            print(self.db)

        ## dump just the names
        else:
            for name in self.db.getEntries():
                print(name)

#-------------------------------------------------------------------------------
class GUI(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, db):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.db = db
        self.scrn = wc.Screen()
        self.scrn.clear()
        self.scrn.SetTitle("Manage Passwords")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        mn = wc.Menu(self.scrn, 'Entries', sorted(self.db.getEntries()) + ['', 'add', 'quit'])
        it = wc.Menu(self.scrn, 'Item', ['edit', 'delete', 'exit'])

        while 1:
            arg = mn.getSel()

            if arg is None or arg == 'quit':
                break

            for e in self.db.find(arg):
                it.setText(str(e))
                s = it.getSel()


        self.scrn.clear()
        self.scrn.close()

#-------------------------------------------------------------------------------
class DB(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.fileName = fileName
        self.revision = "1.0"

        self.entries = []
        self.names = {}
        self.es = es.EncryptedStorageObj(self.fileName, key)

        if oss.exists(self.fileName):
            self.load()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rm(self, e_name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not isinstance(e_name, Entry):
            e = self.find(e_name)
            if not e:
                return
            e = e[0]
        else:
            e = e_name

        del self.names[e.name]
        self.entries.remove(e)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.entries.append(e)
        self.entries.sort(key=lambda s: s.name)
        self.names[e.name] = e

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rev, obj = self.es.load()
        if rev == "1.0":
            self.entries = obj
        else:
            raise Exception('wrong db rev')

        self.names = {}

        for e in self.entries:
            self.names[e.name] = e

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.es.save((self.revision, self.entries))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getEntries(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #return [e.name for e in self.entries]
        l = []
        for e in self.entries:
            if e.name in l:
                print("Duplicate Name:", e.name)
                l.append(e.name + '_')
            else:
                l.append(e.name)
        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isIn(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return name in self.entries

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def find(self, *names):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        el = []
        for name in names:
            try:
                el.append(self.names[name])
            except KeyError:
                pass
        return el

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for e in self.entries:
            s.append(str(e))
        return '\n'.join(s)


#-------------------------------------------------------------------------------
class Entry(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name='', url='', login='', passwd='', desc=''):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.name = name
        self.url = url
        self.login = login
        self.passwd = passwd
        self.desc = desc

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ['\n===================================']
        s.append('Name:   ' + self.name)
        s.append('URL:    ' + self.url)
        s.append('Login:  ' + self.login)
        s.append('Passwd: ' + self.passwd)
        s.append('Desc:   \n' + str(self.desc))
        s.append('\n')
        return '\n'.join(s)


#-------------------------------------------------------------------------------
def getEntryOrDefault(tag, val='', multiLine=False):
#-------------------------------------------------------------------------------
    if not multiLine:
        ch = raw_input(tag)
        if ch:
            return ch
        return val

    print('\n(end with line starting with dot)\n')
    print(tag)

    s = []
    while 1:
        line = raw_input()
        if line and line[0] == '.':
            v = '\n'.join(s)
            if v:
                return v
            return val
        s.append(line)


if __name__ == "__main__":
    main(oss.argv)
