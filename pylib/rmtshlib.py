
CF_DIR  = "cmd/cmd"
CF_FILE = "/cmd/cmd/cmd"
CF_OUTF = "/cmd/res/out"
CF_RESF = "/cmd/res/err"
CF_CDIR = "/cmd/files"

#-------------------------------------------------------------------------------
class RmtshError(Exception):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, str):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(RmtshError, self).__init__(str)

#-------------------------------------------------------------------------------
def help(CMDS, topic = None, msg = ""):
#-------------------------------------------------------------------------------
    """ help - provides a list of available commands or help on specific commands
    """
    l = [""]
    if topic is None or topic not in CMDS:
        for cmd in CMDS.keys():
            l.append(cmd)
    else:
        l.append(CMDS[topic].__doc__)

    return '\n'.join(l) + "\n" + msg + "\n"

