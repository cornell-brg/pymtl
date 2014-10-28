#=======================================================================
# BitStruct Test Suite
#=======================================================================

import math

from pymtl     import *
from Bits      import Bits
from BitStruct import BitStructDefinition, BitField

#-----------------------------------------------------------------------
# Example BitStruct and Enums
#-----------------------------------------------------------------------

class MemMsg( BitStructDefinition ):

  # Enums for type field
  READ  = 0
  WRITE = 1

  # Enums for len field
  BYTE  = 1
  HALF  = 2
  WORD  = 0

  def __init__( s, addr_nbits, data_nbits ):

    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    len_nbits = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    s.type = BitField( 1          )
    s.addr = BitField( addr_nbits )
    s.len  = BitField( len_nbits  )
    s.data = BitField( data_nbits )

    # TODO: test other BitField types (for overlapping fields)
    # BitField( nbits )
    # BitField( start, nbits )
    # BitField( start, stop )  # Excl, like python range

#-----------------------------------------------------------------------
# Hacky BitStruct test
#-----------------------------------------------------------------------

def test_bitstruct_fields():

  # Create MemMsg Bitstruct
  x = MemMsg( 16, 32 )

  # Test v assignment
  assert x.v == 0
  x.v = 0x5f0cd0f0f0f0f
  assert x.v == 0x5f0cd0f0f0f0f

  # Test field nbits attributes
  assert x.type.nbits == 1
  assert x.addr.nbits == 16
  assert x.len.nbits  == 2
  assert x.data.nbits == 32
  assert x.nbits      == 1 + 16 + 2 + 32

  # Test field slices attributes
  assert x.type.slice == slice( 50, 51 )
  assert x.addr.slice == slice( 34, 50 )
  assert x.len.slice  == slice( 32, 34 )
  assert x.data.slice == slice(  0, 32 )
  assert x.slice      == slice( None )

  # Test access to vs
  assert x.type.v == 1
  assert x.addr.v == 0x7c33
  assert x.len.v  == 1
  assert x.data.v == 0x0f0f0f0f
  assert x.nbits  == 1 + 2 + 16 + 32
  assert x.nbits  == 1 + 2 + 16 + 32

  assert MemMsg.READ  == 0
  assert MemMsg.WRITE == 1
  assert MemMsg.BYTE  == 1
  assert MemMsg.HALF  == 2
  assert MemMsg.WORD  == 0

  # Test assignment
  x.type.v = MemMsg.READ
  assert x.type.v == 0
  x.type.v = MemMsg.WRITE
  assert x.type.v == 1

  x.len.v = MemMsg.HALF
  assert x.len.v == 2
  x.len.v = MemMsg.BYTE
  assert x.len.v == 1
  x.len.v = MemMsg.WORD
  assert x.len.v == 0

  x.addr.v = 0xbeef
  assert x.addr.v == 0xbeef

  x.data.v = 0xabcd1234
  assert x.data.v == 0xabcd1234

#-----------------------------------------------------------------------
# Test new instances created by __call__
#-----------------------------------------------------------------------

def test_bitstruct_call():

    # Test instantiation
    msg_type = MemMsg( 16, 32 )
    x = msg_type()
    y = msg_type()
    assert type( x ) == type( y )
    assert x is not y

    # Test updates
    x.addr = 10
    y.addr = 8
    assert x.addr != y.addr

#-----------------------------------------------------------------------
# Test two instances with same params
#-----------------------------------------------------------------------
import pytest
@pytest.mark.xfail
def test_bitstruct_call():

  bits_a = Bits( 8 )
  bits_b = Bits( 8 )

  # Passes.  Bits doesn't use metaclasses.
  assert type( bits_a ) == type( bits_b )

  type_a = MemMsg( 16, 32 )
  type_b = MemMsg( 16, 32 )

  # Fails.  Each call to MemMsg uses metaclassed to build a new class.
  # Possible fixes: caching?
  assert type( type_a ) == type( type_b )

#-----------------------------------------------------------------------
# Check Combinational Logic
#-----------------------------------------------------------------------

