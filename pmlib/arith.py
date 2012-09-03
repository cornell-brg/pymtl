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
    self.temp.value = self.in0.value + self.in1.value + self.cin.value;

  def line_trace( self ):
    return "{:04x} {:04x} {} () {:04x} {}" \
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
    return "{:04x} {:04x} () {:04x}" \
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
    return "{:04x} () {:04x}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# ZeroExtender
#-------------------------------------------------------------------------

class ZeroExtender( Model ):

  def __init__( self, in_nbits = 1, out_nbits = 1 ):

    # Ports

    self.in_ = InPort  ( in_nbits  )
    self.out = OutPort ( out_nbits )

    # Wires

    self.temp = Wire( out_nbits - in_nbits )

    # Connections

    connect( self.out[0:in_nbits],         self.in_  )
    connect( self.out[in_nbits:out_nbits], self.temp )
    connect( self.temp,                    0         )

  def line_trace( self ):
    return "{:04x} () {:04x}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# SignExtender
#-------------------------------------------------------------------------
# The current implementation is not working; it is causing an infinite
# loop in the event queue somehow. The unit tests have been commented out
# for now.

class SignExtender( Model ):

  def __init__( self, in_nbits = 1, out_nbits = 1 ):

    # Ports

    self.in_ = InPort  ( in_nbits  )
    self.out = OutPort ( out_nbits )

    # Wires

    self.temp = Wire( out_nbits - in_nbits )

    # Constants

    self.temp_ones = 2**(out_nbits - in_nbits) - 1
    print self.temp_ones

    self.in_msb    = in_nbits-1
    print self.in_msb

    # Connections

    connect( self.out[0:in_nbits],         self.in_  )
    connect( self.out[in_nbits:out_nbits], self.temp )

  @combinational
  def comb_logic( self ):
    if self.in_[self.in_msb].value:
      self.temp.value = 0;
    else:
      self.temp.value = self.temp_ones;

  def line_trace( self ):
    return "{:04x} () {:04x}" \
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
    if self.in_.value == 0:
      self.out.value = 1
    else:
      self.out.value = 0;

  def line_trace( self ):
    return "{:04x} () {:04x}" \
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
    if self.in0.value == self.in1.value:
      self.out.value = 1
    else:
      self.out.value = 0;

  def line_trace( self ):
    return "{:04x} {:04x} () {:04x}" \
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
    if self.in0.value < self.in1.value:
      self.out.value = 1
    else:
      self.out.value = 0;

  def line_trace( self ):
    return "{:04x} {:04x} () {:04x}" \
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
    if self.in0.value > self.in1.value:
      self.out.value = 1
    else:
      self.out.value = 0;

  def line_trace( self ):
    return "{:04x} {:04x} () {:04x}" \
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
    return "{:04x} () {:04x}" \
      .format( self.in_.value, self.out.value )

#-------------------------------------------------------------------------
# UnsignUnit
#-------------------------------------------------------------------------

class UnsignUnit( Model ):

  def __init__( self, nbits ):

    # Ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

    # Wires

    self.neg_in = Wire( nbits )
    self.sign   = Wire( 1 )

    # Constants

    self.shift_amount = nbits - 1

    # Module instantiation and connections

    self.mux = m = Mux2( nbits )
    connect({
      m.in0 : self.in_,
      m.in1 : self.neg_in,
      m.sel : self.sign,
      m.out : self.out,
    })

  @combinational
  def comb_logic( self ):
    self.sign.value   = self.in_.value >> self.shift_amount
    self.neg_in.value = ~self.in_.value + 1

  def line_trace( self ):
    return "{:04x} () {:04x}" \
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
    return "{:04x} {:04x} () {:04x}" \
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
    return "{:04x} {:04x} () {:04x}" \
      .format( self.in_.value, self.shamt.value, self.out.value )

