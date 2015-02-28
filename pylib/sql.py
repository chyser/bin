#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import sqlite3

class SQLException(Exception): pass

#-------------------------------------------------------------------------------
class DB(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.conn = sqlite3.connect(fileName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dumpTables(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cur = self.conn.cursor()
        cur.execute("select * from sqlite_master where type='table'")

        while 1:
            val = cur.fetchone()
            if val is None:
                return
            yield val


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cursor(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.conn.cursor()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def commit(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.conn.commit()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.conn.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getTable(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return Table(name, self)



#-------------------------------------------------------------------------------
class Table(object):
#-------------------------------------------------------------------------------
    Formats = {
        'int'  : '%d',
        'real' : '%f',
        'text' : "'%s'",
    }

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, db):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.name = name
        self.db = db
        self.cur = db.cursor()

        print(name)
        self.cur.execute('pragma table_info(%s)' % name)
        self.columns = self.cur.fetchall()

        self.exists = bool(self.columns)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, columns):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cols = ','.join(["%s %s" % (c[0], c[1]) for c in columns])
        self.cur.execute("""create table %s (%s)""" % (self.name, cols))
        self.db.commit()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, toClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cur.execute("select * from " + self.name)

        while 1:
            row = self.cur.fetchone()
            if row is None:
                return

            if toClass is None:
                toClass = TableObject

            to = toClass()
            for idx, col in enumerate(self.columns):
                setattr(to, col[1], row[idx])

            yield to

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def insert(self, tobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for col in self.columns:
            s.append(self.Formats[col[2]] % getattr(tobj, col[1]))

        self.cur.execute('insert into %s values (%s)' % (self.name, ','.join(s)))


#-------------------------------------------------------------------------------
class TableObject(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)



#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    db = DB('cool.db')

    cur = db.cursor()

    tbl = db.getTable('boo')

    if not tbl.exists:
        tbl.create([('sara', 'int'), ('amy', 'text')])


    for i in db.dumpTables():
        print(i)
        tbl1 = db.getTable(i[2])
        print(tbl1)


    class cool(object):
        def __init__(self, sara=None, amy=None):
            self.sara = sara
            self.amy = amy

        def __str__(self):
            return "%d -- %s" % (self.sara, self.amy)


    tbl.insert(cool(5, 'wife'))
    tbl.insert(cool(7, 'what'))

    for to in tbl.get(cool):
        print(to)

    db.close()

    res = not __test__(verbose=True)
    oss.exit(res)

