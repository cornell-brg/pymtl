import sys
sys.path.append('..')
from pymtl import *

class Mux2( Model ):

  def __init__( self, W = 16 ):
#    self.in_ = [ InPort( W ) for x in range(2) ]
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.sel = InPort( 1 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 2
    if self.sel.value == 0:
      self.out.value = self.in0.value
    else:
      self.out.value = self.in1.value
#      self.out.value = self.in_[self.sel.value].value

class Mux3( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.sel = InPort( 2 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 3
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    else:
      self.out.value = 0

class Mux4( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.in3 = InPort( W )
    self.sel = InPort( 2 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 4
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    elif self.sel.value == 3:
      self.out.value = self.in3.value
    else:
      self.out.value = 0

class Mux5( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.in3 = InPort( W )
    self.in4 = InPort( W )
    self.sel = InPort( 3 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 5
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    elif self.sel.value == 3:
      self.out.value = self.in3.value
    elif self.sel.value == 4:
      self.out.value = self.in4.value
    else:
      self.out.value = 0

class Mux6( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.in3 = InPort( W )
    self.in4 = InPort( W )
    self.in5 = InPort( W )
    self.sel = InPort( 3 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 6
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    elif self.sel.value == 3:
      self.out.value = self.in3.value
    elif self.sel.value == 4:
      self.out.value = self.in4.value
    elif self.sel.value == 5:
      self.out.value = self.in5.value
    else:
      self.out.value = 0

class Mux7( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.in3 = InPort( W )
    self.in4 = InPort( W )
    self.in5 = InPort( W )
    self.in6 = InPort( W )
    self.sel = InPort( 3 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 7
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    elif self.sel.value == 3:
      self.out.value = self.in3.value
    elif self.sel.value == 4:
      self.out.value = self.in4.value
    elif self.sel.value == 5:
      self.out.value = self.in5.value
    elif self.sel.value == 6:
      self.out.value = self.in6.value
    else:
      self.out.value = 0

class Mux8( Model ):

  def __init__( self, W = 16 ):
    self.in0 = InPort( W )
    self.in1 = InPort( W )
    self.in2 = InPort( W )
    self.in3 = InPort( W )
    self.in4 = InPort( W )
    self.in5 = InPort( W )
    self.in6 = InPort( W )
    self.in7 = InPort( W )
    self.sel = InPort( 3 )
    self.out = OutPort( W )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 8
    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    elif self.sel.value == 3:
      self.out.value = self.in3.value
    elif self.sel.value == 4:
      self.out.value = self.in4.value
    elif self.sel.value == 5:
      self.out.value = self.in5.value
    elif self.sel.value == 6:
      self.out.value = self.in6.value
    elif self.sel.value == 7:
      self.out.value = self.in7.value
    else:
      self.out.value = 0


