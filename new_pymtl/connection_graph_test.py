#=========================================================================
# connection_graph_test.py
#=========================================================================
# Tests verifying the valid construction of connection graphs.

from Model            import Model
from signals          import InPort, OutPort, Wire
from connection_graph import ConnectionEdge

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------
def inst_elab_model( model ):
  x = model()
  x.elaborate()
  return x

def verify_signals( signal_list, ref_list ):
  x = sorted( [(x.name, x.nbits) for x in signal_list ] )
  y = sorted( ref_list )
  assert x == y

def verify_submodules( module_list, ref_list ):
  x = sorted( module_list )
  y = sorted( ref_list )
  assert x == y

def verify_edges( connection_list, ref_list ):
  assert len( connection_list ) == len( ref_list )
  # TODO: could potentially still pass if duplicate items in
  #       connection_list, really need to remove items from ref_list
  def connection_sort( x ):
    return ( x.src_node, x.src_slice, x.dest_node, x.dest_slice )

  c_list = sorted( connection_list, key = connection_sort )
  r_list = sorted( ref_list,        key = connection_sort )
  for x, y in zip( c_list, r_list ):
    assert x.src_node == y.src_node
    assert x.src_slice == y.src_slice
    assert x.dest_node == y.dest_node
    assert x.dest_slice == y.dest_slice


#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class Port_Port( Model ):
  def __init__( s ):
    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_Port_Port():
  m = inst_elab_model( Port_Port )
  verify_signals( m.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out', 8)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in_, m.out ) ] )

#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class Port_RdSl_Port( Model ):
  def __init__( s ):
    s.in_ = InPort ( 8 )
    s.out0 = OutPort( 4 )
    s.out1 = OutPort( 4 )
  def elaborate_logic( s ):
    s.connect( s.in_[0:4], s.out0 )
    s.connect( s.in_[4:8], s.out1 )

def test_Port_RdSl_Port():
  m = inst_elab_model( Port_RdSl_Port )
  verify_signals( m.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out1', 4), ('out0', 4)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in_[0:4], m.out0 ),
                                       ConnectionEdge( m.in_[4:8], m.out1 ),
                                     ] )

#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class Port_RdSl_Overlap_Port( Model ):
  def __init__( s ):
    s.in_ = InPort ( 8 )
    s.out0 = OutPort( 4 )
    s.out1 = OutPort( 6 )
    s.out2 = OutPort( 8 )
  def elaborate_logic( s ):
    s.connect( s.in_[0:4], s.out0 )
    s.connect( s.in_[2:8], s.out1 )
    s.connect( s.in_,      s.out2 )

def test_Port_RdSl_Overlap_Port():
  m = inst_elab_model( Port_RdSl_Overlap_Port )
  verify_signals( m.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out0', 4), ('out1', 6), ('out2', 8)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in_[0:4], m.out0 ),
                                       ConnectionEdge( m.in_[2:8], m.out1 ),
                                       ConnectionEdge( m.in_,      m.out2 ),
                                     ] )

#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class Port_WrSl_Port( Model ):
  def __init__( s ):
    s.in0 = InPort ( 4 )
    s.in1 = InPort ( 4 )
    s.out = OutPort( 8 )
  def elaborate_logic( s ):
    s.connect( s.in0, s.out[0:4] )
    s.connect( s.in1, s.out[4:8] )

def test_Port_WrSl_Port():
  m = inst_elab_model( Port_WrSl_Port )
  verify_signals( m.get_inports(),  [('in0', 4), ('in1', 4), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out', 8), ] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in0, m.out[0:4] ),
                                       ConnectionEdge( m.in1, m.out[4:8] ),
                                     ] )

#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class Port_WrSl_Overlap_Port( Model ):
  def __init__( s ):
    s.in0 = InPort ( 4 )
    s.in1 = InPort ( 6 )
    s.in2 = InPort ( 8 )
    s.out = OutPort( 8 )
    # TODO: this should throw an error!!! Shouldn't be able to overlap
    #       writes to an OutPort...
  def elaborate_logic( s ):
    s.connect( s.in0, s.out[0:4] )
    s.connect( s.in1, s.out[2:8] )
    s.connect( s.in2, s.out      )

