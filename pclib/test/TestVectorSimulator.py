#=========================================================================
# TestVectorSimulator
#=========================================================================
# This class simplifies creating unit tests which simply set certain
# inputs and then check certain outputs every cycle. A user simply needs
# to instantiate and elaborate the model, create a list of test vectors,
# and create two helper functions (one to set the model inputs from the
# test vector and one to verify the model outputs against the test
# vector).
#
# Each test vector should be a list of values, so a collection of test
# vectors is just a list of lists. Each test vector specifies the
# inputs/outputs corresponding to a specific cycle in sequence.
#

from __future__ import print_function

from pymtl import *

class TestVectorSimulator( object ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, model, test_vectors,
                set_inputs_func, verify_outputs_func, wait_cycles = 0 ):

    self.model               = model
    self.set_inputs_func     = set_inputs_func
    self.verify_outputs_func = verify_outputs_func
    self.test_vectors        = test_vectors
    self.wait_cycles         = wait_cycles

  #-----------------------------------------------------------------------
  # Run test
  #-----------------------------------------------------------------------

  def run_test( self, ):

    # Create a simulator using the simulation tool

    sim = SimulationTool( self.model )

    # Iterate setting the inputs and verifying the outputs each cycle

    print()

    sim.reset()
    for test_vector in self.test_vectors:

      # Set inputs
      self.set_inputs_func( self.model, test_vector )

      # Evaluate combinational concurrent blocks in simulator
      if self.wait_cycles == 0:
        sim.eval_combinational()
      else:
        for i in range(self.wait_cycles):
          sim.cycle()

      # Print the line trace
      sim.print_line_trace()

      # Verify outputs
      self.verify_outputs_func( self.model, test_vector )

      # Tick the simulator one cycle
      sim.cycle()

    # Add a couple extra ticks so that the VCD dump is nicer

    sim.cycle()
    sim.cycle()
    sim.cycle()

