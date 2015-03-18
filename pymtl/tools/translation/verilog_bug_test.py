#=======================================================================
# verilog_bug_test.py
#=======================================================================

from pymtl import *

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
def test_bitstruct_tick_reg():

  class AssignBitStructTick( Model ):

    def __init__( s ):
      s.in_ = InPort ( Point() )
      s.out = OutPort( Point() )
      @s.tick_rtl
      def block():
        s.out.x.next = s.in_.x
        s.out.y.next = s.in_.y

  model, sim = setup_sim( AssignBitStructTick() )
  for i in range( 10 ):
    model.in_.x.value = i
    model.in_.y.value = i
    sim.cycle()
    assert model.out == concat( *2*[Bits(4,i)] )

  with open( model.__class__.__name__+'.v', 'r' ) as fp:
    assert 'output reg' in fp.read()

#-----------------------------------------------------------------------
# test_bitstruct_comb_reg
#-----------------------------------------------------------------------
def test_bitstruct_comb_reg():

  class AssignBitStructComb( Model ):
    def __init__( s ):
      s.in_ = InPort ( Point() )
      s.out = OutPort( Point() )
      @s.combinational
      def block():
        s.out.x.value = s.in_.x
        s.out.y.value = s.in_.y

  model, sim = setup_sim( AssignBitStructComb() )
  for i in range( 10 ):
    model.in_.x.value = i
    model.in_.y.value = i
    sim.eval_combinational()
    assert model.out == concat( *2*[Bits(4,i)] )

  with open( model.__class__.__name__+'.v', 'r' ) as fp:
    assert 'output reg' in fp.read()

