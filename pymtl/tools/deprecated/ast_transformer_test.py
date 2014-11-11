#=========================================================================
# ast_tranformer_test.py
#=========================================================================

from ast_transformer import *
from ..ast_helpers   import get_method_ast, print_simple_ast, print_ast

#-------------------------------------------------------------------------
# AST Transformer Checker: Function Decorator
#-------------------------------------------------------------------------
def check_ast( ld, st ):

  def check_decorator( func ):
    tree, src = get_method_ast( func )
    print
    print
    print src

    #print_ast( tree )
    print_simple_ast( tree )

    #load, store = DetectLoadsAndStores().enter( tree )
    new_tree = SimplifiedAST().visit( tree )

    #print_ast( tree )
    print_simple_ast( new_tree )

    return func

  return check_decorator

#-------------------------------------------------------------------------
# Simple Assignments
#-------------------------------------------------------------------------

def test_assign():
  @check_ast( ['s.in_'], ['s.out.v'] )
  def assign( s ):
    s.out.v = s.in_

def test_assign_op():
  @check_ast( ['s.a.v', 's.b', 's.c'], ['s.out.v'] )
  def assign_op( s ):
    s.out.v = s.a.v + s.b + s.c

def test_assign_temp():
  @check_ast( ['s.in_', 'x'], ['x', 's.out.v'] )
  def assign_temp( s ):
    x = s.in_
    s.out.v = x

#-------------------------------------------------------------------------
# Bit Indexing
#-------------------------------------------------------------------------

def test_rd_bit_idx_const():
  @check_ast( ['s.a.v[?]', 's.b[?]'], ['s.out.v'] )
  def rd_bit_idx_const( s ):
    s.out.v = s.a.v[ 0 ] + s.b[ 1 ]

def test_rd_bit_idx_var():
  @check_ast( ['s.c', 's.a.v[?]', 's.d', 's.b[?]'], ['s.out.v'] )
  def rd_bit_idx_var( s ):
    s.out.v = s.a.v[ s.c ] & s.b[ s.d ]

def test_rd_bit_idx_slice_const():
  @check_ast( ['s.a.v[?]', 's.b[?]'], ['s.out.v'] )
  def rd_bit_idx_slice_const( s ):
    s.out.v = s.a.v[ 0:2 ] & s.b[ 4:8 ]

def test_rd_bit_idx_slice_var():
  @check_ast( ['s.s0', 's.s1', 's.a.v[?]'], ['s.out.v'] )
  def rd_bit_idx_slice_var( s ):
    s.out.v = s.a.v[ s.s0:s.s1 ]

def test_wr_bit_idx_const():
  @check_ast( ['s.in0', 's.in1'], ['s.out.v[?]'] )
  def wr_bit_idx_const( s ):
    s.out.v[ 0 ] = s.in0 + s.in1

def test_wr_bit_idx_var():
  @check_ast( ['s.c', 's.in0', 's.in1'], ['s.out.v[?]'] )
  def wr_bit_idx_var( s ):
    s.out.v[ s.c ] = s.in0 + s.in1

def test_wr_bit_idx_slice_const():
  @check_ast( ['s.in0[?]'], ['s.out.v[?]'] )
  def wr_bit_idx_slice_const( s ):
    s.out.v[ 0:1 ] = s.in0[ 3:4 ]

def test_wr_bit_idx_slice_var():
  @check_ast( ['s.s0', 's.s1', 's.a.v'], ['s.out.v[?]'] )
  def wr_bit_idx_slice_var( s ):
    s.out.v[ s.s0:s.s1 ] = s.a.v

#-------------------------------------------------------------------------
# List Indexing
#-------------------------------------------------------------------------

def test_rd_list_idx_const():
  @check_ast( ['s.a[?].v', 's.b[?].v'], ['s.out.v'] )
  def rd_list_idx_const( s ):
    s.out.v = s.a[ 0 ].v + s.b[ 1 ].v

def test_rd_list_idx_var():
  @check_ast( ['s.c', 's.a[?].v', 's.d', 's.b[?]'], ['s.out.v'] )
  def rd_list_idx_var( s ):
    s.out.v = s.a[ s.c ].v & s.b[ s.d ]

def test_rd_list_idx_slice_const():
  @check_ast( ['s.a[?].v', 's.b[?].v'], ['s.out.v'] )
  def rd_list_idx_slice_const( s ):
    s.out.v = s.a[ 0:2 ].v & s.b[ 4:8 ].v

