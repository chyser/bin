import string, bu


from osscripts import *
from bu import Archive, DirFilesNewer, BUError, REVISION

DRIVE = os.getenv("BUDRIVE", "D:")

#-------------------------------------------------------------------------------
def ArchiveDirs(Archive):
#-------------------------------------------------------------------------------
   return ls(DRIVE + "\\[01][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\\%s.cpio" % Archive)

#-------------------------------------------------------------------------------
def GetLatestArchive(Archive):
#-------------------------------------------------------------------------------
    try:
        md = 0
        mf = None
        for f in ArchiveDirs(Archive):
            t = f.split('\\')[1]
            dt = long(t[4:] + t[0:2] + t[2:4])
            if dt > md:
                md = dt
                mf = t
        return DRIVE + "\\%s\\%s.cpio" % (mf, Archive)
    except:
        return None

#-------------------------------------------------------------------------------
def ShowAllArchives():
#-------------------------------------------------------------------------------
    lst = []
    for d in ArchiveDirs('*'):
        t = d.split('\\')[2]
        if t not in lst:
            lst.append(t)

    lst.sort()
    print lst


#-------------------------------------------------------------------------------
def usage(err):
#-------------------------------------------------------------------------------
    print >> sys.stderr, """
ubu [-i] [-s] [name]
    -i : ignore archive newer than files
    -s : show intended actions w/o performing them
    -l : list of possible restore directories
    -f : specify particulr archive file
    -d : specify drive or path prefix
    -z : show all archives
"""
    sys.exit(err)


#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    global DRIVE

    try:
        opts, args = getopt.getopt(sys.argv[1:], "islf:d:z")
    except:
        usage(2)

    ignore_new = show_only = list_dirs = False
    af = None

    for o, a in opts:
        if o == '-i':
            ignore_new = True
        elif o == '-s':
            show_only = True
        elif o == '-l':
            list_dirs = True
        elif o == '-f':
            af = a
        elif o == '-d':
            DRIVE = a
        elif o == '-z':
            ShowAllArchives()
            sys.exit(0)
        else:
            usage(2)

    ## Get the archive name either as a parameter, or as the current directory
    ## name.
    if args:
        dir = args[0]
        cd(dir)
    else:
        dir = pwd()

    ## Get archive name.
    file = basename(dir)

    if list_dirs:
        print ArchiveDirs(file)
        sys.exit(0)

    if af:
        AFile = af
    else:
        AFile = GetLatestArchive(file)

    CFile = 'C:\\bu\\%s.cpio' % file

    print 'Restoring Directory "%s" with "%s:' % (dir, AFile)

    try:

        ## Ensure we got it.
        if not (AFile and exists(AFile)):
            if af:
                raise BUError("""Can't find archive "%s" """ % file)
            else:
                raise BUError("""Can't find archive "%s" on "%s" """ % (file, DRIVE))

        ## Get the archive.
        if not cp(AFile, CFile):
            raise BUError("Can't copy archive!")

        try:
            ## Verify that we are copying in the safe direction.
            if not ignore_new and DirFilesNewer('.', AFile) :
                print "Archive is older than directory contents !!"
                if string.lower(raw_input('Continue [y/n]: ')) != 'y':
                    return 0

            ## Save old backup
            if show_only:
                print >> sys.stderr, "Showing contents only"

                ## Show the "restoring" archive.
                if not cpio('itvz', CFile):
                    raise BUError("Restore Failed: read of archive")

            else:
                mv('$bubak', '$bubak1')

                ## Save current files
                try:
                    Archive('$bubak')
                except BUError:
                    print >> sys.stderr, "Failed to save old files!"
                    if string.lower(raw_input('Continue [y/n]: ')) != 'y':
                        return 0

                ## Expand the "restoring" archive.
                if not cpio('idavmuz', CFile):
                    raise BUError("Actual Restore Failed!")

        finally:
            ## Cleanup
            rm(CFile)

    except BUError, be:
        print >> sys.stderr, be
        return 1

    else:
        return 0


#-------------------------------------------------------------------------------
#main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    print "ubu: Revision '%s'" % REVISION
    exit(main())
