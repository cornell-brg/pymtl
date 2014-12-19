#=========================================================================
# queues_test.py
#=========================================================================

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test   import TestSrcSinkSim
from queues       import Queue, InValRdyQueue, OutValRdyQueue

import pytest

#-------------------------------------------------------------------------
# test_Queue
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
  ('size'), [1, 3, 12]
)
def test_Queue( size ):

  # Create the queue
  queue = Queue( size )

  # Fill up the queue
  for i in range( size ):
    queue.enq( i )
    assert queue.peek()     == 0
    assert queue.is_empty() == False

  # Check the queue is full
  assert queue.is_full()

  # Check enqueuing throws an assert
  with pytest.raises( AssertionError ):
    queue.enq( 0 )

  # Empty the queue, check the order is correct
  for i in range( size ):
    assert queue.deq()     == i
    assert queue.is_full() == False

  # Check the queue is empty
  assert queue.is_empty()

  # Check that dequeuing throws an assert
  with pytest.raises( IndexError ):
    queue.deq()

#------------------------------------------------------------------------
# InValRdyQueueHarness
#------------------------------------------------------------------------
# Model an input Simple or Bypass queue connected to an output register.
class InValRdyQueueHarness( Model ):
  def __init__( s, MsgType, size, pipeq ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size  = size
    s.pipeq = pipeq

  def elaborate_logic( s ):

    msg_type = s.in_.msg.msg_type
    s.queue = InValRdyQueue( msg_type, size=s.size, pipe=s.pipeq )
    s.connect( s.in_, s.queue.in_ )

    s.out_buffer_full = False

    @s.tick
    def logic():

      s.queue.xtick()

      if s.out.val and s.out.rdy:
        s.out_buffer_full = False

      if not s.out_buffer_full and not s.queue.is_empty():
        s.out.msg.next    = s.queue.deq()
        s.out_buffer_full = True

      s.out.val.next = s.out_buffer_full

#-------------------------------------------------------------------------
# test_InValRdyQueue
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
  ('qsize', 'pipeq', 'src_delay', 'sink_delay'),
  [
    (1, 0, 0, 0), (1, 1, 0, 0),
    (1, 0, 3, 0), (1, 1, 3, 0),
    (1, 0, 0, 3), (1, 1, 0, 3),
    (1, 0, 3, 5), (1, 1, 3, 5),
    (2, 0, 0, 0), (2, 1, 0, 0),
    (2, 0, 3, 0), (2, 1, 3, 0),
    (2, 0, 0, 3), (2, 1, 0, 3),
    (2, 0, 3, 5), (2, 1, 3, 5),
  ]
)
def test_InValRdyQueue( dump_vcd, qsize, pipeq, src_delay, sink_delay ):
  msgs  = range( 5 )
  model = InValRdyQueueHarness( Bits( 8 ), qsize, pipeq )
  model.vcd_file = dump_vcd
  sim   = TestSrcSinkSim( model, msgs, msgs, src_delay, sink_delay )
  sim.run_test()

