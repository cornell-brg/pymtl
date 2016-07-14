#=======================================================================
# Adder_multi_bw_test.py
#=======================================================================
# These are testing a combinational adder

from pymtl import *

import os
import random
import pytest

def _sim_setup( model ):
  m = model
  m.elaborate()
  sim = SimulationTool( m )
  sim.reset()
  return m, sim

class Adder_16( SystemCModel ):  
  def __init__( s ):
    s.op_a  = InPort ( 16 )
    s.op_b  = InPort ( 16 )
    s.res_c = OutPort( 16 )
    
    s.set_ports({
      'a' : s.op_a,
      'b' : s.op_b,
      'c' : s.res_c,
    })
    
class Adder_40( SystemCModel ):
  def __init__( s ):
    s.op_a  = InPort ( 40 )
    s.op_b  = InPort ( 40 )
    s.res_c = OutPort( 40 )

    s.set_ports({
      'a' : s.op_a,
      'b' : s.op_b,
      'c' : s.res_c,
    })
    
class Adder_100( SystemCModel ):    
  def __init__( s ):
    s.op_a  = InPort ( 100 )
    s.op_b  = InPort ( 100 )
    s.res_c = OutPort( 100 )

    s.set_ports({
      'a' : s.op_a,
      'b' : s.op_b,
      'c' : s.res_c,
    })

test_16  = [ (0x1234, 0x2143), (0xffe0, 0x0001) ]
test_40  = [ (0x1234567890, 0x2109876543), (0xffe0, 0x0001) ]
test_100 = [ (0x1234567890123456789012345, 0x2109876543210987654321098), (0xffe0, 0x0001) ]


# TODO This is hacky, since I have to register modules earlier
# in systemc world.

@pytest.mark.parametrize( "a,b", test_16)
def test_Adder_16( a, b ):
  m, sim = _sim_setup( Adder_16() )
  
  for i in xrange(10):
    m.op_a.value = a + i
    m.op_b.value = b + i
  
    sim.eval_combinational()
  
    sim.print_line_trace()
    
    assert m.res_c == a + b + i + i
  
  m.destroy()

@pytest.mark.parametrize( "a,b", test_40)
def test_Adder_40( a, b ):
  m, sim = _sim_setup( Adder_40() )
  
  for i in xrange(10):
    m.op_a.value = a + i
    m.op_b.value = b + i
  
    sim.eval_combinational()
  
    sim.print_line_trace()
    
    assert m.res_c == a + b + i + i
  m.destroy()

@pytest.mark.parametrize( "a,b", test_100)
def test_Adder_100( a, b ):
  m, sim = _sim_setup( Adder_100() )
  
  for i in xrange(10):
    m.op_a.value = a + i
    m.op_b.value = b + i
  
    sim.eval_combinational()
  
    sim.print_line_trace()
    
    assert m.res_c == a + b + i + i
  m.destroy()
  
@pytest.mark.parametrize( "a,b", test_16)
def test_Adder_16_2( a, b ):
  m, sim = _sim_setup( Adder_16() )
  
  for i in xrange(10):
    m.op_a.value = a + i
    m.op_b.value = b + i
  
    sim.eval_combinational()
  
    sim.print_line_trace()
    
    assert m.res_c == a + b + i + i
  m.destroy()
