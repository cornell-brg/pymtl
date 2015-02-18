#=========================================================================
# ast_visitor_test.py
#=========================================================================
# Tests for Python AST Visitors.

import pytest

from ast_visitor   import *
from ..ast_helpers import get_method_ast, print_simple_ast
from pymtl         import InPort, OutPort, Wire

#-------------------------------------------------------------------------
# AST Visitor Checker: Function Decorator
#-------------------------------------------------------------------------
# This decorator takes two parameters: a list of expected signals detected
# as loads by the visitor, and a list of expected signals detected as
# stores by the visitor.  Assertions verify that the expected signals
# match the actual signals detected.
# TODO: the order in which you name the signals in each list matters,
#       should fix this later.
def check_ast( ld, st ):

  def check_decorator( func ):
    tree, src = get_method_ast( func )

    print()
    #import debug_utils
    #debug_utils.print_ast( tree )

    load, store = DetectLoadsAndStores().enter( tree )
    print( "LOADS ", load,  "want:", ld )
    print( "STORES", store, "want:", st )
    assert ld == load
    assert st == store

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
# AST Visitor Checker: Function Decorator
#-------------------------------------------------------------------------
def next( func ):
  tree, src = get_method_ast( func )
  #print_simple_ast( tree )
  DetectMissingValueNext( func, 'next' ).visit( tree )

def value( func ):
  tree, src = get_method_ast( func )
  #print_simple_ast( tree )
  DetectMissingValueNext( func, 'value' ).visit( tree )

class Temp( object ):
  def __init__( s ):
    s.i0, s.i1, s.i2  = InPort [3](1)
    s.o0, s.o1, s.o2  = OutPort[3](1)
    s.out             = OutPort[3](1)

def test_noerror_next():
  s = Temp()
  @next
  def logic():
    s.i0.next = 5

def test_error_next():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.i0 = 5

def test_noerror_value():
  s = Temp()
  @value
  def logic():
    s.i0.next = 5

def test_error_value():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.i0 = 5

def test_noerror_tuple():
  s = Temp()
  @next
  def logic():
    s.o0.next,s.o1.next = 5, 6
  @value
  def logic():
    s.o0.value,s.o1.value = 5, 6
  @next
  def logic():
    s.o0.next,s.o1.next,s.o2.next = 5, 6, 7
  @next
  def logic():
    s.o0.value,s.o1.value,s.o2.value = 5, 6, 7

def test_error_tuple():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.o0, s.o1.next = 5, 6
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.o0, s.o1.value = 5, 6
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.o0, s.o1 = 5, 6
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.o0.value, s.o1 = 5, 6
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.o0.next, s.o1, s.o2.next = 5, 6, 7
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.o0.value, s.o1.value, s.o2 = 5, 6, 7

def test_noerror_list():
  s = Temp()
  @next
  def logic():
    [s.o0.next,s.o1.next] = 5, 6
  @value
  def logic():
    [s.o0.value,s.o1.value] = 5, 6

def test_error_list():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      [s.o0,s.o1.next] = 5, 6
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      [s.o0.value,s.o1] = 5, 6

def test_noerror_tuple_packs():
  s = Temp()
  @next
  def logic():
    s.o0.next, (s.o1.next, s.o2.next) = 5, (6, 7)
  @value
  def logic():
    (s.o0.value, s.o1.value), s.o2.value = (5, 6), 7

def test_error_tuple_packs():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.o0.next, (s.o1.next, s.o2) = 5, (6, 7)
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      (s.o0, s.o1.value), s.o2.value = (5, 6), 7

def test_noerror_list_packs():
  s = Temp()
  @next
  def logic():
    s.o0.next, [s.o1.next, s.o2.next] = 5, (6, 7)
  @value
  def logic():
    [s.o0.value, s.o1.value], s.o2.value = (5, 6), 7

def test_error_list_packs():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.o0.next, [s.o1.next, s.o2] = 5, (6, 7)
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      [s.o0, s.o1.value], s.o2.value = (5, 6), 7

def test_noerror_mixed_packs():
  s = Temp()
  @next
  def logic():
    [s.o0.next], (s.o1.next, s.o2.next) = [5], (6, 7)
  @value
  def logic():
    [s.o0.value, s.o1.value], (s.o2.value,) = (5, 6), [7]
  @next
  def logic():
    [s.o0.next], ([s.o1.next], s.o2.next) = [5], ([6], 7)
  @value
  def logic():
    [s.o0.value, (s.o1.value)], (s.o2.value,) = (5, 6), [7]

def test_error_mixed_packs():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      [s.o0], (s.o1.next, s.o2.next) = [5], (6, 7)
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      [s.o0.value, s.o1], (s.o2,) = (5, 6), [7]
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      [s.o0.next], ([s.o1], s.o2.next) = [5], ([6], 7)
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      [s.o0.value, (s.o1)], (s.o2.value,) = (5, 6), [7]

def test_noerror_subscript():
  s = Temp()
  @next
  def logic():
    s.out[0].next = 5
  @value
  def logic():
    s.out[0].value = 5

def test_error_subscript():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.out[0] = 5
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.out[0] = 5

def test_noerror_subscript_tuple():
  s = Temp()
  @next
  def logic():
    s.out[0].next, s.out[1].next = 5,6
  @value
  def logic():
    s.out[0].value, s.out[1].value = 5,6

def test_error_subscript():
  s = Temp()
  with pytest.raises( PyMTLError ):
    @next
    def logic():
      s.out[0].next, s.out[1] = 5,6
  with pytest.raises( PyMTLError ):
    @value
    def logic():
      s.out[0], s.out[1].value = 5,6
