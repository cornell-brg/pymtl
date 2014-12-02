#=========================================================================
# MatrixVecProxy_test
#=========================================================================

import pytest

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle, mem_msgs
from pclib.test   import TestMemory

from MatrixVecFL     import MatrixVecFL
from MatrixVecProxy  import MatrixVecProxy
from MatrixVecBundle import InMatrixVecBundle,OutMatrixVecBundle

#-------------------------------------------------------------------------
# TestDriver
#-------------------------------------------------------------------------

class TestDriver (Model):

  def __init__( s ):

    # Coprocessor Interface

    s.to_cp2   = OutValRdyBundle( 5+32 )
    s.from_cp2 = InMatrixVecBundle()

    # Proxy

    s.mvmult = MatrixVecProxy( s.to_cp2, s.from_cp2 )
    s.done   = False

  def elaborate_logic( s ):

    @s.pausable_tick
    def tick():

      s.mvmult.set_size( 4 )
      s.mvmult.set_src0_addr( 0x0000 )
      s.mvmult.set_src1_addr( 0x0010 )
      s.mvmult.set_dest_addr( 0x0020 )
      s.mvmult.go()

      s.mvmult.set_size( 4 )
      s.mvmult.set_src0_addr( 0x0030 )
      s.mvmult.set_src1_addr( 0x0040 )
      s.mvmult.set_dest_addr( 0x0050 )
      s.mvmult.go()

      s.done = True

  def done( s ):
    return s.done

  def line_trace( s ):
    return s.mvmult.line_trace()

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, num_mvmults, mem_delay ):

    # Create parameters

    memreq_p  = mem_msgs.MemReqParams( 32, 32 )
    memresp_p = mem_msgs.MemRespParams( 32 )

    # Internal state

    s.num_mvmults   = num_mvmults
    s.mvmults_count = 0

    # Instantiate models

    s.driver = TestDriver  (  )
    s.mvmult = MatrixVecFL ()
    s.mem    = TestMemory  ( memreq_p, memresp_p, 1, mem_delay )

  def elaborate_logic( s ):

    s.connect( s.mvmult.from_cpu, s.driver.to_cp2   )
    s.connect( s.mvmult.to_cpu,   s.driver.from_cp2 )
    s.connect( s.mvmult.memreq,   s.mem.reqs[0]     )
    s.connect( s.mvmult.memresp,  s.mem.resps[0]    )

    @s.tick
    def logic():
      if s.mvmult.done():
        s.mvmults_count += 1

  def done( s ):
    return s.mvmults_count == s.num_mvmults

  def line_trace( s ):
    return s.driver.line_trace() + " > " + \
           s.mvmult.line_trace() + " " + s.mem.line_trace()

#-------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "mem_delay", [ 0, 5, 10 ] )
def test( dump_vcd, mem_delay ):

  # Instantiate and elaborate the model

  model = TestHarness( 2, mem_delay )
  model.vcd_file = dump_vcd
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

