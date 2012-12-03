# Arbiter with enable

from   pymtl import *
import pmlib

from RoundRobinArbiter3x3 import RoundRobinArbiter3x3

from pmlib    import TestVectorSimulator


class RoundRobinArbiterEn3x3(Model):

  def __init__(self ):

    # Local Constants

    ARB    = 1
    NO_ARB = 0

    # Interface Ports

    self.en         = InPort  ( 1 )
    self.reqs       = InPort  ( 3 )
    self.grants     = OutPort ( 3 )

    # reqs_mux

    self.reqs_mux   = m = pmlib.muxes.Mux2( 3 )
    connect({
      m.in_[NO_ARB] : 0,
      m.in_[ARB]    : self.reqs,
      m.sel         : self.en
    })

    # round robin arbiter

    self.rr_arbiter = RoundRobinArbiter3x3( )

    connect( self.rr_arbiter.reqs,   self.reqs_mux.out )
    connect( self.rr_arbiter.grants, self.grants       )

  def line_trace(self):
    return "{:03b} | {:03b}".format( self.reqs.value.uint, self.grants.value.uint )

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
    sim.dump_vcd( "test_r3_en_arb" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_en_arb_3( dump_vcd ):
  run_test( dump_vcd, RoundRobinArbiterEn3x3, [


    # en reqs    grants
    [ 0, 0b000,  0b000 ],
    [ 1, 0b000,  0b000 ],

    [ 0, 0b001,  0b000 ],
    [ 1, 0b001,  0b001 ],
    [ 1, 0b010,  0b010 ],
    [ 1, 0b100,  0b100 ],
    [ 0, 0b111,  0b000 ],

    [ 1, 0b111,  0b001 ],
    [ 1, 0b111,  0b010 ],
    [ 1, 0b111,  0b100 ],
    [ 1, 0b111,  0b001 ],

    [ 1, 0b101,  0b100 ],
    [ 1, 0b011,  0b001 ],
    [ 1, 0b110,  0b010 ],
    [ 1, 0b101,  0b100 ],
    [ 1, 0b011,  0b001 ],
  ])

