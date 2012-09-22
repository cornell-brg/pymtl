#=========================================================================
# queues
#=========================================================================
# This file contains unit tests for the queue collection models

from pymtl import *
import pmlib

from queues import SingleElementNormalQueue

#-------------------------------------------------------------------------------
# Single-Element Normal Queue Test Vector Tests
#-------------------------------------------------------------------------------
# Directed performance tests for single element queue. We use the
# TestVectorSimulator to do some white box testing.

def test_single_element_normal_queue_tv( dump_vcd ):

  test_vectors = [

    # Enqueue one element and then dequeue it
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      0,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
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

  model = SingleElementNormalQueue( nbits=16 )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq_val.value  = test_vector[0]
    model.enq_bits.value = test_vector[2]
    model.deq_rdy.value  = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq_rdy.value  == test_vector[1]
    assert model.deq_val.value  == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq_bits.value == test_vector[5]

  # Run the test

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "SingleElementNormalQueue_tv.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------------
# Single-Element Normal Queue Test Source Sink
#-------------------------------------------------------------------------------
# Tests for single element queue using test source and sink.

class TestHarness (Model):

  def __init__( self, ModelType, src_msgs, sink_msgs,
                src_delay, sink_delay, nbits ):

    # Instantiate models

    self.src    = pmlib.TestSource ( nbits, src_msgs,  src_delay  )
    self.queue  = ModelType        ( nbits )
    self.sink   = pmlib.TestSink   ( nbits, sink_msgs, sink_delay )

    # Connect

    connect( self.src.out_val, self.queue.enq_val  )
    connect( self.src.out_rdy, self.queue.enq_rdy  )
    connect( self.src.out_msg, self.queue.enq_bits )
    connect( self.sink.in_val, self.queue.deq_val  )
    connect( self.sink.in_rdy, self.queue.deq_rdy  )
    connect( self.sink.in_msg, self.queue.deq_bits )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " > " + \
           self.queue.line_trace() + " > " + \
           self.sink.line_trace()

def run_single_element_queue_test( dump_vcd, vcd_file_name,
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
                       src_delay, sink_delay, nbits )
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

def test_single_element_delay0x0( dump_vcd ):
  run_single_element_queue_test(
                dump_vcd,
                "SingleElementNormalQueue_src_sink_0x0.vcd",
                SingleElementNormalQueue, 0, 0, 16 )

def test_single_element_delay0x5( dump_vcd ):
  run_single_element_queue_test(
                dump_vcd,
                "SingleElementNormalQueue_src_sink_0x5.vcd",
                SingleElementNormalQueue, 0, 5, 16 )

def test_single_element_delay5x0( dump_vcd ):
  run_single_element_queue_test(
                dump_vcd,
                "SingleElementNormalQueue_src_sink_5x0.vcd",
                SingleElementNormalQueue, 5, 0, 16 )

def test_single_element_delay10x5( dump_vcd ):
  run_single_element_queue_test(
                dump_vcd,
                "SingleElementNormalQueue_src_sink_10x5.vcd",
                SingleElementNormalQueue, 10, 5, 16 )

