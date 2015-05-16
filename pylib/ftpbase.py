import ftplib, socket, time, string, os.path

_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
_CUR_YEAR = time.localtime()[0]

#-------------------------------------------------------------------------------
def _CvtFTPListDate(month, day, tmyr):
#-------------------------------------------------------------------------------
    yr = _CUR_YEAR
    mo = (_MONTHS.index(month) + 1)
    d = int(day)

    try:
        h, m = string.split(tmyr, ':')
        h = int(h); m = int(m)
    except:
        yr = int(tmyr)
        h = m = 0

    return time.mktime((yr, mo, d, h, m, 0, 0, 1, -1))

#-------------------------------------------------------------------------------
def CvtPath(Path):
#-------------------------------------------------------------------------------
    s = ""
    for ch in Path:
        s += (ch == '\\' and '/') or ch
    return s

#-------------------------------------------------------------------------------
class FTPBaseExeception:
#-------------------------------------------------------------------------------
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return s

#-------------------------------------------------------------------------------
class FTPBase(ftplib.FTP):
#-------------------------------------------------------------------------------
    class tfile(file):
        def __init__(self, name, opts = 'r'):
            file.__init__(self, name, opts)

        def write(self, data):
            file.write(self, data + '\n')


    def __init__(self, MachName):
        ftplib.FTP.__init__(self, MachName)
        self.MakeDirs = False

    def SetMakeDirs(self, Act):
        self.MakeDirs = Act

    def GetTextFile(self, RmtName, LocName = None):
        if not LocName: LocName = RmtName

        try:
            f = self.tfile(LocName, 'w')
        except IOError:
            raise FTPBaseExeception("Can't open local file")

        try:
            self.retrlines('RETR ' + RmtName, f.write)
        except socket.error:
            raise FTPBaseExeception("Can't read remote file")
        except IOError:
            raise FTPBaseExeception("Can't write local file")

        bytes = f.tell()
        f.close()
        return bytes

    def GetBinFile(self, RmtName, LocName = None):
        if not LocName: LocName = RmtName

        try:
            f = file(LocName, 'w')
        except IOError:
            raise FTPBaseExeception("Can't open local file")

        try:
            self.retrbinary('RETR ' + RmtName, f.write)
        except socket.error:
            raise FTPBaseExeception("Can't read remote file")
        except IOError:
            raise FTPBaseExeception("Can't write local file")

        bytes = f.tell()
        f.close()
        return bytes

    def Listing(self, Dir = '.'):
        lst = []; dirs = []; files = []
        self.retrlines('LIST ' + Dir, lst.append)

        for l in lst:
            #print l
            words = string.split(l, None, 8)
            if len(words) < 6: continue

            if words[0][0] == 'd':
                #print words[-1]
                dirs.append(string.lstrip(words[-1]))
            else:
                d = _CvtFTPListDate(words[5], words[6], words[7])
                files.append((string.lstrip(words[-1]), int(words[4]), d))

        return dirs, files

    def __MkDirList(self, Name):
        l = [];  h = Name
        while h:
            h, t = os.path.split(h)
            if not h or h == '.': return l
            l.insert(0, h)
        return l

    def __MkRmtDirs(self, RmtName):
        lst = self.__MkDirList(RmtName)
        for l in lst:
            try:
                self.mkd(l)
                print "Made Directory:", l
            except:
                pass

    def __MkLocDirs(self, LocName):
        lst = self.__MkDirList(LocName)
        for l in lst:
            try:
                os.mkdir(l)
                print "Made Directory:", l
            except:
                pass

    def PutTextFile(self, RmtName, LocName = None):
        if not LocName: LocName = RmtName

        if self.MakeDirs: self.__MkRmtDirs(RmtName)

        try:
            f = file(LocName, 'r')
        except IOError:
            raise FTPBaseExeception("Can't open local file")

        try:
            self.storlines('STOR ' + RmtName, f)
        except socket.error:
            raise FTPBaseExeception("Can't write remote file")
        except IOError:
            raise FTPBaseExeception("Can't read local file")

        bytes = f.tell()
        f.close()
        return bytes

    def PutBinFile(self, RmtName, LocName = None):
        if not LocName: LocName = RmtName

        if self.MakeDirs: self.__MkRmtDirs(RmtName)

        try:
            f = file(LocName, 'r')
        except IOError:
            raise FTPBaseExeception("Can't open local file")

        try:
            self.storbinary('STOR ' + RmtName, f)
        except socket.error:
            raise FTPBaseExeception("Can't write remote file")
        except IOError:
            raise FTPBaseExeception("Can't read local file")

        bytes = f.tell()
        f.close()
        return bytes


TEST_LEVEL = 0
#-------------------------------------------------------------------------------
class ftptest:
#-------------------------------------------------------------------------------
    def __init__(self, nm):
        self.cdir = ['', '']
        print "Machine:", nm

    def cwd(self, dir):
        if dir == '..':
            t = self.cdir[0]
            self.cdir[0] = self.cdir[1]
            self.cdir[1] = t
        elif dir == '.':
            pass
        else:
            if dir[0] != '/':
                d = self.cdir[0] + '/' + dir
            else:
                d = dir

            self.cdir[1] = self.cdir[0]
            self.cdir[0] = d

        #print self.cdir

    def pwd(self):
        return self.cdir[0]

    def login(self, nm, pswd):
        return

    def Listing(self):
        if TEST_LEVEL == 1:
            tm = time.time()
        else:
            tm = 100

        if self.cdir[0] == '/spk/sp':
            return ["test1", "test2", "CVS"], [("t1.c", 0, tm), ("t2.c", 0, tm)]

        elif self.cdir[0][-5:-1] == 'test':
            return ["cool" + self.cdir[0][-1], "CVS"], [("t1.c", 0, tm), ("t2.c", 0, tm)]

        elif self.cdir[0][-5:-1] == 'cool':
            return [], [("t1.c", 0, tm), ("t2.c", 0, tm)]

        else:
            return [],[]

    def GetTextFile(self, fname):
        f = file(fname, 'w')
        str = self.pwd() + ' contents\n'
        f.write(str)
        f.close()
        return len(str)

    def quit(self):
        return


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if (__name__ == "__main__"):
    ftp = FTPBase('kirby.fc.hp.com')
    ftp.login("chrish", "kibsop)")

    print ftp.Listing('/tmp')
    ftp.PutTextFile("ftpbase.py")
    ftp.GetTextFile("ftpbase.py", "cool")
    ftp.PutBinFile("ftpbase_bin.py", "ftpbase.py")
    ftp.GetBinFile("ftpbase_bin.py", "cool1")
    ftp.quit()



