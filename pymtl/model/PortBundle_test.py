#=======================================================================
# PortBundle Test Suite
#=======================================================================

from Model      import *
from PortBundle import PortBundle, create_PortBundles
from pymtl      import SimulationTool
from pclib.test import TestVectorSimulator

#---------------------------------------------------------------------
# Example PortBundle
#---------------------------------------------------------------------

class ValRdyBundle( PortBundle ):
  def __init__( s, dtype ):
    s.msg = InPort  ( dtype )
    s.val = InPort  ( 1 )
    s.rdy = OutPort ( 1 )

  def __str__( s ):

    str = "{}".format( s.msg )
    num_chars = len(str)

    if       s.val and not s.rdy:
      str = "#".ljust( num_chars )
    elif not s.val and     s.rdy:
      str = " ".ljust( num_chars )
    elif not s.val and not s.rdy:
      str = ".".ljust( num_chars )

    return str

InValRdyBundle, OutValRdyBundle = create_PortBundles( ValRdyBundle )

#---------------------------------------------------------------------
# Example Module using PortBundle
#---------------------------------------------------------------------

class PortBundleQueue( Model ):

  def __init__( s, dtype ):

    s.enq   = InValRdyBundle ( dtype )
    s.deq   = OutValRdyBundle( dtype )

    s.full  = Wire( 1 )
    s.wen   = Wire( 1 )

  def elaborate_logic( s ):

    s.full  = Wire( 1 )
    s.wen   = Wire( 1 )

    @s.combinational
    def comb():

      s.wen.v       = ~s.full & s.enq.val
      s.enq.rdy.v   = ~s.full
      s.deq.val.v   =  s.full

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

#-----------------------------------------------------------------------
# Test Elaboration
#-----------------------------------------------------------------------

from Model_test import verify_signals, verify_submodules, verify_edges

def test_elaboration():

  m = PortBundleQueue( 8 )
  m.elaborate()

  verify_signals( m.enq.get_ports(),[('enq.msg', 8), ('enq.val', 1), ('enq.rdy', 1),] )
  verify_signals( m.deq.get_ports(),[('deq.msg', 8), ('deq.val', 1), ('deq.rdy', 1),] )

  verify_signals( m.get_inports(),  [('enq.msg', 8), ('enq.val', 1), ('deq.rdy', 1),
                                     ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('deq.msg', 8), ('deq.val', 1), ('enq.rdy', 1)] )
  verify_signals( m.get_wires(),    [('full', 1), ('wen', 1 )] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [] )

#-----------------------------------------------------------------------
# Example Module Connecting PortBundles
#-----------------------------------------------------------------------

class TwoQueues( Model ):

  def __init__( s, dtype ):

    s.in_ = InValRdyBundle ( dtype )
    s.out = OutValRdyBundle( dtype )

    s.q1 = PortBundleQueue ( dtype )
    s.q2 = PortBundleQueue ( dtype )

    s.connect( s.in_,    s.q1.enq )
    s.connect( s.q1.deq, s.q2.enq )
    s.connect( s.q2.deq, s.out    )

#-----------------------------------------------------------------------
# Test Elaboration
#-----------------------------------------------------------------------

def test_connect():

  m = TwoQueues( 8 )
  m.elaborate()
  verify_signals( m.get_inports(),  [('in_.msg', 8), ('in_.val', 1), ('out.rdy', 1),
                                     ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out.msg', 8), ('out.val', 1), ('in_.rdy', 1)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [m.q1, m.q2] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.clk,        m.q1.clk     ),
                                       ConnectionEdge( m.reset,      m.q1.reset   ),
                                       ConnectionEdge( m.clk,        m.q2.clk     ),
                                       ConnectionEdge( m.reset,      m.q2.reset   ),

                                       ConnectionEdge( m.in_.msg,    m.q1.enq.msg ),
                                       ConnectionEdge( m.in_.val,    m.q1.enq.val ),
                                       ConnectionEdge( m.q1.enq.rdy, m.in_.rdy    ),

                                       ConnectionEdge( m.q1.deq.msg, m.q2.enq.msg ),
                                       ConnectionEdge( m.q1.deq.val, m.q2.enq.val ),
                                       ConnectionEdge( m.q2.enq.rdy, m.q1.deq.rdy ),

                                       ConnectionEdge( m.q2.deq.msg, m.out.msg    ),
                                       ConnectionEdge( m.q2.deq.val, m.out.val    ),
                                       ConnectionEdge( m.out.rdy,    m.q2.deq.rdy ),
                                     ] )

#-----------------------------------------------------------------------
# Test Sim
#-----------------------------------------------------------------------

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
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    model.enq.val.v = test_vector[0]
    model.enq.msg.v = test_vector[2]
    model.deq.rdy.v = test_vector[4]

  def tv_out( model, test_vector ):

    assert model.enq.rdy.v == test_vector[1]
    assert model.deq.val.v == test_vector[3]
    if not test_vector[5] == '?':
      assert model.deq.msg.v == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# Example Module using List of PortBundle
