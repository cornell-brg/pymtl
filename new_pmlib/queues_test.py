#=======================================================================
# queues_test.py
#=======================================================================

from new_pymtl    import *
from TestSource   import TestSource
from TestSink     import TestSink
from ValRdyBundle import InValRdyBundle, OutValRdyBundle
from queues       import Queue, InValRdyQueue, OutValRdyQueue

import pytest

#-----------------------------------------------------------------------
# test_Queue
#-----------------------------------------------------------------------
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

#-----------------------------------------------------------------------
# TestHarness
#-----------------------------------------------------------------------
class ValRdyTestHarness( Model ):

  def __init__( s, model_inst, src_msgs,  sink_msgs,
                               src_delay, sink_delay ):

    src_msg_type  = model_inst.in_.msg.msg_type
    sink_msg_type = model_inst.out.msg.msg_type

    s.src   = TestSource( src_msg_type,  src_msgs,  src_delay  )
    s.model = model_inst
    s.sink  = TestSink  ( sink_msg_type, sink_msgs, sink_delay )

  # TODO: get rid of elaborate_logic()?
  def elaborate_logic( s ):
    s.connect( s.src  .out, s.model.in_ )
    s.connect( s.model.out, s.sink .in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.  line_trace() + " > " + \
           s.model.line_trace() + " > " + \
           s.sink. line_trace()

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------
def run_test( model_inst, src_msgs, sink_msgs, src_delay, sink_delay ):

  # Instantiate and elaborate the model

  model = ValRdyTestHarness( model_inst, src_msgs,  sink_msgs,
                                         src_delay, sink_delay )
  model.elaborate()

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

#-----------------------------------------------------------------------
# TestOne
#-----------------------------------------------------------------------
class TestOne( Model ):
  def __init__( s, MsgType, size ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size = size

  def elaborate_logic( s ):

    s.queue = InValRdyQueue( s.in_.msg.msg_type, size=s.size )
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

#-----------------------------------------------------------------------
# test_InValRdyQueue
#-----------------------------------------------------------------------
src_msgs = sink_msgs = range( 20 )
@pytest.mark.parametrize(
    ('qsize', 'src_delay', 'sink_delay'),
    [
      (1, 0,0), (2, 0, 0),
      (1, 3,0), (2, 3, 0),
      (1, 0,3), (2, 0, 3),
      (1, 3,5), (2, 3, 5),
    ]
)
def test_InValRdyQueue( qsize, src_delay, sink_delay ):
  MsgType = Bits( 8 )
  run_test( TestOne( MsgType, qsize ), src_msgs,  sink_msgs,
                                       src_delay, sink_delay )

#-----------------------------------------------------------------------
# TestTwo
#-----------------------------------------------------------------------
class TestTwo( Model ):
  def __init__( s, MsgType, size ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size = size

  def elaborate_logic( s ):

    s.queue = OutValRdyQueue( s.in_.msg.msg_type, size=s.size )
    s.connect( s.out, s.queue.out )

    #s.out_buffer_full = False

    @s.tick
    def logic():

      if s.in_.val and s.in_.rdy and not s.queue.is_full():
        s.queue.enq( s.in_.msg[:] )

      s.queue.xtick()
      s.in_.rdy.next = not s.queue.is_full()

#-----------------------------------------------------------------------
# test_OutValRdyQueue
#-----------------------------------------------------------------------
#def test_OutValRdyQueue( src_delay, sink_delay ):
src_msgs = sink_msgs = range( 20 )
@pytest.mark.parametrize(
    ('qsize', 'src_delay', 'sink_delay'),
    [
      (1, 0,0), (2, 0, 0),
      (1, 3,0), (2, 3, 0),
      (1, 0,3), (2, 0, 3),
      (1, 3,5), (2, 3, 5),
    ]
)
def test_OutValRdyQueue( qsize, src_delay, sink_delay ):
  MsgType = Bits( 8 )
  run_test( TestTwo( MsgType, qsize ), src_msgs,  sink_msgs,
                                       src_delay, sink_delay )

#-----------------------------------------------------------------------
# TestThree
#-----------------------------------------------------------------------
class TestThree( Model ):
  def __init__( s, MsgType, size ):

    s.in_  = InValRdyBundle ( MsgType )
    s.out  = OutValRdyBundle( MsgType )

    s.size = size

  def elaborate_logic( s ):

    s.in_q  = InValRdyQueue ( s.in_.msg.msg_type, size=s.size )
    s.out_q = OutValRdyQueue( s.out.msg.msg_type, size=s.size )
    s.connect( s.in_, s.in_q. in_ )
    s.connect( s.out, s.out_q.out )

    @s.tick
    def logic():

      s.in_q.xtick()

      if not s.in_q.is_empty() and not s.out_q.is_full():
        s.out_q.enq( s.in_q.deq() )

      s.out_q.xtick()

#-----------------------------------------------------------------------
# test_ValRdyQueues
#-----------------------------------------------------------------------
src_msgs = sink_msgs = range( 20 )
@pytest.mark.parametrize(
    ('qsize', 'src_delay', 'sink_delay'),
    [
      (1, 0,0), (2, 0, 0),
      (1, 3,0), (2, 3, 0),
      (1, 0,3), (2, 0, 3),
      (1, 3,5), (2, 3, 5),
    ]
)
def test_ValRdyQueues( qsize, src_delay, sink_delay ):
  MsgType = Bits( 8 )
  run_test( TestThree( MsgType, qsize ), src_msgs,  sink_msgs,
                                         src_delay, sink_delay )
