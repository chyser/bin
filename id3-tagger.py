#!/usr/bin/env python

# ID3 module example program
# $Id: id3-tagger.py,v 1.2 2005/12/29 20:21:04 Owner Exp $

# version 1.2
# written 2 May 1999 by Ben Gertzfield <che@debian.org>

# This program is released under the GNU GPL, version 2 or later.

import getopt, string, re, sys
from id3 import *
from osscripts import ls

version = 1.2
name = 'id3-tagger.py'

#-------------------------------------------------------------------------------
def usage():
#-------------------------------------------------------------------------------
    sys.stderr.write(
"This is %s version %0.1f, a tool for setting ID3 tags in MP3 files.\n\n\
Usage: %s [-t title] [-a artist] [-A album] [-y year] [-c comment] \n\
       %s [-g genre] [-T tracknum] [-d] [-h] [-v] file1 [file2 ...]\n\n\
-d: Delete the ID3 tag from specified file(s) completely\n\
-h: Display this text\n\
-v: Display the version of this program\n\n\
With no arguments, display the ID3 tag of the given file(s).\n" %
       (name, version, name, ' ' * len(name)))

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    options = {}

    try:
	    opts, args = getopt.getopt(argv[1:], 't:a:A:y:c:g:T:dhvl')
    except getopt.error, msg:
	    print msg
	    usage()
	    sys.exit(2)

    for opt, arg in opts:
    	if opt == '-v':
    	    sys.stderr.write("This is %s version %0.1f.\n" % (name, version))
    	    sys.exit(0)

    	if opt == '-h':
    	    usage()
    	    sys.exit(0)

            if arg:
                s = ""
                for i in arg:
                    if i == '^':
                        s += " "
                    else:
                        s += i
                arg = s

    	if opt == '-t':
    	    options['TITLE'] = arg
    	if opt == '-a':
    	    options['ARTIST'] = arg
    	if opt == '-A':
    	    options['ALBUM'] = arg
    	if opt == '-y':
    	    options['YEAR'] = arg
    	if opt == '-c':
    	    options['COMMENT'] = arg
    	if opt == '-g':
    	    options['GENRE'] = arg
            if opt == '-T':
                options['TRACKNUMBER'] = arg
    	if opt == '-d':
    	    options['delete'] = 1

    if len(args) == 0:
    	usage()
    	sys.exit(2)

    a = []
    for f in args:
        a.extend(ls(f))
    args = a

    for file in args:
    	try:
    	    id3info = ID3(file)

            needs_write = 0

            if len(options.keys()) > 0:
                needs_write = 1

            for k, v in options.items():
                if k == 'GENRE' and re.match("\d+$", v):
                    id3info[k] = string.atoi(v)
                else:
                    id3info[k] = v

    	    if options.has_key('delete'):
    		    id3info.delete()

    	    print id3info
            print "\n"

            if needs_write:
                id3info.write()

    	except InvalidTagError, msg:
    	    print "Invalid ID3 tag:", msg
    	    continue

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)
