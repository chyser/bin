#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import sys, httplib, re, urlparse, socket, os, fnmatch, string

from weblib import *

#BASE_DIR = 'I:\\wwwroot\\'
BASE_DIR = 'I:\\wwwroot\\users\\chrish'

#BASE_URL = "http://ntrails"
BASE_URL = "http://ntrails/users/chrish"

OUTPUT_FILE = "I:\\wwwroot\\validate\\results.htm"
PROXY_MACHINE = "web_proxy.fc.hp.com:8088"


WEB_ROOT = BASE_DIR

#
# This is a list of directories containing htm or html files which you don't
# want checked.
#
BAD_DIR_LIST = ['I:\\wwwroot\\code',
                'I:\\wwwroot\\colors',
                'I:\\wwwroot\\validate',
                'I:\\wwwroot\\users\\chrish\\ttd',
                'I:\\wwwroot\\users'
                ]


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: chkurls.py <file_name>

    validate urls found in file

    """
    args, opts = oss.gopt(argv[1:], [], [], main.__doc__)

    Out = None
    try:
        Out = open(OUTPUT_FILE, "w")
    except IOError:
        print("Cannot open output file: " + OUTPUT_FILE)
        sys.exit(2)

    #
    # Generate some HTML looking stuff.
    #
    Out.write("""\
<html>
<body>
<center>
<table>
""")

    #
    # if a parameter has been passed, then just do that file
    #
    if len(sys.argv) > 1:
        Name = sys.argv[1]
        print("Checking: " + Name)

        BURL = BASE_URL + string.replace(Name, '\\', '/')[len(WEB_ROOT):]
        print("    " + BURL)

        Out.write("""\
    <tr>
        <td colspan="2">
            <b>%s</b>
        </td>
    </tr>
""" % Name)

        InputFile = None
        try:
            InputFile = open(Name)
        except IOError:
            print("Cannot open file '%s'" % Name)
            sys.exit(1)

        CheckFile(Out, BURL, InputFile)

    #
    # else walk whole directory
    #
    else:
        os.path.walk(BASE_DIR, CheckFiles, Out)

    Out.write("""\
</table>
</body>
</html>
""")
    Out.close()

    oss.exit()


#-------------------------------------------------------------------------------
def CheckFile(Out, BaseURL, FileObj):
#-------------------------------------------------------------------------------
# This function pulls URLs out of a file and then validates them. The results
# are written to the file 'Out' in HTML
#
    #
    # Get the urls from the file FileObj
    #
    URLs = GetURLs(FileObj)

    #
    # For each URL
    #
    for i in URLs:
        #
        # Construct a full URL given the provided "base URL"
        #
        url = urlparse.urljoin(BaseURL, i)

        #
        # Attempt to read it without the proxy or with the proxy if without fails
        #
        Ret = ValidateURL(url)
        if Ret == 'OUTSIDE FW or CANNOT FIND':
            Ret = ValidateThruProxy(PROXY_MACHINE, url)

        #
        # Make errors show up in red
        #
        if Ret[:7] == 'ERROR 4' or Ret[:7] == 'ERROR 5':
            Ret = '<font color="#ff0000">' + Ret + '</font>'

        Out.write("""\
    <tr>
        <td>
            <a href="%s">
                %s
            </a>
        </td>
        <td>
            %s
        </td>
    </tr>
""" % (url, url, Ret))
        Out.flush()


#-------------------------------------------------------------------------------
def CheckFiles(Out, DirName, Names):
#-------------------------------------------------------------------------------
# This function is called by os.path.walk() for a directory hiearachy search.
#

    #
    # Don't traverse directories on the 'bad' list
    #
    if DirName in BAD_DIR_LIST :
        return

    #
    # Only check 'htm' or 'html' files.
    #
    for fn in Names:
        if not (fnmatch.fnmatch(fn, '*.htm') or fnmatch.fnmatch(fn, '*.html')):
            continue

        FullName = DirName + '\\' + fn
        print("Checking: " + FullName)

        BURL = BASE_URL + string.replace(FullName, '\\', '/')[len(WEB_ROOT):]
        print("    " + BURL)

        Out.write("""\
    <tr>
        <td colspan="2">
            <b>%s</b>
        </td>
    </tr>
""" % FullName)

        InputFile = None
        try:
            InputFile = open(FullName)
        except IOError:
            Out.write("""\
    <tr>
        <td colspan="2">
            <font color="#ff0000">Cannot open file</font>
        </td>
    </tr>
""")
#"
        CheckFile(Out, BURL, InputFile)
        InputFile.close()


if __name__ == "__main__":
    main(oss.argv)
