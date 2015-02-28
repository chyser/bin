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

            OPTS = " /GX /nologo " + OSVER
            DBGOPTS = "/Zi /Od /RTC1 /EHsc /MT"
            PRODOPTS = "/O2"

            LOCAL_INCLUDE = '-I"C:/libcpp/include"'
            LOCAL_INCPATH = 'C:/libcpp/include'
            LIB = ""
            LIBS = ""

            if __ProjectAttr[2] == '6':
		CC = 'python.exe C:/bin/cc.py  ---path "C:/Program Files/Microsoft Visual Studio/VC98/bin/cl1.exe" ---lib $(LIBPATH)'
		OPTS = "/MT  /G5 /GX /nologo " + OSVER

                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual Studio/VC98/include"'
                INCPATH = 'C:/Program Files/Microsoft Visual Studio/VC98/include'
                LIBPATH = 'C:/libcpp/lib;C:/Program Files/Microsoft Visual Studio/VC98/lib'
                LIBS = "user32.lib advapi32.lib comdlg32.lib uuid.lib"

            elif __ProjectAttr[2] == '9':
		CC = 'python.exe C:/bin/cc.py  ---cc cl9 ---lib $(LIBPATH)'
		OPTS = "/W3 /MT /EHsc /nologo " + OSVER
                INCPATH = 'C:/Program Files/Microsoft Visual Studio 9.0/VC/INCLUDE;C:/Program Files/Microsoft SDKs/Windows/v6.0A/include'
                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual Studio 9.0/VC/INCLUDE" -I"C:/Program Files/Microsoft SDKs/Windows/v6.0A/include"'
                LIBPATH = 'C:/WINDOWS/Microsoft.NET/Framework/v3.5;C:/WINDOWS/Microsoft.NET/Framework/v2.0.50727;C:/Program Files/Microsoft Visual Studio 9.0/VC/LIB;C:/Program Files/Microsoft Platform SDK/lib'

                LIB = r'C:\Program Files\Microsoft Visual Studio 9.0\VC\LIB;C:\Program Files\Microsoft SDKs\Windows\v6.0A\lib;'

                VCINSTALLDIR = r'C:/Program Files/Microsoft Visual Studio 9.0/VC'
                VS90COMNTOOLS = r'C:/Program Files/Microsoft Visual Studio 9.0/Common7/Tools/'
		VSINSTALLDIR = r'C:/Program Files/Microsoft Visual Studio 9.0'
		WindowsSdkDir = r'C:/Program Files/Microsoft SDKs/Windows/v6.0A/'

                LIBS = "user32.lib advapi32.lib comdlg32.lib uuid.lib gdi32.lib comctl32.lib kernel32.lib"

            elif __ProjectAttr[2] == '7':
		OPTS = "/W3 /QIfist /nologo " + OSVER
		CC = 'python.exe C:/bin/cc.py  ---cc cl7 ---lib $(LIBPATH)'
                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual C++ Toolkit 2003/include"'
                INCPATH = 'C:/Program Files/Microsoft Visual C++ Toolkit 2003/include;C:/Program Files/Microsoft Platform SDK/include'
                LIBPATH = '"C:/libcpp/lib;C:/Program Files/Microsoft Visual C++ Toolkit 2003/lib;C:/Program Files/Microsoft Platform SDK/lib"'
                LIB = LIBPATH
                LIBS = "user32.lib advapi32.lib comdlg32.lib uuid.lib gdi32.lib comctl32.lib kernel32.lib"

            elif __ProjectAttr[2] == '8':
		OPTS = "/W3 /EHsc /nologo " + OSVER
		CC = 'python.exe C:/bin/cc.py  ---cc cl8 ---lib $(LIBPATH)'
                MS_INCLUDE = '-I"C:/Program Files/Microsoft Visual Studio 8/VC/include"'
                INCPATH = 'C:/Program Files/Microsoft Visual Studio 8/VC/include;C:/Program Files/Microsoft Platform SDK/include'
                LIBPATH = '"C:/Program Files/Microsoft Visual Studio 8/VC/lib;C:/Program Files/Microsoft Platform SDK/lib"'
                LIB = LIBPATH
                LIBS = "user32.lib advapi32.lib comdlg32.lib uuid.lib gdi32.lib comctl32.lib"


            INCLUDE = LOCAL_INCPATH + ';' + INCPATH
            CFLAGS = OPTS + ' ' + LOCAL_INCLUDE + ' ' + MS_INCLUDE

        print r"""
clean:
	$(RM) -f *.obj *.exe *.lib *.dll *.pdb *.ilk *.res *.pp *.rsp

%.obj : %.cpp
	$(CC) -c $(CFLAGS) $(DBGOPTS) $(CPPFLAGS) $<

%.obj : %.cpy
	$(CC) -c  $(CFLAGS) $(DBGOPTS) $(CPPFLAGS) /Tp $<

%.obj : %.c
	$(CC) -c $(CFLAGS) $(DBGOPTS) $<
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




