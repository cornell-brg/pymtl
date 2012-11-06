#=========================================================================
# arbiters_test
#=========================================================================
# This file contains unit tests for the arbiters collection models


from pymtl import *

from pmlib    import TestVectorSimulator
from arbiters import RoundRobinArbiter
from arbiters import RoundRobinArbiterEn

#-------------------------------------------------------------------------
# Round Robin Aribter Tests
#-------------------------------------------------------------------------

# Test Harness

def run_test( dump_vcd, ModelType, nreqs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( nreqs )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.reqs.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.grants.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_rr_arb" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_arb_4( dump_vcd ):
  run_test( dump_vcd, RoundRobinArbiter, 4, [


    # reqs     grants
    [ 0b0000,  0b0000 ],

    [ 0b0001,  0b0001 ],
    [ 0b0010,  0b0010 ],
    [ 0b0100,  0b0100 ],
    [ 0b1000,  0b1000 ],

    [ 0b1111,  0b0001 ],
    [ 0b1111,  0b0010 ],
    [ 0b1111,  0b0100 ],
    [ 0b1111,  0b1000 ],
    [ 0b1111,  0b0001 ],

    [ 0b1100,  0b0100 ],
    [ 0b1010,  0b1000 ],
    [ 0b1001,  0b0001 ],
    [ 0b0110,  0b0010 ],
    [ 0b0101,  0b0100 ],
    [ 0b0011,  0b0001 ],

    [ 0b1110,  0b0010 ],
    [ 0b1101,  0b0100 ],
    [ 0b1011,  0b1000 ],
    [ 0b0111,  0b0001 ],

  ])

#-------------------------------------------------------------------------
# Round Robin Aribter with Enable Tests
#-------------------------------------------------------------------------

# Test Harness

def run_en_test( dump_vcd, ModelType, nreqs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( nreqs )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.en.value   = test_vector[0]
    model.reqs.value = test_vector[1]

  def tv_out( model, test_vector ):
    assert model.grants.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_rr_arb_en" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_arb_en_4( dump_vcd ):
  run_en_test( dump_vcd, RoundRobinArbiterEn, 4, [


    # reqs     grants
    [ 0, 0b0000,  0b0000 ],
    [ 1, 0b0000,  0b0000 ],

    [ 1, 0b0001,  0b0001 ],
    [ 0, 0b0010,  0b0000 ],
    [ 1, 0b0010,  0b0010 ],
    [ 1, 0b0100,  0b0100 ],
    [ 0, 0b1000,  0b0000 ],
    [ 1, 0b1000,  0b1000 ],

    [ 1, 0b1111,  0b0001 ],
    [ 0, 0b1111,  0b0000 ],
    [ 1, 0b1111,  0b0010 ],
    [ 1, 0b1111,  0b0100 ],
    [ 1, 0b1111,  0b1000 ],
    [ 0, 0b1111,  0b0000 ],
    [ 1, 0b1111,  0b0001 ],

    [ 0, 0b1100,  0b0000 ],
    [ 1, 0b1100,  0b0100 ],
    [ 0, 0b1010,  0b0000 ],
    [ 1, 0b1010,  0b1000 ],
    [ 1, 0b1001,  0b0001 ],
    [ 1, 0b0110,  0b0010 ],
    [ 1, 0b0101,  0b0100 ],
    [ 1, 0b0011,  0b0001 ],

    [ 1, 0b1110,  0b0010 ],
    [ 0, 0b1101,  0b0000 ],
    [ 1, 0b1101,  0b0100 ],
    [ 1, 0b1011,  0b1000 ],
    [ 0, 0b0111,  0b0000 ],
    [ 1, 0b0111,  0b0001 ],

  ])
