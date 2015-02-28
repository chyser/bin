#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import re
import glob
import pprint
import fnmatch
import tempfile
import threading
import subprocess

import pylib.lex as lex
import pylib.util as util
import pylib.relib as relib
import pylib.osscripts as oss
import pylib.filewalker as fw

STRICT= False
MAKEFILE_NAMES = ['make.pmk', 'makefile']
DBG = None

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """usage: make.py [options] <target> [<target> ...]

    options:
        -C | --cd      : change dir before running

        -s | --strict  : be strict about dependency existence
        -f | --file    : specify the makefile to use (default: %s)
    """
    usage = oss.mkusage(main.__doc__ % str(MAKEFILE_NAMES))
    args, opts = oss.gopt(argv[1:], [('s', 'strict'), ], [('f', 'file'), 'dbg', ('C', 'cd')], usage)

    mfile = opts.file if opts.file is not None else getFileName()

    global STRICT, DBG
    STRICT = opts.strict
    DBG = opts.dbg

    if opts.cd is not None:
        oss.cd(opts.cd)

    p = Parser()
    try:
        p.parse(mfile)
    except IOError as ex:
        usage(1, str(ex))

    if DBG == 'rules':
        p.dump()
        print("="*75, '\n\n')
        oss.exit(0)

    if DBG in set(['file', 'tokens']):
        oss.exit(0)

    if not args:
        args = ['default']

    try:
        for arg in args:
            p.do(arg)
    except MakeExit as ex:
        print(ex)

    oss.exit(0)


class MakeException(Exception): pass

class MakeSyntaxError(MakeException):
    def __init__(self, msg, fn, ln, line):
        MakeException.__init__(self, "%s %d: %s\n'%s'" % (fn, ln, msg, line))

class MakeError(MakeException):
    def __init__(self, msg, lineNum=None):
        m = "Error: (%d) %s" % (lineNum, str(msg)) if lineNum is not None else "Error: %s" % (str(msg))
        Exception.__init__(self, m)

class MakeExit(MakeException): pass


#-------------------------------------------------------------------------------
def Error(msg):
#-------------------------------------------------------------------------------
    if STRICT:
        raise MakeError(msg)
    else:
        print(msg, file=oss.stderr)


WHITE_SPACE = set([' ', '\t', '\n'])


#
# Provide some builtin commands
#
BUILTINS = {}

#-------------------------------------------------------------------------------
def BUILTIN_echo(args):
#-------------------------------------------------------------------------------
    if '>>' in args:
        s, _, fn = args.rpartition('>>')
        fn = fn.strip()
        s = s.strip()
        with open(fn, 'a') as otf:
            otf.write(s + '\n')
    elif '>' in args:
        s, _, fn = args.rpartition('>')
        fn = fn.strip()
        s = s.strip()
        with open(fn, 'w') as otf:
            otf.write(s + '\n')
    else:
        print(args)


#-------------------------------------------------------------------------------
def BUILTIN_cd(s):
#-------------------------------------------------------------------------------
    oss.cd(s)

for i in dir():
    if i.startswith('BUILTIN_'):
        BUILTINS[i[8:]] = globals()[i]


