"""

A window config mechanism

"""
import wx
import pylib.xmlparse1 as xp
import pylib.osscripts as oss
import traceback
import copyobj

#
# flags
#
WIN_MAXIMIZED = 0x01
WIN_ICONIZED  = 0x02


DEFAULT_CONFIG_DIR = "~/cfgs/"

#-------------------------------------------------------------------------------
def GetFlags(win):
#-------------------------------------------------------------------------------
    flags = 0
    if win.IsMaximized(): flags |= WIN_MAXIMIZED
    if win.IsIconized(): flags |= WIN_ICONIZED
    return flags

#-------------------------------------------------------------------------------
def Flags2Style(flags):
#-------------------------------------------------------------------------------
    style = 0
    if flags & WIN_MAXIMIZED == WIN_MAXIMIZED: style |= wx.MAXIMIZE
    if flags & WIN_ICONIZED == WIN_ICONIZED: style |= wx.ICONIZE
    return style

#-------------------------------------------------------------------------------
class CfgData(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(CfgData, self).__init__()


#-------------------------------------------------------------------------------
class Config(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName = "", path=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Config, self).__init__()
        self.Open(FileName, path)

        ## global config parameters
        self.MainWindowSize = (700, 450)
        self.MainWindowFlags = 0
        self.DefaultBkgdColor = (245, 245, 225)
        self.MainWindowPos = (100,100)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Open(self, FileName, path=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if oss.basename(FileName) == FileName:
            if path is None:
                path = DEFAULT_CONFIG_DIR
            fname = path + '/' + FileName
        else:
            fname = FileName

        self.FileName = oss.expanduser(fname)
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Clr2Tup(self, Clr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return int(Clr[0:2]), int(Clr[2:4]),int(Clr[4:6])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Tup2Clr(self, tup):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return "%02x%02x%02x" % tup

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not oss.exists(self.FileName):
            return

        xm = xp.XMLParsePathList(self.FileName)
        cwins = []

        try:
            dct = xm.Parse(["/config/children/child", "/config/main_win_params"])

            res = dct["/config/main_win_params"][0][0]
            self.MainWindowSize = (int(res["width"]), int(res["height"]))
            self.MainWindowFlags = int(res["flags"])

            if "/config/children/child" in dct:
                for d, cdata in dct["/config/children/child"]:
                    cwins.append((d["name"], int(d["flags"])))
        except:
            traceback.print_exc()
            print "Corrupted Config File -- Ignoring"

        return cwins

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f = file("out.xml", 'w')
        s = file("schema.xml", 'w')

        DmpObj(f, s, 0, "config", self)
        f.close()
        s.close()

#-------------------------------------------------------------------------------
class ConfigMDI(Config):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName = "", path=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Config.__init__(self, FileName, path)
        self.Perspective = ""
        self.projects = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not oss.exists(self.FileName):
            return []

        xm = xp.XMLParsePathList(self.FileName)
        cwins = []

        try:
            dct = xm.Parse(["/config/children/child", "/config/main_win_params", "/config/perspective"])

            res = dct["/config/main_win_params"][0][0]
            self.MainWindowSize = (int(res["width"]), int(res["height"]))
            self.MainWindowFlags = int(res["flags"])
            try:
                self.MainWindowPos =  (int(res["posx"]), int(res["posy"]))
            except KeyError:
                pass

            if "/config/children/child" in dct:
                for d, cdata in dct["/config/children/child"]:
                    cwins.append((d["name"], int(d["flags"])))

            if "/config/perspective" in dct:
                d = dct["/config/perspective"][0][0]
                self.Perspective = d['val']

        except:
            traceback.print_exc()
            print "Corrupted Config File -- Ignoring"

        return cwins

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self, cwins):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xg = xp.XMLGenPath(self.FileName)
        xg.AddPath("/config/main_win_params",
            {"width"  : self.MainWindowSize[0],
             "height" : self.MainWindowSize[1],
             "flags"  : self.MainWindowFlags,
             "bkclr"  : self.Tup2Clr(self.DefaultBkgdColor),
             "posx"   : self.MainWindowPos[0],
             "posy"   : self.MainWindowPos[1],
            })

        for name, flags in cwins:
            xg.AddPath("/config/children/child", {"name" : name, "flags" : flags})


        xg.AddPath("/config/perspective",
            {"val"  : self.Perspective,
            })

        xg.Write()



#-------------------------------------------------------------------------------
class CfgObj(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


import xml.dom.minidom as md

#-------------------------------------------------------------------------------
class BaseConfigObject(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class ConfigObjectException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, obj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        if not isinstance(obj, object):
            raise self.ConfigObjectException('object is not a new style class')

        self._obj = obj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return getattr(self._obj, attr)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setattr__(self, attr, val):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if attr in ['_obj', '_filename', '_defaultDir', '_wt']:
            self.__dict__[attr] = val
        else:
            setattr(self._obj, attr, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class DummyConfigObject(BaseConfigObject):
#-------------------------------------------------------------------------------
    def __init__(self, obj, *args):
        BaseConfigObject.__init__(self, obj)

    def Open(self, FileName):
        pass

    def Load(self):
        None

    def Save(self):
        pass

    def hasChanged(self):
        return True

#-------------------------------------------------------------------------------
class ConfigObject(BaseConfigObject):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, obj, filename, defaultDir = "~/cfgs/"):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseConfigObject.__init__(self, obj)

        self._defaultDir = defaultDir + ('/' if defaultDir else '')
        self._wt = None

        if defaultDir and not oss.exists(defaultDir):
            oss.mkdir(defaultDir)

        self.Open(self._defaultDir + filename)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Open(self, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._filename = oss.expanduser(FileName)
        print "ConfigObject:", self._filename
        if not oss.exists(self._filename):
            self.Save()

        self._wt = oss.FileTimeInt(self._filename)
        self.Load()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xo = xp.XMLToObj()
        try:
            nm, obj = xo.unmarshal(md.parse(self._filename))

            ## do it this way so that stored attributes only overwrite existing attributes
            ## enabling new attributes to default to what is in the code as well as
            ## attributes removed from the code not getting set
            copyobj.CopyObjList(self._obj, obj, [i for i in dir(obj) if i in dir(self._obj) and i not in dir(self._obj.__class__)])
        except:
            pass

        return self._obj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Save(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xo = xp.ObjToXML()

        try:
            oss.mv(self._filename, self._filename + '.bak')
        except IOError:
            pass

        try:
            otf = file(self._filename, 'w')
            otf.write(xo.marshal('config', self._obj) + '\n')
            otf.close()
        except IOError:
            try:
                oss.cp(self._filename + '.bak', self._filename)
            except:
                pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasChanged(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if oss.FileTimeInt(self._filename) > self._wt:
            self._wt = oss.FileTimeInt(self._filename)
            return True


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self._obj.__dict__)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    c = Config()

    c.Save()
    raw_input('done')


