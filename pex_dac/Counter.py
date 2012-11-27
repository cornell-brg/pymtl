#=========================================================================
# Counter.py
#=========================================================================

from   pymtl import *
import pmlib

from   math import ceil, log

from   pmlib.TestVectorSimulator import TestVectorSimulator

# Counter Model

class Counter (Model):

  def __init__( s, max_count ):

    # Local Constants

    s.max_count = max_count
    s.nbits     = int( ceil( log( max_count + 1, 2 ) ) )

    # Interface

    s.increment = InPort  ( 1 )
    s.decrement = InPort  ( 1 )
    s.count     = OutPort ( s.nbits )
    s.zero      = OutPort ( 1 )

    # credit count register

    s.count_reg = pmlib.regs.RegRst( s.nbits, reset_value = max_count )
    connect( s.count_reg.out, s.count )

  @combinational
  def comb( s ):

    if   ( s.increment.value and ~s.decrement.value
         and ( s.count_reg.out.value < s.max_count ) ):
      s.count_reg.in_.value = s.count_reg.out.value + 1
    elif ( ~s.increment.value and s.decrement.value
         and ( s.count_reg.out.value > 0 ) ):
      s.count_reg.in_.value = s.count_reg.out.value - 1
    else:
      s.count_reg.in_.value = s.count_reg.out.value

    s.zero.value = ( s.count_reg.out.value == 0 )

# Unit tests for the counter

def test_reg( dump_vcd ):

  # Test vectors

  test_vectors = [
    # incr decr count zero
    [ 0,   0,   4,    0   ],
    [ 1,   1,   4,    0   ],
    [ 0,   1,   4,    0   ],
    [ 0,   1,   3,    0   ],
    [ 0,   1,   2,    0   ],
    [ 0,   1,   1,    0   ],
    [ 0,   1,   0,    1   ],
    [ 0,   1,   0,    1   ],
    [ 1,   0,   0,    1   ],
    [ 1,   0,   1,    0   ],
    [ 1,   0,   2,    0   ],
    [ 1,   0,   3,    0   ],
    [ 1,   0,   4,    0   ],
    [ 1,   0,   4,    0   ],
    [ 0,   1,   4,    0   ],
    [ 1,   1,   3,    0   ],
    [ 0,   0,   3,    0   ],
    [ 0,   1,   3,    0   ],
    [ 0,   1,   2,    0   ],
  ]

  # Instantiate and elaborate the model

  model = Counter(4)
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.increment.value = test_vector[0]
    model.decrement.value = test_vector[1]

  def tv_out( model, test_vector ):
    assert model.count.value == test_vector[2]
    assert model.zero.value == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "Counter.vcd" )
  sim.run_test()
