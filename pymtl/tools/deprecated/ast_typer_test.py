#=========================================================================
# ast_tranformer_test.py
#=========================================================================

from ast_typer         import TypeAST
from ..ast_helpers     import get_method_ast, print_simple_ast, print_ast
from ...datatypes.Bits import Bits

class M( object ):
  def __init__( self, *args ):
    for x in args:
      setattr( self, x, Bits(4) )
  def lists( self, *args ):
    for x in args:
      setattr( self, x, [Bits(4)] )
    return self

#-------------------------------------------------------------------------
# check_ast
#-------------------------------------------------------------------------
# Decorator for testing TypeAST.
def check_ast( model ):

  def check_decorator( func ):
    tree, src = get_method_ast( func )
    print()
    print()
    print( src )

    #print_simple_ast( tree )

    new_tree = TypeAST( model, func ).visit( tree )

    print_simple_ast( new_tree )

    return func

  return check_decorator

#-------------------------------------------------------------------------
# Simple Assignments
#-------------------------------------------------------------------------

def test_assign():
  s = M( 'out', 'in_' )
  @check_ast( s )
  def assign():
    s.out.v = s.in_

def test_assign_op():
  s = M( 'out', 'a', 'b', 'c' )
  @check_ast( s )
  def assign_op():
    s.out.v = s.a.v + s.b + s.c

def test_assign_temp():
  s = M( 'in_', 'out' )
  @check_ast( s )
  def assign_temp():
    x = s.in_
    s.out.v = x

#-------------------------------------------------------------------------
# Bit Indexing
#-------------------------------------------------------------------------

def test_rd_bit_idx_const():
  s = M( 'out', 'a', 'b' )
  @check_ast( s )
  def rd_bit_idx_const():
    s.out.v = s.a.v[ 0 ] + s.b[ 1 ]

def test_rd_bit_idx_var():
  s = M( 'out', 'a', 'b', 'c', 'd' )
  @check_ast( s )
  def rd_bit_idx_var():
    s.out.v = s.a.v[ s.c ] & s.b[ s.d ]

def test_rd_bit_idx_slice_const():
  s = M( 'out', 'a', 'b' )
  @check_ast( s )
  def rd_bit_idx_slice_const():
    s.out.v = s.a.v[ 0:2 ] & s.b[ 4:8 ]

def test_rd_bit_idx_slice_var():
  s = M( 'out', 'a', 's0', 's1' )
  @check_ast( s )
  def rd_bit_idx_slice_var():
    s.out.v = s.a.v[ s.s0:s.s1 ]

def test_wr_bit_idx_const():
  s = M( 'out', 'in0', 'in1' )
  @check_ast( s )
  def wr_bit_idx_const():
    s.out.v[ 0 ] = s.in0 + s.in1

def test_wr_bit_idx_var():
  s = M( 'out', 'c', 'in0', 'in1' )
  @check_ast( s )
  def wr_bit_idx_var():
    s.out.v[ s.c ] = s.in0 + s.in1

def test_wr_bit_idx_slice_const():
  s = M( 'out', 'in0' )
  @check_ast( s )
  def wr_bit_idx_slice_const():
    s.out.v[ 0:1 ] = s.in0[ 3:4 ]

def test_wr_bit_idx_slice_var():
  s = M( 'out', 's0', 's1', 'a' )
  @check_ast( s )
  def wr_bit_idx_slice_var():
    s.out.v[ s.s0:s.s1 ] = s.a.v

#-------------------------------------------------------------------------
# List Indexing
#-------------------------------------------------------------------------

def test_rd_list_idx_const():
  s = M( 'out' ).lists( 'a', 'b' )
  @check_ast( s )
  def rd_list_idx_const():
    s.out.v = s.a[ 0 ].v + s.b[ 1 ].v

def test_rd_list_idx_var():
  s = M( 'out', 'c', 'd'  ).lists( 'a', 'b' )
  @check_ast( s )
  def rd_list_idx_var():
    s.out.v = s.a[ s.c ].v & s.b[ s.d ]

