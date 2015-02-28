#!/usr/bin/env python
"""

Provides string templating capabilities beyond but compatible with
string.Template()

"""

import sys
import string


#-------------------------------------------------------------------------------
class TemplateException(Exception):
#-------------------------------------------------------------------------------
    """ Exceptions thrown by Template class

        variable I{ex} contains information about possible errors
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, s, ex):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Exception.__init__(self, s)
        self.ex = ex


#-------------------------------------------------------------------------------
class Template(object):
#-------------------------------------------------------------------------------
    """
    Substitutes fields from a provided dictionary into a template string while
    executing embedded python code::

    ExampleTemplateString = '''

    This is some $text that serves as a $doc, but

    I need conditionals

$$$ if onetime is not None:
$$$     i = 45
    The number is $i
$$$ end

    <ul>
$$$ for j in items:
$$$     for i in items:
$$$         url = "date_%s.html" % i
        <li><a html="$url">$j</a></li>
$$$     end
$$$ end
    </ul>
    '''

    using input {'items' : ['cool', 'aidan'], 'text' : 'words', 'doc' : 'thing', 'onetime' : True}
    results in::

    out = '''

    This is some words that serves as a thing, but

    I need conditionals

    The number is 45

    <ul>
        <li><a html="date_cool.html">cool</a></li>
        <li><a html="date_aidan.html">cool</a></li>
        <li><a html="date_cool.html">aidan</a></li>
        <li><a html="date_aidan.html">aidan</a></li>
    </ul>
    '''
    """

    ICmds = set(['if', 'for', 'while', 'try:'])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, template):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
            @type  template: str
            @param template: the template string (remains unmodified)
        """

        object.__init__(self)
        self.template = template
        self.dbg = 0
        self.ddct = None
        self.ex = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def subl(self, ddct):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        perform substitutions on the template using values from ddct and
        return a list of strings broken on the original '\\n' boundaries

        @type  ddct: dict
        @param ddct: contains substitutions (see string.Template) as well as
            any variables used by embedded python code

        @rtype: list
        @return: returns a list broken on '\\n' boundaries
        """

        self.ddct = ddct
        dct = ddct.copy()
        dct['__out__'] = []

        prgm = ['import string']
        indent = 0
        lineNum = 0

        for line in self.template.split('\n'):
            lineNum += 1
            if line.startswith('$$$'):
                pycmd = line[4:]
                pyc = pycmd.split()
                if pyc:
                    if pyc[0] in self.ICmds:
                        indent += 1
                    elif pyc[0] == 'end':
                        indent -= 1
                        continue

                prgm.append(pycmd)
            else:
                if '$' in line:
                    prgm.append(('    '*indent) + "__out__.append(string.Template('''%s''').substitute(globals()))" % line)
                else:
                    prgm.append(('    '*indent) + "__out__.append('''%s''')" % line)

        if self.dbg:
            print ddct
            for ln, v in enumerate(prgm):
                print "%3d:" % (ln+1), v

        try:
            exec('\n'.join(prgm), dct)
        except Exception:
            if self.dbg:
                raise

            ex = sys.exc_info()
            self.ex = str(ex[0]) + ' ' + str(ex[1])
            raise TemplateException("Template Exception", str(ex[0]) + ' ' + str(ex[1]))

        return dct['__out__']

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def printErrors(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        prints any errors from the substitution process
        """

        print self.ex
        print "input dict:", self.ddct
        for ln, v in enumerate(self.template.split('\n')):
            print "%2d:" % (ln+2), v

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sub(self, dct, jn='\n'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        performs the substitution as per L{subl}() with the strings
        joined by jn.

        @type  dct: dict
        @param dct: dictionary containing the substitutions and variable
            needed by the embedded code
        @type  jn: str
        @param jn: string used to join L{subl}()'s list together

        @rtype: str
        @return: returns the string following all substitutions
        """

        return jn.join(self.subl(dct))



#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    import pylib.tester as tester

    t = """

    This is some $text that serves as a $doc, but

    I need conditionals

$$$ if onetime is not None:
$$$     i = 45
    The number is $i
$$$ end

    <ul>
$$$ for j in items:
$$$     for i in items:
$$$         url = "date_%s.html" % i
        <li><a html="$url">$j</a></li>
$$$     end
$$$ end
    </ul>
    """

    tmp = Template(t)
    #tmp.dbg = 1

    #print '------------------'
    #print t
    #print '------------------'
    try:
        val = tmp.sub({'items' : ['cool', 'aidan'], 'text' : 'words', 'doc' : 'thing', 'onetime' : True})
    except TemplateException, ex:
        print tmp.printErrors()
        raise

    good = """

    This is some words that serves as a thing, but

    I need conditionals

    The number is 45

    <ul>
        <li><a html="date_cool.html">cool</a></li>
        <li><a html="date_aidan.html">cool</a></li>
        <li><a html="date_cool.html">aidan</a></li>
        <li><a html="date_aidan.html">aidan</a></li>
    </ul>
    """

###    print "'%s'" % val
###    print "'%s'" % good
###
###    for idx, ch in enumerate(val):
###        if good[idx] != ch:
###            print "error", idx, "'%s'" % ch, "'%s'" % good[idx]

    tester.Assert(val == good, "Substitution Comparison Failed")


    tmp = Template('cvs.exe ci\n$$$ if msg:\n-m "$msg"\n$$$ end\n$file')
    tmp.dbg = 0

    try:
        val1 = tmp.sub({'msg' : '', 'file' : 'cool'}, ' ')
        val2 = tmp.sub({'msg' : 'cool', 'file':'ff'}, ' ')
    except TemplateException:
        print tmp.printErrors()
        raise

    tester.Assert(val1 == 'cvs.exe ci cool', "Substitution Comparison Failed 1")
    tester.Assert(val2 == 'cvs.exe ci -m "cool" ff', "Substitution Comparison Failed 2")


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    def usage(rc, errmsg=""):
        print >> oss.stderr, __doc__
        if errmsg:
            print >> oss.stderr, """\nError:\n""" + str(errmsg)
        oss.exit(rc)

    args, opts = oss.gopt(oss.argv[1:], [], [], usage)

    __test__()
    oss.exit(0)

