#=========================================================================
# ValRdyBundle_test.py
#=========================================================================
# Unit tests for the ValRdy PortBundle.

from new_pymtl    import *
from ValRdyBundle import InValRdyBundle, OutValRdyBundle
from new_pmlib    import TestVectorSimulator

#-------------------------------------------------------------------------
# ValRdyQueue
#-------------------------------------------------------------------------
# Test Queue using the ValRdy interface.
class ValRdyQueue( Model ):

  def __init__( s, nbits ):

    s.enq   = InValRdyBundle( nbits )
    s.deq   = OutValRdyBundle( nbits )

    s.full  = Wire( 1 )
    s.wen   = Wire( 1 )

  def elaborate_logic( s ):

    @s.combinational
    def comb():

      s.wen.v      = ~s.full & s.enq.val
      s.enq.rdy.v  = ~s.full
      s.deq.val.v  = s.full

    @s.posedge_clk
    def seq():

      # Data Register
      if s.wen:
        s.deq.msg.next = s.enq.msg

      # Full Bit
      if s.reset:
        s.full.next = 0
      elif   s.deq.rdy and s.deq.val:
        s.full.next = 0
      elif s.enq.rdy and s.enq.val:
        s.full.next = 1
      else:
        s.full.next = s.full

  def line_trace( s ):

    return "{} () {}".format( s.enq, s.deq )

#-------------------------------------------------------------------------
# test_valrdy_sim
#-------------------------------------------------------------------------
def test_valrdy_sim( dump_vcd ):

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

  model = ValRdyQueue( 16 )
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

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  #if dump_vcd:
  #  sim.dump_vcd( "valrdy_test.vcd" )
  sim.run_test()

##-------------------------------------------------------------------------
## Test Translation
##-------------------------------------------------------------------------
#
#def test_valrdy_translation( ):
#
#    # Create temporary file to write out Verilog
#
#    temp_file = "valrdy_test.v"
#    compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
#                    "-Wno-sensitivity-entire-array " + temp_file)
#    fd = open( temp_file, 'w' )
#
#    # Instantiate and elaborate model
#
#    model = ValRdyQueue( 16 )
#    model.elaborate()
#
#    # Translate
#
#    code = VerilogTranslationTool( model, fd )
#    fd.close()
#
#    # Make sure translation compiles
#    # TODO: figure out a way to group PortBundles during translation?
#
#    x = os.system( compile_cmd )
#    assert x == 0


