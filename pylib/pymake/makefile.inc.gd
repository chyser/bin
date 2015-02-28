default: all
.PHONY: all

@@@

if OS != "LINUX":
    RM = 'rm.exe'
else:
    RM = 'rm'

__DEFAULT_PROJECT = ['CPP', 'VC', '6']

try:
    __ProjectAttr = PROJECT
except NameError:
    __ProjectAttr = __DEFAULT_PROJECT

if __ProjectAttr[0] == "CPP":
    if OS != "LINUX":

        if __ProjectAttr[1] == 'VC':
            RC = 'rc.exe'
            AR = 'lib.exe'

            OSVER = "-D WIN98"

            OPTS = "/MT  /G5 /GX /nologo " + OSVER
            DBGOPTS = "/Zi"
            PRODOPTS = "/O2"

            LOCAL_INCLUDE = '-I"C:/libcpp/include"'

            if __ProjectAttr[2] == '6':
                CC = 'cl1.exe'
                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual Studio/VC98/include"'
                INCPATH = 'C:/libcpp/include;C:/Program Files/Microsoft Visual Studio/VC98/include'
                LIBPATH = 'C:/libcpp/lib;C:/Program Files/Microsoft Visual Studio/VC98/lib'
                LIBS = "user32.lib advapi32.lib comdlg32.lib uuid.lib"
            else:
                CC = 'cl.exe'
                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual C++ Toolkit 2003/include"'
                INCPATH = 'C:/libcpp/include;C:/Program Files/Microsoft Visual C++ Toolkit 2003/include'
                LIBPATH = 'C:/libcpp/lib;C:/Program Files/Microsoft Visual C++ Toolkit 2003/lib'
                LIBS = ""

            __DELAYED_OUTPUT__.append("export LIB := $(LIBPATH)")
            INCLUDE = LOCAL_INCLUDE + ' ' + MS_INCLUDE
            CFLAGS = OPTS + ' ' + INCLUDE

        print r"""
clean:
	$(RM) -f *.obj *.exe *.lib *.dll *.pdb *.ilk *.res *.pp

%.obj : %.cpp
	$(CC) -c $(CFLAGS) $(DBGOPTS) $(CPPFLAGS) $< -o $@

%.obj : %.c
	$(CC) -c $(CFLAGS) $(DBGOPTS) $< -o $@
"""

elif __ProjectAttr[0] == "PYTHON":
    CHECKER = "checker"

    print """

.SUFFIXES: .chk .py
%.chk : %.py
\t$(CHECKER) $<

clean:
\t$(RM) -f *.chk
"""
@@@




