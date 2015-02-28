import sys, os, traceback, cgi, time

DBG_LVL = 0
#-------------------------------------------------------------------------------
def SetDbgLvl(val):
#-------------------------------------------------------------------------------
    global DBG_LVL
    DBG_LVL = val

#-------------------------------------------------------------------------------
def DbgPrint(*arg):
#-------------------------------------------------------------------------------
    try:
        Lvl = int(arg[0])
        arg = arg[1:]
    except:
        return DbgPrint(1, *arg)

    if DBG_LVL >= Lvl:
        print """<br><font color=#ff0000> <b>&lt;DEBUG&gt;&nbsp;&nbsp;"""
        for s in arg:
            print str(s)
        print """</b></font><br>"""

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
def FillObjectFromForm(obj, form):
#-------------------------------------------------------------------------------
    for k in obj.__dict__.keys():
        if form.has_key(k):
            obj.__dict__[k] = form.getfirst(k, "")
    return obj

#-------------------------------------------------------------------------------
def DetermineAction(ActLst, form):
#-------------------------------------------------------------------------------
    for al in ActLst:
        if form.has_key(al):
            return al
    return None


MAIN_PAGE_BEG = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
    <title>
        %s
    </title>

    <meta http-equiv="expires" content="0" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Cache-Control" content="no-cache" />

    <!-- meta data standards can be found at http://eservices.athp.hp.com/documents/metaStan.asp -->
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1252" />
    %s
</head>

<!--
// Body
-->
<body>
"""

MAIN_PAGE_END = """ %s </body> </html>"""



#-------------------------------------------------------------------------------
class WebServer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(WebServer, self).__init__()
        self.PageBegin = MAIN_PAGE_BEG
        self.PageEnd = MAIN_PAGE_END
        self.Title = ""
        self.HeadAdd = ""
        self.EndAdd = ""

        self.path_info = os.environ.get('PATH_INFO', '')
        self.server_name = os.environ.get('SERVER_NAME', '')
        self.script_name = os.environ.get('SCRIPT_NAME', '')
        self.server_port = os.environ.get('SERVER_PORT', '')
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
                print "<br><br><font color=#ff0000>Exception:<br>"
                for l in traceback.format_exception(*sys.exc_info()):
                    print "&nbsp;&nbsp;", l, "<br>"
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
        print self.PageBegin % (self.Title, self.HeadAdd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def PrintPageEnd(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print self.PageEnd % self.EndAdd

