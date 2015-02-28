from osscripts import *
import getopt, sys

#-------------------------------------------------------------------------------
#main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    dir = "."
    file = None
    srt = 0

    try:
        (opts, args) = getopt.getopt(argv[1:], "sf:d:")
    except getopt.GetoptError:
        print "usage: srch [-s] [-d <dir>] [-f <file>] <pattern> "
        print "    -s : sort"
        print "    -d : specify the directory"
        print "    -f : specify the output file"
        exit(1)

    for (o, a) in opts:
        if o == "-d":
            dir = a
        elif o == "-f":
            file = a
        elif o == "-s":
            srt = 1

    l = find(dir, args[0])

    if srt:
        l.sort()

    if file:
        try:
            f = open(file, "w")
        except:
            print "cannot open file " + file + "\n"
            exit(2)
    else:
        f = sys.stdout

    for i in l:
        f.write(i + "\n")

    if file:
        f.close()

    exit(0)