#-----------------------------------------------------------------------

class ParameterizablePortBundleQueue( Model ):

  def __init__( s, dtype, nports ):

    s.nports = nports

    s.enq    = [ InValRdyBundle ( dtype ) for x in range( s.nports ) ]
    s.deq    = [ OutValRdyBundle( dtype ) for x in range( s.nports ) ]

  def elaborate_logic( s ):

    s.full  = [ Wire( 1 ) for x in range( s.nports ) ]
    s.wen   = [ Wire( 1 ) for x in range( s.nports ) ]

    @s.combinational
    def comb():

      for i in range( s.nports ):
        s.wen[i].v       = ~s.full[i] & s.enq[i].val
        s.enq[i].rdy.v   = ~s.full[i]
        s.deq[i].val.v   =  s.full[i]

    @s.posedge_clk
    def seq():

      for i in range( s.nports ):

        # Data Register
        if s.wen[i]:
          s.deq[i].msg.next = s.enq[i].msg

        # Full Bit
        if   s.reset:
          s.full[i].next = 0
        elif s.deq[i].rdy and s.deq[i].val:
          s.full[i].next = 0
        elif s.enq[i].rdy and s.enq[i].val:
          s.full[i].next = 1
        else:
          s.full[i].next = s.full[i]


  def line_trace( s ):

    print_str = ''
    for enq, deq in zip( s.enq, s.deq ):
      print_str += "{} () {} ".format( enq, deq )

    return print_str

#-----------------------------------------------------------------------
# Test Sim
#-----------------------------------------------------------------------

def test_portbundle_param_queue_sim( dump_vcd ):

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

  nports = 4
  model  = ParameterizablePortBundleQueue( 16, nports )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    for i in range( nports ):
      model.enq[i].val.v = test_vector[0]
      model.enq[i].msg.v = test_vector[2]
      model.deq[i].rdy.v = test_vector[4]

  def tv_out( model, test_vector ):

    for i in range( nports ):
      assert model.enq[i].rdy.v   == test_vector[1]
      assert model.deq[i].val.v   == test_vector[3]
      if not test_vector[5] == '?':
        assert model.deq[i].msg.v == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# Test Translation
#-----------------------------------------------------------------------
#
#def test_portbundle_queue_translation( ):
#
#    # Create temporary file to write out Verilog
#
#    temp_file = "PortBundle_test.v"
#    compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
#                    "-Wno-sensitivity-entire-array " + temp_file)
#    fd = open( temp_file, 'w' )
#
#    # Instantiate and elaborate model
#
#    model = PortBundleQueue( 16 )
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
#

#-----------------------------------------------------------------------
# Example Module using List of PortBundle with BitStructs
#-----------------------------------------------------------------------

from ..datatypes.BitStruct_test import MemMsg
class ParameterizablePortBundleBitStructQueue( Model ):

  def __init__( s, nbits, nports ):

    s.nports = nports

    dtype = MemMsg( 16, 32 )
    s.enq = InValRdyBundle [ nports ]( dtype )
    s.deq = OutValRdyBundle[ nports ]( dtype )

  def elaborate_logic( s ):

    s.full  = Wire[ s.nports ]( 1 )
    s.wen   = Wire[ s.nports ]( 1 )

    @s.combinational
    def comb():

      for i in range( s.nports ):
        s.wen[i].v       = ~s.full[i] & s.enq[i].val
        s.enq[i].rdy.v   = ~s.full[i]
        s.deq[i].val.v   =  s.full[i]

    @s.posedge_clk
    def seq():

      for i in range( s.nports ):

        # Data Register
        if s.wen[i]:
          s.deq[i].msg.type_.next = s.enq[i].msg.type_
          s.deq[i].msg.len .next = s.enq[i].msg.len
          s.deq[i].msg.addr.next = s.enq[i].msg.addr
          s.deq[i].msg.data.next = s.enq[i].msg.data

        # Full Bit
        if   s.reset:
          s.full[i].next = 0
        elif s.deq[i].rdy and s.deq[i].val:
          s.full[i].next = 0
        elif s.enq[i].rdy and s.enq[i].val:
          s.full[i].next = 1
        else:
          s.full[i].next = s.full[i]


  def line_trace( s ):

    print_str = ''
    for enq, deq in zip( s.enq, s.deq ):
      print_str += "{} () {} ".format( enq, deq )

    return print_str

def test_portbundle_bitstruct_param_queue_sim( dump_vcd ):

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

  nports = 4
  model  = ParameterizablePortBundleBitStructQueue( 16, nports )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):

    for i in range( nports ):
      model.enq[i].val.v = test_vector[0]
      model.enq[i].msg.v = test_vector[2]
      model.deq[i].rdy.v = test_vector[4]

  def tv_out( model, test_vector ):

    for i in range( nports ):
      assert model.enq[i].rdy.v   == test_vector[1]
      assert model.deq[i].val.v   == test_vector[3]
      if not test_vector[5] == '?':
        assert model.deq[i].msg.v == test_vector[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
