#=======================================================================
# verilog_test.py
#=======================================================================

from pymtl import *

import os
import random
import pytest

def _sim_setup( model, dump_vcd=False ):
  model.vcd_file = dump_vcd
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
    modulename = 'vc_Reg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'verilog', 'vc-regs.v' )

    def __init__( s, nbits ):
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.set_params({
        'p_nbits' : nbits,
      })

      s.set_ports({
        'clk' : s.clk,
        'd'   : s.in_,
        'q'   : s.out,
      })

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
    modulename = 'vc_ResetReg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'verilog', 'vc-regs.v' )

    def __init__( s, nbits, reset_value=0 ):
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.set_params({
        'p_nbits'       : nbits,
        'p_reset_value' : reset_value,
      })

      s.set_ports({
        'clk'   : s.clk,
        'reset' : s.reset,
        'd'     : s.in_,
        'q'     : s.out,
      })

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
    modulename = 'vc_EnResetReg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'verilog', 'vc-regs.v' )

    def __init__( s, nbits, reset_value=0 ):
      s.en  = InPort ( 1 )
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.set_params({
        'p_nbits'       : nbits,
        'p_reset_value' : reset_value,
      })

      s.set_ports({
        'clk'   : s.clk,
        'reset' : s.reset,
        'en'    : s.en,
        'd'     : s.in_,
        'q'     : s.out,
      })

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

#-----------------------------------------------------------------------
# test_EnResetReg
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits,rst", [(4,0),(128,8)])
def test_EnResetReg( nbits, rst ):

  class vc_EnResetReg( VerilogModel ):
    modulename = 'vc_EnResetReg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'verilog', 'vc-regs.v' )

    def __init__( s, nbits, reset_value=0 ):
      s.en  = InPort ( 1 )
      s.in_ = InPort ( nbits )
      s.out = OutPort( nbits )

      s.set_params({
        'p_nbits'       : nbits,
        'p_reset_value' : reset_value,
      })

      s.set_ports({
        'clk'   : s.clk,
        'reset' : s.reset,
        'en'    : s.en,
        'd'     : s.in_,
        'q'     : s.out,
      })

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

#-----------------------------------------------------------------------
# test_auto_Reg
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits", (4,128))
def test_auto_Reg( nbits ):

  class RegVRTL( VerilogModel ):
    def __init__( s, p_nbits ):
      s.d = InPort ( p_nbits )
      s.q = OutPort( p_nbits )

    #def line_trace():
    #  return '{q} {d}'.format( **dir(s) )

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( RegVRTL(nbits) )
  for i in range( 10 ):
    m.d.value = i
    sim.cycle()
    sim.print_line_trace()
    assert m.q == i

#-----------------------------------------------------------------------
# test_auto_EnResetReg
#-----------------------------------------------------------------------
class EnResetRegVRTL( VerilogModel ):
  def __init__( s, p_nbits, p_reset_value=0 ):
    s.en  = InPort ( 1 )
    s.d   = InPort ( p_nbits )
    s.q   = OutPort( p_nbits )

@pytest.mark.parametrize("nbits,rst", [(4,0),(128,8)])
def test_auto_EnResetReg( nbits, rst ):

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( EnResetRegVRTL(nbits,rst) )
  last = rst
  assert m.q == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    assert m.q == last

#-----------------------------------------------------------------------
# test_wrapped_VerilogModel
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits,rst", [(4,0),(128,8)])
def test_wrapped_VerilogModel( nbits, rst ):

  class ModelWrapper( Model ):
    def __init__( s, nbits, rst=0 ):
      s.en  = InPort ( 1 )
      s.d   = InPort ( nbits )
      s.q   = OutPort( nbits )

      s.mod = EnResetRegVRTL( nbits, rst )

      s.connect_dict({
        s.en : s.mod.en,
        s.d  : s.mod.d,
        s.q  : s.mod.q,
      })

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( ModelWrapper(nbits,rst) )
  last = rst
  assert m.q == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    assert m.q == last

#-----------------------------------------------------------------------
# test_chained_VerilogModel
#-----------------------------------------------------------------------
@pytest.mark.parametrize("nbits,rst", [(6,0),(128,8)])
def test_chained_VerilogModel( dump_vcd, nbits, rst ):

  class ModelChainer( Model ):
    def __init__( s, nbits, rst=0 ):
      s.en  = InPort ( 1 )
      s.d   = InPort ( nbits )
      s.q   = OutPort( nbits )

      s.mod = m = EnResetRegVRTL[3]( nbits, rst )

      for x in s.mod:
        s.connect( s.en, x.en )

      s.connect_dict({
        s.d    : m[0].d,
        m[0].q : m[1].d,
        m[1].q : m[2].d,
        m[2].q : s.q,
      })

    def line_trace( s ):
      return '{d} {q}'.format( **dir(s) )

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( ModelChainer(nbits,rst), dump_vcd )
  last = rst
  assert m.q == rst

  import collections
  pipeline = collections.deque( maxlen=3 )
  pipeline.extend( [rst]*3 )

  # Super hacky line tracing!
  Model.line_trace = lambda m: '{} {} {}'.format( m.d, m.q, pipeline )

  print()
  for i in range( 20 ):
    en  = random.randint(0,1)
    if en:
      pipeline.appendleft( i )

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    sim.print_line_trace()
    assert m.q == pipeline[-1]

