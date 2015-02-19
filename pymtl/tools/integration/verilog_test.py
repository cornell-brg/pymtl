#=======================================================================
# verilog_test.py
#=======================================================================

from pymtl import *

import os
import random
import pytest

def _sim_setup( model ):
  m = TranslationTool( model )
  m.elaborate()
  sim = SimulationTool( m )
  sim.reset()
  return m, sim

#-----------------------------------------------------------------------
# test_Reg
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits", (4,128))
def test_Reg( nbits ):

  class vc_Reg( VerilogModel ):
    module   = 'vc_Reg'
    filename = os.path.join( os.path.dirname(__file__), 'test/vc-regs.v' )

    def __init__( s, nbits ):
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.params = {
        'p_nbits' : nbits,
      }

      s.connections = {
        s.clk   : 'clk',
        s.in_   : 'd',
        s.out   : 'q',
      }

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( vc_Reg(nbits) )
  for i in range( 10 ):
    m.in_.value = i
    sim.cycle()
    assert m.out == i

#-----------------------------------------------------------------------
# test_ResetReg
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits,rst", [(4,0),(128,8)])
def test_ResetReg( nbits, rst ):

  class vc_ResetReg( VerilogModel ):
    module   = 'vc_ResetReg'
    filename = os.path.join( os.path.dirname(__file__), 'test/vc-regs.v' )

    def __init__( s, nbits, reset_value=0 ):
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.params = {
        'p_nbits'       : nbits,
        'p_reset_value' : reset_value,
      }

      s.connections = {
        s.clk   : 'clk',
        s.reset : 'reset',
        s.in_   : 'd',
        s.out   : 'q',
      }

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( vc_ResetReg(nbits,rst) )
  assert m.out == rst
  for i in range( 10 ):
    m.in_.value = i
    sim.cycle()
    assert m.out == i

#-----------------------------------------------------------------------
# test_EnResetReg
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits,rst", [(4,0),(128,8)])
def test_EnResetReg( nbits, rst ):

  class vc_EnResetReg( VerilogModel ):
    module   = 'vc_EnResetReg'
    filename = os.path.join( os.path.dirname(__file__), 'test/vc-regs.v' )

    def __init__( s, nbits, reset_value=0 ):
      s.en  = InPort ( 1 )
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.params = {
        'p_nbits'       : nbits,
        'p_reset_value' : reset_value,
      }

      s.connections = {
        s.clk   : 'clk',
        s.reset : 'reset',
        s.en    : 'en',
        s.in_   : 'd',
        s.out   : 'q',
      }

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( vc_EnResetReg(nbits,rst) )
  last = rst
  assert m.out == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.in_.value = i
    m.en .value = en
    sim.cycle()
    assert m.out == last
