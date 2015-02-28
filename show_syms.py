#!/usr/bin/python

import os


def show_sym(sym):
    #os.system('find . -name "*.[chS]" | xargs fgrep %s | less' % sym)
    os.system('C:/bin/find_sym.bat ' + sym)


while 1:
    os.system("clear")
    ch = raw_input("sym> ")
    if ch == '_quit':
        break

    d = ch.split()
    try:
        if d[0].startswith('s'):
            os.chdir('arch/sparc')
        show_sym(d[1])
        os.chdir('../..')
    except:
        show_sym(ch)

