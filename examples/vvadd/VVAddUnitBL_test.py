#=========================================================================
# VVAddBL_test.py
#=========================================================================

from pymtl        import *
from pclib.ifaces import mem_msgs
from pclib.test   import TestMemory
from VVAddUnitBL  import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, memreq_params, memresp_params,
                dest_addr, src0_addr, src1_addr, size ):

    # Instantiate models

    s.vvadd = VVAddUnitBL( memreq_params, memresp_params,
                           dest_addr, src0_addr, src1_addr, size )

    s.mem = TestMemory( memreq_params, memresp_params, 1, 0 )

  def elaborate_logic( s ):

    s.connect( s.vvadd.memreq,  s.mem.reqs[0]  )
    s.connect( s.vvadd.memresp, s.mem.resps[0] )

  def done( s ):
    return s.vvadd.done()

  def line_trace( s ):
    return s.vvadd.line_trace() + " " + s.mem.line_trace()

#-------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------

def test_basic( dump_vcd ):

  # Create parameters

  memreq_params  = mem_msgs.MemReqParams( 32, 32 )
  memresp_params = mem_msgs.MemRespParams( 32 )

  # Instantiate and elaborate the model

  model = TestHarness( memreq_params, memresp_params,
                       0x0200, 0x0000, 0x0100, 6 )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Write test data into the test memory

  for i in xrange(6):
    model.mem.mem.mem[ 0x0000 + i*4 ] = 11+i
    model.mem.mem.mem[ 0x0100 + i*4 ] = 21+i
    model.mem.mem.mem[ 0x0200 + i*4 ] = 0

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

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

  # Verify the output

  for i in xrange(6):
    assert model.mem.mem.mem[ 0x0200 + i*4 ] == 11+i + 21+i

