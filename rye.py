#!/usr/bin/env python
import sys
import rparser
from pypy.rlib.objectmodel import we_are_translated

def entry_point(argv):
    
    if len(argv) < 2:
        #if not we_are_translated():
        #    ast = rparser.parse_file('test.rb')
        #    rparser.walk_tree(ast)
        print "Error: No script file specified"
        return 1
    else:
        filename = argv[1]
    ast = rparser.parse_file(filename)
    rparser.walk_tree(ast)
    return 0
    
def target(*args):
    return entry_point, None
    
    
if __name__ == "__main__":
    entry_point(sys.argv)
