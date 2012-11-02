#=========================================================================
# Round Robin Arbiter Suite
#=========================================================================

from pymtl import *

from pmlib             import TestVectorSimulator
from RoundRobinArbiter import RoundRobinArbiter

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test( dump_vcd, ModelType, nreqs, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( nreqs )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    #model.kin.value  = test_vector[1]
    for i in range( nreqs ):
      model.reqs.value = test_vector[2]

  def tv_out( model, test_vector ):

    assert model.grants.value == test_vector[3]
    #assert model.kout.value  == test_vector[4]

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


    # str      kin  reqs     grants   kout

    # TODO: kin not supported right now!
    #[ "0000",  1,   0b0000,  0b0000,  1  ],
    #[ "1111",  1,   0b1111,  0b0000,  1  ],

    [ "0000",  0,   0b0000,  0b0000,  0  ],

    [ "0001",  0,   0b0001,  0b0001,  1  ],
    [ "0010",  0,   0b0010,  0b0010,  1  ],
    [ "0100",  0,   0b0100,  0b0100,  1  ],
    [ "1000",  0,   0b1000,  0b1000,  1  ],

    [ "1111",  0,   0b1111,  0b0001,  1  ],
    [ "1111",  0,   0b1111,  0b0010,  1  ],
    [ "1111",  0,   0b1111,  0b0100,  1  ],
    [ "1111",  0,   0b1111,  0b1000,  1  ],
    [ "1111",  0,   0b1111,  0b0001,  1  ],

    [ "1100",  0,   0b1100,  0b0100,  1  ],
    [ "1010",  0,   0b1010,  0b1000,  1  ],
    [ "1001",  0,   0b1001,  0b0001,  1  ],
    [ "0110",  0,   0b0110,  0b0010,  1  ],
    [ "0101",  0,   0b0101,  0b0100,  1  ],
    [ "0011",  0,   0b0011,  0b0001,  1  ],

    [ "1110",  0,   0b1110,  0b0010,  1  ],
    [ "1101",  0,   0b1101,  0b0100,  1  ],
    [ "1011",  0,   0b1011,  0b1000,  1  ],
    [ "0111",  0,   0b0111,  0b0001,  1  ],

  ])


