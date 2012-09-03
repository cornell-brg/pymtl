#=========================================================================
# Muxes
#=========================================================================
# Asserting that a select value is out of range is not currently
# translatable.

from pymtl import *

#-------------------------------------------------------------------------
# Mux2
#-------------------------------------------------------------------------

class Mux2( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.sel = InPort  ( 1     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 2

    if self.sel.value == 0:
      self.out.value = self.in0.value
    else:
      self.out.value = self.in1.value

  def line_trace( self ):
    return "{:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux3
#-------------------------------------------------------------------------

class Mux3( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.sel = InPort  ( 2     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 3

    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    else:
      self.out.value = self.in2.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux4
#-------------------------------------------------------------------------

class Mux4( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.in3 = InPort  ( nbits )
    self.sel = InPort  ( 2     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 4

    if self.sel.value == 0:
      self.out.value = self.in0.value
    elif self.sel.value == 1:
      self.out.value = self.in1.value
    elif self.sel.value == 2:
      self.out.value = self.in2.value
    else:
      self.out.value = self.in3.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.in3.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux5
#-------------------------------------------------------------------------

class Mux5( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.in3 = InPort  ( nbits )
    self.in4 = InPort  ( nbits )
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

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
    else:
      self.out.value = self.in4.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.in3.value.uint, self.in4.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux6
#-------------------------------------------------------------------------

class Mux6( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.in3 = InPort  ( nbits )
    self.in4 = InPort  ( nbits )
    self.in5 = InPort  ( nbits )
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

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
    else:
      self.out.value = self.in5.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.in3.value.uint, self.in4.value.uint, self.in5.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux7
#-------------------------------------------------------------------------

class Mux7( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.in3 = InPort  ( nbits )
    self.in4 = InPort  ( nbits )
    self.in5 = InPort  ( nbits )
    self.in6 = InPort  ( nbits )
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

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
    else:
      self.out.value = self.in6.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.in3.value.uint, self.in4.value.uint, self.in5.value.uint,
               self.in6.value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux8
#-------------------------------------------------------------------------

class Mux8( Model ):

  def __init__( self, nbits = 1 ):

    self.in0 = InPort  ( nbits )
    self.in1 = InPort  ( nbits )
    self.in2 = InPort  ( nbits )
    self.in3 = InPort  ( nbits )
    self.in4 = InPort  ( nbits )
    self.in5 = InPort  ( nbits )
    self.in6 = InPort  ( nbits )
    self.in7 = InPort  ( nbits )
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

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
    else:
      self.out.value = self.in7.value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in0.value.uint, self.in1.value.uint, self.in2.value.uint,
               self.in3.value.uint, self.in4.value.uint, self.in5.value.uint,
               self.in6.value.uint, self.in7.value.uint,
               self.sel.value.uint, self.out.value.uint )