#-------------------------------------------------------------------------
# OutValRdyQueueHarness
#-------------------------------------------------------------------------
class OutValRdyQueueHarness( Model ):
  def __init__( s, MsgType, size, bypassq ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size    = size
    s.bypassq = bypassq

  def elaborate_logic( s ):

    msg_type = s.in_.msg.msg_type
    s.queue = OutValRdyQueue( msg_type, size=s.size, bypass=s.bypassq )
    s.connect( s.out, s.queue.out )

    #s.out_buffer_full = False

    @s.tick
    def logic():

      # TODO: this behavior is strange, bypass acts like simple + simple
      # but simple acts like rdy is getting set a cycle late... fix?
      s.queue.xtick()

      if s.in_.val and s.in_.rdy:
        s.queue.enq( s.in_.msg[:] )

      s.in_.rdy.next = not s.queue.is_full()


#-------------------------------------------------------------------------
# test_OutValRdyQueue
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
  ('qsize', 'bypassq', 'src_delay', 'sink_delay'),
  [
    (1, 0, 0, 0), (1, 1, 0, 0),
    (1, 0, 3, 0), (1, 1, 3, 0),
    (1, 0, 0, 3), (1, 1, 0, 3),
    (1, 0, 3, 5), (1, 1, 3, 5),
    (2, 0, 0, 0), (2, 1, 0, 0),
    (2, 0, 3, 0), (2, 1, 3, 0),
    (2, 0, 0, 3), (2, 1, 0, 3),
    (2, 0, 3, 5), (2, 1, 3, 5),
  ]
)
def test_OutValRdyQueue( dump_vcd, qsize, bypassq, src_delay, sink_delay ):
  msgs  = range( 5 )
  model = OutValRdyQueueHarness( Bits( 8 ), qsize, bypassq )
  model.vcd_file = dump_vcd
  sim   = TestSrcSinkSim( model, msgs, msgs, src_delay, sink_delay )
  sim.run_test()

#-------------------------------------------------------------------------
# InOutValRdyQueueHarness
#-------------------------------------------------------------------------
class InOutValRdyQueueHarness( Model ):
  def __init__( s, MsgType, size, pipeq, bypassq ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size    = size
    s.pipeq   = pipeq
    s.bypassq = bypassq

  def elaborate_logic( s ):

    s.in_q  = InValRdyQueue ( s.in_.msg.msg_type, size=s.size, pipe  =s.pipeq  )
    s.out_q = OutValRdyQueue( s.out.msg.msg_type, size=s.size, bypass=s.bypassq)
    s.connect( s.in_, s.in_q. in_ )
    s.connect( s.out, s.out_q.out )

    @s.tick
    def logic():

      # Automatically enq from input / deq from output
      s.in_q.xtick()
      s.out_q.xtick()

      # Transfer data from input to output queue
      if not s.in_q.is_empty() and not s.out_q.is_full():
        s.out_q.enq( s.in_q.deq() )

#-------------------------------------------------------------------------
# test_InOutValRdyQueues
#-------------------------------------------------------------------------
@pytest.mark.parametrize(
  ('qsize', 'pipeq', 'bypassq', 'src_delay', 'sink_delay'),
  [
    (1, 0, 0, 0, 0), (1, 0, 1, 0, 0), (1, 1, 0, 0, 0), (1, 1, 1, 0, 0),
    (1, 0, 0, 3, 0), (1, 0, 1, 3, 0), (1, 1, 0, 3, 0), (1, 1, 1, 3, 0),
    (1, 0, 0, 0, 3), (1, 0, 1, 0, 3), (1, 1, 0, 0, 3), (1, 1, 1, 0, 3),
    (1, 0, 0, 3, 5), (1, 0, 1, 3, 5), (1, 1, 0, 3, 5), (1, 1, 1, 3, 5),
    (2, 0, 0, 0, 0), (2, 0, 1, 0, 0), (2, 1, 0, 0, 0), (2, 1, 1, 0, 0),
    (2, 0, 0, 3, 0), (2, 0, 1, 3, 0), (2, 1, 0, 3, 0), (2, 1, 1, 3, 0),
    (2, 0, 0, 0, 3), (2, 0, 1, 0, 3), (2, 1, 0, 0, 3), (2, 1, 1, 0, 3),
    (2, 0, 0, 3, 5), (2, 0, 1, 3, 5), (2, 1, 0, 3, 5), (2, 1, 1, 3, 5),
  ]
)
def test_InOutValRdyQueues( dump_vcd, qsize, pipeq, bypassq,
                            src_delay, sink_delay ):
  msgs  = range( 10 )
  model = InOutValRdyQueueHarness( Bits( 8 ), qsize, pipeq, bypassq )
  model.vcd_file = dump_vcd
  sim   = TestSrcSinkSim( model, msgs, msgs, src_delay, sink_delay )
  sim.run_test()

