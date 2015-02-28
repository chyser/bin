import sys, os, os.path, re, getopt, glob

from osscripts import *

TMPNAME = r"C:\tmp\cvf.txt"

#-------------------------------------------------------------------------------
def CvtFile(FileName, Force = 0):
#-------------------------------------------------------------------------------
    fn, ext = os.path.splitext(FileName)

    nf = fn + '.txt'

    if not Force and exists(nf) and newerthan(nf, FileName):
        print >>sys.stderr, "Already converted"
        return

    cmd = r"C:\bin\pdftotext.exe -ascii7 " + FileName + ' ' + TMPNAME
    os.system(cmd)

    ex = re.compile(r"[ ]+")

    try:
        try:
            ipf = file(TMPNAME, 'r')
            opf = file(nf, 'w')

            text = ipf.read()
            print >>opf, re.sub(ex, ' ', text),
        except:
            raise
    finally:
        #os.unlink(TMPNAME)
        pass

#-------------------------------------------------------------------------------
def Usage(err):
#-------------------------------------------------------------------------------
    print >> sys.stderr, "usage: cvtpdf.py <pdf filename>"
    sys.exit(err)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?o:", ["help", "output="])
    except getopt.GetoptError:
        Usage(1)

    for o, a in opts:
        if o in ("-?", "--help"):
            Usage(0)

    infiles = []
    for fn in args:
        infiles.extend(glob.glob(fn))

    for fn in infiles:
        print >>sys.stderr, "Converting:", fn
        CvtFile(fn)

