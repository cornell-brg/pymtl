#=========================================================================
# Counter_test.py
#=========================================================================

from Counter import Counter

from pmlib.TestVectorSimulator import TestVectorSimulator


# Unit tests for the counter

def test_counter( dump_vcd ):

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
