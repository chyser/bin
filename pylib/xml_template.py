import cgi
import pylib.osscripts as oss

from string import Template
import pylib.xmlparse as xmp
import pylib.relib as rl

class xmlTemplateException(Exception): pass


#-------------------------------------------------------------------------------
class xmlTemplate(object):
#-------------------------------------------------------------------------------
    """ roughly modelled on kid, but simpler
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ss):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(xmlTemplate, self).__init__()
        self.ss = ss
        self.mp = {}
        self.keywords = set(['py_if', 'py_for', 'py_replace', 'py_exec', 'py_content', 'py_include'])
        self.special = {'py_space' : '&nbsp;', 'py_lt' : '&lt;', 'py_gt' : '&gt;'}
        self.error = None
        self.nn = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.nn = xmp.xmlNode(self.ss)
        except xmp.ExpatError, ex:
            s = rl.scanf("$$: line $$, column $$")
            self.error = s.scan(str(ex))
            raise xmlTemplateException("xmlTemplate Error")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printError(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = self.error
        print "\nError: " + t[0] + "\n" + self.ss.split('\n')[int(t[1])-1] + "\n" + (' '*(int(t[2]))) + '^\n\n'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printErrorHtml(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        t = self.error
        print "<pre><code>"
        print cgi.escape(("\nError: '%s', line: %s, col: %s" % t) + "\n" + self.ss.split('\n')[int(t[1])-1] + "\n" + (' '*(int(t[2]))) + '^\n\n')
        print "</code></pre>"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def genXml(self, n, ss, mp):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ["<%s" % n.tag]
        for k, v in n.attr.items():
            if k not in self.keywords:
                s.append(' %s="%s"' % (k, v))
        s.append(">" + ss + n.text.strip() + "</%s>" % n.tag)
        return Template(''.join(s)).substitute(mp)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def chkNode(self, nn, mp):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print "chkNode -- tag:", nn.tag

        if "py_if" in nn.attr:
            try:
                #print nn.attr["py_if"]
                #print eval(nn.attr["py_if"], mp)

                if eval(nn.attr["py_if"], mp):
                    s = []
                    for n in nn.nodes:
                        s.append(self.chkNode(n, mp))
                    return self.genXml(nn, '\n'.join(s), mp)
            except NameError, ne:
                print >> oss.stdout, "py_if", ne

        elif "py_for" in nn.attr:
            s = []
            var, seq = nn.attr["py_for"].split(':')
            if seq in mp:
                for ss in self.mp[seq]:
                    mp[var] = ss
                    sss = []
                    for n in nn.nodes:
                        sss.append(self.chkNode(n, mp))
                    s.append(self.genXml(nn, ''.join(sss), mp))
            return ''.join(s)

        elif "py_replace" in nn.attr:
            try:
                return str(eval(nn.attr["py_replace"], mp))
            except NameError:
                return self.genXml(nn, '', mp)

        elif "py_content" in nn.attr:
            try:
                nn.text = str(eval(nn.attr["py_content"], mp))
            except NameError:
                pass
            return self.genXml(nn, '', mp)

        elif "py_exec" in nn.attr:
            try:
                exec(nn.attr["py_exec"], mp)
                return ''
            except NameError:
                return ''

        elif "py_include" in nn.attr:
            try:
                return file(nn.attr["py_include"]).read()
            except NameError:
                return self.genXml(nn, '', mp)

        else:
            s = []
            for n in nn.nodes:
                s.append(self.chkNode(n, mp))
            return self.genXml(nn, ''.join(s), mp)

        return ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sub(self, *map, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if map:
            self.mp = map[0]
            self.mp.update(kw)
        else:
            self.mp = kw
        self.mp.update(self.special)

        if self.nn is None:
            self.parse()

        return Template(self.chkNode(self.nn, self.mp)).substitute(self.mp)


