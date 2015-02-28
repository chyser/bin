#!/usr/bin/env python
"""
Library:
    Class wrapper around expat
"""


from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import xml.dom.minidom
import xml.parsers.expat

import xml.sax.saxutils
e = escape = xml.sax.saxutils.escape
u = unescape = xml.sax.saxutils.unescape

def quoteattr(val):
    return xml.sax.saxutils.quoteattr(str(val))

q = quoteattr

class xmlNodeException(Exception): pass
class ParseError(Exception): pass

#from xmlparse1 import *

#-------------------------------------------------------------------------------
class xmlNode(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s=None, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.parent = None

        self.tag = ''          ## node tag

        self.text = ''         ## concatenation of all text
        self.textchunks = []   ## list of non-consecutive text chunks found

        self.attr = {}         ## attributes in the node
        self.attrorder = []    ## list to maintain attribute order

        self.elem = None

        self.nodes = []        ## child xmlNodes
        self.allnodes = []     ## all children to include text, comments etc

        self.comments  = []      ## list of comments found
        self.leadingCmnt = None  ## comment that proceeds a node but indented similar

        ## if not raise exceptions on missing attributes return self.default
        if 'default' in kwds:
            self.setDefault(kwds['default'])
        else:
            self.raiseExceptions = True
            self.default = None

        self.attr_multiline = kwds.get('attr_multiline', 5)
        self.post_nl = kwds.get('post_nl', 0)

        ## create a node from string
        if s is not None:
            self.create(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setDefault(self, default=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ set a default value for failed attribute lookup, thus no exceptions
        """
        self.raiseExceptions = False
        self.default = default

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ create a node from a string
        """
        try:
            return self._createElem(xml.dom.minidom.parseString(s))
        except xml.parsers.expat.ExpatError, ex:
            raise xmlNodeException(ex)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findChildren(self, tag=None, equal=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of all children that match or don't match tag
            if tag is None return all children
        """
        if tag is None: return self.nodes

        if equal:
            return [n for n in self.nodes if n.tag == tag]
        return [n for n in self.nodes if n.tag != tag]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findChild(self, tag):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return child that matches
        """
        try:
            return self.findChildren(tag)[0]
        except IndexError:
            return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findPath(self, pth):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of nodes that match the specified '/' separated tag path
        """
        p = [self.tag] + pth.split('/') if pth[0] != '/' else pth.split('/')[1:]
        return self._fp(p)


    #
    # Dictionary-like access to attributes
    #

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
    def update(self, dct):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.attr.update(dct)
        self.attrorder = self.attr.keys()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.attr.copy()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return list(self.attrorder)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def values(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.attr.values()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def items(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return [(k, self.attr[k]) for k in self.attrorder]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __dict__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.attr

    #
    # adding child nodes, comments, and text
    #

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, xn_s, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add a node or a node created from a string return the node
        """
        if isinstance(xn_s, xmlNode):
            xn = xn_s
        elif isinstance(xn_s, (str, unicode)):
            xn = xmlNode(xn_s, **kwds)
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
        self.text += text
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
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        self._genStr(s, 0)
        return ''.join(s)

    ## compatibility
    genStr = __str__

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.writeFile(oss.stdout, ident)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeFile(self, fl, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        fl.write(self.genStr())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printTree(self, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.leadingCmnt:
            print(("    "*ident) + "lcmnt:  " + self.leadingCmnt)

        print(("    "*ident) + "tag:  " + self.tag)
        print(("    "*ident) + "attr: " + str(self.attr))

        for typ, c in self.allnodes:
            if typ == 'cmnt':
                print(("    "*ident) + "cmnt:  " + c)
            elif typ == 'text':
                print(("    "*ident) + "text:  " + c)
            else:
                c.printTree(ident + 1)
            print()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _fp(self, pthl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a list of nodes that match path list 'pthl'
        """
        if not pthl or self.tag != pthl[0]:
            return []

        pth = pthl[1:]
        if not pth:
            return [self]

        l = []
        for c in self.nodes:
            l.extend(c._fp(pth))
        return l

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _mkCmnt(self, c, ident, nl=True):
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
            space = True
            cmt = cmt[:-1]
        else:
            space = False

        for line in cmt.split('\n'):
            s.append(("    "*ident) + line + '\n')
        s.append(("    "*ident) + '-->\n')
        if space and nl:
            s.append('\n')
        return ''.join(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _genStr(self, s, ident):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.leadingCmnt is not None:
            s.append(self._mkCmnt(self.leadingCmnt, ident, nl=False))

        ## write the tag line
        tg = ["<%s" % self.tag]

        ## decoration for attributes
        if len(self.attr) < self.attr_multiline:
            bch = " ";  ech = tch = ''
        else:
            tg.append('\n')
            bch = "    "*(ident+1)
            tch = "    "*(ident)
            ech = '\n'

        ## walk attribute in order of being added
        for k in self.attrorder:
            tg.append('%s%s=%s%s' % (bch, k, quoteattr(self.attr[k]), ech))

        tg.append("%s>\n" % tch if self.allnodes else "%s/>\n" % tch)
        s.append("    "*(ident) + "".join(tg))

        ## if no children
        if not self.allnodes:
            if self.post_nl:
                s.append('\n'*self.post_nl)
            return

        ## generate nodes in order
        for typ, val in self.allnodes:
            if typ == 'cmnt':
                s.append(self._mkCmnt(val, ident+1))

            elif typ == 'text':
                s.append(("    "*ident) + escape(val))

            elif typ == 'node':
                val._genStr(s, ident+1)


        ## closing tag
        s.append(("    "*ident) + "</%s>\n" % self.tag)
        s.append('\n'*(self.post_nl+1))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _createElem(self, elem):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if elem.nodeType == 9:
            for en in elem.childNodes:
                n = self._createElem(en)
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
                    n._createElem(e)
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


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester

    def validate(s):
        if verbose:
            print(s)


    s="""<?xml version="1.0" encoding="UTF-8"?>
<!-- outer comment -->
<test:root xmlns:test="http://hp.com/capman/config/types">
    <!-- leading comment -->
    <test:pet cat="boo"/>
</test:root>
<!-- outer comment -->
"""
    xn = xmlNode(s)

    xn.copy()
    xn.keys()
    xn.values()
    xn.items()
    dict(xn)

    if verbose:
        xn.printTree()

    xn.genStr()
    s = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <!-- comment -->
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

    if verbose:
        print()
        xn.printTree()

    lst = xn.findChildren("pet")
    for l in lst:
        validate(l)

    for i in xn.findPath('/root/pet'):
        validate(i)

    for i in xn.findPath('/root/list/a'):
        validate(i)

    for i in xn.findPath('/root/list'):
        for j in i.findPath('a'):
            validate(j)

    return 0



if __name__ == "__main__":
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


