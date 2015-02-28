#!/usr/bin/env python
"""
usage:

"""

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def printit(s, p):
#-------------------------------------------------------------------------------
    print "%s -> '%s'" % (s, p[0]), p.linespan(0)


gID = 0
gComments = {}

#-------------------------------------------------------------------------------
# lexer
#-------------------------------------------------------------------------------
tokens = ('SYMBOL','INTEGER',
          'PLUS','MINUS','MULT','DIVIDE',
          'ASSIGN', 'EASSIGN',
          'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE',
          'COMMA', 'SEMICOLON', 'DOT', 'ARROW',
          'LINECOMMENT', 'COMMENT', 'NEWLINE', 'IMPORT', 'MAIN',
          'EQ', 'NE', 'LT', 'GT', 'LTE', 'GTE', 'AND', 'OR', 'NOT',
          'PLUSASSIGN', 'MINUSASSIGN', 'MULTASSIGN', 'DIVIDEASSIGN',
          'DEF', 'IF', 'FOR', 'WHILE', 'GOTO', 'RETURN', 'BREAK', 'CONTINUE',
          'SWITCH', 'IN', 'ELSE', 'OUT',
          'STRING0', 'CHAR'
         )

def t_LINECOMMENT(t):
    r'//.*'
    gComments[t.lineno] = t.value

def t_COMMENT(t):
    r'/\*(.|\n)*\*/'
    gComments[t.lineno] = t.value

t_EQ      = r'=='
t_NE      = r'!='
t_LT      = r'<'
t_LTE     = r'<='
t_GT      = r'>'
t_NOT     = r'!'
t_GTE     = r'>='
t_AND     = r'&&'
t_OR      = r'\|\|'

t_DOT     = r'\.'
t_ARROW   = r'->'

t_PLUSASSIGN   = r'\+='
t_MINUSASSIGN  = r'-='
t_MULTASSIGN   = r'\*='
t_DIVIDEASSIGN = r'/='

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIVIDE = r'/'

t_ASSIGN = r'='
t_EASSIGN = r':='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'{'
t_RBRACKET = r'}'
t_LBRACE = r'\['
t_RBRACE = r'\]'
t_COMMA = r','
t_SEMICOLON = r';'

t_STRING0  = r'"(\\"|[^"])*"'
t_CHAR = r"'.'"

reserved = {
    'def'    : 'DEF',
    'if'     : 'IF',
    'for'    : 'FOR',
    'while'  : 'WHILE',
    'else'   : 'ELSE',
    'goto'   : 'GOTO',
    'return' : 'RETURN',
    'break'  : 'BREAK',
    'continue' : 'CONTINUE',
    'switch' : 'SWITCH',
    'in'     : 'IN',
    'out'    : 'OUT',
    'import' : 'IMPORT',
    'main'   : 'MAIN'
}

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'SYMBOL')
    return t

def t_INTEGER(t):
    r'\d+'
    return t

# Ignored characters
t_ignore = " \t"

def t_NEWLINE(t):
    r'\n+'
    t.lineno += t.value.count("\n")

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex(debug=0)


gINDENT_LVL = 0
gOutFile = None

#-------------------------------------------------------------------------------
# parser
#-------------------------------------------------------------------------------

types = []

# Parsing rules
precedence = (
    ('left', 'EQ'),
    ('left', 'NE'),
    ('left', 'LT'),
    ('left', 'LTE'),
    ('left', 'GT'),
    ('left', 'GTE'),

    ('left', 'OR'),
    ('left', 'AND'),
    ('right', '!'),
    ('left', 'IN'),

    ('left','PLUS','MINUS'),
    ('left','MULT','DIVIDE'),
    ('right','UMINUS'),
    )

def p_component(p):
    '''component : component component
                 | funcdecl
                 | mstatement
    '''
    if p[1] is not None:
        print >> gOutFile, p[0]

    print "p_complist -> '%s'" % p[1]

def p_funcdecl_0(p):
    'funcdecl : DEF SYMBOL LPAREN fparamlist RPAREN body'
    p[0] = 'void ' + p[2] + '(' + p[4] + ')\n' + p[6]
    printit("p_funcdecl_0", p)

def p_funcdecl_1(p):
    'funcdecl : DEF type SYMBOL LPAREN fparamlist RPAREN body'
    p[0] = p[2] + ' ' + p[3] + '(' + p[5] + ')\n' + p[7]
    printit("p_funcdecl_1", p)

def p_body(p):
    'body : LBRACKET mstatement RBRACKET'
    p[0] = '{\n' + p[2] + '\n}\n'

def p_body_empty(p):
    'body : LBRACKET RBRACKET'
    p[0] = '{\n' + '\n}\n'


def p_bstatement(p):
    '''bstatement : body
                  | statement
    '''
    p[0] = p[1]