def test_rd_list_idx_slice_const():
  s = M( 'out' ).lists( 'a', 'b' )
  @check_ast( s )
  def rd_list_idx_slice_const():
    s.out.v = s.a[ 0:2 ].v & s.b[ 4:8 ].v

def test_rd_list_idx_slice_var():
  s = M( 'out', 's0', 's1' ).lists( 'a' )
  @check_ast( s )
  def rd_list_idx_slice_var():
    s.out.v = s.a[ s.s0:s.s1 ].v

def test_wr_list_idx_const():
  s = M( 'in0', 'in1' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_const():
    s.out[ 0 ].v = s.in0 + s.in1

def test_wr_list_idx_var():
  s = M( 'c', 'in0', 'in1' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_var():
    s.out[ s.c ].v = s.in0 + s.in1

def test_wr_list_idx_slice_const():
  s = M( 'in0' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_slice_const():
    s.out[ 0:1 ].v = s.in0[ 3:4 ]

def test_wr_list_idx_slice_var():
  s = M( 's0', 's1', 'a' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_slice_var():
    s.out[ s.s0:s.s1 ].v = s.a.v

def test_wr_list_idx_op():
  s = M( 's0', 'a' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_slice_op():
    s.out[i + s.s0].v = s.a.v

def test_wr_list_idx_slice_op():
  s = M( 's0', 'a' ).lists( 'out' )
  @check_ast( s )
  def wr_list_idx_slice_op():
    s.out[i:i + s.s0].v = s.a.v

#-------------------------------------------------------------------------
# If Statements
#-------------------------------------------------------------------------

def test_if_else():
  s = M( 'if0', 'out', 'in0', 'in1' )
  @check_ast( s )
  def if_else():
    if s.if0:
      s.out.v = s.in0
    else:
      s.out.v = s.in1

def test_if_elif_else():
  s = M( 'if0', 'if1', 'out', 'in0', 'in1', 'in2' )
  @check_ast( s )
  def if_elif_else():
    if   s.if0:
      s.out.v = s.in0
    elif s.if1:
      s.out.v = s.in1
    else:
      s.out.v = s.in2

def test_if_elif_and():
  s = M( 'if0', 'if1', 'if2', 'out', 'in0', 'in1', 'in2' )
  @check_ast( s )
  def if_elif_and():
    if   s.if0 and s.if1:
      s.out.v = s.in0
    elif s.if0 and s.if2:
      s.out.v = s.in1
    else:
      s.out.v = s.in2

def test_if_elif_elif():
  s = M( 'if0', 'if1', 'if2', 'out', 'in0', 'in1', 'in2' )
  @check_ast( s )
  def if_elif_else():
    if   s.if0:
      s.out.v = s.in0
    elif s.if1:
      s.out.v = s.in1
    elif s.if2:
      s.out.v = s.in2

def test_nested_if():
  s = M( 'if0', 'if1', 'if2', 'out', 'in0', 'in1' )
  @check_ast( s )
  def logic():
    if s.if0:
      if   s.if1:
        s.out.v = s.in0
      elif s.if2:
        s.out.v = s.in1

def test_nested_else():
  s = M( 'if0', 'if1', 'if2', 'out', 'in0', 'in1' )
  @check_ast( s )
  def logic():
    if s.if0:
      s.out.v = s.in0
    else:
      if   s.if1:
        s.out.v = s.in0
      elif s.if2:
        s.out.v = s.in1

def test_nested_elif():
  s = M( 'if0', 'if1', 'if2', 'if3', 'out', 'in0', 'in1' )
  @check_ast( s )
  def logic():
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
  s = M()
  a = [None]
  # TODO: fails if a is empty, how to handle this?
  @check_ast( s )
  def logic():
    for i in range( 10 ):
      a[i] = i

##-------------------------------------------------------------------------
## While Loops
##-------------------------------------------------------------------------
## TODO
#
