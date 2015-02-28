#!/usr/bin/env python
"""

"""

import sqlite3
import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)


#-------------------------------------------------------------------------------
class SQLite(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.con = sqlite3.connect(fileName)

        #con.execute("create table tags(type, file, lineNum, class, func, sig, doc)")


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def execute(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.con.execute(*args)


#-------------------------------------------------------------------------------
class SQLiteInteractive(SQLite):
#-------------------------------------------------------------------------------

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getTables(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.execute("select * from SQLITE_MASTER")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def help(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def execute(self, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return SQLite.execute(self, *args)
        except sqlite3.OperationalError as e:
            print e
            return []



if __name__ == "__main__":
    main(oss.argv)
    oss.exit(0)