def p_mstatement_1(p):
    '''mstatement : statement
    '''
    p[0] = p[1] + '\n'
    printit("p_mstatement_1", p)

def p_mstatement_2(p):
    '''mstatement : mstatement statement
    '''
    p[0] = p[1] + '\n' + p[2] + '\n'
    printit("p_mstatement_2", p)


def p_statement_empty(p):
    '''statement : SEMICOLON
    '''
    p[0] = p[1]

def p_statement_comment(p):
    '''statement : LINECOMMENT
                 | COMMENT
    '''
    p[0] = p[1]

def p_statement_assign(p):
    '''statement : astatement SEMICOLON
    '''
    p[0] = p[1] + ';'

def p_statement_assign_1(p):
    '''astatement : complexsymbol assigntok
    '''
    p[0] = p[1] + p[2]

def p_statement_assign_2(p):
    '''astatement : complexsymbol PLUSASSIGN expression
                  | complexsymbol MINUSASSIGN expression
                  | complexsymbol MULTASSIGN expression
                  | complexsymbol DIVIDEASSIGN expression
    '''
    p[0] = p[1] + ' ' + p[2] + ' ' + p[3]


def p_assigntok_1(p):
    '''assigntok : ASSIGN expression
    '''
    p[0] = ' = ' + p[2]

def p_assigntok_2(p):
    '''assigntok : assigntok assigntok
    '''
    p[0] = p[1] + p[2]

def p_statement_typedecl_0(p):
    '''statement : type SYMBOL SEMICOLON
    '''
    p[0] = p[1] + ' ' + p[2] + ';'

def p_statement_typedecl_1(p):
    '''statement : type SYMBOL ASSIGN expression SEMICOLON
    '''
    p[0] = p[1] + ' ' + p[2] + ' = ' + p[4] + ';'

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN bstatement
    '''
    p[0] = 'if (' + p[3] + ')\n' + p[5]

def p_statement_if_else(p):
    '''statement : IF LPAREN expression RPAREN bstatement ELSE bstatement
    '''
    p[0] = 'if (' + p[3] + ')\n' + p[5] + 'else\n' + p[7]

def p_statement_for_idx(p):
    '''statement : FOR LPAREN astatement SEMICOLON expression SEMICOLON astatement RPAREN bstatement
    '''
    p[0] = 'for (' + p[3] + '; ' + p[5] + '; ' + p[7] + ')\n' + p[9]

def p_statement_for_in(p):
    '''statement : FOR LPAREN complexsymbol IN complexsymbol RPAREN bstatement
    '''
    global gID
    gID += 1
    p[0] =  '\n// for (%s in %s) \n' % (p[3], p[5])
    p[0] += ('for (iter _itr%d; ' % (gID)) + ('%s.in(%s, itr%d);)\n' % (p[5], p[3], gID)) + p[7]

def p_while(p):
    '''statement : WHILE LPAREN expression RPAREN bstatement
    '''
    p[0] = 'while (' + p[3] + ')\n' + p[5]

def p_statement_import(p):
    '''statement : IMPORT flist SEMICOLON
    '''
    p[0] = p[2]
    printit("p_statement_import", p)

def p_statement_single(p):
    '''statement : CONTINUE SEMICOLON
                 | BREAK SEMICOLON
                 | RETURN SEMICOLON
                 | funcexpr SEMICOLON
    '''
    p[0] = p[1] + ';'

def p_statement_return(p):
    '''statement : RETURN expression SEMICOLON
    '''
    p[0] = 'return(' + p[2] + ');\n'

def p_flist_1(p):
    '''flist : SYMBOL
    '''
    p[0] = "#include <%s.h>     // import %s\n" % (p[1], p[1])

def p_flist_2(p):
    '''flist : flist COMMA flist
    '''
    p[0] = p[1] + p[3]

## expressions
def p_expression_single(p):
    '''expression : INTEGER
                  | CHAR
                  | complexsymbol
                  | funcexpr
    '''
    p[0] = p[1]

def p_expression_single_0(p):
    '''expression : STRING0
    '''
    p[0] = 'string(%s)' % p[1]

def p_expression_not(p):
    '''expression : NOT expression
    '''
    p[0] = '!(' + p[2] + ')'

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = '-' + p[2]

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = '(' + p[2] + ')'

def p_expression(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LTE expression
                  | expression GT expression
                  | expression GTE expression
                  | expression AND expression
                  | expression OR expression
    '''
    p[0] = p[1] + ' ' + p[2] + ' ' + p[3]

def p_expression_assign(p):
    '''expression : LPAREN complexsymbol EASSIGN expression RPAREN
    '''
    p[0] = '(' + p[2] + ' = ' + p[4] + ' /* %s := %s */)' % (p[2], p[4])

