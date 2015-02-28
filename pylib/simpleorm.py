#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import sqlite3

class SimpleORMException(Exception): pass


#-------------------------------------------------------------------------------
class Column(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, type, unique=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.unique = unique
        self.type = type

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getStr(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        u = 'UNIQUE' if self.unique else ''
        return '%s %s %s' % (name, self.type, u)


#-------------------------------------------------------------------------------
class ColumnInteger(Column):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, unique=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Column.__init__(self, 'INTEGER', unique)


#-------------------------------------------------------------------------------
class ColumnText(Column):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, unique=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Column.__init__(self, 'TEXT', unique)


#-------------------------------------------------------------------------------
class ColumnReal(Column):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, unique=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Column.__init__(self, 'REAL', unique)



#-------------------------------------------------------------------------------
class DB(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName=':memory:'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.conn = sqlite3.connect(fileName)
        self.conn.row_factory = sqlite3.Row

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getTables(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of the tables in the database
        """
        c = self.conn.execute("select * from sqlite_master where type='table'")
        return c.fetchall()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getColumns(self, tableName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of coulmns for 'tableName'
        """
        c = self.conn.execute('pragma table_info(%s)' % tableName)
        return c.fetchall()

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
    def getTable(self, tableName, ObjClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get a Table(object) from 'tableName'
        """
        return Table(tableName, self, ObjClass)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmTable(self, tableName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.conn.execute('drop table ?', tableName)


#-------------------------------------------------------------------------------
class Table(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name, db, ObjClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.table_object = TableObject if ObjClass is None else ObjClass
        self.indexIdx = 0
        self.name = name

        self.db = db
        self.cur = db.cursor()

        self.columns = self.db.getColumns(name)
        self.exists = bool(self.columns)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, columns=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(columns, tuple):
            cols = ','.join(["%s %s" % (c[0], c[1]) if isinstance(c, tuple) else c for c in columns])
        else:
            if columns is None:
                columns = self.table_object

            d = []
            for colName in dir(columns):
                ff = getattr(columns, colName)
                if isinstance(ff, Column):
                    d.append(ff.getStr(colName))
            if not d:
                raise SimpleORMException("Can't create a table with no columns")

            cols = ','.join(d)

        self.cur.execute("""create table %s (%s)""" % (self.name, cols))
        self.columns = self.db.getColumns(self.name)
        self.exists = bool(self.columns)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, extra='', ObjClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if ObjClass is None:
            ObjClass = self.table_object

        s = [col[1] for col in self.columns]

        try:
            for row in self.cur.execute("select _rowid_, %s from %s %s" % (','.join(s), self.name, extra)):
                yield self.createTableObject(row, ObjClass)

        except sqlite3.OperationalError as ex:
            raise SimpleORMException(str(extra) + ' -- Error: ' + ex.message)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getOne(self, extra='', ObjClass=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if ObjClass is None:
            ObjClass = self.table_object

        s = [col[1] for col in self.columns]

        try:
            self.cur.execute("select _rowid_,%s from %s %s" % (','.join(s), self.name, str(extra)))
        except sqlite3.OperationalError as ex:
            raise SimpleORMException(str(extra) + ' -- Error: ' + ex.message)

        row = self.cur.fetchone()
        if row is not None:
            return self.createTableObject(row, ObjClass)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def createTableObject(self, row, ObjClass):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tobj = ObjClass()
        tobj._table_ = self
        tobj._rowid_ = row[0]

        for idx, col in enumerate(self.columns):
            setattr(tobj, col[1], row[idx+1])

        tobj.fromDB()
        return tobj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def insert(self, tobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tobj.toDB()
        t = [getattr(tobj, col[1], None) for col in self.columns]
        p = ['?']*len(t)
        self.cur.execute('insert into %s values (%s)' % (self.name, ','.join(p)), tuple(t))
        tobj._rowid_ = self.cur.lastrowid
        tobj._table_ = self
        return tobj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cur.execute('truncate table ' + self.name)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delete(self, tobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cur.execute('delete from ? where _rowid_=?', (self.name, tobj._rowid_))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self, tobj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ["%s=?" % col[1] for col in self.columns]
        t = [getattr(tobj, col[1], None) for col in self.columns]
        self.cur.execute('update %s set %s where _rowid_=%d' % (self.name, ','.join(s), tobj._rowid_), tuple(t))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def createIndex(self, columnName, indexName=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if indexName is None:
            indexName = '%s_index_%d' % (self.name, self.indexIdx)
            self.indexIdx += 1
        self.cur.execute('create index %s on %s (%s)' % (indexName, self.name, columnName))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return '%s -- %s' % (self.name, str(['%s:%s' % (c[1], c[2]) for c in self.columns]))


#-------------------------------------------------------------------------------
class TableObject(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self._table_ = None
        self._rowid_ = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def fromDB(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ hook called immediately after 'column' fields are loaded from db
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def toDB(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ hook called immeidiately prior to saving 'column' fields to db
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._table_.update(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delete(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._table_.delete(self)

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
    import pylib.tester as tester

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class cool(TableObject):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sara = ColumnInteger()
        amy = ColumnText()

        def __init__(self, sara=None, amy=None):
            TableObject.__init__(self)
            self.sara = sara
            self.amy = amy

        def __str__(self):
            return str(self.sara) + ' ' + str(self.amy)

    db = DB()

    tbl = db.getTable('boo', ObjClass=cool)
    if not tbl.exists:
        tbl.create()

    for i in db.getTables():
        tbl1 = db.getTable(i[2])
        tester.Assert(str(tbl1) == "boo -- [u'amy:TEXT', u'sara:INTEGER']")

    tt = tbl.insert(cool(5, 'wife'))
    tbl.insert(cool(7, 'what'))

    ans = ['5 wife', '7 what']
    for idx, to in enumerate(tbl.get()):
        tester.Assert(str(to) == ans[idx])

    to = tbl.getOne("where amy='wife'")
    tester.Assert(str(to) == '5 wife')
    tester.Assert(str(tt) == '5 wife')

    to.sara = 13
    to.update()

    ans = ['13 wife', '7 what']
    for idx, to in enumerate(tbl.get()):
        tester.Assert(str(to) == ans[idx])

    db.close()
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

