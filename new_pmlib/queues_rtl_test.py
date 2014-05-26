#=========================================================================
# queues_rtl_test.py
#=========================================================================
# This file contains unit tests for the queue collection models

from new_pymtl import *
from new_pmlib import TestVectorSimulator, TestSource, TestSink

from queues_rtl import SingleElementNormalQueue
from queues_rtl import SingleElementBypassQueue
from queues_rtl import SingleElementPipelinedQueue
from queues_rtl import SingleElementSkidQueue
from queues_rtl import NormalQueue

#=========================================================================
# Test Vector Tests - Single-Entry
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Normal Queue Test Vector Tests
#-------------------------------------------------------------------------
# Directed performance tests for single element queue. We use the
# TestVectorSimulator to do some white box testing.
def test_single_element_normal_queue_tv( dump_vcd, test_verilog ):

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
  if test_verilog:
    model = get_verilated( model )
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
  if dump_vcd:
    sim.dump_vcd( "SingleElementNormalQueue_tv.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Test Vector Tests
#-------------------------------------------------------------------------
# Directed performance tests for single element queue. We use the
# TestVectorSimulator to do some white box testing.
def test_single_element_bypass_queue_tv( dump_vcd, test_verilog ):

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
    [ 1,      1,      0x0003,  1,      1,      0x0003  ],
    [ 1,      1,      0x0004,  1,      1,      0x0004 ],
    [ 0,      1,      0x0004,  0,      1,      '?'    ],

  ]

  # Instantiate and elaborate the model

  model = SingleElementBypassQueue( 16 )
  if test_verilog:
    model = get_verilated( model )
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
  if dump_vcd:
    sim.dump_vcd( "SingleElementBypassQueue_tv.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Test Vector Tests
#-------------------------------------------------------------------------
# Directed performance tests for single element piped queue. We use the
# TestVectorSimulator to do some white box testing.
def test_single_element_pipe_queue_tv( dump_vcd, test_verilog ):

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
  if test_verilog:
    model = get_verilated( model )
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
  if dump_vcd:
    sim.dump_vcd( "SingleElementPipelinedQueue_tv.vcd" )
  sim.run_test()

#=========================================================================
# Source Sink Tests - Single-Entry
#=========================================================================

#-------------------------------------------------------------------------
# Source Sink Test Harness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay, nbits, test_verilog ):

    # Instantiate models

    s.src    = TestSource ( nbits, src_msgs,  src_delay  )
    s.queue  = ModelType  ( nbits )
    s.sink   = TestSink   ( nbits, sink_msgs, sink_delay )

    if test_verilog:
      s.queue = get_verilated( s.queue )

  def elaborate_logic( s ):

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
# Single-Element Normal Queue Test Source Sink
#-------------------------------------------------------------------------
# Tests for single element queue using test source and sink.

def run_single_element_queue_test( dump_vcd, test_verilog, vcd_file_name,
                  ModelType, src_delay, sink_delay, nbits ):

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
                       src_delay, sink_delay, nbits, test_verilog )
  model.elaborate()

  # Run the test

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

def test_single_element_norm_delay0x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementNormalQueue_src_sink_0x0.vcd",
                SingleElementNormalQueue, 0, 0, 16 )

def test_single_element_norm_delay0x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementNormalQueue_src_sink_0x5.vcd",
                SingleElementNormalQueue, 0, 5, 16 )

def test_single_element_norm_delay5x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementNormalQueue_src_sink_5x0.vcd",
                SingleElementNormalQueue, 5, 0, 16 )

def test_single_element_norm_delay10x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementNormalQueue_src_sink_10x5.vcd",
                SingleElementNormalQueue, 10, 5, 16 )

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Test Source Sink
#-------------------------------------------------------------------------
# Tests for single element queue using test source and sink.

def run_single_element_queue_test( dump_vcd, test_verilog, vcd_file_name,
                  ModelType, src_delay, sink_delay, nbits ):

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
                       src_delay, sink_delay, nbits, test_verilog )
  model.elaborate()

  # Run the test

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

def test_single_element_byp_delay0x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementBypassQueue_src_sink_0x0.vcd",
                SingleElementBypassQueue, 0, 0, 16 )

def test_single_element_byp_delay0x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementBypassQueue_src_sink_0x5.vcd",
                SingleElementBypassQueue, 0, 5, 16 )

def test_single_element_byp_delay5x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementBypassQueue_src_sink_5x0.vcd",
                SingleElementBypassQueue, 5, 0, 16 )

def test_single_element_byp_delay10x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementBypassQueue_src_sink_10x5.vcd",
                SingleElementBypassQueue, 10, 5, 16 )

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Test Source Sink
#-------------------------------------------------------------------------
# Tests for single element queue using test source and sink.

def run_single_element_queue_test( dump_vcd, test_verilog, vcd_file_name,
                                   ModelType, src_delay, sink_delay, nbits ):

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
                       src_delay, sink_delay, nbits, test_verilog )
  model.elaborate()

  # Run the test

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

def test_single_element_pipe_delay0x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementPipelinedQueue_src_sink_0x0.vcd",
                SingleElementPipelinedQueue, 0, 0, 16 )

def test_single_element_pipe_delay0x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementPipelinedQueue_src_sink_0x5.vcd",
                SingleElementPipelinedQueue, 0, 5, 16 )

def test_single_element_pipe_delay5x0( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementPipelinedQueue_src_sink_5x0.vcd",
                SingleElementPipelinedQueue, 5, 0, 16 )

def test_single_element_pipe_delay10x5( dump_vcd, test_verilog ):
  run_single_element_queue_test(
                dump_vcd, test_verilog,
                "SingleElementPipelinedQueue_src_sink_10x5.vcd",
                SingleElementPipelinedQueue, 10, 5, 16 )

#=========================================================================
# Test Vector Tests - Multi-Entry
#=========================================================================

#-------------------------------------------------------------------------
# Normal Queue
#-------------------------------------------------------------------------
# Tests for Multiple Entry Normal Queues

def run_test_queue( dump_vcd, test_verilog, ModelType, num_entries,
                    test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( num_entries, 16 )
  if test_verilog:
    model = get_verilated( model )
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
  if dump_vcd:
    sim.dump_vcd( "test_queue" + str(num_entries) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Two Element Queue
#-------------------------------------------------------------------------

def test_queue_2( dump_vcd, test_verilog ):
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
# Three Element Queue
#-------------------------------------------------------------------------

def test_queue_3( dump_vcd, test_verilog ):
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

#-------------------------------------------------------------------------
# Single Element Skid Queue
#-------------------------------------------------------------------------
def test_single_element_pipe_queue_tv( dump_vcd, test_verilog ):

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
  if test_verilog:
    model = get_verilated( model )
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
  if dump_vcd:
    sim.dump_vcd( "SingleElementPipelinedQueue_tv.vcd" )
  sim.run_test()