def p_expression_member(p):
    '''expression : complexsymbol IN complexsymbol
    '''
    p[0] = '%s.isIn(%s) /* %s in %s */' % (p[3], p[1], p[1], p[3])


def p_expression_funccall_0(p):
    '''funcexpr : complexsymbol LPAREN RPAREN
    '''
    p[0] = p[1] + '()'

def p_expression_funccall_1(p):
    '''funcexpr : complexsymbol LPAREN paramlist RPAREN
    '''
    p[0] = p[1] + '(' + p[3] + ')'

def p_paramlist_multiple(p):
    '''paramlist : paramlist COMMA paramlist
    '''
    p[0] = p[1] + ', ' + p[3]
    printit("p_paramlist_multiple", p)

def p_paramlist_single(p):
    '''paramlist : expression
    '''
    p[0] = p[1]
    printit("p_paramlist_single", p)


def p_fparamlist_1(p):
    '''fparamlist : fparams
    '''
    p[0] = p[1]
    printit("p_fparamlist_1", p)

def p_fparamlist_2(p):
    '''fparamlist : fparams COMMA fparamlist
    '''
    p[0] = p[1] + ', ' + p[3]
    printit("p_fparamlist_2", p)


def p_fparams_single(p):
    'fparams : type SYMBOL'
    p[0] = p[1] + ' ' + p[2]
    printit("p_fparams_single", p)

def p_fparams_single_0(p):
    '''fparams : OUT type SYMBOL
               | IN type SYMBOL
    '''
    if p[1] == 'out':
        p[0] = p[2] + ' &' + p[3]
    else:
        p[0] = p[2] + ' ' + p[3]
    printit("p_fparams_single_0", p)

def p_type(p):
    '''type : SYMBOL
    '''
    p[0] = p[1]
    if p[0] not in types:
        types.append(p[0])
    printit("p_type", p)

def p1_type_dict(p):
    '''type : LBRACKET type COMMA type RBRACKET
    '''
    p[0] = "dict<%s, %s >" % (p[2], p[4])
    if p[0] not in types:
        types.append(p[0])
    printit("p_type_dict", p)

def p_type_list(p):
    '''type : LBRACE type RBRACE
    '''
    p[0] = "list<%s >" % p[2]
    if p[0] not in types:
        types.append(p[0])
    printit("p_type_list", p)

def p1_type_tuple(p):
    '''type : LPAREN tuplist RPAREN
    '''
    p[0] = 'tuple<%s >' % p[2]
    if p[0] not in types:
        types.append(p[0])
    printit("p_type_tuple", p)

def p1_tuplist_1(p):
    '''tuplist : type
    '''
    p[0] = p[1]
    printit("p_tuplist_1", p)

def p1_tuplist_2(p):
    '''tuplist : type COMMA tuplist
    '''
    p[0] = p[1] + ', ' + p[3]
    printit("p_tuplist_2", p)

def p1_type_func_1(p):
    '''type : DEF LPAREN tuplist RPAREN
    '''
    p[0] = '(*def)(%s)' % p[3]
    printit("p_type_func_1", p)

def p1_type_func_0(p):
    '''type : DEF LPAREN RPAREN
    '''
    p[0] = '(*def)()'
    printit("p_type_func_0", p)

def p_complexsymbol_1(p):
    '''complexsymbol : SYMBOL
    '''
    p[0] = p[1]
    printit("p_complexsymbol_1", p)

def p_complexsymbol_2(p):
    '''complexsymbol : complexsymbol DOT complexsymbol
                 | complexsymbol ARROW complexsymbol
    '''
    p[0] = p[1] + p[2] + p[3]
    printit("p_complexsymbol_2", p)

def p_complexsymbol_3(p):
    '''complexsymbol : complexsymbol LBRACE expression RBRACE
    '''
    p[0] = p[1] +'[' + p[3] + ']'
    printit("p_complexsymbol_3", p)

gFileName = ""
gOpts = None

def p_error(p):
    print "Error: %d : Syntax error at '%s' (%s)" % (p.lineno, p.value, p.type)
    print '>>>', file(gFileName).readlines()[p.lineno-1]
    if not gOpts.go:
        oss.exit(2)

import ply.yacc as yacc
yacc.yacc()

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, "\nError:\n" + str(errmsg)
    oss.exit(rc)

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    global gFileName, gOutFile, gOpts

    args, opts = oss.gopt(argv[1:], [('g', 'go')], [], usage)
    args = oss.paths(args)
    gOpts = opts

    for a in args:
        if a.ext == '':
            gFileName = a + '.myc'
        else:
            gFileName = a

        gOutFile = file(a.name + '.mcpp', 'wU')
        yacc.parse(file(gFileName).read(), debug=1)
        print "\n"
        print 'types:', types
        print 'comments:', gComments

        gOutFile.close()


    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

