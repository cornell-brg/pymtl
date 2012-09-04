#=========================================================================
# RegIncrFlat Test Suite
#=========================================================================

from pymtl import *

from RegIncrFlat import RegIncrFlat

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

  # Create a list of lists to hold the test vectors

  test_vectors = [
    # in   out
    [  1,  '?'],
    [  2,   2 ],
    [ 13,   3 ],
    [ 42,  14 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 42,  43 ],
    [ 51,  43 ],
    [ 51,  52 ],
  ]

  # Instantiate and elaborate the model

  model = RegIncrFlat()
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pex-regincr-RegIncrFlat_test_basics.vcd" )

  # Iterate setting the inputs and verifying the outputs each cycle

  print ""

  sim.reset()
  for test_vector in test_vectors:

    # Set inputs
    model.in_.value = test_vector[0]

    # Evaluate combinational concurrent blocks in simulator
    sim.eval_combinational()

    # Print the line trace
    sim.print_line_trace()

    # Verify outputs
    if test_vector[1] != '?':
      assert model.out.value == test_vector[1]

    # Tick the simulator one cycle
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

