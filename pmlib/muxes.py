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

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(2) ]
    self.sel = InPort  ( 1     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 2

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    else:
      self.out.value = self.in_[1].value

  def line_trace( self ):
    return "{:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux3
#-------------------------------------------------------------------------

class Mux3( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(3) ]
    self.sel = InPort  ( 2     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 3

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    else:
      self.out.value = self.in_[2].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux4
#-------------------------------------------------------------------------

class Mux4( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(4) ]
    self.sel = InPort  ( 2     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 4

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    elif self.sel.value == 2:
      self.out.value = self.in_[2].value
    else:
      self.out.value = self.in_[3].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.in_[3].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux5
#-------------------------------------------------------------------------

class Mux5( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(5) ]
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 5

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    elif self.sel.value == 2:
      self.out.value = self.in_[2].value
    elif self.sel.value == 3:
      self.out.value = self.in_[3].value
    else:
      self.out.value = self.in_[4].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.in_[3].value.uint, self.in_[4].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux6
#-------------------------------------------------------------------------

class Mux6( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(6) ]
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 6

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    elif self.sel.value == 2:
      self.out.value = self.in_[2].value
    elif self.sel.value == 3:
      self.out.value = self.in_[3].value
    elif self.sel.value == 4:
      self.out.value = self.in_[4].value
    else:
      self.out.value = self.in_[5].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.in_[3].value.uint, self.in_[4].value.uint, self.in_[5].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux7
#-------------------------------------------------------------------------

class Mux7( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(7) ]
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 7

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    elif self.sel.value == 2:
      self.out.value = self.in_[2].value
    elif self.sel.value == 3:
      self.out.value = self.in_[3].value
    elif self.sel.value == 4:
      self.out.value = self.in_[4].value
    elif self.sel.value == 5:
      self.out.value = self.in_[5].value
    else:
      self.out.value = self.in_[6].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.in_[3].value.uint, self.in_[4].value.uint, self.in_[5].value.uint,
               self.in_[6].value.uint,
               self.sel.value.uint, self.out.value.uint )

#-------------------------------------------------------------------------
# Mux8
#-------------------------------------------------------------------------

class Mux8( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):

    self.in_ = [ InPort( nbits ) for x in xrange(8) ]
    self.sel = InPort  ( 3     )
    self.out = OutPort ( nbits )

  @combinational
  def comb_logic( self ):
    assert self.sel.value < 8

    if self.sel.value == 0:
      self.out.value = self.in_[0].value
    elif self.sel.value == 1:
      self.out.value = self.in_[1].value
    elif self.sel.value == 2:
      self.out.value = self.in_[2].value
    elif self.sel.value == 3:
      self.out.value = self.in_[3].value
    elif self.sel.value == 4:
      self.out.value = self.in_[4].value
    elif self.sel.value == 5:
      self.out.value = self.in_[5].value
    elif self.sel.value == 6:
      self.out.value = self.in_[6].value
    else:
      self.out.value = self.in_[7].value

  def line_trace( self ):
    return "{:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:04x} {:01x} () {:04x}" \
      .format( self.in_[0].value.uint, self.in_[1].value.uint, self.in_[2].value.uint,
               self.in_[3].value.uint, self.in_[4].value.uint, self.in_[5].value.uint,
               self.in_[6].value.uint, self.in_[7].value.uint,
               self.sel.value.uint, self.out.value.uint )

