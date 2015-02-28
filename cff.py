

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import fnmatch
import mkcvs


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: cff
        -i | --ignore      : ignore this file (or filespec)
        -l | --ignorelist  : dump list of ignored files
        -a | --add         : add the files to CVS

    list the files that have NOT been checked into the CVS archive

    """
    args, opts = oss.gopt(argv[1:], [('l', 'ignorelist'), ('a', 'add')], [], [], [('i', 'ignore')], main.__doc__)

    if oss.exists('CVS'):
        if opts.ignore:
            with open(".cffignore", "a") as igf:
                for i in opts.ignore:
                    print(i, file=igf)
                oss.exit(0)

        if opts.add is not None:
            lst = doDir()
            for l in lst:
                print('cvs add ' + oss.basename(l))
                oss.r('cvs add ' + oss.basename(l))
            oss.exit(0)

        if opts.ignorelist is not None:
            lst = list(mkcvs.IGNORE_PATTERNS)
            with open(".cffignore") as igf:
                for line in igf:
                    line = line[:-1]
                    lst.append(line)
            print(lst)

        lst = doDir()
        for l in lst:
            print(l)

    else:
        print('montone')
        pth = oss.findFilePathUp('_MTN')

        if pth:
            lst = oss.r('mtn ls unknown', '|').split('\n')
            pwd = oss.normpath(oss.pwd())

            for i in lst:
                if (pth + i).startswith(pwd):
                    print(i)

    oss.exit(0)


#-------------------------------------------------------------------------------
def ignoreFile(fn, ignr=None):
#-------------------------------------------------------------------------------
    for pat in mkcvs.IGNORE_PATTERNS:
        if fnmatch.fnmatch(fn, pat):
            return True

    if ignr:
        for pat in ignr:
            if fnmatch.fnmatch(fn, pat):
                return True



#-------------------------------------------------------------------------------
def doDir(dir = '.'):
#-------------------------------------------------------------------------------
    try:
        inf = open("CVS/Entries")
    except IOError:
        oss.usage(3, "Not a CVS archive")

    have = set()
    for line in inf:
        try:
            have.add(line.split('/')[1].upper())
        except:
            pass
    inf.close()

    ignr = set()
    try:
        with open(".cffignore") as igf:
            for line in igf:
                ignr.add(line.strip())
    except IOError:
        pass

    lst = []
    for f in oss.ls():
        f = oss.basename(f)
        if ignoreFile(f, ignr):
            continue

        if oss.IsDir(f):
            if not oss.exists(f + '/CVS'):
                if f.upper() not in have:
                    lst.append("%s/%s/" % (dir, f))
            else:
                opwd = oss.pwd()
                oss.cd(f)
                lst.extend(doDir(dir + '/' + f))
                oss.cd(opwd)
        elif f.upper() not in have:
            lst.append("%s/%s" % (dir, f))

    return lst


if __name__ == "__main__":
    main(oss.argv)


