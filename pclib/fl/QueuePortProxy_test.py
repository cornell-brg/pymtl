#=========================================================================
# QueuePortProxy_test
#=========================================================================

from __future__ import print_function

import pytest
import collections

from pymtl      import *
from pclib.test import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from QueuePortProxy import InQueuePortProxy, OutQueuePortProxy

#-------------------------------------------------------------------------
# Function Implementation
#-------------------------------------------------------------------------
# This is a plain function implementation which copies n messages from an
# input queue to an output queue.

def queue_copy( n, in_queue, out_queue ):

  for _ in range(n):
    out_queue.append( in_queue.popleft() )

#-------------------------------------------------------------------------
# Test for underlying queue_copy
#-------------------------------------------------------------------------

def test_queue_copy():

  data = [ 11, 12, 13, 14, 15, 16 ]
  in_queue  = collections.deque(data)
  out_queue = collections.deque()

  queue_copy( len(data), in_queue, out_queue )

  assert list(out_queue) == data

#-------------------------------------------------------------------------
# QueueCopy
#-------------------------------------------------------------------------
# An example model that simply copies n messages from an input val/rdy
# interface to an output val/rdy interface.
class QueueCopy( Model ):

  def __init__( s, dtype, nmsgs ):

    s.nmsgs = nmsgs

    # Queue interfaces

    s.in_ = InValRdyBundle  ( dtype )
    s.out = OutValRdyBundle ( dtype )

    # QueuePortProxy objects

    s.in_queue  = InQueuePortProxy  ( s.in_ )
    s.out_queue = OutQueuePortProxy ( s.out )

    # This looks like a regular tick block, but because it is a
    # pausable_tick there is something more sophisticated is going on.
    # The first time we call the tick, the queue_copy function will try
    # and access the input queue. This will get proxied to the
    # InQueuePortProxy object which will check the val/rdy interface. If
    # the interface is not valid, we cannot return the data to the
    # underlying queue_copy function so instead we use greenlets to
    # switch back to the pausable tick function. The next time we call
    # tick, we call the wrapper function again, and essentially we jump
    # back into the InQueuePortProxy object to see if the interface is
    # valid yet. When the interface is eventually valid, the
    # InQueuePortProxy object will return the data and the underlying
    # queue_copy function will move onto the next element. Currently the
    # queue port proxy objects include infinite internal queues so the
    # output queue can never stall.

    @s.tick_fl
    def logic():
      queue_copy( s.nmsgs, s.in_queue, s.out_queue )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.in_queue.line_trace() + s.out_queue.line_trace() + ")"

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, src_msgs, sink_msgs, src_delay, sink_delay ):

    s.src   = TestSource ( 32, src_msgs,  src_delay  )
    s.qcopy = QueueCopy  ( 32, len(src_msgs)         )
    s.sink  = TestSink   ( 32, sink_msgs, sink_delay )

    s.connect( s.src.out,   s.qcopy.in_ )
    s.connect( s.qcopy.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " > " + \
           s.qcopy.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------
@pytest.mark.parametrize( "src_delay,sink_delay", [
  (  0, 0  ),
  ( 10, 5  ),
  (  5, 10 ),
])
def test( dump_vcd, src_delay, sink_delay ):

  # Test messages

  data = [ 11, 12, 13, 14, 15, 16 ]
  src_msgs  = data
  sink_msgs = data

  # Instantiate and elaborate the model

  model = TestHarness( src_msgs, sink_msgs, src_delay, sink_delay )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

