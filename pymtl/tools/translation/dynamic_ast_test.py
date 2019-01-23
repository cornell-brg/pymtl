#=======================================================================
# dynamic_ast_test.py
#=======================================================================
# This is the test case that verifies the dynamic AST support of PyMTL.
#
# Author : Peitian Pan
# Date   : Jan 23, 2019

import pytest
import random

from ast import *
from pymtl import *
from pclib.test import run_test_vector_sim
from verilator_sim import TranslationTool

pytestmark = requires_verilator

class DynamicAST(Model):
    def __init__( s ):
        s.in_ = InPort(10)
        s.out = OutPort(10)

        # Testing free vars in the closure
        s.self_param = 1
        closure_param = 2

        # @s.posedge_clk
        # def dynamic_block():
        #   s.out.next = s.in_ + s.self_param + closure_param + Bits( 10, 3 )

        # Dynamically generate AST
        tree = Module( body = [
          FunctionDef( name = 'dynamic_block', args = arguments( args = [], defaults = [] ),
            body = [
              Assign(
                targets = [
                  Attribute( value = Attribute( value = Name( id = 's',\
                    ctx = Load() ), attr = 'out', ctx = Load() ), attr =\
                    'next', ctx = Store() )
                ],
                value = BinOp(
                  left = BinOp(
                    left = BinOp(
                      left = Attribute( value = Name( id = 's', ctx =\
                        Load() ), attr = 'in_', ctx = Load() ),
                      op = Add(),
                      right = Attribute( value = Name( id = 's', ctx =\
                        Load() ), attr = 'self_param', ctx = Load() )
                    ),
                    op = Add(),
                    right = Name( id = 'closure_param', ctx = Load() )
                  ),
                  op = Add(),
                  right = Call(
                    func = Name( id = 'Bits', ctx = Load() ),
                    args = [ Num( n = 10 ), Num( n = 3 ) ],
                    keywords = [],
                    starargs = None,
                    kwargs = None
                  )
                )
              )
            ],
            decorator_list = [
              Attribute( value = Name( id = 's', ctx = Load() ), attr =\
                'posedge_clk', ctx = Load() )
            ],
            returns = None
          )
        ] )

        # Fix missing line numbers, etc
        tree = fix_missing_locations(tree)

        # Specifiy the union of globals() and locals() so the free
        # variables in the closure can be captured.
        exec(compile(tree, filename='<dynamic_ast>', mode='exec')) in globals().update( locals() )

        # As with #175, the user needs to supplement the dynamic AST to
        # the .ast field of the generated function object. 
        dynamic_block.ast = tree

def test_dynamic_ast_simulation():
    m = DynamicAST()

    test_vector_table = [('in_', 'out*')]
    last_result = '?'
    for _ in xrange( 10 ):
        in_ = Bits( 10, random.randint( 0, 100 ) )
        test_vector_table.append( [ in_, last_result ] )
        last_result = Bits( 10, in_ + 6 )

    run_test_vector_sim( m, test_vector_table )

def test_dynamic_ast_translation():
    m = DynamicAST()

    tool = TranslationTool(m)
