from osscripts import *
from string import *

USAGE = "usage: cpcpp2c [-c | -cpp] <src> <dest>"


print argc
if (argc < 4):
    print USAGE
    exit(1)


#
# cleanup paths
#
dest = join(split(argv[3], '/'), '\\')
src = join(split(argv[2], '/'), '\\')

if (argv[1] == "-c"):
    for file in ls(src + '\\' + '*.cpp'):
	base,ext = split(basename(file), '.')
	new = "%s\%s.c" % (dest, base)
	print "%s --> %s" % (file, new)
	cp(file, new)

elif (argv[1] == "-cpp"):
    for file in ls(src + '\\' + '*.c'):
	base,ext = split(basename(file), '.')
	new = "%s\%s.cpp" % (dest, base)
	print "%s --> %s" % (file, new)
	cp(file, new)

else:
    print USAGE
    exit(1)
