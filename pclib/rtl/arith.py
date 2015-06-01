#=======================================================================
# arith.py
#=======================================================================
'''Collection of translatable arithmetic components.'''

from pymtl import *

#-----------------------------------------------------------------------
# Adder
#-----------------------------------------------------------------------
class Adder( Model ):

  def __init__( s, nbits = 1 ):

    s.in0  = InPort  ( nbits )
    s.in1  = InPort  ( nbits )
    s.cin  = InPort  ( 1     )

    s.out  = OutPort ( nbits )
    s.cout = OutPort ( 1     )

    # Wires

    twidth = nbits + 1
    s.temp = Wire( twidth )

    # Connections

    s.connect( s.out,  s.temp[0:nbits] )
    s.connect( s.cout, s.temp[nbits]   )

    @s.combinational
    def comb_logic():

      # Zero extend the inputs by one bit so we can generate an extra
      # carry out bit

      t0 = zext( s.in0, twidth )
      t1 = zext( s.in1, twidth )

      s.temp.value = t0 + t1 + s.cin

  def line_trace( s ):
    return "{} {} {} () {} {}" \
      .format( s.in0, s.in1, s.cin, s.out, s.cout )

#-----------------------------------------------------------------------
# Subtractor
#-----------------------------------------------------------------------
class Subtractor( Model ):

  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      s.out.value = s.in0 - s.in1

  def line_trace( s ):
    return "{} {} () {}".format( s.in0, s.in1, s.out )

#-----------------------------------------------------------------------
# Incrementer
#-----------------------------------------------------------------------
class Incrementer( Model ):

  def __init__( s, nbits = 1, increment_amount = 1 ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      s.out.value = s.in_ + increment_amount

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# ZeroExtender
#-----------------------------------------------------------------------
class ZeroExtender( Model ):

  def __init__( s, in_nbits = 1, out_nbits = 1 ):

    s.in_ = InPort  ( in_nbits  )
    s.out = OutPort ( out_nbits )

    @s.combinational
    def comb_logic():
      s.out.value = zext( s.in_, out_nbits )

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# SignExtender
#-----------------------------------------------------------------------
class SignExtender( Model ):

  def __init__( s, in_nbits = 1, out_nbits = 1 ):

    assert in_nbits <= out_nbits

    s.in_ = InPort  ( in_nbits  )
    s.out = OutPort ( out_nbits )

    @s.combinational
    def comb_logic():
      s.out.value = sext( s.in_, out_nbits )

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# Zero Comparator
#-----------------------------------------------------------------------
class ZeroComparator( Model ):

  def __init__( s, nbits = 1 ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( 1     )

    @s.combinational
    def comb_logic():
      s.out.value = s.in_ == 0

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# Equal Comparator
#-----------------------------------------------------------------------
class EqComparator( Model ):

  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

    @s.combinational
    def comb_logic():
      s.out.value = s.in0 == s.in1

  def line_trace( s ):
    return "{} {} () {}".format( s.in0, s.in1, s.out )

#-----------------------------------------------------------------------
# Less-Than Comparator
#-----------------------------------------------------------------------
class LtComparator( Model ):

  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

    @s.combinational
    def comb_logic():
      s.out.value = s.in0 < s.in1

  def line_trace( s ):
    return "{} {} () {}".format( s.in0, s.in1, s.out )

#-----------------------------------------------------------------------
# Greater-Than Comparator
#-----------------------------------------------------------------------
class GtComparator( Model ):

  def __init__( s, nbits = 1 ):

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( 1     )

    @s.combinational
    def comb_logic():
      s.out.value = s.in0 > s.in1

  def line_trace( s ):
    return "{} {} () {}".format( s.in0, s.in1, s.out )

#-----------------------------------------------------------------------
# SignUnit
#-----------------------------------------------------------------------
class SignUnit( Model ):

  def __init__( s, nbits = 1 ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      s.out.value = ~s.in_ + 1

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# UnsignUnit
#-----------------------------------------------------------------------
class UnsignUnit( Model ):

  def __init__( s, nbits ):

    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      if s.in_[nbits-1]:
        s.out.value = ~s.in_ + 1
      else:
        s.out.value = s.in_

  def line_trace( s ):
    return "{} () {}".format( s.in_, s.out )

#-----------------------------------------------------------------------
# LeftLogicalShifter
#-----------------------------------------------------------------------
class LeftLogicalShifter( Model ):

  def __init__( s, inout_nbits = 1, shamt_nbits = 1 ):

    s.in_   = InPort  ( inout_nbits )
    s.shamt = InPort  ( shamt_nbits )
    s.out   = OutPort ( inout_nbits )

    @s.combinational
    def comb_logic():
      s.out.value = s.in_ << s.shamt

  def line_trace( s ):
    return "{} {} () {}".format( s.in_, s.shamt, s.out )

#-----------------------------------------------------------------------
# RightLogicalShifter
#-----------------------------------------------------------------------
class RightLogicalShifter( Model ):

  def __init__( s, inout_nbits = 1, shamt_nbits = 1 ):

    s.in_   = InPort  ( inout_nbits )
    s.shamt = InPort  ( shamt_nbits )
    s.out   = OutPort ( inout_nbits )

    @s.combinational
    def comb_logic():
      s.out.value = s.in_ >> s.shamt

  def line_trace( s ):
    return "{} {} () {}".format( s.in_, s.shamt, s.out )

