from osscripts import *
import string, re

#-------------------------------------------------------------------------------
def man_osscriptscmd(cmd):
#-------------------------------------------------------------------------------
    f = open("C:\\bin\\pylib\\pylib\\osscripts.py")

    state = 0
    expdef = re.compile("def[ ]+%s[ ]*[(]" % cmd)
    while 1:
        line = f.readline()
        if not line: break
        if state == 0:
            m = expdef.match(line)
            if m:
                print "%s" % line[:-1]
                state = 1
        elif state == 1:
            state = 2
        elif state == 2:
            if line[0] != "#":
                break
            print "%s" % line[:-1]
    f.close()

#-------------------------------------------------------------------------------
def man_osscripts():
#-------------------------------------------------------------------------------
    f = open("C:\\bin\\pylib\\pylib\\osscripts.py")

    expdef = re.compile(r"def[ ]+([a-zA-Z][_a-zA-Z0-9]*)[ ]*[(]")
    expvar = re.compile(r"([a-zA-Z][_a-zA-Z0-9]*)[ ]*=")

    while 1:
        line = f.readline()
        if not line: break

        m = expdef.match(line)
        if m: print "cmd - %s" % m.group(1)

        m = expvar.match(line)
        if m: print "var - %s" % m.group(1)

    f.close()


#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    if argc == 1:
        print "man: [<sh cmd> | mks | python [cmd] | pydoc <module> | msh [cmd]]"
        return

    if argv[1] == "python":
        if argc == 2:
            StartFile("C:\\python25\\doc\\index.html")
        else:
            StartFile("C:\\python25\\doc\\%s\\index.html" % argv[2])
        return

    if argv[1] == "pydoc":
         r(r"python C:\python25\lib\pydoc.py " + argv[2])
         return

    if argv[1] == "mks":
        StartFile("C:\\etc\\toolkit.hlp")
        return

    if argv[1] == "osscripts":
       if argc == 3:
           man_osscriptscmd(argv[2])
       else:
           man_osscripts()
       return

    ## must be a command
    r("man1.exe %s" % argv[1])


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if (__name__ == "__main__"):
    main()
