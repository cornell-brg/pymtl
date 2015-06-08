#=======================================================================
# verilog_test.py
#=======================================================================

from pymtl import *

import os
import random
import pytest

def _sim_setup( model, all_verilog, dump_vcd='' ):
  model.vcd_file = dump_vcd
  m = TranslationTool( model ) if all_verilog else model
  m.elaborate()
  sim = SimulationTool( m )
  sim.reset()
  return m, sim

#-----------------------------------------------------------------------
# test_Reg
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,all_verilog",
 [(4,True),(128,False)]
)
def test_Reg( nbits, all_verilog ):

  class vc_Reg( VerilogModel ):
    modulename = 'vc_Reg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'vc-regs.v' )

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

  m, sim = _sim_setup( vc_Reg(nbits), all_verilog )
  for i in range( 10 ):
    m.in_.value = i
    sim.cycle()
    sim.print_line_trace()
    assert m.out == i

#-----------------------------------------------------------------------
# test_ResetReg
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(4,0,True), (4,0,False), (128,8,True), (128,8,False)]
)
def test_ResetReg( nbits, rst, all_verilog ):

  class vc_ResetReg( VerilogModel ):
    modulename = 'vc_ResetReg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'vc-regs.v' )

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

  m, sim = _sim_setup( vc_ResetReg(nbits,rst), all_verilog )
  assert m.out == rst
  for i in range( 10 ):
    m.in_.value = i
    sim.cycle()
    sim.print_line_trace()
    assert m.out == i

#-----------------------------------------------------------------------
# test_EnResetReg
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(4,0,True), (4,0,False), (128,8,True), (128,8,False)]
)
def test_EnResetReg( nbits, rst, all_verilog ):

  class vc_EnResetReg( VerilogModel ):
    modulename = 'vc_EnResetReg'
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'vc-regs.v' )

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

  m, sim = _sim_setup( vc_EnResetReg(nbits,rst), all_verilog )
  last = rst
  assert m.out == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.in_.value = i
    m.en .value = en
    sim.cycle()
    sim.print_line_trace()
    assert m.out == last

#-----------------------------------------------------------------------
# test_auto_Reg
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,all_verilog",
 [(4,True),(128,False)]
)
def test_auto_Reg( nbits, all_verilog ):

  class RegVRTL( VerilogModel ):
    def __init__( s, p_nbits ):
      s.d = InPort ( p_nbits )
      s.q = OutPort( p_nbits )

    def line_trace( s ):
      return '{q} {d}'.format( **s.__dict__ )

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  print
  m, sim = _sim_setup( RegVRTL(nbits), all_verilog )
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

@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(4,0,True), (4,0,False), (128,8,True), (128,8,False)]
)
def test_auto_EnResetReg( nbits, rst, all_verilog ):

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( EnResetRegVRTL(nbits,rst), all_verilog )
  last = rst
  assert m.q == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    sim.print_line_trace()
    assert m.q == last

#-----------------------------------------------------------------------
# test_auto_EnResetReg_BitStruct
#-----------------------------------------------------------------------
class verilog_test_BitStruct( BitStructDefinition ):
  def __init__( s, nbits ):
    s.src  = BitField( nbits )
    s.dest = BitField( nbits )

@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(4,0,True), (4,0,False), (128,8,True), (128,8,False)]
)
def test_auto_EnResetReg_BitStruct( nbits, rst, all_verilog ):

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  MsgType= verilog_test_BitStruct( nbits )
  m, sim = _sim_setup( EnResetRegVRTL(MsgType,rst), all_verilog )
  last = rst
  assert m.q == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    sim.print_line_trace()
    assert m.q == last
    assert concat(m.q.src, m.q.dest) == last

#-----------------------------------------------------------------------
# test_wrapped_VerilogModel
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(4,0,True), (4,0,False), (128,8,True), (128,8,False)]
)
def test_wrapped_VerilogModel( nbits, rst, all_verilog ):

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

  m, sim = _sim_setup( ModelWrapper(nbits,rst), all_verilog )
  last = rst
  assert m.q == rst

  for i in range( 10 ):
    en   = random.randint(0,1)
    last = i if en else last

    m.d  .value = i
    m.en .value = en
    sim.cycle()
    sim.print_line_trace()
    assert m.q == last

