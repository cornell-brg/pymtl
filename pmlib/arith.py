#=========================================================================
# Arithmetic components
#=========================================================================

from pymtl import *
from muxes import *

#-------------------------------------------------------------------------
# Adder
#-------------------------------------------------------------------------

class Adder( Model ):

  def __init__( self, nbits = 1 ):

    # Constants

    self.nbits = nbits

    # Ports

    self.in0  = InPort  ( nbits )
    self.in1  = InPort  ( nbits )
    self.cin  = InPort  ( 1     )

    self.out  = OutPort ( nbits )
    self.cout = OutPort ( 1     )

    # Wires

    self.temp = Wire( nbits+1 )

    # Connections

    connect( self.out,  self.temp[0:nbits] )
    connect( self.cout, self.temp[nbits]   )

  @combinational
  def comb_logic( self ):

    # Zero extend the inputs by one bit so we can generate an extra
    # carry out bit

    in0 = self.in0.value.zext( self.nbits + 1 )
    in1 = self.in1.value.zext( self.nbits + 1 )

    self.temp.value = in0 + in1 + self.cin.value

  def line_trace( self ):
    return "{} {} {} () {} {}" \
      .format( self.in0.value, self.in1.value, self.cin.value,
               self.out.value, self.cout.value )

#-------------------------------------------------------------------------
# Subtractor
#-------------------------------------------------------------------------

class Subtractor( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value - self.in1.value;

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in0.value, self.in1.value, self.out.value )

#-------------------------------------------------------------------------
# Incrementer
#-------------------------------------------------------------------------

class Incrementer( Model ):

  def __init__( self, nbits = 1, increment_amount = 1 ):

    # Ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

    # Constants

    self.increment_amount = increment_amount

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value + self.increment_amount

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# ZeroExtender
#-------------------------------------------------------------------------

class ZeroExtender( Model ):

  def __init__( self, in_nbits = 1, out_nbits = 1 ):

    # Ports

    self.in_ = InPort  ( in_nbits  )
    self.out = OutPort ( out_nbits )

    # WORKAROUND: Connecting a constant a slice directly doesn't work
    # yet, but when it does we can remove this temporary wire.

    self.temp = Wire( out_nbits - in_nbits )

    # Connections

    connect( self.out[0:in_nbits],         self.in_  )
    connect( self.out[in_nbits:out_nbits], self.temp )
    connect( self.temp,                    0         )

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# SignExtender
#-------------------------------------------------------------------------

class SignExtender( Model ):

  def __init__( self, in_nbits = 1, out_nbits = 1 ):

    # Checks

    assert in_nbits <= out_nbits

    # Ports

    self.in_ = InPort  ( in_nbits  )
    self.out = OutPort ( out_nbits )

    # Connect input port directly to corresponding bottom bits of output

    connect( self.out[0:in_nbits], self.in_  )

    # Connect msb of input port to each remaining bit of output port

    for i in xrange(out_nbits - in_nbits):
      connect( self.out[in_nbits+i], self.in_[in_nbits-1] )

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# Zero Comparator
#-------------------------------------------------------------------------

class ZeroComparator( Model ):

  def __init__( self, nbits = 1 ):

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1     )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value == 0

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# Equal Comparator
#-------------------------------------------------------------------------

class EqComparator( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.out = OutPort ( 1     )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value == self.in1.value

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in0.value, self.in1.value, self.out.value )

#-------------------------------------------------------------------------
# Less-Than Comparator
#-------------------------------------------------------------------------

class LtComparator( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.out = OutPort ( 1     )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value < self.in1.value

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in0.value, self.in1.value, self.out.value )

#-------------------------------------------------------------------------
# Greater-Than Comparator
#-------------------------------------------------------------------------

class GtComparator( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.out = OutPort ( 1     )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value > self.in1.value

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in0.value, self.in1.value, self.out.value )

#-------------------------------------------------------------------------
# SignUnit
#-------------------------------------------------------------------------

class SignUnit( Model ):

  def __init__( self, nbits = 1 ):

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    self.out.value = ~self.in_.value + 1

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# UnsignUnit
#-------------------------------------------------------------------------

class UnsignUnit( Model ):

  def __init__( self, nbits ):

    # Constants

    self.nbits = nbits

    # Ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    if self.in_.value[self.nbits-1]:
      self.out.value = ~self.in_.value + 1
    else:
      self.out.value = self.in_.value

  def line_trace( self ):
    return "{} () {}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# LeftLogicalShifter
#-------------------------------------------------------------------------

class LeftLogicalShifter( Model ):

  def __init__( self, inout_nbits = 1, shamt_nbits = 1 ):

    self.in_   = InPort  ( inout_nbits )
    self.shamt = InPort  ( shamt_nbits )
    self.out   = OutPort ( inout_nbits )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value << self.shamt.value

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in_.value, self.shamt.value, self.out.value )

