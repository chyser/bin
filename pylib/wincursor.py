#!/usr/bin/env python
import pylib.osscripts as oss


import win32console as w32con
import pywintypes

#-------------------------------------------------------------------------------
class Screen(object):
#-------------------------------------------------------------------------------
    """ Object managing the screen in a 'windows' console window
    """
    class ScreenException(Exception): pass
    class CoordinateException(ScreenException): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Screen, self).__init__()
        self.hout = w32con.GetStdHandle(w32con.STD_OUTPUT_HANDLE)
        self.hin = w32con.GetStdHandle(w32con.STD_INPUT_HANDLE)

        self.oldHINMode = self.hin.GetConsoleMode()
        self.oldHOUTMode = self.hout.GetConsoleMode()
        #print "0x%0x" % self.oldHINMode, "0x%0x" % self.oldHOUTMode

        self.SetMode(0xf8, 0x3)

        self.info = self.hout.GetConsoleScreenBufferInfo()
        self.screen = self.info["Window"]

        ## location of current cursor
        self.x = 0
        self.y = 0
        self.updateXY()

        self.clearInput()

        self.ignSet = set([16,17,18,19,112,46,33,34,20,91])

        if title is not None:
            self.SetTitle(title)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetMode(self, i, o):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.oldHINMode = i
        self.oldHOUTMode = 0
        self.hin.SetConsoleMode(i)
        self.hout.SetConsoleMode(o)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.hin.SetConsoleMode(self.oldHINMode)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ clear the screen
        """
        self.setXY(0,0)
        self.hout.SetConsoleMode(3)
        self.write(' '*((self.screen.Bottom+1)*(self.screen.Right+1)))
        self.hout.SetConsoleMode(3)
        self.setXY(0,0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def SetTitle(self, title):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ set the window title
        """
        w32con.SetConsoleTitle(title)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clearInput(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ clear any unporcessed input events
        """
        while self.hin.PeekConsoleInput(1):
            self.hin.ReadConsoleInput(100)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keyPressed(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ determine whether a key is pressed, return True (yes), False (no)
        """
        while 1:
            res = self.hin.PeekConsoleInput(1)
            if not res: return False

            ch = res[0]
            if ch.EventType == w32con.KEY_EVENT and ch.KeyDown:
                return True
            else:
                ## currently throwing away everything else
                self.hin.ReadConsoleInput(1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateXY(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ update the current cursor state
        """
        self.x, self.y = self.getXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getXY(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ get the current cursor location
        """
        p = self.hout.GetConsoleScreenBufferInfo()["CursorPosition"]
        return p.X, p.Y

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setXY(self, x,  y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ set the cursor to (x,y)
        """
        self.x = x
        self.y = y
        try:
            self.hout.SetConsoleCursorPosition(w32con.PyCOORDType(x, y))
        except pywintypes.error as ex:
            if ex[0] == 87:
                raise self.CoordinateException(ex)
            raise self.ScreenException(ex)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeXY(self, x, y, obj, line=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ write 'obj' to specified location while preserving the current cursor
        """
        ox, oy = self.getXY()
        self.setXY(x, y)
        self.write(obj, line)
        self.setXY(ox, oy)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self, obj, line=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ write 'obj' at the current cursor location
        """
        s = str(obj)
        if line:
            x, y = self.getXY()
            s0 = s + ' '*(self.screen.Right-(len(s)+x))
            self.hout.WriteConsole(s0)
            self.setXY(x + len(s), y)
        else:
            self.hout.WriteConsole(s)
            self.updateXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeStatus(self, s, y=0, x=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ treats the last line as a status line writing 's' there
        """
        s = str(s)
        self.writeXY(x, self.screen.Bottom - y, s + ' '*(self.screen.Right-(len(s)+x)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readKey(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while 1:
            ch = self.hin.ReadConsoleInput(1)[0]
            #print(ch)

            if ch.EventType == w32con.KEY_EVENT and ch.KeyDown and ch.VirtualKeyCode not in self.ignSet:
                ## (left control key) 0x8 | *right control key) 0x4 == 0xc
                if ch.ControlKeyState & 0x0c:
                    ch.VirtualKeyCode += 1000

                if ch.ControlKeyState & 0x10:
                    ch.VirtualKeyCode += 2000
                self.writeStatus("Key: " + str(ch.VirtualKeyCode))
                return ch

            if ch.EventType == w32con.MOUSE_EVENT:
                self.writeStatus("Mouse: " + str(ch))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readInput(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        while 1:
            ch = self.readKey()
            #print(ch.Char, ch.VirtualKeyCode)
            if ch.VirtualKeyCode == 13 or ch.VirtualKeyCode == 27:
                return ''.join(s)

            self.write(ch.Char)
            s.append(ch.Char)


KEY_MAP = {
    13   : 'RET',
     8   : 'BKSP',
    1072 : 'BKSP',
    38   : 'UP',
    40   : 'DOWN',
    37   : 'LEFT',
    39   : 'RGHT',
    36   : 'HOME',
    25   : 'END',
     9   : 'TAB',
}


#-------------------------------------------------------------------------------
class Console(object):
#-------------------------------------------------------------------------------
    """ Object representing a 'console'
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, title='', screen=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Console, self).__init__()

        self.screen = Screen() if screen is None else screen
        self.prompt = "test> "
        self.promptContinue = 'test>> '
        self.continuationChar = '\\'

        self.history = []
        self.screen.SetTitle(title)

        self.vi = ViKeyMapping()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeXY(self, x, y, obj, line=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.screen.writeXY(x, y, obj, line)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addHistory(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            if cmd == self.history[0]: return
        except IndexError:
            pass
        self.history.insert(0, cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getHistory(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.historyIdx < 0:
            self.historyIdx = 0
        if self.historyIdx >= len(self.history):
            self.historyIdx = len(self.history)-1

        try:
            return self.history[self.historyIdx]
        except IndexError:
            return ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.screen.clear()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setCursor(self, x=None, y=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if x is not None:
            if x < self.pl: x = self.pl
            if x > self.pl + len(self.cmd): x = self.pl + len(self.cmd)
            self.x = x

        if y is not None:
            self.y = y

        try:
            self.screen.setXY(self.x, self.y)
        except Screen.CoordinateException:
            self.x = 0
            self.y += 1
            self.screen.setXY(self.x, self.y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setNewLine(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.screen.setXY(0, self.y+1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addChar(self, ch, insert=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmd.insert(self.x - self.pl, ch)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x, y = self.screen.getXY()
        self.screen.setXY(self.pl, self.y)
        self.write(''.join(self.cmd))
        self.setCursor(x)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.screen.write(s, line=True)
        self.x, self.y = self.screen.getXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.screen.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getCmdStr(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return ''.join(self.cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setCmdStr(self, cmd, x = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmd = [ch for ch in cmd]
        if x is not None:
            self.x = x
            self.screen.setXY(x, self.y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def read_input(self, completionListFunc = None, prompt=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmd = []
        self.vi.reset()

        if prompt is None:
            prompt = self.prompt

        return self._read_input(completionListFunc, prompt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _read_input(self, completionListFunc, prompt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.pl = len(prompt)
        self.write(prompt)

        self.historyIdx = 0

        while 1:
            self.update()

            ch = self.screen.readKey()
            key = ch.VirtualKeyCode

            actions = [KEY_MAP[key]] if key in KEY_MAP else WordStarKeyMapping(key, self.screen.readKey)
            if not actions:
                actions = self.vi.getKey(key)

            if not actions:
                actions = ['KEY']

            for action in actions:
                ## return key
                if action == 'RET':
                    cmdstr = self.getCmdStr()
                    self.setNewLine()

                    if cmdstr.endswith(self.continuationChar):
                        del self.cmd[-1]
                        return self._read_input(completionListFunc, self.promptContinue)

                    self.addHistory(cmdstr)
                    return cmdstr

                ## backspace
                elif action == 'BKSP':
                    if self.x != self.pl:
                        #print "\n", self.x, self.pl, "\n"
                        try:
                            del self.cmd[self.x - self.pl - 1]
                        except IndexError:
                            pass
                        self.setCursor(self.x-1)

                ## up arrow
                elif action == 'UP':
                    cmd = self.getHistory()
                    self.historyIdx += 1
                    self.setCmdStr(cmd, self.pl + len(cmd))

                ## down arrow
                elif action == 'DOWN':
                    self.historyIdx -= 1
                    cmd = self.getHistory()
                    self.setCmdStr(cmd, self.pl + len(cmd))

                ## left arrow
                elif action == 'LEFT':
                    self.setCursor(self.x-1)

                ## right arrow
                elif action == 'RGHT':
                    self.setCursor(self.x+1)

                ## home
                elif action == 'HOME':
                    self.setCursor(self.pl)

                ## end
                elif action == 'END':
                    self.setCursor(self.pl + len(self.cmd))

                ## tab (auto completion)
                elif action == 'TAB':

                    ## returns either:
                    ## - none for no matches
                    ## - a str which is the new cmd string
                    ## - a list of choices
                    res = completionListFunc(self, self.getCmdStr())

                    if res is not None:
                        if isinstance(res, (str, unicode)):
                            self.setCmdStr(res, self.pl + len(res))
                        else:
                            x = self.x
                            self.setNewLine()
                            self.write(' '.join(res))
                            self.setNewLine()
                            self.write(self.prompt)
                            self.update()
                            self.setCursor(x)

                elif action == 'RM_EOL':
                    self.cmd = self.cmd[:(self.x-self.pl)]

                elif action == 'DEL_CHAR':
                    try:
                        del self.cmd[self.x-self.pl]
                    except IndexError:
                        pass

                elif action == 'EDITOR':
                    otf = open('/tmp/mysh.txt', 'w')
                    otf.write(self.getCmdStr())
                    otf.close()
                    oss.r('vi /tmp/mysh.txt')
                    inf = open('/tmp/mysh.txt')

                    cmdstr = ' '.join([line[:-1] for line in inf.readlines()])
                    self.clear()
                    self.write(prompt)
                    self.setCmdStr(cmdstr, self.pl)

                elif action == 'NOP':
                    pass

                ## other key
                else:
                    self.addChar(ch.Char)
                    self.setCursor(self.x+1)


#-------------------------------------------------------------------------------
class Menu(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, screen, title=None, labels=None, text=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.scrn = screen
        self.scrn.clear()
        self.title = title

        self.labels = [v.strip() for v in labels] if labels else []
        self.text = [v.strip() for v in text.split('\n')] if text else []
        self.sx, self.sy = self.getStartXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setText(self, text):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.text = [v.strip() for v in text.split('\n')]
        self.sx, self.sy = self.getStartXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setLabels(self, labels):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.labels = [v.strip() for v in labels]
        self.sx, self.sy = self.getStartXY()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getStartXY(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ## account for title, sel, and empty spacing lines
        y = (self.scrn.screen.Bottom - len(self.labels) - len(self.text))/4
        y = y - 3
        if not (0 <= y < self.scrn.screen.Bottom):
            y = 0

        x = 0
        for v in self.labels + self.text + [self.title, 'Sel: ']:
            l = len(v)
            if l > x: x = l

        x = (self.scrn.screen.Right - x)/2 - 2
        if not (0 <= x < self.scrn.screen.Right):
            x = 0

        return x, y

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def drawMenu(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.scrn.clear()
        self.scrn.writeXY(self.sx, self.sy, self.title)

        y = 2  # title and a blank line
        for v in self.text:
            self.scrn.writeXY(self.sx, self.sy + y, v)
            y += 1

        y += 1  # add a blnk line

        idx = 0
        idxmap = {}
        for lbl in self.labels:
            if lbl:
                ## is it a separator
                if lbl.startswith('---'):
                    self.scrn.writeXY(self.sx, self.sy + y, '---------')
                else:
                    self.scrn.writeXY(self.sx, self.sy + y, "%2d %s" % (idx, lbl))
                    idxmap[idx] = lbl
                    idx += 1
            y += 1

        y += 1 # add a blank line
        self.prompt(y)
        return y, idxmap

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prompt(self, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.scrn.writeXY(self.sx, self.sy + y, "Sel:                ")
        self.scrn.setXY(self.sx + 5, self.sy + y)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getSel(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        y, idxmap = self.drawMenu()

        while 1:
            self.prompt(y)
            ch = self.scrn.readInput()

            if ch is None or ch in ['quit', 'exit']:
                return

            try:
                return idxmap[int(ch)]
            except (ValueError, KeyError):
                pass


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [], [])

    ## if left in bad state
    if args:
        Screen().SetMode(0xf7, 0x3)
        oss.exit()


    s = Screen('menu')
    print(s.readKey())
    print(s.readKey())
    print(s.readKey())
    print(s.readKey())


    oss.exit()

    m = Menu(s, 'cool', ["cooler", "dog", "aidan", "aiden"], "how is this\nstuff\nis cool")
    print(m.getSel())
    oss.exit()

    def getCompList(cons, cmdstr):
        l = ["cooler", "dog", "aidan", "aiden"]
        cmd = cmdstr.split()
        ll = [cc for cc in l if cc.startswith(cmd[-1])]
        if not ll:
            return

        if len(ll) == 1:
            cmd[-1] = ll[0]
            return ' '.join(cmd)
        else:
            return ll

    c = Console("Title")
    try:
        c.clear()

        for i in range(30):
            res = c.read_input(getCompList)
            if res == "clear":
                c.clear()
                continue
            elif res == "exit":
                print "\n\n"
                break
            print "\n\nres:", res

    finally:
       c.close()


#-------------------------------------------------------------------------------
def WordStarKeyMapping(key, readCharFunc):
#-------------------------------------------------------------------------------
    """ wordstar conversions
    """

    ## Ctrl-q
    if key == 1081:
        key = readCharFunc().VirtualKeyCode

        ## ctrl-s
        if key == 1083: return ['HOME']

        ## ctrl-d
        if key == 1068: return ['END']

        ## ctrl-y
        if key == 1089: return ['RM_EOL']

    ## ctrl-d
    if key == 1068: return ['RGHT']

    ## ctrl-s
    if key == 1083: return ['LEFT']

    ## ctrl-e
    if key == 1069: return ['UP']

    ## ctrl-x
    if key == 1088: return ['DOWN']

    ## ctrl-g
    if key == 1071: return ['DEL_CHAR']

    ## ctrl-v
    if key == 1086: return ['EDITOR']



#-------------------------------------------------------------------------------
class ViKeyMapping(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.reset()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.state = 'insert'
        self.oneTime = 0
        self.cnt = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getKey(self, key):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.oneTime > 0:
            self.oneTime -= 1

            if self.oneTime == 0:
                self.state = 'cmd'

        if self.state == 'insert':
            if key == 27:
                self.state = 'cmd'
                return ['NOP']
        else:
            ## r
            if key == 82:
                self.state = 'insert'
                self.oneTime = 2
                return ['DEL_CHAR']

            ## l
            if key == 76:
                cnt = 1 if self.cnt is None else self.cnt
                self.cnt = None
                return ['RGHT'] * cnt

            ## h
            if key == 72:
                cnt = 1 if self.cnt is None else self.cnt
                self.cnt = None
                return ['LEFT'] * cnt

            ## j
            if key == 74:
                cnt = 1 if self.cnt is None else self.cnt
                self.cnt = None
                return ['DOWN'] * cnt

            ## k
            if key == 75:
                cnt = 1 if self.cnt is None else self.cnt
                self.cnt = None
                return ['UP'] * cnt

            ## x
            if key == 88:
                cnt = 1 if self.cnt is None else self.cnt
                self.cnt = None
                return ['DEL_CHAR'] * cnt

            ## i
            if key == 73:
                self.state = 'insert'
                return ['NOP']

            ## a
            if key == 65:
                self.state = 'insert'
                return ['RGHT']

            ## shift-A
            if key == 2065:
                self.state = 'insert'
                return ['END']

            if 49 <= key <= 57:
                if self.cnt is None:
                    self.cnt = key - 48
                else:
                    self.cnt = 10 * self.cnt + key - 48

            ## 0
            if key == 48:
                if self.cnt is None:
                    return ['HOME']

                self.cnt = 10 * self.cnt

            return ['NOP']


if __name__ == "__main__":
    main(oss.argv)