def test_rd_list_idx_slice_var():
  @check_ast( ['s.s0', 's.s1', 's.a[?].v'], ['s.out.v'] )
  def rd_list_idx_slice_var( s ):
    s.out.v = s.a[ s.s0:s.s1 ].v

def test_wr_list_idx_const():
  @check_ast( ['s.in0', 's.in1'], ['s.out[?].v'] )
  def wr_list_idx_const( s ):
    s.out[ 0 ].v = s.in0 + s.in1

def test_wr_list_idx_var():
  @check_ast( ['s.c', 's.in0', 's.in1'], ['s.out[?].v'] )
  def wr_list_idx_var( s ):
    s.out[ s.c ].v = s.in0 + s.in1

def test_wr_list_idx_slice_const():
  @check_ast( ['s.in0[?]'], ['s.out[?].v'] )
  def wr_list_idx_slice_const( s ):
    s.out[ 0:1 ].v = s.in0[ 3:4 ]

def test_wr_list_idx_slice_var():
  @check_ast( ['s.s0', 's.s1', 's.a.v'], ['s.out[?].v'] )
  def wr_list_idx_slice_var( s ):
    s.out[ s.s0:s.s1 ].v = s.a.v

def test_wr_list_idx_op():
  @check_ast( [], [] )
  def wr_list_idx_slice_op( s ):
    s.out[i + s.s0].v = s.a.v

def test_wr_list_idx_slice_op():
  @check_ast( [], [] )
  def wr_list_idx_slice_op( s ):
    s.out[i:i + s.s0].v = s.a.v

#-------------------------------------------------------------------------
# If Statements
#-------------------------------------------------------------------------

def test_if_else():
  # TODO: prevent duplication?
  @check_ast( ['s.if0', 's.in0', 's.in1'], ['s.out.v', 's.out.v'] )
  def if_else( s ):
    if s.if0:
      s.out.v = s.in0
    else:
      s.out.v = s.in1

def test_if_elif_else():
  @check_ast( ['s.if0', 's.in0', 's.if1', 's.in1', 's.in2'],
              ['s.out.v']*3 )
  def if_elif_else( s ):
    if   s.if0:
      s.out.v = s.in0
    elif s.if1:
      s.out.v = s.in1
    else:
      s.out.v = s.in2

def test_if_elif_and():
  @check_ast( ['s.if0', 's.if1', 's.in0', 's.if0', 's.if2', 's.in1', 's.in2'],
              ['s.out.v']*3 )
  def if_elif_and( s ):
    if   s.if0 and s.if1:
      s.out.v = s.in0
    elif s.if0 and s.if2:
      s.out.v = s.in1
    else:
      s.out.v = s.in2

def test_if_elif_elif():
  @check_ast( ['s.if0', 's.in0', 's.if1', 's.in1', 's.if2', 's.in2'],
              ['s.out.v']*3 )
  def if_elif_else( s ):
    if   s.if0:
      s.out.v = s.in0
    elif s.if1:
      s.out.v = s.in1
    elif s.if2:
      s.out.v = s.in2

def test_nested_if():
  @check_ast( ['s.if0', 's.if1', 's.in0', 's.if2', 's.in1' ],
              ['s.out.v']*2 )
  def logic( s ):
    if s.if0:
      if   s.if1:
        s.out.v = s.in0
      elif s.if2:
        s.out.v = s.in1

def test_nested_else():
  @check_ast( ['s.if0', 's.in0', 's.if1', 's.in0', 's.if2', 's.in1' ],
              ['s.out.v']*3 )
  def logic( s ):
    if s.if0:
      s.out.v = s.in0
    else:
      if   s.if1:
        s.out.v = s.in0
      elif s.if2:
        s.out.v = s.in1

def test_nested_elif():
  @check_ast( ['s.if0', 's.in0', 's.if3', 's.if1', 's.in0', 's.if2', 's.in1' ],
              ['s.out.v']*3 )
  def logic( s ):
    if s.if0:
      s.out.v = s.in0
    elif s.if3:
      if   s.if1:
        s.out.v = s.in0
      elif s.if2:
        s.out.v = s.in1

#-------------------------------------------------------------------------
# For Loops
#-------------------------------------------------------------------------
def test_for_loop_const():
  @check_ast( [], [] )
  def logic( s ):
    for i in range( 10 ):
      a[i] = i

#-------------------------------------------------------------------------
# While Loops
#-------------------------------------------------------------------------
# TODO