def test_Port_WrSl_Overlap_Port():
  m = inst_elab_model( Port_WrSl_Overlap_Port )
  verify_signals( m.get_inports(),  [('in0', 4), ('in1', 6), ('in2', 8),
                                     ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out', 8)] )
  verify_signals( m.get_wires(),    [] )
  #verify_submodules( )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in0, m.out[0:4] ),
                                       ConnectionEdge( m.in1, m.out[2:8] ),
                                       ConnectionEdge( m.in2, m.out ),
                                     ] )


#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class SubMod( Model ):
  def __init__( s ):
    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )

  def elaborate_logic( s ):
    s.mod  = Port_Port()

    s.connect( s.in_, s.mod.in_ )
    s.connect( s.out, s.mod.out )

def test_SubMod():
  m = inst_elab_model( SubMod )

  verify_signals( m.mod.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.mod.get_outports(), [('out', 8)] )
  verify_signals( m.mod.get_wires(),    [] )
  verify_submodules( m.mod.get_submodules(), [] )
  verify_edges( m.mod.get_connections(), [ ConnectionEdge( m.mod.in_, m.mod.out ) ] )

  verify_signals( m.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out', 8)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules(), [ m.mod ] )
  # Make sure direction is correct!
  verify_edges( m.get_connections(), [ ConnectionEdge( m.clk,     m.mod.clk ),
                                       ConnectionEdge( m.reset,   m.mod.reset ),
                                       ConnectionEdge( m.in_,     m.mod.in_ ),
                                       ConnectionEdge( m.mod.out, m.out ),
                                     ] )

#-------------------------------------------------------------------------
# Test0
#-------------------------------------------------------------------------
class SubMod_SL( Model ):
  def __init__( s ):
    s.in1  = InPort (  4 )
    s.in2  = InPort (  4 )
    s.in3  = InPort ( 16 )
    s.out1 = OutPort(  4 )
    s.out2 = OutPort(  4 )
    s.out3 = OutPort( 16 )

  def elaborate_logic( s ):
    s.mod1  = Port_Port()
    s.mod2  = Port_Port()

    s.connect( s.in1,       s.mod1.in_[0:4] )
    s.connect( s.in2,       s.mod1.in_[4:8] )
    s.connect( s.in3[0:8],  s.mod2.in_      )

    s.connect( s.out1,      s.mod1.out[0:4] )
    s.connect( s.out2,      s.mod1.out[4:8] )
    s.connect( s.out3[0:8], s.mod2.out      )

    s.connect( s.in3[8:16], s.out3[8:16]    )

def test_SubMod_SL():
  m = inst_elab_model( SubMod_SL )

  verify_signals( m.mod1.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.mod1.get_outports(), [('out', 8)] )
  verify_signals( m.mod1.get_wires(),    [] )
  verify_submodules( m.mod1.get_submodules(), [] )
  verify_edges( m.mod1.get_connections(), [ ConnectionEdge( m.mod1.in_, m.mod1.out ) ] )

  verify_signals( m.mod2.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.mod2.get_outports(), [('out', 8)] )
  verify_signals( m.mod2.get_wires(),    [] )
  verify_submodules( m.mod2.get_submodules(), [] )
  verify_edges( m.mod2.get_connections(), [ ConnectionEdge( m.mod2.in_, m.mod2.out ) ] )

  verify_signals( m.get_inports(),  [('in1', 4), ('in2', 4), ('in3', 16),
                                     ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out1', 4), ('out2', 4), ('out3', 16)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules(), [ m.mod1, m.mod2 ] )
  # Make sure direction is correct!
  verify_edges( m.get_connections(), [ ConnectionEdge( m.clk,        m.mod1.clk      ),
                                       ConnectionEdge( m.reset,      m.mod1.reset    ),
                                       ConnectionEdge( m.clk,        m.mod2.clk      ),
                                       ConnectionEdge( m.reset,      m.mod2.reset    ),
                                       ConnectionEdge( m.in1,        m.mod1.in_[0:4] ),
                                       ConnectionEdge( m.in2,        m.mod1.in_[4:8] ),
                                       ConnectionEdge( m.in3[0:8],   m.mod2.in_      ),
                                       ConnectionEdge( m.mod1.out[0:4], m.out1,      ),
                                       ConnectionEdge( m.mod1.out[4:8], m.out2,      ),
                                       ConnectionEdge( m.mod2.out     , m.out3[0:8], ),
                                       ConnectionEdge( m.in3[8:16],  m.out3[8:16]    ),
                                     ] )

