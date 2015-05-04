#=======================================================================
# verilog_bug_test.py
#=======================================================================

import pytest

from pymtl      import *
from exceptions import VerilatorCompileError

pytestmark = requires_verilator

#-----------------------------------------------------------------------
# Point BitStruct
#-----------------------------------------------------------------------
class Point( BitStructDefinition ):
  def __init__( s ):
    s.x = BitField(4)
    s.y = BitField(4)

#-----------------------------------------------------------------------
# setup_sim
#-----------------------------------------------------------------------
def setup_sim( model ):
  model = TranslationTool( model )
  model.elaborate()
  sim = SimulationTool( model )
  return model, sim

#-----------------------------------------------------------------------
# test_bitstruct_tick_reg
#-----------------------------------------------------------------------
@pytest.mark.parametrize(
  'config', ['Tick','TickFields','Comb','CombFields']
)
def test_bitstruct_reg( config ):

  class AssignBitStruct( Model ):
    def __init__( s, config=None ):
      s.in_ = InPort ( Point() )
      s.out = OutPort( Point() )

      if   config == 'Tick':
        @s.tick_rtl
        def block():
          s.out.next = s.in_

      elif config == 'TickFields':
        @s.tick_rtl
        def block():
          s.out.x.next = s.in_.x
          s.out.y.next = s.in_.y

      elif config == 'Comb':
        @s.combinational
        def block():
          s.out.value = s.in_

      elif config == 'CombFields':
        @s.combinational
        def block():
          s.out.x.value = s.in_.x
          s.out.y.value = s.in_.y

      else: raise Exception( 'Invalid config =', config )

  # verify verilator simulation

  model, sim = setup_sim( AssignBitStruct( config ) )
  for i in range( 10 ):
    input_value       = concat( *2*[Bits(4,i)] )
    model.in_.value   = input_value
    sim.cycle()
    assert model.out == input_value

  # read verilog to verify our output signal is being declared as a reg
  # (required by Synopsys design compiler)

  with open( model.__class__.__name__+'.v', 'r' ) as fp:
    assert 'output reg' in fp.read()

#-----------------------------------------------------------------------
# test_verilator_compile_error
#-----------------------------------------------------------------------
def test_verilator_compile_error( ):
  class TestVerilatorCompileError( Model ):
    def __init__( s ):
      s.in_ = InPort(8)
      s.out = OutPort(8)
      @s.combinational
      def logic():
        s.in_.value = s.out

  with pytest.raises( VerilatorCompileError ):
    model = TestVerilatorCompileError()
    model, sim = setup_sim( model )

