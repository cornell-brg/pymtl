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

  #-----------------------------------------------------------------------
  # Structual design -- not working
  #-----------------------------------------------------------------------
  # Structual design made of bit-wise complementer, MSB generater
  # and mux2. But simulation went into an endless loop. It gets confused
  # when updating the combinational logics when multiple ports are
  # connected together.
  # A substitution is appended.
  #

class SignExtStructual( Model ):

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

  #-----------------------------------------------------------------------
  # Substitution design
  #-----------------------------------------------------------------------

class SignExt( Model ):

  def __init__( self, W_IN = 16, W_OUT = 32 ):
    self.in_ = InPort( W_IN )
    self.out = OutPort( W_OUT )

    # wire
    self.temp = Wire ( W_OUT - W_IN )

    # sub module
    self.msb = MSB( W_IN )

    # local parameters
    self.zero = 0
    self.comp = 2 ** ( W_OUT - W_IN ) - 1
    self.count = 0

    #connections
    connect( self.out[0:W_IN], self.in_ )
    connect( self.out[W_IN:W_OUT], self.temp )
    connect( self.msb.in_, self.in_ )

  @combinational
  def comb_logic( self ):
    if self.count < 30:
      print "\n", self.count, "times calling the comb_logic()!"
      print "Input:", self.in_.value
      print "Output:", self.out.value
      print "MSB:", self.msb.in_.value
      print "MSB out:", self.msb.out.value
    self.count = self.count + 1
    if self.msb.out.value == 1:
      self.temp.value = self.comp
    else:
      self.temp.value = self.zero

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

#-------------------------------------------------------------------------
# Sign operater
#-------------------------------------------------------------------------

class Sign( Model ):

  def __init__( self, W = 16 ):
    self.in_ = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = ~self.in_.value + 1

#-------------------------------------------------------------------------
# UnSign operater
#-------------------------------------------------------------------------

class UnSign( Model ):                                                              
                                                                                    
  def __init__( self, bits ):                                                       
    self.in_ = InPort( bits )                                                       
    self.out = OutPort( bits )                                                      
                                                                                    
    self.neg_in = Wire( bits )                                                      
    self.sign = Wire( 1 )                                                           
    self.bits = bits                                                                
                                                                                    
    self.mux = Mux2( bits )                                                     
    connect( self.mux.in0, self.in_ )
    connect( self.mux.in1, self.neg_in )
    connect( self.mux.sel, self.sign )
    connect( self.mux.out, self.out )                                                                      
                                                                                    
  @combinational                                                                    
  def comb_logic( self ):                                                                  
    self.sign.value = self.in_.value >> ( self.bits - 1)    
    self.neg_in.value = ~self.in_.value + 1                                         

#-------------------------------------------------------------------------
# ZeroExtend operater
#-------------------------------------------------------------------------

class ZeroExtend( Model ):

  def __init__( self, nbits ):
    self.in_ = InPort( nbits )
    self.out = OutPort( 2*nbits )

  @combinational
  def comb( self ):
    self.out.value = self.in_.value + 0

#-------------------------------------------------------------------------
#  Shift Logical Left Operator 
#-------------------------------------------------------------------------

class ShiftLogLeft( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value << self.in1.value

#-------------------------------------------------------------------------
# Shift Logical Right Operator 
#-------------------------------------------------------------------------

class ShiftLogRight( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    self.out.value = self.in0.value >> self.in1.value
