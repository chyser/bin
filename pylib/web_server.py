import sys
import os
import traceback
import cgi
import time
from string import Template

import BaseHTTPServer
import urllib

escape = cgi.escape

DBG_LVL = 0
LOGFILENAME = None
LOGFILE = sys.stdout

#-------------------------------------------------------------------------------
def SetDbgLvl(val):
#-------------------------------------------------------------------------------
    global DBG_LVL
    DBG_LVL = val

#-------------------------------------------------------------------------------
def DbgPrint(*arg):
#-------------------------------------------------------------------------------
    try:
        lvl = int(arg[0])
        arg = arg[1:]
    except:
        lvl = 1

    if DBG_LVL >= lvl:
        print """<br><font color=#ff0000> <b>&lt;DEBUG&gt;&nbsp;&nbsp;"""
        print ' '.join([str(v) for v in arg])
        print """</b></font><br>"""

#-------------------------------------------------------------------------------
def log(*arg):
#-------------------------------------------------------------------------------
    try:
        lvl = int(arg[0])
        arg = arg[1:]
    except:
        lvl = 1

    if DBG_LVL >= lvl:
        s = ' '.join([str(v) for v in arg]) + '\n'
        if LOGFILENAME is not None:
            oss.echo(s, LOGFILENAME, 'a')
        else:
            oss.stdout.write(s)

#-------------------------------------------------------------------------------
def MessageBox(Msg):
#-------------------------------------------------------------------------------
    print """
        <script language="javascript" type="text/javascript">
        <!--
        confirm("%s")
        // -->
        </script>
        """ % Msg

#-------------------------------------------------------------------------------
def FillObjectFromForm(obj, form, default=""):
#-------------------------------------------------------------------------------
    for k in obj.__dict__.keys():
        if k in form:
            obj.__dict__[k] = form.getfirst(k, default)
    return obj

#-------------------------------------------------------------------------------
def DetermineAction(ActLst, form):
#-------------------------------------------------------------------------------
    for al in ActLst:
        if al in form:
            return al

#-------------------------------------------------------------------------------
def CreateStyleSheetLink(sheetName, media="all", title="WebPage"):
#-------------------------------------------------------------------------------
    """ XHTML compliant link
    """

    return '<link rel="stylesheet" type="text/css" href="%s" media="%s" title="%s" />' % (sheetName, media, title)

#-------------------------------------------------------------------------------
def GenError(errMsg, Heading="Error:"):
#-------------------------------------------------------------------------------
    return """<p class="ERROR">""" + ("<br/><b>%s</b><br/>" % Heading) + errMsg + "<br/><br/></p>"

#-------------------------------------------------------------------------------
def PrintError(errMsg):
#-------------------------------------------------------------------------------
    print GenError(errMsg)


MAIN_PAGE_BEG = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
    <title>
        ${Title}
    </title>
    <style>
    <!--
        p.ERROR {
            position:fixed;
            top:0;
            left:0;
            width:100%;
            color:black; background-color:white; font-family:Courier;
            white-space:pre; z-index:500; padding:10px;
        }
    -->
    </style>

    <meta http-equiv="expires" content="0" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Cache-Control" content="no-cache" />

    <!-- meta data standards can be found at http://eservices.athp.hp.com/documents/metaStan.asp -->
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1252" />
    ${HeadAdd}
</head>

