#=========================================================================
# Arithmetic components
#=========================================================================

import sys
sys.path.append('..')
from pymtl import *

from muxes import *
from bit import *

#-------------------------------------------------------------------------
# 1-bit Full Adder
#-------------------------------------------------------------------------

class FullAdder( Model ):

  def __init__( self ):
    self.in0 = InPort( 1 )
    self.in1 = InPort( 1 )
    self.cin = InPort( 1 )
    self.out = OutPort( 1 )
    self.cout = OutPort( 1 )

  @combinational
  def comb_logic( self ):
    self.out.value = (self.in0.value ^ self.in1.value ^ self.cin.value);
    self.cout.value = ((self.in0.value & self.in1.value) | \
                       (self.in1.value & self.cin.value) | \
                       (self.in0.value & self.cin.value));

#-------------------------------------------------------------------------
# Adder
#-------------------------------------------------------------------------

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
    connect(self.cout, self.temp[W])

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
# Incrementer
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
    connect( self.out[0:W_IN], self.in_ )
    connect( self.out[W_IN:W_OUT], self.temp )

  @combinational
  def comb_logic( self ):
    self.temp.value = 0;

#-------------------------------------------------------------------------
# Sign-Extension
#-------------------------------------------------------------------------
# Doesn't work yet.
# TODO: finish the design
#

class SignExt( Model ):

  def __init__( self, W_IN = 16, W_OUT = 32 ):
    self.in_ = InPort( W_IN )
    self.out = OutPort( W_OUT )

    self.counter = 0

    # wire
    self.temp = Wire( W_OUT - W_IN )

    # sub modules
    self.msb = MSB( W_IN )
    self.rev = REV( W_OUT - W_IN )
    self.mux2 = Mux2( W_OUT - W_IN )

    #connections
    connect( self.msb.in_, self.in_ )
    connect( self.msb.out, self.mux2.sel )
    connect( self.rev.in_, self.temp )
    connect( self.mux2.in0, self.temp )
    connect( self.mux2.in1, self.rev.out )
    connect( self.out[0:W_IN], self.in_ )
    connect( self.out[W_IN:W_OUT], self.mux2.out )

  @combinational
  def comb_logic( self ):
    self.temp.value = 0
#    print "\n"
#    print "Counter:", self.counter
#    self.counter = self.counter + 1
#    print "self:", self.in_.value, self.out.value
#    print "MSB:", self.msb.in_.value, self.msb.out.value
#    print "REV:", self.rev.in_.value, self.rev.out.value
#    print "MUX2:", self.mux2.in0.value, self.mux2.in1.value, self.mux2.sel.value, self.mux2.out.value

#-------------------------------------------------------------------------
# Equal comparator
#-------------------------------------------------------------------------

class CmpEQ( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( 1 )

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
    self.out = OutPort( 1 )

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
    self.out = OutPort( 1 )

  @combinational
  def comb_logic( self ):
    self.out.value = 1 if self.in0.value > self.in1.value else 0;

