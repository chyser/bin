import sys, getopt, string

DEBUG = 0

gList = [
    ((1.0,  'fl_oz'), (2.0,    'tbsp')),
    ((1.0,  'tbsp'),  (3.0,    'tsp')),
    ((1.0,  'tsp'),   (5.0,    'ml')),
    ((8.0,  'fl_oz'), (1.0,    'cup')),
    ((16.0, 'fl_oz'), (1.0,    'pint')),
    ((2,    'pint'),  (1.0,    'quart')),
    ((4,    'quart'), (1.0,    'gal')),
    ((1,    'l'),     (1000.0, 'ml')),

    ((1.0,  'oz'),    (28.349, 'g')),
    ((1.0,  'kg'),    (1000.0, 'g')),
    ((1.0,  'kg'),    (2.2047, 'lb')),

    ((1.0,  'in'),    (2.54,   'cm')),
    ((1.0,  'm'),     (100.0,  'cm')),
    ((1.0,  'cm'),    (10.0,   'mm')),
    ((1.0,  'km'),    (1000.0, 'm')),
    ((12.0, 'in'),    (1.0,    'ft')),
    ((3.0,  'ft'),    (1.0,    'yd')),
    ((1.0,  'mi'),    (1.609,  'km')),
    ((1.0,  'n_mi'),  (1.151,  'mi'))
    ]

#-------------------------------------------------------------------------------
def LookUp(su, du, times = 0):
#-------------------------------------------------------------------------------
    global gList

    if DEBUG: print ' '*times, su, du
    if times > len(gList):
        return (None, None)

    for i in gList:
        if su == i[0][1] or su == i[1][1]:
            swap = su == i[1][1]

            if swap:
                j = 0;  k = 1
            else:
                j = 1;  k = 0

            if du == i[j][1]:
                num = i[k][0]
                denom = i[j][0]
                if DEBUG: print ' '*times, "%f/%f %s -- %s" % (num, denom, su, du)

            else:
                num, denom = LookUp(i[j][1], du, times + 1)
                if not num: continue

                num *= i[k][0]
                denom *= i[j][0]
                if DEBUG: print ' '*times, "%f/%f %s -- %s" % (num, denom, su, du)

            return (num, denom)
    return (None, None)


#-------------------------------------------------------------------------------
def Units():
#-------------------------------------------------------------------------------
    l = []
    for a,b in gList:
        a1, a2 = a
        b1, b2 = b

        if a2 not in l:
            l.append(a2)

        if b2 not in l:
            l.append(b2)

    return l

#-------------------------------------------------------------------------------
def usage(err):
#-------------------------------------------------------------------------------
    print >> sys.stderr, """
usage: convert <num> <units1> <units2>
    convert num units1 into units2
    units can be:\n    """

    for i in Units():
        print >> sys.stderr, i,
    print >> sys.stderr,  ''

    sys.exit(err)

#-------------------------------------------------------------------------------
def main():
#-------------------------------------------------------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?")
    except getopt.GetoptError:
        usage(1)

    for o,a in opts:
        if o in '-?':
            usage(0)
        else:
            usage(1)

    amt = float(args[0])
    su = args[1]
    du = args[2]

    denom, num  = LookUp(su, du)

    if not num:
        print "Conversion between %s and %s not found" % (su, du)
        sys.exit(10)

    print "%f %s equals %f %s" % (amt, su, amt * num / denom, du)



#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if (__name__ == "__main__"):
    main()

