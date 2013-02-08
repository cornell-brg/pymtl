#-------------------------------------------------------------------------
# Test Queue using ValRdy interface
#-------------------------------------------------------------------------

from pymtl import *

from valrdy import InValRdyBundle, OutValRdyBundle

from valrdy_test import ValRdyQueue

import pmlib
import os

from pymtl.verilator_sim import get_verilated

#-------------------------------------------------------------------------
# Test Sim
#-------------------------------------------------------------------------

def test_portbundle_queue_sim( dump_vcd ):

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

  model = get_verilated( ValRdyQueue( 16 ) )
  model.elaborate()

  # Since the verilated module doesn't have line_trace defined, instead
  # we hackily add the line_trace method to the existing wrapper instance.
  def temp( self ):
    return "{} {} {} () {} {} {}"\
      .format( self.enq.msg.value, self.enq.val.value, self.enq.rdy.value,
               self.deq.msg.value, self.deq.val.value, self.deq.rdy.value )
  import types
  f = types.MethodType( temp, model, ValRdyQueue )
  model.line_trace = f


  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.value = test_vector[0]
    model.enq.msg.value = test_vector[2]
    model.deq.rdy.value = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.value == test_vector[1]
    assert model.deq.val.value == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.value == test_vector[5]

  # Run the test

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "valrdy_test.vcd" )
  sim.run_test()