<!--
// Body
-->
<body>
"""

MAIN_PAGE_END = """ %s </body> </html>"""



#-------------------------------------------------------------------------------
class BaseWebServer(object):
#-------------------------------------------------------------------------------
    """ A CGI web framework
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.PageBegin = MAIN_PAGE_BEG
        self.PageEnd = MAIN_PAGE_END
        self.Title = ""
        self.HeadAdd = ""
        self.EndAdd = ""

        self.path_info = ""
        self.server_name = ""
        self.script_name = ""
        self.server_port = ""
        self.init()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def init(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.url0 = "http://%s:%s%s" % (self.server_name, self.server_port, self.script_name)
        self.url = self.url0 + self.path_info

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        DbgPrint("h")
        try:
            try:
                self.form = cgi.FieldStorage()
                self.begin()

                self.PrintPageBeg()
                self.ServiceRequest()

            except:
                PrintError(traceback.format_exc())
        finally:
            self.PrintPageEnd()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def begin(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ServiceRequest(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ Override this function to handle the web request
        """
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DisplayHomePage(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print "WebUtil WebServer Home Page"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PrintPageBeg(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print "Content-type: text/html"
        print "Pragma: no-cache"
        print

        tp = Template(self.PageBegin)
        s = tp.substitute(Title = self.Title, HeadAdd = self.HeadAdd)
        print s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PrintPageEnd(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print self.PageEnd % self.EndAdd


#-------------------------------------------------------------------------------
class WebServer(BaseWebServer):
#-------------------------------------------------------------------------------
    """ A CGI web framework

        - instantiated per HTTP request
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseWebServer.__init__(self)
        self.path_info = os.environ.get('PATH_INFO', '')
        self.server_name = os.environ.get('SERVER_NAME', '')
        self.script_name = os.environ.get('SCRIPT_NAME', '')
        self.server_port = os.environ.get('SERVER_PORT', '')
        self.init()

CGIWebServer = WebServer

#-------------------------------------------------------------------------------
class StandaloneWebServer(BaseHTTPServer.BaseHTTPRequestHandler, BaseWebServer):
#-------------------------------------------------------------------------------
    """ Standalone we framework

        - instantiated per HTTP request
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, request, client_address, ss):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, ss)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __parseInput(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        BaseWebServer.__init__(self)

        rest, sep, query = self.path.partition('?')
        script, sep, rest = rest.partition('/')

        env = {}
        env['REQUEST_METHOD'] = self.command
        env['QUERY_STRING'] = query

        uqrest = urllib.unquote(rest)

        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host

        env['REMOTE_ADDR'] = self.client_address[0]

        authorization = self.headers.getheader("authorization")
        if authorization:
            authorization = authorization.split()
            if len(authorization) == 2:
                import base64, binascii
                env['AUTH_TYPE'] = authorization[0]
                if authorization[0].lower() == "basic":
                    try:
                        authorization = base64.decodestring(authorization[1])
                    except binascii.Error:
                        pass
                    else:
                        authorization = authorization.split(':')
                        if len(authorization) == 2:
                            env['REMOTE_USER'] = authorization[0]

        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader

        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)

        ua = self.headers.getheader('user-agent')
        if ua:
            env['HTTP_USER_AGENT'] = ua

        co = filter(None, self.headers.getheaders('cookie'))
        if co:
            env['HTTP_COOKIE'] = ', '.join(co)

        for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH', 'HTTP_USER_AGENT', 'HTTP_COOKIE'):
            env.setdefault(k, "")

        self.send_response(200, "Script output follows")

        self.form = cgi.FieldStorage(self.rfile, environ=env)
        self.path_info = uqrest
        self.server_name = self.server.server_name
        self.script_name = script
        self.server_port = str(self.server.server_port)
        self.init()

        oldstdout = sys.stdout
        sys.stdout = self.wfile
        try:
            try:
                self.begin()
                self.PrintPageBeg()
                self.ServiceRequest()

            except:
                PrintError(traceback.format_exc())
        finally:
            self.PrintPageEnd()
            sys.stdout = oldstdout

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def do_GET(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__parseInput()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def do_POST(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.__parseInput()


#-------------------------------------------------------------------------------
def RunStandaloneWebServer(server, host='', port=8000, msg=None):
#-------------------------------------------------------------------------------
    httpd = BaseHTTPServer.HTTPServer((host, port), server)
    if msg:
        print msg
    httpd.serve_forever()


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester

    class TestServer(StandaloneWebServer):
        def ServiceRequest(self):
            print "cool"

    RunStandaloneWebServer(TestServer)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


