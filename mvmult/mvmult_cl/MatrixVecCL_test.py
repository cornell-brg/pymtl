#=========================================================================
# MatrixVecCL_test
#=========================================================================

import pytest

from pymtl import *
from pclib import *

from MatrixVecCL import MatrixVecCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, num_mvmults, src_msgs, src_delay, mem_delay ):

    # Create parameters

    memreq_p  = mem_msgs.MemReqParams( 32, 32 )
    memresp_p = mem_msgs.MemRespParams( 32 )

    # Internal state

    s.num_mvmults   = num_mvmults
    s.mvmults_count = 0

    # Instantiate models

    s.src    = TestSource  ( 37, src_msgs, src_delay )
    s.mvmult = MatrixVecCL ()
    s.mem    = TestMemory  ( memreq_p, memresp_p, 1, mem_delay )

  def elaborate_logic( s ):

    s.connect( s.mvmult.from_cpu, s.src.out      )
    s.connect( s.mvmult.memreq,   s.mem.reqs[0]  )
    s.connect( s.mvmult.memresp,  s.mem.resps[0] )

    @s.tick
    def logic():
      if s.mvmult.done():
        s.mvmults_count += 1

  def done( s ):
    return s.mvmults_count == s.num_mvmults

  def line_trace( s ):
    return s.src.line_trace()   + " > " + \
      s.mvmult.line_trace() + " " + s.mem.line_trace()

#-------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "src_delay,mem_delay", [
  (  0,  0 ),
  (  5,  0 ),
  ( 10,  0 ),
  (  0,  5 ),
  (  0, 10 ),
  (  5,  5 ),
  ( 10, 10 ),
])
def test( src_delay, mem_delay ):

  # Test messages

  src_msgs = [

    # First matrix-vector multiplication

    Bits( 37, 0x100000004 ), # set size      = 4
    Bits( 37, 0x200000000 ), # set src0_addr = 0x0000
    Bits( 37, 0x300000010 ), # set src1_addr = 0x0010
    Bits( 37, 0x400000020 ), # set dest_addr = 0x0020
    Bits( 37, 0x000000001 ), # go

    # Second matrix-vector multiplication

    Bits( 37, 0x100000004 ), # set size      = 4
    Bits( 37, 0x200000030 ), # set src0_addr = 0x0000
    Bits( 37, 0x300000040 ), # set src1_addr = 0x0010
    Bits( 37, 0x400000050 ), # set dest_addr = 0x0020
    Bits( 37, 0x000000001 ), # go

  ]

  # Instantiate and elaborate the model

  model = TestHarness( 2, src_msgs, src_delay, mem_delay )
  model.elaborate()

  # Write test data into the test memory

  data = [ 7,  36, 30, 93, 58, 88, 41, 20, 0, 0, 0, 0,
           7, -36, 57, 93, -2, 88, 99, 12, 0, 0, 0, 0 ]

  for i in xrange(len(data)):

    bits = Bits( 32, data[i] )
    for j in xrange(4):
      model.mem.mem.mem[4*i+j] = bits[j*8:j*8+8]

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

  data_ref = [ 7,  36, 30, 93, 58, 88, 41, 20, 6664, 0, 0, 0,
               7, -36, 57, 93, -2, 88, 99, 12, 3577, 0, 0, 0 ]

  for i in xrange(len(data_ref)):

    bits = Bits( 32 )
    for j in xrange(4):
      bits[j*8:j*8+8] = model.mem.mem.mem[4*i+j]

    bits_ref = Bits( 32, data_ref[i] )

    assert bits == bits_ref
