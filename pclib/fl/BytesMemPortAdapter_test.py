#=========================================================================
# BytesMemPortAdapter_test
#=========================================================================

from __future__ import print_function

import pytest
import random
import struct

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemMsg4B

from pclib.test import TestMemory

from Bytes               import Bytes
from BytesMemPortAdapter import BytesMemPortAdapter

#-------------------------------------------------------------------------
# Function Implementation
#-------------------------------------------------------------------------
# This is a plain function implementation which copies n bytes in memory.

def mem_copy( mem, src_ptr, dest_ptr, nbytes ):

  for i in range(nbytes):
    mem[dest_ptr+i] = mem[src_ptr+i]

#-------------------------------------------------------------------------
# Test for underlying mem_copy
#-------------------------------------------------------------------------

def test_mem_copy():

  data = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 ]
  data_bytes = Bytes(18)
  for i in range(18):
    data_bytes[i] = data[i]

  mem_copy( data_bytes, 4, 12, 4 )

  data_ref = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 4, 5, 6, 7, 16, 17 ]
  data_ref_bytes = Bytes(18)
  for i in range(18):
    data_ref_bytes[i] = data_ref[i]

  assert data_bytes == data_ref_bytes

#-------------------------------------------------------------------------
# MemCopy
#-------------------------------------------------------------------------
# An example model that simply copies n bytes from a source pointer to a
# destination pointer in a memory.

class MemCopy (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem_ifc_types, src_ptr, dest_ptr, nbytes ):

    s.src_ptr  = src_ptr
    s.dest_ptr = dest_ptr
    s.nbytes   = nbytes
    s.done     = False

    # Memory request/response ports

    s.memreq   = InValRdyBundle  ( mem_ifc_types.req  )
    s.memresp  = OutValRdyBundle ( mem_ifc_types.resp )

    # BytesMemPortAdapter object

    s.mem = BytesMemPortAdapter( s.memreq, s.memresp )

    # This looks like a regular tick block, but because it is a
    # pausable_tick there is something more sophisticated is going on.
    # The first time we call the tick, the mem_copy function will try to
    # ready from memory. This will get proxied to the BytesMemPortAdapter
    # which will create a memory request and send it out the memreq port.
    # Since we do not have the data yet, we cannot return the data to the
    # mem_copy function so instead we use greenlets to switch back to the
    # pausable tick function. The next time we call tick we jump back
    # into the BytesMemPortAdapter object to see if the response has
    # returned. When the response eventually returns, the
    # BytesMemPortAdapter object will return the data and the underlying
    # mem_copy function will move onto writing the memory.

    @s.tick_fl
    def logic():
      if not s.reset:
        mem_copy( s.mem, s.src_ptr, s.dest_ptr, s.nbytes )
        s.done = True

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.mem.line_trace() + ")"

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, src_ptr, dest_ptr, nbytes, stall_prob, latency ):

    # Instantiate models

    s.mcopy = MemCopy( MemMsg4B(), src_ptr, dest_ptr, nbytes )
    s.mem   = TestMemory( MemMsg4B(), 1, stall_prob, latency )

    # Connect models

    s.connect( s.mcopy.memreq,  s.mem.reqs[0]  )
    s.connect( s.mcopy.memresp, s.mem.resps[0] )

  def done( s ):
    return s.mcopy.done

  def line_trace( s ):
    return s.mcopy.line_trace() + " " + s.mem.line_trace()

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "stall_prob,latency",
                          [ (0,0), (0.2,2), (0.5,4) ] )
def test( dump_vcd, stall_prob, latency ):

  # Test data we want to write into memory

  data = [ random.randint(0,0xffffffff) for _ in range(8) ]

  # Convert test data into byte array

  data_bytes = struct.pack("<{}I".format(len(data)),*data)

  # Instantiate and elaborate the model

  th = TestHarness( 0x1000, 0x2000, len(data_bytes), stall_prob, latency )
  th.vcd_file = dump_vcd
  th.elaborate()

  # Write the data into the test memory

  th.mem.write_mem( 0x1000, data_bytes )

  # Create a simulator using the simulation tool

  sim = SimulationTool( th )

  # Run the simulation

  print()

  sim.reset()
  while not th.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Read the data back out of the test memory

  result_bytes = th.mem.read_mem( 0x2000, len(data_bytes) )

  # Convert result bytes into list of ints

  result = list(struct.unpack("<{}I".format(len(data)),buffer(result_bytes)))

  # Compare result to original data

  assert result == data

