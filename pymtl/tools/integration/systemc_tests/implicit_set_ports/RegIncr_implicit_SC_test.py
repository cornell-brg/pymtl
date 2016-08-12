#=======================================================================
# RegIncr_implicit_SC_test.py
#=======================================================================

import random
import pytest

from pymtl import *

from RegIncr_implicit_SC     import RegIncr_implicit_SC

simple_test_vectors = [
  ( 4,  5),
  ( 6,  7),
  ( 2,  3),
  (15, 16),
  ( 8,  9),
  ( 0,  1),
  (10, 11),
]

#-----------------------------------------------------------------------
# test_simple
#-----------------------------------------------------------------------
def test_simple():

  # instantiate the model and elaborate it

  model = RegIncr_implicit_SC()

  model.elaborate()

  # create the simulator

  sim = SimulationTool( model )
  sim.reset() # remember to reset!
  
  # verify the model

  print

  for input_vector, expected_out in simple_test_vectors:

    model.in_.value = input_vector
    
    sim.eval_combinational() # This is only for this model's line trace
                             # and is not guaranteed to work in general
                             # since verilog import already have this 
                             # inport trace problem.
    sim.print_line_trace()
    
    sim.cycle()

    assert model.out == expected_out

  sim.print_line_trace()
  
  model.destroy()

#-----------------------------------------------------------------------
# gen_test_vectors
#-----------------------------------------------------------------------
def gen_test_vectors( nbits, size=10 ):

  vectors = []
  for i in range( size ):
    input_value = Bits( nbits, random.randrange( 2**nbits ) )
    vectors.append( (input_value, input_value + 1) )

  return vectors

#-----------------------------------------------------------------------
# test_random
#-----------------------------------------------------------------------
def test_random():

  # elaborate model

  model = RegIncr_implicit_SC()
  model.elaborate()

  # create the simulator

  sim = SimulationTool( model )
  sim.reset() # remember to reset!

  # verify the model

  print
  for input_vector, expected_out in gen_test_vectors( 32 ):
    #print input_vector, expected_out
    model.in_.value = input_vector
    sim.eval_combinational()
    sim.print_line_trace()
    sim.cycle()
    assert model.out == expected_out
  sim.print_line_trace()
  
  model.destroy()
  

