#=========================================================================
# BitStruct Test Suite
#=========================================================================

import math

from new_pymtl import *
from Bits      import Bits
from BitStruct import BitStruct, Field

#-------------------------------------------------------------------------
# Example BitStruct and Enums
#-------------------------------------------------------------------------

class MemMsg( BitStruct ):

  # Enums for type field
  READ  = 0
  WRITE = 1

  # Enums for len field
  BYTE  = 1
  HALF  = 2
  WORD  = 0

  def __init__( s, addr_nbits, data_nbits ):

    print "TEST INIT"
    assert data_nbits % 8 == 0

    # Calculate number of bits needed to store msg len
    len = int( math.ceil( math.log( data_nbits/8, 2 ) ) )

    # Declare the MemoryMsg fields
    s.type = Field( 1 )
    s.addr = Field( addr_nbits )
    s.len  = Field( len )
    s.data = Field( data_nbits )

    # TODO: test other Field types (for overlapping fields)
    # Field( nbits )
    # Field( start, nbits )
    # Field( start, stop )  # Excl, like python range

#-------------------------------------------------------------------------
# Hacky BitStruct test
#-------------------------------------------------------------------------

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

  # Test field slices attributes
  assert x.type_slice == slice( 50, 51 )
  assert x.addr_slice == slice( 34, 50 )
  assert x.len_slice  == slice( 32, 34 )
  assert x.data_slice == slice(  0, 32 )

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

#-------------------------------------------------------------------------
# Check Combinational Logic
#-------------------------------------------------------------------------

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

#-------------------------------------------------------------------------
# Check Sequential Logic
#-------------------------------------------------------------------------

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

#-------------------------------------------------------------------------
# Check Connectivity
#-------------------------------------------------------------------------

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

  sim = SimulationTool(model)

  assert model.in_.nbits      == 1 + 2 + 16 + 32
  assert model.in_.nbits      == 1 + 2 + 16 + 32
  assert model.in_.type.nbits == 1
  assert model.in_.addr.nbits == 16
  assert model.in_.len.nbits  == 2
  assert model.in_.data.nbits == 32

  # TODO: Doing port_walk here shows all temporary slices generated
  #       above as connections!  Fix this somehow?
  #       Is this still relevant?
  #import debug_utils
  #debug_utils.port_walk(model)

  assert model.type.v == 0
  assert model.addr.v == 0
  assert model.len.v  == 0
  assert model.data.v == 0

  assert model.out.type.v == 0
  assert model.out.addr.v == 0
  assert model.out.len.v  == 0
  assert model.out.data.v == 0

  model.in_.v = 0x5f0cd0f0f0f0f
  assert model.in_.v == 0x5f0cd0f0f0f0f

  sim.eval_combinational()

  assert model.type.v == 1
  assert model.addr.v == 0x7c33
  assert model.len.v  == 1
  assert model.data.v == 0x0f0f0f0f

  assert model.out.type.v == 1
  assert model.out.len.v  == 1
  assert model.out.addr.v == 0x7c33
  assert model.out.data.v == 0x0f0f0f0f
  assert model.out.v      == 0x5f0cd0f0f0f0f

  model.in_.len.v = MemMsg.HALF
  assert model.out.len.v == MemMsg.HALF

