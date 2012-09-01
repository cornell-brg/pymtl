#=========================================================================
# Bitwise operater
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

#-------------------------------------------------------------------------
# reverse operater
#-------------------------------------------------------------------------

class REV( Model ):

  def __init__( self, W = 16 ):
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = ~self.in_.value

#-------------------------------------------------------------------------
# MSB operater
#-------------------------------------------------------------------------

class MSB( Model ):

  def __init__( self, W = 16 ):
    self.in_ = InPort( W )
    self.out = OutPort( 1 )

    #connection
    connect( self.out, self.in_[W-1] )

#-------------------------------------------------------------------------
# Double connection test
#-------------------------------------------------------------------------

class DoubleCon( Model ):

  def __init__( self, ):
    self.in_ = InPort( 1 )
    self.out = OutPort( 2 )

    #connection
    connect( self.out[0], self.in_ )
    connect( self.out[1], self.in_ )

#-------------------------------------------------------------------------
# Triple connection test
#-------------------------------------------------------------------------

class TriCon( Model ):

  def __init__( self, ):
    self.in_ = InPort( 1 )
    self.out = OutPort( 3 )

    #connection
    connect( self.in_, self.out[0] )
    connect( self.in_, self.out[2] )
    connect( self.in_, self.out[1] )

#  @combinational
#  def comb_logic( self ):
#    print "input connections", self.in_.connections
#    print "output connections", self.out.connections

#-------------------------------------------------------------------------
# Concatenater
#-------------------------------------------------------------------------

class CAT( Model ):

  def __init__( self, W_IN0 = 16, W_IN1 = 16 ):
    self.in0 = InPort( W_IN0 )
    self.in1 = InPort( W_IN1 )
    self.out = OutPort( W_IN0 + W_IN1 )

    self.shiftbits = W_IN0

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value | ( self.in1.value << self.shiftbits )

#-------------------------------------------------------------------------
# Signal extension
#-------------------------------------------------------------------------

  #-------------------------------------------------------------------------
  # Extend twice
  #-------------------------------------------------------------------------

class EXT2( Model ):

  def __init__( self, W = 1 ):
    self.in_ = InPort( W )
    self.out = OutPort( W * 2 )

    self.shiftbits = W

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value | ( self.in_.value << self.shiftbits )

  #-------------------------------------------------------------------------
  # Extend n times
  #-------------------------------------------------------------------------
  # Recursive call
  # with no for-loop allowing us to assign out with a variable length
  #   expression, we design this kind of function using recursive call
  #   to generate a highly structual module

#class EXTN( Model ):
#
#  def __init__( self, W = 1, N = 3 ):
#    self.in_ = InPort( W )
#    self.out = OutPort( W * N )
#
#    # Localparameter
#    self.n = N
#
#    # Sub module
#    assert N > 2
#    self.cat = CAT( W * (N-1), W )
#    # Even reaching boundry, we still have to generate a sub module
#    #   otherwise the code will be not translatable
#    if N == 3:
#      self.extn = EXT2( W )
#    else:
#      self.extn = EXTN( W, N-1 )
#
#    # Connections
#    connect( self.out, self.cat.out )
#
#  @combinational
#  def comb_logic( self ):
#    self.cat.in1.value = self.in_.value
#    self.cat.in0.value = self.extn.out.value if self.n > 2 else self.in_.value
#    # no matter if N is greater than 2, we can't let the input float
#    #if self.n > 2:
#    self.extn.in_.value = self.in_.value

