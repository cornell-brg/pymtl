#=========================================================================
# Arithmetic components
#=========================================================================

from new_pymtl import *
from Mux       import Mux

#-------------------------------------------------------------------------
# Adder
#-------------------------------------------------------------------------

class Adder( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    # Constants

    s.nbits  = nbits
    s.twidth = nbits + 1

    # Ports

    s.in0  = InPort  ( nbits )
    s.in1  = InPort  ( nbits )
    s.cin  = InPort  ( 1     )

    s.out  = OutPort ( nbits )
    s.cout = OutPort ( 1     )

  def elaborate_logic( s ):

    # Wires

    s.temp = Wire( s.nbits+1 )

    # Connections

    s.connect( s.out,  s.temp[0:s.nbits] )
    s.connect( s.cout, s.temp[s.nbits]   )

    @s.combinational
    def comb_logic():

      # Zero extend the inputs by one bit so we can generate an extra
      # carry out bit

      t0 = zext( s.in0, s.twidth )
      t1 = zext( s.in1, s.twidth )

      s.temp.value = t0 + t1 + s.cin.value


  def line_trace( s ):
    return "{} {} {} () {} {}" \
      .format( s.in0.value, s.in1.value, s.cin.value,
               s.out.value, s.cout.value )

#-------------------------------------------------------------------------
# Subtractor
#-------------------------------------------------------------------------

class Subtractor( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in0.value - s.in1.value;

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in0.value, s.in1.value, s.out.value )

#-------------------------------------------------------------------------
# Incrementer
#-------------------------------------------------------------------------

class Incrementer( Model ):

  @capture_args
  def __init__( s, nbits = 1, increment_amount = 1 ):

    # Ports

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

    # Constants

    s.increment_amount = increment_amount

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in_.value + s.increment_amount

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# ZeroExtender
#-------------------------------------------------------------------------

class ZeroExtender( Model ):

  @capture_args
  def __init__( s, in_nbits = 1, out_nbits = 1 ):

    s.in_nbits  = in_nbits
    s.out_nbits = out_nbits

    # Ports

    s.in_ = InPort  ( in_nbits  )
    s.out = OutPort ( out_nbits )

  def elaborate_logic( s ):

    @s.combinational
    def comb_logic():
      s.out.value = zext( s.in_, s.out_nbits)

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# SignExtender
#-------------------------------------------------------------------------

class SignExtender( Model ):

  @capture_args
  def __init__( s, in_nbits = 1, out_nbits = 1 ):

    # Checks

    assert in_nbits <= out_nbits
    s.in_nbits  = in_nbits
    s.out_nbits = out_nbits

    # Ports

    s.in_ = InPort  ( in_nbits  )
    s.out = OutPort ( out_nbits )

  def elaborate_logic( s ):

    @s.combinational
    def comb_logic():
      s.out.value = sext( s.in_, s.out_nbits )

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# Zero Comparator
#-------------------------------------------------------------------------

class ZeroComparator( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( 1     )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in_.value == 0

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# Equal Comparator
#-------------------------------------------------------------------------

class EqComparator( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in0.value == s.in1.value

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in0.value, s.in1.value, s.out.value )

#-------------------------------------------------------------------------
# Less-Than Comparator
#-------------------------------------------------------------------------

class LtComparator( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in0.value < s.in1.value

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in0.value, s.in1.value, s.out.value )

#-------------------------------------------------------------------------
# Greater-Than Comparator
#-------------------------------------------------------------------------

class GtComparator( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in0.value > s.in1.value

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in0.value, s.in1.value, s.out.value )

#-------------------------------------------------------------------------
# SignUnit
#-------------------------------------------------------------------------

class SignUnit( Model ):

  @capture_args
  def __init__( s, nbits = 1 ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = ~s.in_.value + 1

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# UnsignUnit
#-------------------------------------------------------------------------

class UnsignUnit( Model ):

  @capture_args
  def __init__( s, nbits ):

    # Constants

    s.nbits = nbits

    # Ports

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      if s.in_.value[s.nbits-1]:
        s.out.value = ~s.in_.value + 1
      else:
        s.out.value = s.in_.value

  def line_trace( s ):
    return "{} () {}" \
      .format( s.in_.value, s.out.value )

#-------------------------------------------------------------------------
# LeftLogicalShifter
#-------------------------------------------------------------------------

class LeftLogicalShifter( Model ):

  @capture_args
  def __init__( s, inout_nbits = 1, shamt_nbits = 1 ):

    s.in_   = InPort  ( inout_nbits )
    s.shamt = InPort  ( shamt_nbits )
    s.out   = OutPort ( inout_nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in_.value << s.shamt.value

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in_.value, s.shamt.value, s.out.value )

#-------------------------------------------------------------------------
# RightLogicalShifter
#-------------------------------------------------------------------------

class RightLogicalShifter( Model ):

  @capture_args
  def __init__( s, inout_nbits = 1, shamt_nbits = 1 ):

    s.in_   = InPort  ( inout_nbits )
    s.shamt = InPort  ( shamt_nbits )
    s.out   = OutPort ( inout_nbits )

  def elaborate_logic( s ):
    @s.combinational
    def comb_logic():
      s.out.value = s.in_.value >> s.shamt.value

  def line_trace( s ):
    return "{} {} () {}" \
      .format( s.in_.value, s.shamt.value, s.out.value )

