"""
usage:

"""

import pylib.osscripts as oss
import re

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def split(pat, line):
#-------------------------------------------------------------------------------
    tokens1 = re.split(pat, line[:-1])
    tokens = []
    for t in tokens1:
        if t:
            tokens.append(t)
    return tokens

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [], usage)

    inf = file(args[0])
    id = 0

    for line in inf:
        try:
            if line[-2] == ':':
                tokens = split(r'[ :]', line[:-1])
                print "\niter itr%d;" % id
                print "for(; %s.in(%s, itr%d);)" % (tokens[3], tokens[1], id)
            else:
                tokens = split(r"[ ,]", line)
                if tokens[0] == "print":
                    print "cout ",
                    for tok in tokens[1:]:
                        print "<<", tok,
                    print ";"

        except: pass



    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)