class CombLogicMsgModel( Model ):
  def __init__( s ):

    # TODO: would like to have below syntax, but then s.in_ and s.out
    #       point to the same Bits object!
    #       (Remember, MemMsg() and Bits() return an object instance,
    #       not a type!)
    #       How should we do this syntax?
    #msg = MemMsg( 16, 32 )
    #s.in_ = InPort ( msg )
    #s.out = OutPort( msg )

    s.in_ = InPort ( MemMsg( 16, 32 ) )
    s.out = OutPort( MemMsg( 16, 32 ) )

  def elaborate_logic( s ):

    @s.combinational
    def logic():

      s.out.type.v = s.in_.type
      s.out.len.v  = s.in_.len
      s.out.addr.v = s.in_.addr
      s.out.data.v = s.in_.data

def test_msg_comb_logic():

  model = CombLogicMsgModel()
  model.elaborate()
  sim   = SimulationTool(model)

  assert model.in_.nbits      == 1 + 2 + 16 + 32
  assert model.in_.type.nbits == 1
  assert model.in_.len.nbits  == 2
  assert model.in_.addr.nbits == 16
  assert model.in_.data.nbits == 32

  assert model.out.type.slice == slice( 50, 51 )
  assert model.out.addr.slice == slice( 34, 50 )
  assert model.out.len.slice  == slice( 32, 34 )
  assert model.out.data.slice == slice(  0, 32 )
  assert model.out.slice      == slice( None )

  model.in_.v = 1
  assert model.out.v == 0
  sim.eval_combinational()
  assert model.out.v == 1

  model.in_.v = 2
  sim.eval_combinational()
  assert model.out.v == 2

  model.in_.v = 0x5f0cd0f0f0f0f
  sim.eval_combinational()

  assert model.out.type.v == 1
  assert model.out.len.v  == 1
  assert model.out.addr.v == 0x7c33
  assert model.out.data.v == 0x0f0f0f0f
  assert model.out.v      == 0x5f0cd0f0f0f0f

  model.in_.len.v = MemMsg.BYTE
  sim.eval_combinational()
  assert model.out.len.v == MemMsg.BYTE

#-----------------------------------------------------------------------
# Check Sequential Logic
#-----------------------------------------------------------------------

class SeqLogicMsgModel( Model ):
  def __init__( s ):

    s.in_ = InPort ( MemMsg( 16, 32 ) )
    s.out = OutPort( MemMsg( 16, 32 ) )

  def elaborate_logic( s ):

    @s.posedge_clk
    def logic():

      s.out.type.next = s.in_.type
      s.out.len.next  = s.in_.len
      s.out.addr.next = s.in_.addr
      s.out.data.next = s.in_.data


def test_msg_seq_logic():

  model = SeqLogicMsgModel()
  model.elaborate()

  sim = SimulationTool(model)

  assert model.in_.nbits      == 1 + 2 + 16 + 32
  assert model.in_.type.nbits == 1
  assert model.in_.len.nbits  == 2
  assert model.in_.addr.nbits == 16
  assert model.in_.data.nbits == 32

  assert model.out.type.slice == slice( 50, 51 )
  assert model.out.addr.slice == slice( 34, 50 )
  assert model.out.len.slice  == slice( 32, 34 )
  assert model.out.data.slice == slice(  0, 32 )
  assert model.out.slice      == slice( None )

  sim.reset()

  model.in_.v = 1
  assert model.out.v == 0
  sim.cycle()
  assert model.out.v == 1

  model.in_.v = 2
  sim.eval_combinational()
  assert model.out.v == 1
  sim.cycle()
  assert model.out.v == 2

  model.in_.v = 0x5f0cd0f0f0f0f
  sim.cycle()
  assert model.out.v == 0x5f0cd0f0f0f0f

  model.in_.len.v = MemMsg.HALF
  sim.cycle()
  assert model.out.len.v == MemMsg.HALF
  assert model.out.v     == 0x5f0ce0f0f0f0f

#-----------------------------------------------------------------------
# Check Connectivity
#-----------------------------------------------------------------------

