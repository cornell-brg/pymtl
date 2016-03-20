#=======================================================================
# Model_test.py
#=======================================================================
# Tests verifying the valid construction and elaboration of models.

from __future__ import print_function

from Model            import Model
from signals          import InPort, OutPort, Wire
from ConnectionEdge   import ConnectionEdge, PyMTLConnectError
from ..datatypes.Bits import Bits

import pytest

#-----------------------------------------------------------------------
# Utility Functions
#-----------------------------------------------------------------------

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
    return (x.src_node.fullname, x.src_slice, x.dest_node.fullname, x.dest_slice)

  c_list = sorted( connection_list, key = connection_sort )
  r_list = sorted( ref_list,        key = connection_sort )
  for x, y in zip( c_list, r_list ):
    assert x.src_node == y.src_node
    assert x.src_slice == y.src_slice
    print( x.src_node.name, y.src_node.name )
    print( x.dest_node.name, y.dest_node.name )
    assert x.dest_node == y.dest_node
    assert x.dest_slice == y.dest_slice


#-----------------------------------------------------------------------
# Port_Port_Bits
#-----------------------------------------------------------------------

class Port_Port_Bits( Model ):
  def __init__( s ):
    s.in_ = InPort ( Bits( 8 ) )
    s.out = OutPort( Bits( 8 ) )
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_Port_Port_Bits():
  m = inst_elab_model( Port_Port_Bits )
  verify_signals( m.get_inports(),  [('in_', 8), ('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out', 8)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules() , [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( m.in_, m.out ) ] )

#-----------------------------------------------------------------------
# Port_Port
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Port_RdSl_Port
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Port_RdSl_Overlap_Port
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Port_WrSl_Port
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Port_WrSl_Overlap_Port
#-----------------------------------------------------------------------

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


#-----------------------------------------------------------------------
# SubMod
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# SubMod_SL
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# PortWire
#-----------------------------------------------------------------------
# TODO: add wire tests!

#-----------------------------------------------------------------------
# PortConst
#-----------------------------------------------------------------------

class PortConst( Model ):
  def __init__( s ):
    s.out0 = OutPort( 4 )
    s.out1 = OutPort( 4 )

  def elaborate_logic( s ):
    s.connect( 8,      s.out0 )
    s.connect( s.out1,      4 )

def test_PortConst():
  m = inst_elab_model( PortConst )

  verify_signals( m.get_inports(),  [('clk', 1), ('reset', 1)] )
  verify_signals( m.get_outports(), [('out0', 4), ('out1', 4)] )
  verify_signals( m.get_wires(),    [] )
  verify_submodules( m.get_submodules(), [] )
  verify_edges( m.get_connections(), [ ConnectionEdge( 8, m.out0 ),
                                       ConnectionEdge( 4, m.out1 )
                                     ] )

#-----------------------------------------------------------------------
# PortConstAssertSize
#-----------------------------------------------------------------------

class PortConstAssertSize1( Model ):
  def __init__( s ):
    s.out = OutPort( 4 )
  def elaborate_logic( s ):
    s.connect( s.out, 32 )

class PortConstAssertSize2( Model ):
  def __init__( s ):
    s.out = OutPort( 4 )
  def elaborate_logic( s ):
    s.connect( 32, s.out )

def test_PortConstAssertSize():
  with pytest.raises( PyMTLConnectError ):
    m = inst_elab_model( PortConstAssertSize1 )
  with pytest.raises( PyMTLConnectError ):
    m = inst_elab_model( PortConstAssertSize2 )

#-----------------------------------------------------------------------
# ModelArgsHash
#-----------------------------------------------------------------------
# Verify that we create unique hashes for the following four
# combinations:
#
#   - constructor without default values + instance uses pos args
#   - constructor without default values + instance uses kw  args
#   - constructor with    default values + instance uses pos args
#   - constructor with    default values + instance uses kw  args
#

def cmp_class_name_eq( model1, model2 ):
  model1.elaborate()
  model2.elaborate()
  assert model1.class_name == model2.class_name

def cmp_class_name_neq( model1, model2 ):
  model1.elaborate()
  model2.elaborate()
  assert model1.class_name != model2.class_name

class ModelArgsHashWithoutDefault( Model ):
  def __init__( s, arg1, arg2 ):
    s.arg1 = arg1
    s.arg2 = arg2

def test_ModelArgsHashWithoutDefault():

  M = ModelArgsHashWithoutDefault

  cmp_class_name_eq  ( M(      3,      4 ), M(      3,      4 ) )
  cmp_class_name_neq ( M(      3,      4 ), M(      5,      6 ) )

  cmp_class_name_eq  ( M(      3, arg2=4 ), M(      3, arg2=4 ) )
  cmp_class_name_neq ( M(      3, arg2=4 ), M(      5, arg2=6 ) )

  cmp_class_name_eq  ( M( arg1=3, arg2=4 ), M( arg1=3, arg2=4 ) )
  cmp_class_name_neq ( M( arg1=3, arg2=4 ), M( arg1=5, arg2=6 ) )

  cmp_class_name_eq  ( M( arg2=4, arg1=3 ), M( arg1=3, arg2=4 ) )
  cmp_class_name_neq ( M( arg2=4, arg1=3 ), M( arg1=5, arg2=6 ) )

class ModelArgsHashWithDefault( Model ):
  def __init__( s, arg1=1, arg2=2 ):
    s.arg1 = arg1
    s.arg2 = arg2

def test_ModelArgsHashWithDefault():

  M = ModelArgsHashWithDefault

  cmp_class_name_eq  ( M(      3,      4 ), M(      3,      4 ) )
  cmp_class_name_neq ( M(      3,      4 ), M(      5,      6 ) )

  cmp_class_name_eq  ( M(      3, arg2=4 ), M(      3, arg2=4 ) )
  cmp_class_name_neq ( M(      3, arg2=4 ), M(      5, arg2=6 ) )

  cmp_class_name_eq  ( M( arg1=3, arg2=4 ), M( arg1=3, arg2=4 ) )
  cmp_class_name_neq ( M( arg1=3, arg2=4 ), M( arg1=5, arg2=6 ) )

  cmp_class_name_eq  ( M( arg2=4, arg1=3 ), M( arg1=3, arg2=4 ) )
  cmp_class_name_neq ( M( arg2=4, arg1=3 ), M( arg1=5, arg2=6 ) )

  cmp_class_name_eq  ( M(      3 ), M(      3 ) )
  cmp_class_name_neq ( M(      3 ), M(      5 ) )

  cmp_class_name_eq  ( M( arg1=3 ), M( arg1=3 ) )
  cmp_class_name_neq ( M( arg1=3 ), M( arg1=5 ) )

#-----------------------------------------------------------------------
# ClassNameCollision
#-----------------------------------------------------------------------
# A model's class_name is generated during elaboration based on a hash of
# the list of arguments and their values. If two models have the same
# class name, same args, and same arg values (e.g., two Mux's each with 2
# ports and 47 bits, but one is one-hot and one is not), the hashes will
# collide. In Verilog translation, collided names result in both modules
# pointing at the same module definition, so one is incorrect.
#
# This collision is prevented by adding the model's __module__ to the hash
# generation (_gen_class_name). A class's __module__ will be different
# when importing from different modules.
#
# This test case creates two models of class name ClassNameCollisionModel,
# one in this module and one in the Model_dummy_test.py module. They have
# the same name and same args. The test case checks that their Model
# class_name's do not collide after elaborate.

from Model_dummy_test import ClassNameCollisionModel as ClassNameCollisionModelDummy

class ClassNameCollisionModel( Model ):
  def __init__( s, arg1, arg2 ):
    s.arg1 = arg1
    s.arg2 = arg2

def test_ClassNameCollision():
  model1 = ClassNameCollisionModel     ( 1, 2 ) # same arg values
  model2 = ClassNameCollisionModelDummy( 1, 2 ) # same arg values
  model1.elaborate()
  model2.elaborate()
  assert model1.class_name != model2.class_name

#-----------------------------------------------------------------------
# ClassNameCollisionSameModule
#-----------------------------------------------------------------------
# The ClassNameCollision test case checks for class name collisions due to
# same-name same-args classes in _different_ modules. Collisions can still
# happen if the same-name same-arg classes are in the same module. This
# test case checks for this kind of collision using two classes named
# "ClassNameCollision" placed at different levels of the hierarchy, but
# instantiated with the same name and same args.
#
# TODO: This corner case is not yet fixed and may not need to be fixed. If
# this seems like it is ever going to happen in practice, we will need
# this test case to pass. This test case will pass if we use __class__ in
# the class name generation (_gen_class_name). While this always avoids
# collisions, it also gives a differently named translated Verilog file on
# every run. Having the filename always changing can make it difficult for
# other tools to point to the generated Verilog. Using __module__ in the
# hash generation still avoids class name collisions across modules but
# also keeps the name of the translated Verilog file the same. It means we
# are not avoiding same-class-name same-args collisions in the same
# module, but this seems kind of rare.

# class ClassNameCollisionSameModule( Model ):
#   def __init__( s, arg1, arg2 ):
#     s.arg1 = arg1
#     s.arg2 = arg2
#
#   class ClassNameCollisionSameModule( Model ):
#     def __init__( s, arg1, arg2 ):
#       s.arg1 = arg1
#       s.arg2 = arg2
#
# def test_ClassNameCollisionSameModule():
#   model1 = ClassNameCollisionSameModule( 1, 2 )
#   model2 = ClassNameCollisionSameModule.ClassNameCollisionSameModule( 1, 2 )
#   model1.elaborate()
#   model2.elaborate()
#   assert model1.class_name != model2.class_name

