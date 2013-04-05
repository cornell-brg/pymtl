#=========================================================================
# TestVectorSimulator Test Suite
#=========================================================================

from new_pymtl import *

from TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# Incrementer
#-------------------------------------------------------------------------

class Incrementer( Model ):

  def __init__( self ):

    self.in_ = InPort  ( 16 )
    self.out = OutPort ( 16 )

  def elaborate_logic( self ):

    @self.combinational
    def comb_logic():
      self.out.value = self.in_.value + 1

  def line_trace( self ):
    return "{:04x} () {:04x}" \
      .format( self.in_.uint(), self.out.uint() )

#-------------------------------------------------------------------------
# test_basics
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

  # Test vectors

  test_vectors = [
    # in      out
    [ 0x0000, 0x0001 ],
    [ 0x0001, 0x0002 ],
    [ 0x000a, 0x000b ],
    [ 0x0401, 0x0402 ],
    [ 0xffff, 0x0000 ],
  ]

  # Instantiate and elaborate the model

  model = Incrementer()
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestVectorSimulator_test.vcd" )
  sim.run_test()

