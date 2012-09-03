#=========================================================================
# GcdUnitBL Test Suite
#=========================================================================

from pymtl import *
import pmlib

from GcdUnitBL import GcdUnitBL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Instantiate models

    self.src  = pmlib.TestSource ( 64, src_msgs,  src_delay  )
    self.gcd  = ModelType        ()
    self.sink = pmlib.TestSink   ( 32, sink_msgs, sink_delay )

    # Connect chain

    connect_chain([ self.src, self.gcd, self.sink ])

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + \
           self.gcd.line_trace() + " > " + \
           self.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def concat( a, b ):
  return ( a << 32 | b )

def run_gcd_test( dump_vcd, vcd_file_name,
                  ModelType, src_delay, sink_delay ):

  # Test messages

  m = [
    concat( 15,  5 ),  5,
    concat(  5, 15 ),  5,
    concat(  7, 13 ),  1,
    concat( 75, 45 ), 15,
    concat( 36, 96 ), 12,
  ]

  src_msgs  = m[::2]
  sink_msgs = m[1::2]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 0 x 0
#-------------------------------------------------------------------------

def test_delay0x0( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay0x0.vcd",
                GcdUnitBL, 0, 0 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 10 x 5
#-------------------------------------------------------------------------

import pytest
@pytest.mark.xfail
def test_delay10x5( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay10x5.vcd",
                GcdUnitBL, 10, 5 )

#-------------------------------------------------------------------------
# GcdUnitBL unit test with delay = 5 x 10
#-------------------------------------------------------------------------

@pytest.mark.xfail
def test_delay5x10( dump_vcd ):
  run_gcd_test( dump_vcd, "pex-gcd-GcdUnitBL_test_delay5x10.vcd",
                GcdUnitBL, 5, 10 )

