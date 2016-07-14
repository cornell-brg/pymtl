#=======================================================================
# RegAndIncr_test.py
#=======================================================================

import random
import pytest

from pymtl import *

from RegAndIncrSC     import RegAndIncrSC

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

  model = RegAndIncrSC()

  model.elaborate()

  # create the simulator

  sim = SimulationTool( model )
  sim.reset() # remember to reset!
  
  # verify the model

  print

  for input_vector, expected_out in simple_test_vectors:
    sim.print_line_trace()
    
    model.in_.value = input_vector
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

  model = RegAndIncrSC()
  model.elaborate()

  # create the simulator

  sim = SimulationTool( model )
  sim.reset() # remember to reset!

  # verify the model

  print
  for input_vector, expected_out in gen_test_vectors( 32 ):
    sim.print_line_trace()
    
    model.in_.value = input_vector
    sim.cycle()
    
    assert model.out == expected_out
    
  sim.print_line_trace()
  
  model.destroy()
  