class PortMsgModel( Model ):
  def __init__( s ):
    s.msg = MemMsg( 16, 32 )

    s.in_ = InPort ( s.msg )
    s.out = OutPort( s.msg )

  def elaborate_logic( s ):

    s.type = Wire( s.msg.type.nbits )
    s.len  = Wire( s.msg.len.nbits  )
    s.addr = Wire( s.msg.addr.nbits )
    s.data = Wire( s.msg.data.nbits )

    s.connect( s.in_.type, s.type )
    s.connect( s.in_.len,  s.len  )
    s.connect( s.in_.addr, s.addr )
    s.connect( s.in_.data, s.data )

    s.connect( s.out.type, s.type )
    s.connect( s.out.len,  s.len  )
    s.connect( s.out.addr, s.addr )
    s.connect( s.out.data, s.data )

def test_msg_ports():

  model = PortMsgModel()
  model.elaborate()

  # Test port slices attributes (InPort, OutPort, Wire) before Sim init

  assert model.in_.slice      == slice( None )
  assert model.in_.type.slice == slice( 50, 51 )
  assert model.in_.addr.slice == slice( 34, 50 )
  assert model.in_.len.slice  == slice( 32, 34 )
  assert model.in_.data.slice == slice(  0, 32 )

  assert model.out.slice      == slice( None )
  assert model.out.type.slice == slice( 50, 51 )
  assert model.out.addr.slice == slice( 34, 50 )
  assert model.out.len.slice  == slice( 32, 34 )
  assert model.out.data.slice == slice(  0, 32 )

  assert model.type.slice     == slice( None )
  assert model.addr.slice     == slice( None )
  assert model.len.slice      == slice( None )
  assert model.data.slice     == slice( None )

  # Create simulator

  sim = SimulationTool(model)

  # Test nbits attributes (InPort, OutPort, Wire)

  assert model.in_.nbits      == 1 + 2 + 16 + 32
  assert model.in_.type.nbits == 1
  assert model.in_.addr.nbits == 16
  assert model.in_.len.nbits  == 2
  assert model.in_.data.nbits == 32

  assert model.out.nbits      == 1 + 2 + 16 + 32
  assert model.out.type.nbits == 1
  assert model.out.addr.nbits == 16
  assert model.out.len.nbits  == 2
  assert model.out.data.nbits == 32

  assert model.type.nbits     == 1
  assert model.addr.nbits     == 16
  assert model.len.nbits      == 2
  assert model.data.nbits     == 32

  # Test field slices attributes (InPort, OutPort, Wire)

  assert model.in_.slice      == slice( None )
  assert model.in_.type.slice == slice( 50, 51 )
  assert model.in_.addr.slice == slice( 34, 50 )
  assert model.in_.len.slice  == slice( 32, 34 )
  assert model.in_.data.slice == slice(  0, 32 )

  assert model.out.slice      == slice( None )
  assert model.out.type.slice == slice( 50, 51 )
  assert model.out.addr.slice == slice( 34, 50 )
  assert model.out.len.slice  == slice( 32, 34 )
  assert model.out.data.slice == slice(  0, 32 )

  assert model.type.slice     == slice( None )
  assert model.addr.slice     == slice( None )
  assert model.len.slice      == slice( None )
  assert model.data.slice     == slice( None )

  # Test initial values (InPort, OutPort, Wire)

  assert model.in_      == 0
  assert model.in_.type == 0
  assert model.in_.addr == 0
  assert model.in_.len  == 0
  assert model.in_.data == 0

  assert model.out      == 0
  assert model.out.type == 0
  assert model.out.addr == 0
  assert model.out.len  == 0
  assert model.out.data == 0

  assert model.type     == 0
  assert model.addr     == 0
  assert model.len      == 0
  assert model.data     == 0

  # Test whole assignment

  model.in_.v            = 0x5f0cd0f0f0f0f
  assert model.in_      == 0x5f0cd0f0f0f0f

  sim.eval_combinational()

  assert model.in_      == 0x5f0cd0f0f0f0f
  assert model.in_.type == 1
  assert model.in_.len  == 1
  assert model.in_.addr == 0x7c33
  assert model.in_.data == 0x0f0f0f0f

  assert model.type     == 1
  assert model.addr     == 0x7c33
  assert model.len      == 1
  assert model.data     == 0x0f0f0f0f

  assert model.out      == 0x5f0cd0f0f0f0f
  assert model.out.type == 1
  assert model.out.len  == 1
  assert model.out.addr == 0x7c33
  assert model.out.data == 0x0f0f0f0f

  # Test field assignment

  model.in_.len.v        = MemMsg.HALF
  assert model.out.len  == MemMsg.HALF
  assert model.out      == 0x5f0ce0f0f0f0f

  model.in_.type.v       = MemMsg.WRITE
  model.in_.addr.v       = 0
  model.in_.len.v        = MemMsg.WORD
  model.in_.data.v       = 0x88888888
  assert model.out      == 0x4000088888888

