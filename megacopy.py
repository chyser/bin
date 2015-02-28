import string
from osscripts import *

DIRNAME = "\\temp\\megacopy"

USAGE = "usage: megacopy [<src> A: | A: <dest>]"

#-------------------------------------------------------------------------------
def BlowUp(Src):
#-------------------------------------------------------------------------------
    if not exists(Src):
        print '"%s" does nto exist' % Src
        exit(1)

    OldDir = pwd()
    if not cp(Src, DIRNAME + '\\'):
        print "MC ERR: 1"
        exit(2)

    cd(DIRNAME)

    r("chunk %s >nul" % Src)

    rm(Src)
    idx = 0

    for i in ls():
        print "Copying : '%s'" % i

        if not cp(i, "A:\\") :
            raw_input("\n!!! Next Floppy !!!\n")
            if not cp(i, "A:\\") :
                print "MC ERR: 2"
                exit(3)
            else:
                idx = idx + 1
        else:
            idx = idx + 1

    try:
       file = open("A:\\mcidx", "w")
    except IOError:
        print "Can't open idx file"
        exit(4)

    file.write("%d" % (idx-1))
    file.close()
    cd(OldDir)


#-------------------------------------------------------------------------------
def PutBack(Dst):
#-------------------------------------------------------------------------------
    OldDir = pwd()
    cd(DIRNAME)
    idx = 0
    OIdx = 100000

    raw_input("Put floppy in A:")
    while 1:
        if exists("A:\\mcidx") :
            try:
               file = open("A:\\mcidx")
            except IOError:
                print "Can't open idx file"
                exit(4)

            OIdx = string.atoi(file.read())
            print "Found IDX - %d" % OIdx
            file.close()

        for i in ls("A:\\") :
            print "Copying '%s'" % i
            if not cp("A:\\%s" % i, ".") :
                print "MC ERR: 3"
                exit(3)
            else:
                idx = idx + 1

        if OIdx <= idx:
            break

        raw_input("\n!!! Next Floppy !!!\n")

    r("chunk %s >nul" % basename(Dst))

    cd(OldDir)
    name = DIRNAME + '\\' + basename(Dst)
    print name
    if not cp(name, Dst) :
        print "MC ERR: 5"
        exit(5)


#-------------------------------------------------------------------------------
#main
#-------------------------------------------------------------------------------
if __name__ == "__main__":

    if argc != 3:
        print USAGE
        exit(1)

    if argv[1] != 'A:' and argv[2] != 'A:':
        print USAGE
        print argv[1] + ' ' + argv[2]
        exit(1)


    OldDir = pwd()

    try:
        if not mkdir(DIRNAME):
            print "MC ERR: 0"
            exit(2)
    except:
        pass

    if argv[1] == 'A:' :
        PutBack(argv[2])
    else:
        BlowUp(argv[1])

    #
    # cleanup
    #
    OldDir = pwd()
    cd(DIRNAME)
    for i in ls():
        rm(i)
    cd(OldDir)
    rmdir(DIRNAME)

