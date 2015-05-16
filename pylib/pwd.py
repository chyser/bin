"""
Mimics posix password file access for NT
"""

#-------------------------------------------------------------------------------
class PwdEntry:
#-------------------------------------------------------------------------------
    """ All of the fields of 'passwd' entry
    """
    def __init__(self, Name, Passwd, UID, GID, NmCmt, Dir, Shell):
        self.pw_name = Name
        self.pw_passwd = Passwd
        self.pw_uid = UID
        self.pw_gid = GID
        self.pw_gecos = NmCmt
        self.pw_dir = Dir
        self.pw_shell = Shell

PASSWDDB = {'chrish': PwdEntry('chrish', 'x', 500, 600, 'Chris Hyser', '/users/chrish', 'msh')}

#-------------------------------------------------------------------------------
def getpwnam(name):
#-------------------------------------------------------------------------------
    try:
        return PASSWDDB[name]
    except:
        return None

#-------------------------------------------------------------------------------
def getpwuid(uid):
#-------------------------------------------------------------------------------
    for k, i in PASSWDDB.items():
        if i.pw_uid == uid:
	        return i

    return None

#-------------------------------------------------------------------------------
def getpwall():
#-------------------------------------------------------------------------------
    return PASSWDDB.values()
