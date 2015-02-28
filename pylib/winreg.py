#!/usr/bin/env python
"""
Library:

"""

import _winreg
#-------------------------------------------------------------------------------
class RegKey(object):
#-------------------------------------------------------------------------------
    """ windows registry manipulation
    """

    HKEY_LOCAL_MACHINE = HKLM = _winreg.HKEY_LOCAL_MACHINE
    HKEY_CURRENT_USER = HKCU = _winreg.HKEY_CURRENT_USER

    REG_BINARY = _winreg.REG_BINARY
    REG_DWORD = _winreg.REG_DWORD
    REG_DWORD_LITTLE_ENDIAN = _winreg.REG_DWORD_LITTLE_ENDIAN
    REG_DWORD_BIG_ENDIAN = _winreg.REG_DWORD_BIG_ENDIAN
    REG_EXPAND_SZ = _winreg.REG_EXPAND_SZ
    REG_LINK = _winreg.REG_LINK
    REG_MULTI_SZ = _winreg.REG_MULTI_SZ
    REG_NONE = _winreg.REG_NONE
    REG_RESOURCE_LIST = _winreg.REG_RESOURCE_LIST
    REG_SZ = _winreg.REG_SZ                                ## string

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, key, subKey='', read=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        if isinstance(key, RegKey):
            key = key.key

        acc = _winreg.KEY_READ if read else _winreg.KEY_SET_VALUE

        for p in subKey.split('/'):
            key = _winreg.OpenKey(key, p, 0, acc)
        self.key = key

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create(self, subKey):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _winreg.CreateKey(self.key, subKey)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getValue(self, vname):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return _winreg.QueryValueEx(self.key, vname)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setValue(self, vname, value, typ=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if typ is None:
            typ = self.REG_SZ
        _winreg.SetValueEx(self.key, vname, 0, typ, value)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delete(self, subKey):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _winreg.DeleteKey(self.key, subKey)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delValue(self, vname):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _winreg.DeleteKey(self.key, vname)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _winreg.CloseKey(self.key)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        i = 0
        while 1:
            try:
                yield _winreg.EnumKey(self.key, i)
                i += 1
            except WindowsError, ex:
                s = str(ex)
                if s.startswith('[Error 259]'):
                    raise StopIteration
                raise

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def values(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        i = 0
        while 1:
            try:
                yield _winreg.EnumValue(self.key, i)
                i += 1
            except WindowsError, ex:
                s = str(ex)
                if s.startswith('[Error 259]'):
                    raise StopIteration
                raise



#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    return 0

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)



    res = not __test__()
    oss.exit(res)


