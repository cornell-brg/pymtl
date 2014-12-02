#=========================================================================
# TestVectorSimulator_test.py
#=========================================================================

from pymtl      import *
from pclib.test import TestVectorSimulator

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
      self.out.value = self.in_ + 1

  def line_trace( self ):
    return "{} () {}".format( self.in_, self.out )

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
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    if test_vector[1] != '?':
      assert model.out == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

