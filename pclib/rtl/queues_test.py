#=========================================================================
# queues_test.py
#=========================================================================
# This file contains unit tests for the queue collection models

import pytest

from pymtl      import *
from pclib.test import TestVectorSimulator, TestSource, TestSink

from queues import SingleElementNormalQueue
from queues import SingleElementBypassQueue
from queues import SingleElementPipelinedQueue
from queues import SingleElementSkidQueue
from queues import NormalQueue

#=========================================================================
# Test Vector Tests - Single-Entry
#=========================================================================

#-------------------------------------------------------------------------
# test_1entry_normal_queue_tv
#-------------------------------------------------------------------------
def test_1entry_normal_queue_tv( dump_vcd, test_verilog ):
  '''Single-Element Normal Queue Test Vector Tests

  Directed performance tests for single element queue. We use the
  TestVectorSimulator to do some white box testing.
  '''

  test_vectors = [

    # Enqueue one element and then dequeue it
    # enq.val enq.rdy enq.msg  deq.val deq.rdy deq.msg
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      0,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq.val enq.rdy enq.msg  deq.val deq.rdy deq.msg
    [ 1,      1,      0x0002,  0,      0,      '?'    ],
    [ 1,      0,      0x0003,  1,      0,      0x0002 ],
    [ 0,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      1,      0x0002 ],
    [ 1,      1,      0x0003,  0,      1,      '?'    ],
    [ 1,      0,      0x0004,  1,      1,      0x0003 ],
    [ 1,      1,      0x0004,  0,      1,      '?'    ],
    [ 0,      0,      0x0004,  1,      1,      0x0004 ],
    [ 0,      1,      0x0004,  0,      1,      '?'    ],

  ]

  # Instantiate and elaborate the model

  model = SingleElementNormalQueue( 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value   == test_vector[1]
    assert model.deq.val.value   == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_1entry_bypass_queue_tv
#-------------------------------------------------------------------------
def test_1entry_bypass_queue_tv( dump_vcd, test_verilog ):
  """Single-Element Bypass Queue Test Vector Tests

  Directed performance tests for single element queue. We use the
  TestVectorSimulator to do some white box testing.
  """

  test_vectors = [

    # Enqueue one element and then dequeue it
    # enq.val enq.rdy enq.msg  deq.val deq.rdy deq.msg
    [ 1,      1,      0x0001,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq.val enq.rdy enq.msg  deq.val deq.rdy deq.msg
    [ 1,      1,      0x0002,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      0,      0x0002 ],
    [ 0,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      1,      0x0002 ],
    [ 1,      1,      0x0003,  1,      1,      0x0003 ],
    [ 1,      1,      0x0004,  1,      1,      0x0004 ],
    [ 0,      1,      0x0004,  0,      1,      '?'    ],

  ]

  # Instantiate and elaborate the model

  model = SingleElementBypassQueue( 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value   == test_vector[1]
    assert model.deq.val.value   == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_1entry_pipe_queue_tv
#-------------------------------------------------------------------------
def test_1entry_pipe_queue_tv( dump_vcd, test_verilog ):
  """Single-Element Pipelined Queue Test Vector Tests.

  Directed performance tests for single element piped queue. We use the
  TestVectorSimulator to do some white box testing.
  """

  test_vectors = [

    # Enqueue one element and then dequeue it
    # enq.val enq.rdy enq.bits deq.val deq.rdy deq.bits
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      1,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      1,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq.val enq.rdy enq.bits deq.val deq.rdy deq.bits
    [ 1,      1,      0x0002,  0,      0,      '?'    ],
    [ 1,      0,      0x0003,  1,      0,      0x0002 ],
    [ 0,      0,      0x0000,  1,      0,      0x0002 ],
    [ 1,      1,      0x0003,  1,      1,      0x0002 ],
    [ 1,      1,      0x0004,  1,      1,      0x0003 ],
    [ 0,      1,      0x0000,  1,      1,      0x0004 ],
    [ 0,      1,      0x0000,  0,      1,      '?'    ],

  ]

  # Instantiate and elaborate the model

  model = SingleElementPipelinedQueue( 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value    == test_vector[1]
    assert model.deq.val.value    == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#=========================================================================
# Source Sink Tests - Single-Entry
#=========================================================================

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):
  """Source Sink Test Harness."""

  def __init__( s, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay, dtype, test_verilog, dump_vcd ):

    # Instantiate models

    s.src    = TestSource ( dtype, src_msgs,  src_delay  )
    s.queue  = ModelType  ( dtype )
    s.sink   = TestSink   ( dtype, sink_msgs, sink_delay )

    s.      vcd_file = dump_vcd
    s.queue.vcd_file = dump_vcd

    if test_verilog:
      s.queue = TranslationTool( s.queue )

    # Connect

    s.connect( s.src.out,  s.queue.enq )
    s.connect( s.sink.in_, s.queue.deq )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return "{} > {} > {}".format( s.src.line_trace(),
                                  s.queue.line_trace(),
                                  s.sink.line_trace() )

#-------------------------------------------------------------------------
# run_1entry_queue_test
#-------------------------------------------------------------------------
def run_1entry_queue_test( dump_vcd, test_verilog, ModelType,
                                   src_delay, sink_delay, dtype ):
  """Tests for single element queue using test source and sink."""

  q_msgs = [
      0x0001,
      0x0002,
      0x0003,
      0x0004,
      0x0005,
      0x0006,
      0x0007,
      0x0008
  ]

  # Instantiate and elaborate the model

  model = TestHarness( ModelType, q_msgs, q_msgs,
                       src_delay, sink_delay, dtype, test_verilog, dump_vcd )
  model.elaborate()

  # Run the test

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

@pytest.mark.parametrize( "src_delay,sink_delay,dtype", [
  (  0, 0, 16 ),
  (  0, 5, 16 ),
  (  5, 0, 16 ),
  ( 10, 5, 16 ),
])
def test_1entry_normal( dump_vcd, test_verilog, src_delay, sink_delay, dtype ):
  run_1entry_queue_test( dump_vcd, test_verilog,
                SingleElementNormalQueue, src_delay, sink_delay, dtype )

@pytest.mark.parametrize( "src_delay,sink_delay,dtype", [
  (  0, 0, 16 ),
  (  0, 5, 16 ),
  (  5, 0, 16 ),
  ( 10, 5, 16 ),
])
def test_1entry_bypass( dump_vcd, test_verilog, src_delay, sink_delay, dtype ):
  run_1entry_queue_test( dump_vcd, test_verilog,
                SingleElementBypassQueue, src_delay, sink_delay, dtype )

@pytest.mark.parametrize( "src_delay,sink_delay,dtype", [
  (  0, 0, 16 ),
  (  0, 5, 16 ),
  (  5, 0, 16 ),
  ( 10, 5, 16 ),
])
def test_1entry_pipe( dump_vcd, test_verilog, src_delay, sink_delay, dtype ):
  run_1entry_queue_test( dump_vcd, test_verilog,
                SingleElementPipelinedQueue, src_delay, sink_delay, dtype )

#=========================================================================
# Test Vector Tests - Multi-Entry
#=========================================================================

#-------------------------------------------------------------------------
# run_test_queue
#-------------------------------------------------------------------------
def run_test_queue( dump_vcd, test_verilog, ModelType, num_entries,
                    test_vectors ):
  """Tests for Multiple Entry Queues."""

  # Instantiate and elaborate the model

  model = ModelType( num_entries, 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value   == test_vector[1]
    assert model.deq.val.value   == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# test_2entry_normal
#-------------------------------------------------------------------------
def test_2entry_normal( dump_vcd, test_verilog ):
  """Two Element Normal Queue."""
  run_test_queue( dump_vcd, test_verilog, NormalQueue, 2, [
    # Enqueue one element and then dequeue it
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      1,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0002,  0,      0,      '?'    ],
    [ 1,      1,      0x0003,  1,      0,      0x0002 ],
    [ 0,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      1,      0x0002 ],
    [ 1,      1,      0x0004,  1,      0,      '?'    ],
    [ 1,      0,      0x0004,  1,      1,      0x0003 ],
    [ 1,      1,      0x0005,  1,      0,      '?'    ],
    [ 0,      0,      0x0005,  1,      1,      0x0004 ],
    [ 0,      1,      0x0005,  1,      1,      0x0005 ],
    [ 0,      1,      0x0005,  0,      1,      '?'    ],
  ])

#-------------------------------------------------------------------------
# test_3entry_normal
#-------------------------------------------------------------------------
def test_3entry_normal( dump_vcd, test_verilog ):
  """Three Element Queue."""
  run_test_queue( dump_vcd, test_verilog, NormalQueue, 3, [
    # Enqueue one element and then dequeue it
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      1,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0002,  0,      0,      '?'    ],
    [ 1,      1,      0x0003,  1,      0,      0x0002 ],
    [ 1,      1,      0x0004,  1,      0,      0x0002 ],
    [ 1,      0,      0x0005,  1,      0,      0x0002 ],
    [ 0,      0,      0x0005,  1,      0,      0x0002 ],
    [ 1,      0,      0x0005,  1,      1,      0x0002 ],
    [ 1,      1,      0x0005,  1,      1,      0x0003 ],
    [ 1,      1,      0x0006,  1,      1,      0x0004 ],
    [ 1,      1,      0x0007,  1,      1,      0x0005 ],
    [ 0,      1,      0x0000,  1,      1,      0x0006 ],
    [ 0,      1,      0x0000,  1,      1,      0x0007 ],
    [ 0,      1,      0x0000,  0,      1,      '?'    ],
  ])

#=========================================================================
# Skid Queue tests
#=========================================================================

#-------------------------------------------------------------------------
# test_1entry_skid
#-------------------------------------------------------------------------
def test_1entry_skid( dump_vcd, test_verilog ):
  """Single Element Skid Queue."""

  test_vectors = [

    # Enqueue one element and then dequeue it
    # enq.val enq.rdy enq.bits deq.val deq.rdy deq.bits
    [ 1,      1,      0x0001,  1,      1,      0x0001 ],
    [ 1,      0,      0x0006,  1,      0,      0x0001 ],
    [ 1,      1,      0x0006,  1,      1,      0x0006 ],
    [ 0,      1,      0x0008,  1,      1,      0x0006 ],
    [ 0,      1,      0x0008,  0,      0,      0x0006 ],
    [ 1,      1,      0x000a,  1,      1,      0x000a ],
    [ 0,      1,      0x000c,  1,      1,      0x000a ]

  ]

  # Instantiate and elaborate the model

  model = SingleElementSkidQueue( 16 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value    == test_vector[1]
    assert model.deq.val.value    == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

