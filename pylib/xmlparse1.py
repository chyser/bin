"""
Class wrapper around expat
"""
import sys
import types

import xml.dom
import xml.dom.minidom
import xml.parsers.expat
import pylib.osscripts as oss

from xml.parsers.expat import ExpatError

import xml.sax.saxutils

e = escape = xml.sax.saxutils.escape
u = unescape = xml.sax.saxutils.unescape

#-------------------------------------------------------------------------------
def quoteattr(val):
#-------------------------------------------------------------------------------
    """ quote val to be a legitimate xml attribute
    """
    return xml.sax.saxutils.quoteattr(str(val))

q = quoteattr

#-------------------------------------------------------------------------------
class ParseError(Exception):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Exception.__init__(self, s)
        self.ErrorMessage = s


#-------------------------------------------------------------------------------
class ParserObjBase(object):
#-------------------------------------------------------------------------------
    """ This class should be overridden with some subset of the following methods
        provided:

            def StartElement(self, Name, Attrs): pass
            def EndElement(self, Name): pass
            def CharData(self, Data): pass
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ParserObjBase, self).__init__()

        self.p = xml.parsers.expat.ParserCreate()
        self.p.StartElementHandler  = self.StartElement
        self.p.EndElementHandler    = self.EndElement
        self.p.CharacterDataHandler = self.CharData

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ParseFile(self, FileName, FileMustExist = True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ parses file Filename. the overridden functions are assumed to set
            internal state which may be accessed after this call. FileMustExist
            is a boolean which cause an IOError exception if FileName not present
        """
        FileName = oss.expanduser(FileName)
        try:
            f = file(FileName, 'rU')
        except IOError, err:
            if not FileMustExist and err.errno == 2: return
            raise

        self.p.ParseFile(f)
        f.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ParseFileObj(self, inf):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.p.ParseFile(inf)

    def StartElement(self, Name, Attrs): pass
    def EndElement(self, Name): pass
    def CharData(self, Data): pass