#-------------------------------------------------------------------------------
class RuleSet(list):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def findMatch(self, target, exclude=None, hasCmds=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if exclude is None:
            exclude = set()

        for rule in self:
            if fnmatch.fnmatch(target, rule.pattern) and rule not in exclude and (not hasCmds or rule.cmds):
                if rule.canBuild(target):
                    return rule


#-------------------------------------------------------------------------------
def getRuleClass(pattern):
#-------------------------------------------------------------------------------
    if pattern[0] == '.':
        return GenericRule
    return Rule


#-------------------------------------------------------------------------------
class Rule(object):
#-------------------------------------------------------------------------------
    vPatt = re.compile(r"\$([<@*]|[0-9][0-9]*)")

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, pattern, deps):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.parent = parent
        self.pattern = pattern
        self.deps = deps
        self.cmds = []
        self.complete = threading.Event()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def finalize(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if ',' in self.pattern:
            patterns = [pat.strip() for pat in self.pattern.split(',')]
            self.pattern = patterns[0]

            for pat in patterns[1:]:
                self.parent.rules.append(self.copy(pat))

        if not any((cmd.strip() for cmd in self.cmds)):
            self.cmds = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self, pattern=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if pattern is None:
            pattern = self.pattern

        rule = getRuleClass(pattern)(self.parent, pattern, self.deps)
        rule.cmds = self.cmds
        return rule

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def canBuild(self, target):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCmd(self, cmd):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmds.append(cmd)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDeps(self, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.deps

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def execute(self, target, parallel=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.cmds:
            rule = self.parent.rules.findMatch(target, set([self]), hasCmds=True)
            if rule is None:
                Error('No rules to build "%s"' % target)
                return

            self.cmds = rule.cmds

        cmds = self.processCmds(target)

        if parallel:
            tid = threading.Thread(target=self.real_execute, args=(target, cmds))
            tid.start()
        else:
            self.real_execute(target, cmds)
        return self.complete

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def processCmds(self, tgt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def repl(mo):
            sym = mo.group(1)
            if sym == '<':
                return tgt.rsplit('.', 1)[0]

            if sym == '@':
                return tgt

            if sym == '*':
                return ' '.join(self.getDeps(tgt))

            try:
                return self.getDeps(tgt)[int(sym)]
            except IndexError:
                return ''
            except ValueError:
                pass

            raise MakeError('bad substitution "%s":' % sym)

        def replCall(mo):
            return "'''" + repl(mo) + "'''"

        return [self.vPatt.sub(replCall, cmd) if cmd.lstrip().startswith('call') else self.vPatt.sub(repl, cmd) for cmd in self.cmds]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def real_execute(self, tgt, cmds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        script = []
        args = prgm = eof = strip = None

        state = 0

        env = dict(self.parent.mobj.env)
        oss.cd(self.parent.curDir)

        for line in cmds:
            if state == 0:
                if '<<<' in line:
                    state = 1
                    strip, line = util.leadingSpaces(line)
                    a, eof = relib.split('<<<', line)
                    prgm = a[0]
                    try:
                        args = a[1:]
                    except IndexError:
                        args = []
                else:
                    line = line.strip()
                    if line:
                        s = line.split(' ', 1)

                        if s[0] in BUILTINS:
                            BUILTINS[s[0]](s[1])

                        elif s[0] == 'set':
                            try:
                                var, _, val = s[1].partition('=')
                                var = var.strip().encode('ascii', 'ignore')
                                if _ == '=':
                                    val = val.strip().encode('ascii', 'ignore')
                                    env[var] = val
                                else:
                                    print(var, '=', env[var])
                            except IndexError:
                                pprint.pprint(env)

                        elif s[0] == 'call':
                            cmd = self.parent.evalPython(s[1])
                            if cmd is not None:
                                self.runCmd(tgt, cmd, env)

                        else:
                            self.runCmd(tgt, line, env)

            elif state == 1:
                if line.strip() == eof[0]:
                    otf = tempfile.NamedTemporaryFile(delete=False)
                    name = otf.name
                    otf.writelines(script)
                    otf.close()

                    try:
                        self.runCmd(tgt, prgm + ' ' + name + ' ' + ' '.join(args), env, True)
                    finally:
                        oss.rm(name)

                    script = []
                    args = prgm = eof = strip = None
                    state = 0
                else:
                    ln = line[strip:]
                    if len(ln) == 0:
                        ln = '\n'
                    script.append(ln)

        self.complete.set()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runCmd(self, tgt, cmd, env, silent=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if cmd[0] == '@':
            silent = True
            cmd = cmd[1:]

        if cmd[0] == '-':
            cmd = cmd[1:]
            ignoreError = True
        else:
            ignoreError = False

        s = cmd.split(' ', 1)
        if s[0].endswith('.py'):
            fx = oss.which(s[0])
            if fx is None:
                raise MakeExit('make.py: [%s] Error: Cannot find "%s"' % (tgt, s[0]))

            try:
                cmd = 'python ' + fx + ' ' + s[1]
            except IndexError:
                cmd = 'python ' + fx

        if cmd[0] == '@':
            silent = True
            cmd = cmd[1:]

        if not silent:
            print(cmd)

        try:
            rc = subprocess.call(cmd, env=env)
            if rc != 0:
                if not ignoreError:
                    raise MakeExit('make.py: [%s] Error: %d' % (tgt, rc))

        except WindowsError as ex:
            if not ignoreError:
                MakeExit('make.py: [%s] Error: "%s"' % (tgt, str(ex)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return 'pattern: "%s"\n\ndeps: %s\n\ncmds: %s' % (self.pattern, pprint.pformat(self.deps), pprint.pformat(self.cmds))


#-------------------------------------------------------------------------------
class GenericRule(Rule):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ruleSet, pattern, deps):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Rule.__init__(self, ruleSet, '*' + pattern, deps)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getDeps(self, arg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        arg = arg.rpartition('.')[0]
        return [arg + dep if dep[0] == '.' else dep for dep in self.deps]


#-------------------------------------------------------------------------------
class Parser(object):
#-------------------------------------------------------------------------------
    varReplPattern = re.compile(r"\$\((.*?)\)")

    lexer = lex.PLex([':', ',', '\\+=', '=', lex.STRING, lex.SSTRING])

    class MObj(object):
        def __init__(self, vars):
            self.vars = vars
            self.env = dict(os.environ)
            self.lines = []

        def __setitem__(self, key, val):
            self.vars[key] = val

        def __getitem__(self, key):
            return self.vars[key]

        def __contains__(self, key):
            return key in self.vars

        def getEnv(self, key):
            return self.env[key]

        def putEnv(self, var, val):
            var = var.encode('ascii', 'ignore')
            val = val.encode('ascii', 'ignore')
            self.env[var] = val

        def delEnv(self, key):
            del self.env['key']

        def put(self, line):
            self.lines.append(line)

        def lex(s):
            return Parser.lexer.lex(s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.rules = RuleSet()
        self.symbols = {}
        self.lineNum = 0

        self.mobj = self.MObj(self.symbols)
        self.codeEnv = {'mobj' : self.mobj}

        self.curDir = oss.pwd()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for rule in self.rules:
            rule.complete.clear()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def processed(self, line):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def repl(mo):
            sym = mo.group(1)
            if sym not in self.symbols:
                raise MakeError('unknown symbol "%s"' % sym, self.lineNum)
            return self.symbols[sym]

        return self.varReplPattern.sub(repl, line)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse(self, fn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ parse the file named 'fn'
        """
        with open(fn, 'rU') as infl:
            inf = fw.FileWalker(infl, fn)

            curRule = None
            code = []
            codeLineNum = 0
            codeName = ''

            state = 0
            for self.fileName, self.lineNum, line in inf:
                if state == 0:
                    if line.startswith('<python'):
                        state = 1
                        code = []
                        codeLineNum = self.lineNum
                        codeName = line
                        continue

                    if DBG == 'file':
                        print(line.rstrip())

                    if line[0] == '#':
                        continue

                    if line[0] not in WHITE_SPACE:
                        line = line.rstrip()

                        token = self.lexer.lex(line)

                        if DBG == 'tokens':
                            print('tokens:', token)

                        if '=' == token[1]:
                            self.symbols[token[0]] = self.processed(' '.join(token[2:]))
                            continue

                        if '+=' == token[1]:
                            self.symbols[token[0]] = self.symbols.get(token[0], '') + ' ' + self.processed(' '.join(token[2:]))
                            continue

                        try:
                            idx = token.index(':')
                        except ValueError:
                            raise MakeSyntaxError('incorrect rule', self.fileName, self.lineNum, line)

                        pattern = self.processed(' '.join(token[:idx]))
                        deps = self.expandWildCards([self.processed(dep) for dep in token[idx+1:]])

                        if curRule is not None:
                            curRule.finalize()

                        curRule = getRuleClass(pattern)(self, pattern, deps)
                        self.rules.append(curRule)

                    else:
                        if curRule is not None:
                            curRule.addCmd(self.processed(line))

                elif state == 1:
                    if line.startswith('</python>'):
                        state = 0
                        self.runPython(code, self.fileName, inf, codeName, codeLineNum)
                    else:
                        code.append(line)

            if curRule is not None:
                curRule.finalize()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runPython(self, code, fileName='internal', inf=None, codeName='internal', codeLineNum=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cc = compile(('\n' * codeLineNum) + '\n'.join(code), fileName, 'exec')

        exec cc in self.codeEnv

        if inf and self.mobj.lines:
            inf.add(self.mobj.lines, codeName)
            self.mobj.lines = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def evalPython(self, code):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        res = eval(code, self.codeEnv)
        if res is None:
            return None
        if isinstance(res, list):
            return ' '.join([str(r) for r in res])
        return str(res)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expandWildCards(self, deps):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        d = []
        for dep in deps:
            if dep[0] not in ['"', "'"]:
                dd = glob.glob(dep)
                if not dd:
                    d.append(dep)
                else:
                    d.extend(dd)
            else:
                d.append(dep)
        return d

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def do(self, target, lvl=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ find a rule for 'target', resolve dependencies and build if necessary
        """
        rule = self.rules.findMatch(target)

        ## if there is no way to build 'target' then don't wait on the build
        if rule is None:
            if not oss.exists(target):
                Error('File does not exist. "%s"' % target)
            return

        ## resolve dependencies and then build 'target' if needed
        return self.resolve(target, rule, lvl+1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolve(self, target, rule, lvl):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ resolve all dependencies, then build 'target' if needed.
        """
        ## all the dependencies that need to build will return events
        for e in [self.do(dep, lvl) for dep in rule.getDeps(target)]:
            if e is not None: e.wait()

        ## now that we have waited for any builds of dependencies, see if we should build
        if not oss.exists(target) or any((oss.exists(dep) and not oss.newerthan(target, dep) for dep in rule.getDeps(target))):
            return rule.execute(target, parallel=False)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for r in self.rules:
            print('-'*40)
            print(r)


#-------------------------------------------------------------------------------
def getFileName():
#-------------------------------------------------------------------------------
    for name in MAKEFILE_NAMES:
        if oss.exists(name):
            return name


if __name__ == "__main__":
    main(oss.argv)
