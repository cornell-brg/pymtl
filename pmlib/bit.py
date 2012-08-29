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