#-------------------------------------------------------------------------
# RightLogicalShifter
#-------------------------------------------------------------------------

class RightLogicalShifter( Model ):

  def __init__( self, inout_nbits = 1, shamt_nbits = 1 ):

    self.in_   = InPort  ( inout_nbits )
    self.shamt = InPort  ( shamt_nbits )
    self.out   = OutPort ( inout_nbits )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value >> self.shamt.value

  def line_trace( self ):
    return "{} {} () {}" \
      .format( self.in_.value, self.shamt.value, self.out.value )

#-------------------------------------------------------------------------
# Bits Counter Tree Style
#-------------------------------------------------------------------------
# Count how many ones are in the input.
# The other style is to use several small Lookup Tables and add together
# the results.

class BitsCounter_Tree32( Model ):

  def __init__( self ):

    # Ports

    self.in_  = InPort  ( 32 )
    self.out  = OutPort ( 6 )

    # Wires

    self.temp = Wire( 32 )

    # Connections

    connect( self.out, self.temp[0:6] )

  @combinational
  def comb_logic( self ):

    # Count how many ones are in the input. Start by counting the 
    # neighbour two bits, then count neighbour four bits, until
    # neighbour 16 bits. Each result is stored in different space of the 
    # data so they don't interfere with each other.

    self.temp.value = ((self.in_.value  >> 1 ) & 0x55555555) + (self.in_.value  & 0x55555555)
    self.temp.value = ((self.temp.value >> 2 ) & 0x33333333) + (self.temp.value & 0x33333333)
    self.temp.value = ((self.temp.value >> 4 ) & 0x0f0f0f0f) + (self.temp.value & 0x0f0f0f0f)
    self.temp.value = ((self.temp.value >> 8 ) & 0x00ff00ff) + (self.temp.value & 0x00ff00ff)
    self.temp.value = ((self.temp.value >> 16) & 0x0000ffff) + (self.temp.value & 0x0000ffff)

  def line_trace( self ):
    return "{} ({}) {}" \
      .format( self.in_.value, self.temp.value, self.out.value )

#-------------------------------------------------------------------------
# Trailing Zero Counter
#-------------------------------------------------------------------------
# Counting consecutive trailing zero bits

class TrailingZeroCounter( Model ):

  def __init__( self ):

    # Ports

    self.in_  = InPort  ( 32 )
    self.out  = OutPort ( 6 )

    # Wires

    self.xor_result = Wire( 32 )

    # Bits counter unit

    self.bits_cnt = BitsCounter_Tree32()
    connect( self.bits_cnt.in_, self.xor_result )

  @combinational
  def comb_logic( self ):

    # Count how many trailing zeros are in the input.
    # First we take the input and minus it by 1, so the trailing zeros
    # will become all ones and the last one will will become zero.
    # Then we xor input with this result. Higher bits are the same so
    # they becomes 0 and lower bits will differ, including the last
    # one and the trailing zeros.

    self.xor_result.value = self.in_.value ^ (self.in_.value - 1)

    # Then we count how many ones are in the xor result.
    # Number of zeros should be number of ones in the xor_result - 1

    self.out.value = self.bits_cnt.out.value - 1 if self.in_.value != 0 else 32

  def line_trace( self ):

    line_trace_str = "?"

    line_trace_str += "{} {}" \
        .format( self.xor_result.value, self.bits_cnt.out.value )

    return "{} ({}) {}" \
      .format( self.in_.value, line_trace_str, self.out.value )

#-------------------------------------------------------------------------
# Trailing One Counter
#-------------------------------------------------------------------------
# Counting consecutive trailing one bits

class TrailingOneCounter( Model ):

  def __init__( self ):

    # Ports

    self.in_  = InPort  ( 32 )
    self.out  = OutPort ( 6 )

    # Wires

    self.xor_result = Wire( 32 )

    # Bits counter unit

    self.bits_cnt = BitsCounter_Tree32()
    connect( self.bits_cnt.in_, self.xor_result )

  @combinational
  def comb_logic( self ):

    # Count how many trailing ones are in the input.
    # First we take the input and add it by 1, so the trailing ones
    # will become all zeros and the last zero will will become one.
    # Then we xor input with this result. Higher bits are the same so
    # they becomes 0 and lower bits will differ, including the last
    # zero and the trailing ones.

    self.xor_result.value = self.in_.value ^ (self.in_.value + 1)

    # Then we count how many ones are in the xor result.
    # Number of zeros should be number of ones in the xor_result - 1

    self.out.value = self.bits_cnt.out.value - 1 if self.in_.value != 0xffffffff else 32

  def line_trace( self ):

    line_trace_str = "?"

    line_trace_str += "{} {}" \
        .format( self.xor_result.value, self.bits_cnt.out.value )

    return "{} ({}) {}" \
      .format( self.in_.value, line_trace_str, self.out.value )