#-----------------------------------------------------------------------
# Check List of PortMsg
#-----------------------------------------------------------------------
class SeqLogicMsgListModel( Model ):
  def __init__( s ):

    s.in_ = [ InPort ( MemMsg( 16, 32 ) ) for x in range( 4 ) ]
    s.out = [ OutPort( MemMsg( 16, 32 ) ) for x in range( 4 ) ]

  def elaborate_logic( s ):

    @s.posedge_clk
    def logic():

      for i in range( 4 ):
        s.out[ i ].type.next = s.in_[ i ].type
        s.out[ i ].len.next  = s.in_[ i ].len
        s.out[ i ].addr.next = s.in_[ i ].addr
        s.out[ i ].data.next = s.in_[ i ].data

def test_msg_seq_list_logic():

  model = SeqLogicMsgListModel()
  model.elaborate()

  sim = SimulationTool(model)

  sim.reset()

  for i in range( 4 ):
    model.in_[ i ].v = 1
    assert model.out[ i ].v == 0
  sim.cycle()
  for i in range( 4 ):
    assert model.out[ i ].v == 1

  for i in range( 4 ):
    model.in_[ i ].v = 2
    sim.eval_combinational()
    assert model.out[ i ].v == 1
  sim.cycle()
  for i in range( 4 ):
    assert model.out[ i ].v == 2

  for i in range( 4 ):
    model.in_[ i ].v = 0x5f0cd0f0f0f0f
  sim.cycle()
  for i in range( 4 ):
    assert model.out[ i ].v == 0x5f0cd0f0f0f0f

  for i in range( 4 ):
    model.in_[ i ].len.v = MemMsg.HALF
  sim.cycle()
  for i in range( 4 ):
    assert model.out[ i ].len.v == MemMsg.HALF
    assert model.out[ i ].v     == 0x5f0ce0f0f0f0f

#=======================================================================
# Buggy Struct
#=======================================================================
# This bug it intermtittent!  The challenge here is two interconnected
# models have compatible ports in terms of bitwidth, but different
# specific message types (one is Bits, the other BitStruct).
#
# - TH         input/out are Bits(32)     (bitwidth = 32 )
# - BasicModel input/out are MyStruct(16) (bitwidth = 32 )
#
# Because connected signals are collapsed into a single signal during
# simulator construction, it must be chosen to be Bits or BitStruct.
# The simulator uses Python sets, which have non-deterministic orderings
# so depending on the memory ids of a given run the input/output port
# may be set to the Bits or BitStruct type.  If it is set to the
# BitStruct type then the below test will fail.
#
import pytest
@pytest.mark.xfail
def test_buggy_struct():

  from new_pmlib import InValRdyBundle, OutValRdyBundle

  #---------------------------------------------------------------------
  # Struct
  #---------------------------------------------------------------------
  class MyStruct( BitStructDefinition ):
    def __init__( s, nbits):
      s.src  = BitField( nbits)
      s.dest = BitField( nbits )

  class BasicModel( Model ):
    def __init__(s):
      msg_type = MyStruct( 16 )
      s.input  = InValRdyBundle ( msg_type )
      s.out    = OutValRdyBundle( msg_type )

    def elaborate_logic(s):
      @s.combinational
      def logic():
        s.out.msg.src.value  = s.input.msg.dest
        s.out.msg.dest.value = s.input.msg.src

  class TH( Model ):
    def __init__(s):
      s.input = InValRdyBundle ( 32 )
      s.out   = OutValRdyBundle( 32 )

    def elaborate_logic(s):
      s.toy   = BasicModel()
      s.connect( s.input, s.toy.input )
      s.connect( s.out,   s.toy.out   )

  model = TH()
  model.elaborate()
  sim = SimulationTool( model )

  sim.reset()

  model.input.msg.value = 0x12345678
  sim.cycle()
  assert model.out.msg == 0x56781234
