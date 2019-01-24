#=======================================================================
# dynamic_ast_test.py
#=======================================================================
# Tests for dynamic AST support of PyMTL.

import pytest

from ast import *
from pymtl import *
from random import randrange

from SimulationTool_seq_test import setup_sim, local_setup_sim

#-----------------------------------------------------------------------
# DynamicAST
#-----------------------------------------------------------------------

def test_DynamicAST( setup_sim ):

  class DynamicAST( Model ):
    
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

  m, sim = setup_sim( DynamicAST() )

  for i in range( 10 ):
    k = Bits( 10, randrange( 0, 2**9 ) )
    m.in_.value = k
    sim.cycle()
    assert m.out == ( k + 6 )
