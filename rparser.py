import sys
import os
from pypy.rlib.parsing import parsing
from pypy.rlib.parsing.deterministic import LexerError
from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from pypy.rlib.parsing.parsing import PackratParser
from pypy.rlib.parsing.lexer import Lexer, SourcePos, Token
from pypy.rlib.parsing.parsing import ParseError
from pypy.rlib.parsing.tree import RPythonVisitor, Nonterminal, Node, Symbol

# Hack to fix translator issue
import py.test
class FixConfig:
    class option:
        view = False
py.test.config = FixConfig

grammar = open('language.grammar').read()
sample_code = open('test.rb').read()


class DisplayTreeVisitor(RPythonVisitor):
    
    def __init__(self):
        self.depth = 0
        self.indent = '  '
    
    def spacing(self):
        s = ''
        for i in xrange(self.depth):
            s += self.indent
        return s
    
    def general_symbol_visit(self, node):
        print self.spacing() + node.symbol, str(node.token.source)
        
    def general_nonterminal_visit(self, node):
        print self.spacing() + node.symbol
    

def walk_tree(node):
    visitor = DisplayTreeVisitor()
    walk_node(visitor, node)
    
def walk_node(visitor, node):
    visitor.dispatch(node)
    if isinstance(node, Nonterminal):
        visitor.depth += 1
        for c in node.children:
            walk_node(visitor, c)
        visitor.depth -= 1
   

## Build the parser function and the ToAST thingy.
try:
    regexs, rules, ToAST = parse_ebnf(grammar)
except ParseError,e:
    print e.nice_error_message()
    raise

parsef = make_parse_function(regexs, rules, eof=True)


def readfile(filename):
    """Reads a text file (using builtin os module stuff)"""
    contents = ""
    fp = os.open(filename, os.O_RDONLY, 0777)
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        contents += read
    os.close(fp)
    return contents

def fix_parse_tree(ast):
    toast = ToAST()
    return toast.transform(ast)

def parse_code(contents):
    try:
        raw_ast = parsef(contents)
        ast = fix_parse_tree(raw_ast)
        return ast
    except ParseError, e:
        print "at line", e.source_pos.lineno, ", column:", e.source_pos.columnno
        print e.nice_error_message()
    return None

def parse_file(filename):
    contents = readfile(filename)
    return parse_code(contents)
