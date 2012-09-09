#=========================================================================
# Single bit mini test
#=========================================================================

from pymtl import *

from regs import *
from arith import *

#-------------------------------------------------------------------------
# slice within a model ver1
#-------------------------------------------------------------------------

class slice_in_model_ver1( Model ):

  def __init__( self, nbits = 1 ):

    # ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1 )

    # connections
    
    connect( self.out, self.in_[0] )
#    connect( self.in_[0], self.out )

  def line_trace( self ):
    return "{:04x} () {:04x}" \
      .format( self.in_.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# slice within a model ver2
#-------------------------------------------------------------------------

class slice_in_model_ver2( Model ):

  def __init__( self, nbits = 1 ):

    # ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1 )

    # connections
    
    connect( self.in_[nbits-1], self.out )

  def line_trace( self ):
    return "{:04x} () {:04x}" \
      .format( self.in_.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# slice between two models ver1
#-------------------------------------------------------------------------

class slice_bet_models_1( Model ):

  def __init__( self, nbits = 1 ):

    # ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1 )

    # reg
    
    self.reg = Reg ( nbits )
    connect( self.reg.in_, self.in_ )

    # connections
    
    connect( self.reg.out[0], self.out )
#    connect( self.out, self.reg.out[0] )

  def line_trace( self ):
    return "{:04x} ( {:04x} ) {:04x}" \
      .format( self.in_.value.uint,\
               self.reg.out.value.uint,
               self.out.value.uint,
             )

#-------------------------------------------------------------------------
# slice between two models ver2
#-------------------------------------------------------------------------

class slice_bet_models_2( Model ):

  def __init__( self, nbits = 1 ):

    # ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1 )

    # reg
    
    self.reg = Reg ( 1 )
    connect( self.reg.in_, self.in_[0] )

    # connections
    
    connect( self.reg.out, self.out )

  def line_trace( self ):
    return "{:04x} ( {:04x} ) {:04x}" \
      .format( self.in_.value.uint,\
               self.reg.out.value.uint,
               self.out.value.uint,
             )

#-------------------------------------------------------------------------
# slice between two models ver3
#-------------------------------------------------------------------------

class slice_bet_models_3( Model ):

  def __init__( self, nbits = 1 ):

    # ports

    self.in_ = InPort  ( nbits )
    self.out = OutPort ( 1 )

    # reg
    
    self.reg = Reg ( 1 )
    connect( self.reg.in_, self.in_[0] )

    # connections
    
    connect( self.reg.out, self.out )

  def line_trace( self ):
    return "{:04x} ( {:04x} ) {:04x}" \
      .format( self.in_.value.uint,\
               self.reg.out.value.uint,
               self.out.value.uint,
             )
