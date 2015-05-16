#!/usr/bin/env python

import pylib.osscripts as oss

LDMSCREEN = "screen -h 10000 -S chrish"
#LDMSCREEN = "screen -D -R chrish"

SCREEN = "screen -D -R -h 10000 -S chrish"

machs = {
    "q15"  : ["cd /rpool/chrish",  LDMSCREEN, "", ". profile", "clear", "ldm ls"],
    "q13"  : ["cd /rpool2/chrish", LDMSCREEN, "", ". profile", "clear", "ldm ls"],
    "q31"  : ["cd /rpool3/chrish", LDMSCREEN, "", ". profile", "clear", "ldm ls"],
    "q41"  : ["cd /rpool/chrish",  LDMSCREEN, "", ". profile", "clear", "ldm ls"],
    "q100" : ["cd /rpool2/chrish", LDMSCREEN, "", ". profile", "clear", "ldm ls"],

    "q40"  : ["sudo su -", "cd /rpool2/chrish", LDMSCREEN, ". profile", "clear", "ldm ls"],

    "q16"  : ["screen -D -R -h 10000"],
    "q10"  : ["screen -D -R -h 10000"],
    "root@144.25.15.107" : ["screen -D -R -h 10000"],
}


#------------------------------------------------------------------------------
def main(argv):
#------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], "")

    if not args:
        args = machs.keys()

    for m in args:
        if m not in machs:
	    print "unknown machine", m
	    continue

        print "Opening", m
	session = oss.r("qdbus org.kde.konsole /Konsole newSession", '$').strip()
        s = oss.r("qdbus org.kde.konsole /Sessions/%s setTitle 1 %s" % (session, m), '|')
        if s.strip():
            print s.rstrip()

        s = oss.r('qdbus org.kde.konsole /Sessions/%s sendText "ssh %s"' % (session, m), '|')
        if s.strip():
            print s.rstrip()

        s = oss.r('~/bin/qdsendnl %s' % session, '|')
        if s.strip():
            print s.rstrip()

        for cmd in machs[m]:
    	    if cmd:
	        s = oss.r('qdbus org.kde.konsole /Sessions/%s sendText "%s"' % (session, cmd), '|')
                if s.strip():
                    print s.rstrip()
	    s = oss.r('~/bin/qdsendnl %s' % session, '|')
            if s.strip():
                print s.rstrip()


if __name__ == "__main__":
    main(oss.argv)