#-------------------------------------------------------------------------------
class XMLParser(ParserObjBase):
#-------------------------------------------------------------------------------
    """ A class with a simple Parse method which compares a XML path "/dfdf/dfdf/
        and returns a tuple of Attr dict and CData string
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLParser, self).__init__()
        self.path = []
        self.FileName = FileName
        self.Results = []
        self.tRes = None
        self.tChar = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Parse(self, Path):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.TPath = Path
        self.ParseFile(self.FileName)
        return self.Results

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def StartElement(self, Name, Attrs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.path.append(Name)

        if self.TPath == '/'.join(self.path):
            self.tRes = Attrs

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CharData(self, Data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.tChar.append(Data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def EndElement(self, Name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.tRes is not None:
            self.Results.append((self.tRes, ''.join(self.tChar)))
            self.tRes = None
            self.tChar = []

        self.path.pop()

#-------------------------------------------------------------------------------
class XMLParsePathList(ParserObjBase):
#-------------------------------------------------------------------------------
    """ A class with a simple Parse method which compares XML paths "/dfdf/dfdf/
        and returns a path indexed dictionary of tuple Attr dict and CData string
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLParsePathList, self).__init__()
        self.FileName = FileName
        self.path = []
        self.Results = {}
        self.attrs = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Parse(self, PathList):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.PathList = PathList
        self.ParseFile(self.FileName)
        return self.Results

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def StartElement(self, Name, Attrs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.path.append(Name)
        p = '/'  + '/'.join(self.path)

        if p in self.PathList:
            self.curPath = p
            self.attrs = Attrs
            self.cdata = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CharData(self, Data):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.attrs is not None:
            self.cdata.append(Data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def EndElement(self, Name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.attrs is not None:
            self.Results.setdefault(self.curPath, []).append((self.attrs, unescape(''.join(self.cdata))))
            self.attrs = None

        self.path.pop()


#-------------------------------------------------------------------------------
class XMLGenPath(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class XMLGenPathException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            super(XMLGenPathException, self).__init__(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, FileName):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLGenPath, self).__init__()
        self.dct = {}
        self.path = {}
        self.FileName = FileName

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddPath(self, Path, lst):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if Path[0] != '/':
            raise XMLGenPath.XMLGenPathException("path must have leading '/'")

        dct = self.dct
        for i in Path[1:].split('/'):
            if i not in dct: dct[i] = {}
            dct = dct[i]

        lt = self.path.setdefault(Path, [])

        if isinstance(lst, list):
            lt.extend(lst)
        elif isinstance(lst, tuple):
            lt.append(lst)
        elif isinstance(lst, dict):
            lt.append((lst, ""))
        else:
            raise XMLGenPath.XMLGenPathException("incorrect value of lst")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def wrt(self, otf, sdct, p, pth):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if pth in self.path:
            for dct, cdata in self.path[pth]:
                print >> otf, "<%s" % (p),
                for ky, vl in dct.items():
                    print >> otf, "%s=%s" % (ky, quoteattr(str(vl))),
                print >> otf, (cdata == "" and "/>") or ">%s</%s>" % (escape(str(cdata)), p)
        else:
            print >> otf, "<%s>" % p
            for d in sdct.keys():
                self.wrt(otf, sdct[d], d, pth + '/' + d)
            print >> otf, "</%s>" % p

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Write(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        otf = file(self.FileName, 'w')
        print >> otf, '<?xml version="1.0"?>'

        l = self.dct.keys()[0]
        self.wrt(otf, self.dct[l], l, '/' + l)
        otf.close()


#-------------------------------------------------------------------------------
class ObjToXML(object):
#-------------------------------------------------------------------------------
    """ transform an object into an XML string

        Usage Rules:
            USE_OBJ_TO_XML_MARSHAL - call method _ObjToXMLMarshal(self, ObjToXML obj) if it exists

    """

    USE_OBJ_TO_XML_MARSHAL = 0x1
    MARSHAL_ALL_ATTR       = 0x2
    USE_XMLSCHEMA_TYPES    = 0x4


    #---------------------------------------------------------------------------
    class ObjToXMLException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, Rules=USE_OBJ_TO_XML_MARSHAL | MARSHAL_ALL_ATTR):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ObjToXML, self).__init__()
        self.Rules = Rules

        self.sa = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def typeDispatch(self, obj, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        meth = getattr(self, "_marshal_" + type(obj).__name__, self._marshal_obj)
        return meth(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_NoneType(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:NoneType"'
        self.sa.append(("    "*ident) + "<%s%s />" % (tag, typ))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_int(self, tag, val, ident=0, typ=' type="pyd:int"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, long(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_long(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_int(tag, val, ident, ' type="pyd:long"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_float(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:float"'
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, float(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_complex(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:complex"'
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, complex(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_bool(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:bool"'
        self.sa.append(("    "*ident) + '<%s%s>%s</%s>' % (tag, typ, bool(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_str(self, tag, val, ident=0, typ = ' type="pyd:str"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(("    "*ident) + "<%s%s>%s</%s>" % (tag, typ, escape(str(val)), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_unicode(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_str(tag, val, ident, ' type="pyd:unicode"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_list(self, tag, val, ident=0, typ = ' type="pyd:list"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))
        for i in val:
            self.typeDispatch(i, '_' + tag, i, ident+1)
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_tuple(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_list(tag, val, ident, ' type="pyd:tuple"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_dict(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:dict"'
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))
        for k,v in val.items():
            self.typeDispatch(v, k, v, ident+1)
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_obj(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:class_%s"' % type(val).__name__
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))

        if self.Rules & ObjToXML.USE_OBJ_TO_XML_MARSHAL:
            meth = getattr(val, "_ObjToXMLMarshal", None)
            if meth is not None:
                meth(self)
                self.sa.append(('    '*ident) + '</%s>' % val.__name__)
                return

        _cls = getattr(val, '__class__', None)
        cls = (_cls and dir(_cls)) or []

        for attr in dir(val):
            if attr not in cls:
                if self.Rules & ObjToXML.MARSHAL_ALL_ATTR or attr[0] != '_':
                    v = getattr(val, attr)
                    self.typeDispatch(v, attr, v, ident+1)
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def marshal(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa = []
        self.typeDispatch(val, tag, val, ident)
        return '\n'.join(self.sa)

#-------------------------------------------------------------------------------
class XMLToObj(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class XMLToObjException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, modList = sys.modules.values(), newObj=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLToObj, self).__init__()
        self.modList = modList
        if newObj is not None:
            self.newObj = newObj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def newObj(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for mod in self.modList:
            if mod and name in mod.__dict__:
                cls = mod.__dict__[name]
                base = cls.__bases__[0]
                #print mod.__dict__[name], mod.__dict__[name].__bases__
                return base.__new__(cls, None)

        raise XMLToObj.XMLToObjException('No class: "%s"' % name)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getText(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rc = []
        for node in elem.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def typeDispatch(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = elem.getAttribute('type').split(':')[1]
        meth = getattr(self, '_unmarshal_' + typ, self._unmarshal_obj)
        return meth(typ, elem)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_NoneType(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_int(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, int(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_str(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, unescape(str(self.getText(elem)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_unicode(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, unicode(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_float(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, float(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_bool(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, self.getText(elem) == "True"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_complex(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, complex(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_list(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                l.append(self.typeDispatch(node)[1])
        return elem.tagName, l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_tuple(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        attr, val = self._unmarshal_list(typ, elem)
        return attr, tuple(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_dict(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = {}
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                attr, val = self.typeDispatch(node)
                d[attr] = val

        return elem.tagName, d

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_obj(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        o = self.newObj(typ[6:])
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                attr, val = self.typeDispatch(node)
                setattr(o, attr, val)

        return elem.tagName, o

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unmarshal_str(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import xml.dom.minidom
        return self.unmarshal(xml.dom.minidom.parseString(s))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unmarshal(self, dom):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.typeDispatch(dom.documentElement)


#-------------------------------------------------------------------------------
class ObjToXML2(object):
#-------------------------------------------------------------------------------
    """ transform an object into an XML string

        Usage Rules:
            USE_OBJ_TO_XML_MARSHAL - call method _ObjToXMLMarshal(self, ObjToXML obj) if it exists

    """

    USE_OBJ_TO_XML_MARSHAL = 0x1
    MARSHAL_ALL_ATTR       = 0x2
    USE_XMLSCHEMA_TYPES    = 0x4


    #---------------------------------------------------------------------------
    class ObjToXMLException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, Rules=USE_OBJ_TO_XML_MARSHAL | MARSHAL_ALL_ATTR):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(ObjToXML2, self).__init__()
        self.Rules = Rules

        self.sa = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def typeDispatch(self, obj, *args):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        meth = getattr(self, "_marshal_" + type(obj).__name__, self._marshal_obj)
        return meth(*args)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_NoneType(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:NoneType"'
        self.sa.append(("    "*ident) + "<%s%s />" % (tag, typ))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_int(self, tag, val, ident=0, typ=' type="pyd:int"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, long(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_long(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_int(tag, val, ident, ' type="pyd:long"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_float(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:float"'
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, float(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_complex(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:complex"'
        self.sa.append(("    "*ident) + "<%s%s>%ld</%s>" % (tag, typ, complex(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_bool(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:bool"'
        self.sa.append(("    "*ident) + '<%s%s>%s</%s>' % (tag, typ, bool(val), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_str(self, tag, val, ident=0, typ = ' type="pyd:str"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(("    "*ident) + "<%s%s>%s</%s>" % (tag, typ, escape(str(val)), tag))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_unicode(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_str(tag, val, ident, ' type="pyd:unicode"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_list(self, tag, val, ident=0, typ = ' type="pyd:list"'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))
        for i in val:
            self.typeDispatch(i, '_' + tag, i, ident+1)
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_tuple(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._marshal_list(tag, val, ident, ' type="pyd:tuple"')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_dict(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:dict"'
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))
        for k,v in val.items():
            self.sa.append(('    '*(ident+1)) + '<%s%s>' % ('_dict', ''))
            self.typeDispatch(k, '_key', k, ident+2)
            self.typeDispatch(v, '_val', v, ident+2)
            self.sa.append(('    '*(ident+1)) + '</%s>' % '_dict')
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _marshal_obj(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = ' type="pyd:class_%s"' % type(val).__name__
        self.sa.append(('    '*ident) + '<%s%s>' % (tag, typ))

        if self.Rules & ObjToXML.USE_OBJ_TO_XML_MARSHAL:
            meth = getattr(val, "_ObjToXMLMarshal", None)
            if meth is not None:
                meth(self)
                self.sa.append(('    '*ident) + '</%s>' % val.__name__)
                return

        _cls = getattr(val, '__class__', None)
        cls = (_cls and dir(_cls)) or []

        for attr in dir(val):
            if attr not in cls:
                if self.Rules & ObjToXML.MARSHAL_ALL_ATTR or attr[0] != '_':
                    v = getattr(val, attr)
                    self.typeDispatch(v, attr, v, ident+1)
        self.sa.append(('    '*ident) + '</%s>' % tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def marshal(self, tag, val, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.sa = []
        self.typeDispatch(val, tag, val, ident)
        return '\n'.join(self.sa)

#-------------------------------------------------------------------------------
class XMLToObj2(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class XMLToObjException(Exception):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, s):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            Exception.__init__(self, s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, modList = sys.modules.values(), newObj=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLToObj2, self).__init__()
        self.modList = modList
        if newObj is not None:
            self.newObj = newObj

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def newObj(self, name):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for mod in self.modList:
            if mod and name in mod.__dict__:
                cls = mod.__dict__[name]
                base = cls.__bases__[0]
                #print mod.__dict__[name], mod.__dict__[name].__bases__
                return base.__new__(cls, None)

        raise XMLToObj.XMLToObjException('No class: "%s"' % name)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getText(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rc = []
        for node in elem.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def typeDispatch(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        typ = elem.getAttribute('type').split(':')[1]
        meth = getattr(self, '_unmarshal_' + typ, self._unmarshal_obj)
        return meth(typ, elem)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_NoneType(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_int(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, int(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_str(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, unescape(str(self.getText(elem)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_unicode(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, unicode(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_float(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, float(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_bool(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, self.getText(elem) == "True"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_complex(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return elem.tagName, complex(self.getText(elem))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_list(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        l = []
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                l.append(self.typeDispatch(node)[1])
        return elem.tagName, l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_tuple(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        attr, val = self._unmarshal_list(typ, elem)
        return attr, tuple(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_dict_element(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        key = value = None
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                attr, val = self.typeDispatch(node)
                if node.nodeName == "_key":
                    key = val
                elif node.nodeName == "_val":
                    value = val
                else:
                    raise XMLToObj2.XMLToObjException('Illegal dict_element tag')
        return key, value

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_dict(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = {}
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                attr, val = self._unmarshal_dict_element('', node)
                d[attr] = val

        return elem.tagName, d

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _unmarshal_obj(self, typ, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        o = self.newObj(typ[6:])
        for node in elem.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                attr, val = self.typeDispatch(node)
                setattr(o, attr, val)

        return elem.tagName, o

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unmarshal_str(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        import xml.dom.minidom
        return self.unmarshal(xml.dom.minidom.parseString(s))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unmarshal(self, dom):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.typeDispatch(dom.documentElement)


#-------------------------------------------------------------------------------
class XMLConfigBase(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(XMLConfigBase, self).__init__()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _getOptionalAttributes(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## optional values are a dict with attribute name as key and value the
        ## class type which must support default construction
        return {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## handle optional values
        if attr == "_xcbOptionalAttributes":
            setattr(self, "_xcbOptionalAttributes", self._getOptionalAttributes())
            return self._xcbOptionalAttributes

        return self._xcbOptionalAttributes[attr]()


class xmlNodeException(Exception): pass

#-------------------------------------------------------------------------------
class xmlNode(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s_d = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(xmlNode, self).__init__()
        self.parent = None
        self.tag = ''
        self.text = ''
        self.textchunks = []
        self.attr = {}
        self.elem = None
        self.nodes = []
        self.allnodes = []
        self.comments  = []
        self.raiseExceptions = True
        self.leadingCmnt = None
        self.default = None
        self.attrorder = []

        if s_d is not None:
            if isinstance(s_d, (str, unicode)):
                self.create(s_d)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setDefault(self, default):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.raiseExceptions = False
        self.default = default

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findChildren(self, tag):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [n for n in self.nodes if n.tag == tag]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findChild(self, tag):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return self.findChildren(tag)[0]
        except IndexError:
            return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _fp(self, pth):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not pth:
            return []

        p = pth[0]
        pth = pth[1:]

        if self.tag != p:
            return []

        if not pth:
            return [self]

        l = []
        for c in self.nodes:
            l.extend(c._fp(pth))
        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findPath(self, pth):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if pth[0] != '/':
            p = [self.tag] + pth.split('/')
        else:
            p = pth.split('/')[1:]
        return self._fp(p)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def createElem(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if elem.nodeType == 9:
            for en in elem.childNodes:
                n = self.createElem(en)
            return self

        elif elem.nodeType == 1:
            self.elem = elem
            self.tag = elem.tagName

            # attributes
            l = elem.attributes.length
            for i in range(l):
                a = elem.attributes.item(i)
                self.attrorder.append(a.name)
                self.attr[a.name] = a.nodeValue

            for e in elem.childNodes:
                ## text
                if e.nodeType == 3:
                    self.text += e.data
                    self.textchunks.append(e.data)
                    self.allnodes.append(('text', e.data))

                ## comment
                elif e.nodeType == 8:
                    if self.tag:
                        self.comments.append(e.data)
                        self.allnodes.append(('cmnt', e.data))
                    else:
                        self.leadingCmnt = e.data

                ## node
                else:
                    n = xmlNode()
                    n.parent = self
                    v = n.createElem(e)
                    if n.tag:
                        self.nodes.append(n)
                        self.allnodes.append(('node', n))

        elif elem.nodeType == 3:
            return None

        elif elem.nodeType == 8:
            if self.tag:
                self.comments.append(elem.data)
                self.allnodes.append(('cmnt', elem.data))
            else:
                self.leadingCmnt = elem.data


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __contains__(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return key in self.attr

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getitem__(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.raiseExceptions:
            return self.attr[key]
        return self.attr.get(key, self.default)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __setitem__(self, key, value):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ preserve order
        """
        self.attrorder.append(key)
        self.attr[key] = escape(value)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get(self, key, val=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.attr.get(key, val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, xn_s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(xn_s, xmlNode):
            xn = xn_s
        elif isinstance(xn_s, (str, unicode)):
            xn = xmlNode(xn_s)
        else:
            raise xmlNodeException('cannot create node of this type')

        self.nodes.append(xn)
        self.allnodes.append(('node', xn))
        return xn

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCmnt(self, comment):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ creates an xml comment
            if startswith '\\n' (ie string representation of '\n' not '\n'
            then a newline is added before comment
        """
        self.allnodes.append(('cmnt', escape(comment)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addText(self, text):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.textchunks.append(escape(text))
        self.allnodes.append(('text', escape(text)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addLeadingCmnt(self, comment):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ creates an xml comment before this node
            if startswith '\\n' (ie string representation of '\n' not '\n'
            then a newline is added before comment
        """
        self.leadingCmnt = escape(comment)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            return self.createElem(xml.dom.minidom.parseString(s))
        except xml.parsers.expat.ExpatError, ex:
            raise ParseError(str(ex))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.writeFile(sys.stdout, ident)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeFile(self, fl, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fl.write(self.genStr())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __mkCmnt(self, c, ident):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ creates an xml comment from c
        """
        if c.startswith('\\n'):
            s = ['\n']; cmt = c[2:]
        else:
            s = []; cmt = c

        s.append(("    "*ident) + "<!-- ")

        l = cmt.split('\n')
        if len(l) == 1:
            s.append(cmt + ' -->\n')
            return ''.join(s)

        if cmt.endswith('\n'):
            cmt = cmt[:-1]
        for line in cmt.split('\n'):
            # print line
            s.append(("    "*ident) + line + '\n')
        s.append(("    "*ident) + '-->\n')
        return ''.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _genStr(self, s, ident):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.leadingCmnt is not None:
            s.append(self.__mkCmnt(self.leadingCmnt, ident))

        ## write the tag line
        tg = ["<%s" % self.tag]

        ## decorate attributes
        inline = len(self.attr) < 5

        if inline:
            bch = " ";  ech = tch = ''
        else:
            tg.append('\n')
            bch = "    "*(ident+1)
            tch = "    "*(ident)
            ech = '\n'

        ## walk attribute in order of being added
        for k in self.attrorder:
            v = self.attr[k]
            tg.append('%s%s=%s%s' % (bch, k, q(v), ech))

        if self.allnodes:
            tg.append("%s>\n" % tch)
        else:
            tg.append("%s/>\n" % tch)

        s.append("    "*(ident) + "".join(tg))


        if not self.allnodes:
            return

        for typ, val in self.allnodes:
            if typ == 'cmnt':
                s.append(self.__mkCmnt(val, ident+1))

            elif typ == 'text':
                s.append(("    "*ident) + e(val))

            elif typ == 'node':
                val._genStr(s, ident+1)

            s.append('\n')

        s.append(("    "*ident) + "</%s>\n" % self.tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def genStr(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        self._genStr(s, 0)
        return ''.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printTree(self, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.leadingCmnt:
            print ("    "*ident) + "lcmnt:  " + self.leadingCmnt

        print ("    "*ident) + "tag:  " + self.tag
        print ("    "*ident) + "attr: " + str(self.attr)

        for typ, c in self.allnodes:
            if typ == 'cmnt':
                print ("    "*ident) + "cmnt:  " + c
            elif typ == 'text':
                print ("    "*ident) + "text:  " + c
            else:
                c.printTree(ident + 1)
            print

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.tag + ": '%s'" % self.text.strip()


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    if 0:
        xg = XMLGenPath("text.xml")

        xg.AddPath("cool/some/connor", [({'width':'123'}, ""), ({'width':'124'}, "cool\n")])
        xg.AddPath("cool/some/aidan", [({'width':'123'}, ""), ({'width':'124'}, "cool\n")])

        xg.Write()

    s="""<?xml version="1.0" encoding="UTF-8"?>
<test:root xmlns:test="http://hp.com/capman/config/types">
    <test:pet cat="boo"/>
</test:root>
"""
    xn = xmlNode(s)

    xn.printTree()

    s="""<?xml version="1.0" encoding="UTF-8"?>
<root>
    <pet cat="boo"/>
    <pet dog="no"/>
    <list>
        <a>
          cool
        </a>
        <a>
          cool
        </a>
    </list>
</root>
"""
    xn = xmlNode(s)

    print
    xn.printTree()

    lst = xn.findChildren("pet")
    for l in lst:
        print l

    for i in xn.findPath('/root/pet'):
        print i

    for i in xn.findPath('/root/list/a'):
        print i

    for i in xn.findPath('/root/list'):
        for j in i.findPath('a'):
            print j

