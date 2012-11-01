#=========================================================================
# Queue Test Suite
#=========================================================================

from pymtl import *

from pmlib       import TestVectorSimulator
from Queue       import NormalQueue

#-------------------------------------------------------------------------
# Test Harness
#-------------------------------------------------------------------------

def run_test_queue( dump_vcd, ModelType, size, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( size, 16 )
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

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_queue" + str(num_inputs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Two Element Queue
#-------------------------------------------------------------------------

def test_queue_2( dump_vcd ):
  run_test_queue( dump_vcd, NormalQueue, 2, [
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
    [ 1,      1,      0x0003,  1,      0,      '?'    ],
    [ 1,      0,      0x0004,  1,      1,      0x0003 ],
    [ 1,      1,      0x0004,  1,      0,      '?'    ],
    [ 0,      0,      0x0004,  1,      1,      0x0003 ],
    [ 0,      1,      0x0004,  1,      1,      0x0004 ],
    [ 0,      1,      0x0004,  0,      1,      '?'    ],
  ])

#-------------------------------------------------------------------------
# Three Element Queue
#-------------------------------------------------------------------------

def test_queue_3( dump_vcd ):
  run_test_queue( dump_vcd, NormalQueue, 3, [
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

