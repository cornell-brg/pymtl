# Arbiter with enable

from   pymtl import *
import pmlib

from RoundRobinArbiter5x5 import RoundRobinArbiter5x5

from pmlib    import TestVectorSimulator


class RoundRobinArbiterEn5x5(Model):

  def __init__(self ):

    # Local Constants

    ARB    = 1
    NO_ARB = 0

    # Interface Ports

    self.en         = InPort  ( 1 )
    self.reqs       = InPort  ( 5 )
    self.grants     = OutPort ( 5 )

    # reqs_mux

    self.reqs_mux   = m = pmlib.muxes.Mux2( 5 )
    connect({
      m.in_[NO_ARB] : 0,
      m.in_[ARB]    : self.reqs,
      m.sel         : self.en
    })

    # round robin arbiter

    self.rr_arbiter = RoundRobinArbiter5x5( )

    connect( self.rr_arbiter.reqs,   self.reqs_mux.out )
    connect( self.rr_arbiter.grants, self.grants       )

  def line_trace(self):
    return "{:05b} | {:05b}".format( self.reqs.value.uint, self.grants.value.uint )

#-------------------------------------------------------------------------
# Round Robin Aribter Tests
#-------------------------------------------------------------------------

# Test Harness

def run_test( dump_vcd, ModelType, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.reqs.value = test_vector[1]
    model.en.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.grants.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_rr_en_arb" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_en_arb_5( dump_vcd ):
  run_test( dump_vcd, RoundRobinArbiterEn5x5, [


    # en  reqs      grants
    [ 0,  0b00000,  0b00000 ],
    [ 1,  0b00000,  0b00000 ],

    [ 0, 0b00001,  0b00000 ],
    [ 1, 0b00001,  0b00001 ],
    [ 1, 0b00010,  0b00010 ],
    [ 1, 0b00100,  0b00100 ],
    [ 0, 0b11111,  0b00000 ],
    [ 1, 0b01000,  0b01000 ],
    [ 1, 0b10000,  0b10000 ],

    [ 1, 0b11111,  0b00001 ],
    [ 1, 0b11111,  0b00010 ],
    [ 1, 0b11111,  0b00100 ],
    [ 1, 0b11111,  0b01000 ],
    [ 1, 0b11111,  0b10000 ],
    [ 1, 0b11111,  0b00001 ],

    [ 1, 0b11000,  0b01000 ],
    [ 1, 0b10100,  0b10000 ],
    [ 1, 0b10001,  0b00001 ],
    [ 1, 0b00110,  0b00010 ],
    [ 1, 0b00101,  0b00100 ],
    [ 1, 0b00011,  0b00001 ],
  ])

