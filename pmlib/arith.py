#=========================================================================
# Arithmetic components
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

#-------------------------------------------------------------------------
# Adders
#-------------------------------------------------------------------------

class FullAdder( Model ):

  def __init__( self ):
    self.in0 = InPort( 1 )
    self.in1 = InPort( 1 )
    self.cin = InPort( 1 )
    self.out = OutPort( 1 )
    self.cout = OutPort( 1 )

    self.temp = Wire(2)

    # connections
    connect(self.out, self.temp[0])
    connect(self.cout, self.temp[1])

  @combinational
  def comb_logic( self ):
    self.temp.value = self.in0.value + self.in1.value + self.cin.value;

#    self.out.value = (self.in0.value + self.in1.value + self.cin.value);
#    self.cout.value = ((self.in0.value and self.in1.value) or \
#                       (self.in1.value and self.cin.value) or \
#                       (self.in0.value and self.cin.value));

class Adder( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.cin = InPort( 1 )

    self.out = OutPort( W )
    self.cout = OutPort( 1 )

    self.temp = Wire( W+1 )

    #connections
    connect(self.out, self.temp[0:W])
    connect(self.cout, self.temp[W:W+1])

  @combinational
  def comb_logic( self ):
    self.temp.value = self.in0.value + self.in1.value + self.cin.value;

#-------------------------------------------------------------------------
# Subtractor
#-------------------------------------------------------------------------

class Sub( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value - self.in1.value;

#-------------------------------------------------------------------------
# Incrememter
#-------------------------------------------------------------------------

class Inc( Model ):

  def __init__( self, W = 16, INC = 1 ):
    self.in_ = InPort( W )
    self.out = OutPort( W )
    self.inc = INC

  @combinational
  def comb_logic( self ):
    self.out.value = self.in_.value + self.inc;

#-------------------------------------------------------------------------
# Zero-Extension
#-------------------------------------------------------------------------

class ZeroExt( Model ):

  def __init__( self, W_IN = 16, W_OUT = 32 ):
    self.in_ = InPort( W_IN )
    self.out = OutPort( W_OUT )

    self.temp = Wire( W_OUT - W_IN )

    #connections
    connect( self.out[0:(W_IN-1)], self.in_ )
    connect( self.out[W_IN:(W_OUT-1)], self.temp )

  @combinational
  def comb_logic( self ):
    self.temp.value = 0;

#-------------------------------------------------------------------------
# Sign-Extension
#-------------------------------------------------------------------------

class SignExt( Model ):

  def __init__( self, W_IN = 16, W_OUT = 32 ):
    self.in_ = InPort( W_IN )
    self.out = OutPort( W_OUT )

    #connections
    connect( self.out[0:(W_IN-1)], self.in_ )
    for x in xrange(W_IN, W_OUT):
      connect( self.out[x], self.in_[W_IN-1] )

#-------------------------------------------------------------------------
# Equal comparator
#-------------------------------------------------------------------------

class CmpEQ( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = 1 if self.in0.value == self.in1.value else 0;

#-------------------------------------------------------------------------
# Less-Than comparator
#-------------------------------------------------------------------------

class CmpLT( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = 1 if self.in0.value < self.in1.value else 0;

#-------------------------------------------------------------------------
# Greater-Than comparator
#-------------------------------------------------------------------------

class CmpGT( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = 1 if self.in0.value > self.in1.value else 0;

