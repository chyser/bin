#!/usr/bin/env python
"""
usage:

"""

import compiler

import pylib.debug as dbg
import pylib.osscripts as oss
from compiler.ast import Node

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """
Error:
""" + str(errmsg)
    oss.exit(rc)


#-------------------------------------------------------------------------------
def pprintAst(ast, indent='    ', stream=oss.stdout):
#-------------------------------------------------------------------------------
    "Pretty-print an AST to the given output stream."
    rec_node(ast, 0, indent, stream.write)

#-------------------------------------------------------------------------------
def rec_node(node, level, indent, write):
#-------------------------------------------------------------------------------
    "Recurse through a node, pretty-printing it."
    pfx = indent * level
    if isinstance(node, Node):
        write(pfx)
        write(node.__class__.__name__)
        write('(')

        if any(isinstance(child, Node) for child in node.getChildren()):
            for i, child in enumerate(node.getChildren()):
                if i != 0:
                    write(',')
                write('\n')
                rec_node(child, level+1, indent, write)
            write('\n')
            write(pfx)
        else:
            # None of the children as nodes, simply join their repr on a single
            # line.
            write(', '.join(repr(child) for child in node.getChildren()))

        write(')')

    else:
        write(pfx)
        write(repr(node))



#-------------------------------------------------------------------------------
class Compiler(object):
#-------------------------------------------------------------------------------

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class SyntaxError(Exception):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class Cxt(object):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, state, classargs=''):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            object.__init__(self)
            self.state = state
            self.classargs = classargs
            self.args = {}
            self.lvl = 0
            self.vars = {}
            self.decGlobal = {}

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __str__(self):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            return '[State: ' + self.state + ', lvl: ' + str(self.lvl) + ', vars: ' + str(self.vars) + '] '


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName, debug=True):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.cur = Compiler.Cxt('GLOBAL')
        self.cxt = [self.cur]
        self.fileName = fileName
        self.lines = file(fileName, 'rU').readlines()

        if debug:
            self.sp = ' '
            self.arg = ', '
        else:
            self.sp = ''
            self.arg = ','
        self.debug = debug

        self.nvar = 0
        self.globals = {}
        self.funclass = {}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cxt.pop(0)
        self.cur = self.cxt[0]
        print 'pop:', self.cur.lvl
        return self.cur

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def push(self, cxt, adj=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cxt.lvl = self.cur.lvl + 1 + adj
        print 'push:', cxt.lvl
        self.cxt.insert(0, cxt)
        self.cur = cxt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isVar(self, kind, var):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for cxt in self.cxt:
            if cxt.state == kind:
                return var in cxt.vars or var in cxt.args

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nextVar(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        nv = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'[self.nvar]
        self.nvar += 1
        return nv

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def op(self, o):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.debug:
            return o
        return self.sp + o + self.sp

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nl(self, idx = 0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not self.debug:
            return ''
        return '\n' + '    '*(self.cur.lvl + idx)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getLine(self, ln):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.debug:
            return '// ' + self.lines[ln-1].strip() + '  -- [%3d]' % ln
        return ''

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for cxt in self.cxt:
            print cxt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hFunction(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        res = []
        for an in node.argnames:
            if an != 'self':
                res.append(an)

        if self.cur.state == 'GLOBAL':
            self.push(Compiler.Cxt('FUNC'))
            for an in res:
                self.cur.args[an] = self.nextVar()

            code = self.compile(node.code)
            self.funclass[node.name] = self.nextVar()
            s = self.nl(-1) + self.getLine(node.lineno)
            s += self.nl(-1) + 'function ' + node.name + '(' + self.arg.join(res) + ')' + self.sp + '{'
            if self.cur.vars:
                s += self.nl() + 'var ' + self.arg.join(self.cur.vars.keys()) +';'

            s += self.nl() + code
            s +=  self.nl(-1) + '}' + self.nl(-1)
            self.pop()
            return s

        ## needs to be handled differently then the declaration of a regular
        ## method
        if node.name == '__init__':
            self.push(Compiler.Cxt('FUNC'))
            for an in res:
                self.cur.args[an] = self.nextVar()
            s = self.nl(-1) + self.getLine(node.lineno)
            code = self.compile(node.code)
            if self.cur.vars:
                s += self.nl() + 'var ' + self.arg.join(self.cur.vars.keys()) +';'
            s += self.nl() + code
            self.pop()
            self.cur.classargs = self.arg.join(res)
            return s

        ## assign methods to the 'inherited' prototype
        self.push(Compiler.Cxt('FUNC'))
        for an in res:
            self.cur.args[an] = self.nextVar()
        code = self.compile(node.code)
        s = self.nl(-1) + self.getLine(node.lineno)
        s += self.nl(-1) + 'this.prototype.' + node.name + self.op('=') + 'function(' + self.arg.join(res) + ')' + self.sp + '{'
        if self.cur.vars:
            s += self.nl() + 'var ' + self.arg.join(self.cur.vars.keys()) +';'
        s += self.nl() + code
        s += self.nl(-1) + '}' + self.nl(-1)
        self.pop()
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hClass(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        name = node.name
        self.funclass[name] = self.nextVar()

        self.push(Compiler.Cxt('CLASS'))
        code = self.compile(node.code)
        s = self.nl(-1) + self.getLine(node.lineno)
        s += self.nl(-1) + "%s%sfunction(%s)%s{" % (name, self.op('='), self.cur.classargs, self.sp)
        s += self.nl() + 'this.prototype' + self.op('=') + 'new %s();' % (node.bases[0].name)
        s += self.nl() + code
        s += self.nl(-1) + '}' + self.nl(-1)
        self.pop()
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hStmt(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        res = []
        for n in node.getChildren():
            res.append(self.compile(n))
        return self.nl().join(res)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hAssign(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        res = []
        for n in node.nodes:
            lh = self.compile(n)
            res.append(lh)
        res.append(self.compile(node.expr))
        return ''.join(res) + ';'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hAssName(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #if node.name == 'gg': self.dump()

        if self.cur.state == 'GLOBAL':
            if node.name not in self.cur.vars:
                self.globals[node.name] = self.nextVar()
            return node.name + self.op('=')

        elif self.cur.state == 'CLASS':
            if node.name not in self.cur.vars:
                self.cur.vars[node.name] = self.nextVar()
            return 'this.protoype.' + node.name + self.op('=')

        elif self.cur.state == 'FUNC':
            ## if declared global, must not be a local
            if node.name not in self.cur.decGlobal:
                if not self.isVar('FUNC', node.name):
                    self.cur.vars[node.name] = self.nextVar()
            return node.name + self.op('=')
        else:
            assert 0
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hIf(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = self.nl() + self.getLine(node.lineno)
        s += self.nl() + 'if' + self.sp + '('
        for idx, n in enumerate(node.tests):
            test = self.compile(n[0])
            if idx != 0:
                s += self.nl() + 'else if' + self.sp + '('
            s += test + ')' + self.sp + '{'
            self.cur.lvl += 1
            s += self.nl() + self.compile(n[1])
            self.cur.lvl -= 1
            s += self.nl() + '}' + self.nl()
        print 'else:', node.else_
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hWhile(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = self.nl() + self.getLine(node.lineno)
        s += self.nl() + 'while' + self.sp + '('
        test = self.compile(node.test)
        s += test + ')' + self.sp + '{'
        self.cur.lvl += 1
        s += self.nl() + self.compile(node.body)
        self.cur.lvl -= 1
        s += self.nl() + '}' + self.nl()
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hCompare(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ch = node.getChildren()

        if len(ch) == 5:
            s = self.compile(ch[0])
            s += self.op(ch[1])
            code = self.compile(ch[2])
            s += code
            s += self.op('&&')
            s += code
            s += self.op(ch[3])
            s += self.compile(ch[4])

        elif len(ch) == 3:
            s = self.compile(ch[0])
            s += self.op(ch[1])
            s += self.compile(ch[2])
        else:
            assert 0
            pass

        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hAnd(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ''
        for n in node.nodes[:-1]:
            s += self.compile(n) + self.op('&&')
        s += self.compile(node.nodes[-1])
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hOr(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = ''
        for n in node.nodes[:-1]:
            s += self.compile(n) + self.op('||')
        s += self.compile(node.nodes[-1])
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hFor(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
###        print 'For:'
###        print node.assign
###        print node.list, type(node.list)
###        print node.body

        lst = self.compile(node.list)
        self.cur.vars['$i'] = self.nextVar()

        s = self.getLine(node.lineno)
        s += self.nl() + 'for' + self.sp + '($i=0;' + self.sp + '$i<' + lst + '.length;' + self.sp + '++$i)' + self.sp + '{'
        self.cur.lvl += 1
        s += self.nl() + self.compile(node.assign) + lst + '[$i];'
        s += self.nl() + self.compile(node.body)
        self.cur.lvl -= 1
        s += self.nl() + '}' + self.nl()
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hGetattr(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print 'Getattr'
        print node.expr
        print node.attrname
        nm = self.compile(node.expr)

        if nm == 'self':
            nm = 'this'
        return nm + '.' + node.attrname


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def gt(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return node.__class__.__name__

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compile(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(node, Node):
            typ = self.gt(node)

            mbr = getattr(self, 'h'+typ, None)
            if mbr:
                res = mbr(node)

            elif typ == 'AssAttr':
                lh = self.compile(node.expr)
                if lh == 'self': lh = 'this'
                return lh + '.' + node.attrname + self.op('=')

            elif typ == 'AugAssign':
                return self.nl() + self.compile(node.node) + self.op(node.op) + self.compile(node.expr) + ';'

            elif typ == 'Const':
                if isinstance(node.value, (str, unicode)):
                    ## TODO: call a func that escapes
                    return '"' + node.value + '"'
                return str(node.value)

            elif typ == 'Name':
                return node.name

            elif typ == 'Add':
                return self.compile(node.left) + self.op('+') + self.compile(node.right)
            elif typ == 'Sub':
                return self.compile(node.left) + self.op('-') + self.compile(node.right)
            elif typ == 'Mul':
                return self.compile(node.left) + self.op('*') + self.compile(node.right)
            elif typ == 'Div':
                return self.compile(node.left) + self.op('/') + self.compile(node.right)

            elif typ == 'UnarySub':
                if self.gt(node.expr) != 'Const':
                    return '(-1*(' + self.compile(node.expr) + '))'
                return '-' + self.compile(node.expr)

            elif typ == 'UnaryAdd':
                return self.compile(node.expr)

            elif typ == 'Not':
                return '!(' + self.compile(node.expr) + ')'

            elif typ == 'Break':
                return 'break;'

            elif typ == 'Continue':
                return 'continue;'

            elif typ == 'Module':
                res = ''
                for n in node.getChildren():
                    res += self.compile(n)

            elif typ == 'CallFunc':
                res = []
                for a in node.args:
                    res.append(self.compile(a))
                return self.compile(node.node)+'(' + self.arg.join(res) + ')'

            elif typ == 'Return':
                return 'return ' + self.compile(node.value) + ';'

            elif typ == 'Pass':
                return ';'

            else:
                print "Node (%s):" % typ, node, dir(node)
                res = '@@' + typ + '@@ '
                for n in node.getChildren():
                    res += str(self.compile(n))
            return res

        #print "NOT NODE: ", node
        return ''


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('d', 'debug'), ('p', 'printast')], [], usage)

    mod = compiler.parseFile(args[0])

    if opts.printast:
        pprintAst(mod)

    print '\n=============='
    res = Compiler(args[0], not opts.debug).compile(mod)
    print '\n=============='

    print res

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

