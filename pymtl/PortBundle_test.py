#=========================================================================
# PortBundle Test Suite
#=========================================================================

from model      import *
from simulate   import *
from translate  import *

from PortBundle import PortBundle, create_PortBundles

import pmlib

import os

#-------------------------------------------------------------------------
# Example PortBundle
#-------------------------------------------------------------------------

class ValRdyBundle( PortBundle ):
  def __init__( self, nbits ):
    self.msg = InPort  ( nbits )
    self.val = InPort  ( 1 )
    self.rdy = OutPort ( 1 )

InValRdyBundle, OutValRdyBundle = create_PortBundles( ValRdyBundle )

#-------------------------------------------------------------------------
# Example Module using PortBundle
#-------------------------------------------------------------------------

class PortBundleQueue(Model):

  def __init__( self, nbits ):

    self.enq   = InValRdyBundle( nbits )
    self.deq   = OutValRdyBundle( nbits )

    self.full  = Wire( 1 )
    self.wen   = Wire( 1 )

  @combinational
  def comb( self ):

    self.wen.value       = ~self.full.value & self.enq.val.value
    self.enq.rdy.value   = ~self.full.value
    self.deq.val.value   = self.full.value

  @posedge_clk
  def seq( self ):

    # Data Register
    if self.wen.value:
      self.deq.msg.next = self.enq.msg.value

    # Full Bit
    if self.reset.value:
      self.full.next = 0
    elif   self.deq.rdy.value and self.deq.val.value:
      self.full.next = 0
    elif self.enq.rdy.value and self.enq.val.value:
      self.full.next = 1
    else:
      self.full.next = self.full.value


  def line_trace( self ):

    return "{} {} {} () {} {} {}"\
      .format( self.enq.msg.value, self.enq.val.value, self.enq.rdy.value,
               self.deq.msg.value, self.deq.val.value, self.deq.rdy.value )


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

  model = PortBundleQueue( 16 )
  model.elaborate()

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
    sim.dump_vcd( "PortBundle_test.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Test Translation
#-------------------------------------------------------------------------

def test_portbundle_queue_translation( ):

    # Create temporary file to write out Verilog

    temp_file = "PortBundle_test.v"
    compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                    "-Wno-sensitivity-entire-array " + temp_file)
    fd = open( temp_file, 'w' )

    # Instantiate and elaborate model

    model = PortBundleQueue( 16 )
    model.elaborate()

    # Translate

    code = VerilogTranslationTool( model, fd )
    fd.close()

    # Make sure translation compiles
    # TODO: figure out a way to group PortBundles during translation?

    x = os.system( compile_cmd )
    assert x == 0