#-----------------------------------------------------------------------
# test_chained_VerilogModel
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(6,2,True), (6,2,False),]
)
def test_chained_VerilogModel( dump_vcd, nbits, rst, all_verilog ):

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
      return '{d} {q}'.format( **s.__dict__ )

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( ModelChainer(nbits,rst), all_verilog, dump_vcd )
  assert m.q == rst

  import collections
  pipeline = collections.deque( maxlen=3 )
  pipeline.extend( [rst]*3 )

  # Super hacky line tracing!
  #import types
  #m.line_trace = types.MethodType(
  #    lambda x: '{} {} {}'.format( x.d, x.q, pipeline ), m
  #)

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

#-----------------------------------------------------------------------
# test_chained_VerilogModel
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "nbits,rst,all_verilog",
  [(6,2,True), (6,2,False),]
)
def test_chained_param_VerilogModel( dump_vcd, nbits, rst, all_verilog ):

  class EnResetRegParamVRTL( VerilogModel ):
    def __init__( s, p_nbits, p_reset_value=0, p_id=0 ):
      s.en  = InPort ( 1 )
      s.d   = InPort ( p_nbits )
      s.q   = OutPort( p_nbits )

  class ModelChainer( Model ):
    def __init__( s, nbits, rst=0 ):
      s.en  = InPort ( 1 )
      s.d   = InPort ( nbits )
      s.q   = OutPort( nbits )

      s.mod = m = [EnResetRegParamVRTL( nbits, rst, x ) for x in range(3)]

      for x in s.mod:
        s.connect( s.en, x.en )

      s.connect_dict({
        s.d    : m[0].d,
        m[0].q : m[1].d,
        m[1].q : m[2].d,
        m[2].q : s.q,
      })

    def line_trace( s ):
      return '{d} {q}'.format( **s.__dict__ )

  #---------------------------------------------------------------------
  # test
  #---------------------------------------------------------------------

  m, sim = _sim_setup( ModelChainer(nbits,rst), all_verilog, dump_vcd )
  assert m.q == rst

  import collections
  pipeline = collections.deque( maxlen=3 )
  pipeline.extend( [rst]*3 )

  # Super hacky line tracing!
  #import types
  #m.line_trace = types.MethodType(
  #    lambda x: '{} {} {}'.format( x.d, x.q, pipeline ), m
  #)

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

#-----------------------------------------------------------------------
# test_lint_warning
#-----------------------------------------------------------------------
@pytest.mark.parametrize( "all_verilog", (True,False) )
def test_lint_warning( dump_vcd, all_verilog ):

  class AdderLintVRTL( VerilogModel ):
    def __init__( s, nbits ):
      s.in0  = InPort  ( nbits )
      s.in1  = InPort  ( nbits )
      s.cin  = InPort  ( 1     )
      s.out  = OutPort ( nbits )
      s.cout = OutPort ( 1     )
    def line_trace( s ):
      return '{in0}+{in1}+{cin} = {cout},{out}'.format( **s.__dict__ )

  # Linter warnings should cause Verilation to fail!

  nbits = 8
  with pytest.raises( Exception ):
    m, sim = _sim_setup( AdderLintVRTL(nbits), all_verilog, dump_vcd )

  # Not necessary, Lint warning

  #randint = random.randint
  #def do_add( in0, in1, cin ):
  #  in0  = Bits( nbits, in0 )
  #  in1  = Bits( nbits, in1 )
  #  cin  = Bits( 1,     cin )

  #  m.in0.value, m.in1.value, m.cin.value = in0, in1, cin
  #  sim.cycle()
  #  sim.print_line_trace()

  #  # Check Results
  #  temp = zext(in0,nbits+1) + zext(in1,nbits+1) + cin
  #  assert m.out  == temp[0:nbits]
  #  assert m.cout == temp[nbits]

  ## test random values
  #print
  #for i in range( 10 ):
  #  do_add( randint(0,2**nbits-1), randint(0,2**nbits-1), randint(0,1) )

  ## test max
  #do_add( 2**nbits-1, 2**nbits-1, 1 )

