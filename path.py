
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pylib.osscripts as oss
import win32api


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """
    usage: path [options]

    options:
        -m | --move <srcidx> <destidx>  : move source idx to destination idx
        -r | --remove <idx>             : remove element specified by idx
        -a | --append <path>            : append a path
        -i | --insert <idx> <path>      : insert path at idx

    """
    args, opts = oss.gopt(argv[1:], [('m', 'move'), ('r', 'remove'), ('a', 'append')], [('i', 'insert')], main.__doc__)

    if opts.move:
        try:
            src = int(args[0])
            dst = int(args[1])
        except:
            opts.usage(1, "Incorrect move statement")

        lst = oss.env['PATH'].split(';')
        val = lst[src]
        del lst[src]
        lst.insert(dst, val)
        oss.export('PATH=%s' % ';'.join(lst))

    elif opts.remove:
        lst = oss.env['PATH'].split(';')

        try:
            for a in args:
                lst[int(a)] = None

            lst = [l for l in lst if l]
        except:
            opts.usage(1, "Incorrect remove statement")

        oss.export('PATH=%s' % ';'.join(lst))

    elif opts.append:
        lst = oss.env['PATH'].split(';')
        for a in args:
            lst.append(a)
        oss.export('PATH=%s' % ';'.join(lst))

    elif opts.insert:
        lst = oss.env['PATH'].split(';')
        lst.insert(int(opts.insert), args[0])
        oss.export('PATH=%s' % ';'.join(lst))

    else:
        display()

    oss.exit(0)


#-------------------------------------------------------------------------------
def display():
#-------------------------------------------------------------------------------
    lst = oss.env['PATH'].split(';')
    for i, l in enumerate(lst):
        try:
            d = win32api.GetLongPathName(l)
        except:
            d = l
        try:
            s = win32api.GetShortPathName(l)
        except:
            s = ""

        print("%02d:" % i, d)
        if s and s.lower() != d.lower():
            print("   ", s)


if __name__ == "__main__":
    main(oss.argv)

