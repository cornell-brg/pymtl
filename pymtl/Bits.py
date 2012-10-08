import math

# From the web
# http://www.velocityreviews.com/forums/t668122-number-of-bits-sizeof-int.html

def _num_bits( x ):

  # Special cases

  # I added the +=1 when it is negative since we need an extra bit to be
  # able to store the sign bit and distinguish between the positive and
  # negative versions? -cbatten

  n = 1
  if x == 0:
    return 0
  elif x < 0:
    x = -x
    n += 1

  # Find upper bound of the form 2^(2^n) >= x

  while True:
    y = x >> n
    if y == 0:
      break
    x = y
    n <<= 1

  # Now binary search until we're done

  a = n
  while n > 0:
    n >>= 1
    y = x >> n
    if y > 0:
      x = y
      a += n

  return a

class Bits(object):
  """Class emulating limited precision values of a set bitwidth."""

  def __init__(self, width, value = 0, trunc = False ):

    # Make sure width is non-zero and that we have space for the value

    assert width > 0
    if not trunc:
      assert width >= _num_bits(value)

    self.width = width
    self.wmask = (1 << self.width) - 1

    self.shift_trunc = int( math.ceil( math.log( self.width , 2) ) )

    # If the value is negative then we calculate the twos complement
    # TODO: isn't this unnecessary?
    if isinstance( value, Bits ):
      value_uint = value._uint
    else:
      value_uint = value
    if ( value < 0 ):
      value_uint = ~(-value) + 1

    self._uint = value_uint & self.wmask

  @property
  def uint(self):
    """Return the unsigned integer representation of the bits."""
    return self._uint

  @property
  def int(self):
    """Return the integer representation of the bits."""
    if ( self[self.nbits-1] ):
      twos_complement = ~self + 1
      return -twos_complement._uint
    else:
      return self._uint

  # TODO: remove
  @uint.setter
  def uint(self, value):
    assert self.width >= _num_bits(value)
    self._uint = (value & self.wmask)

  # This matches the nbits syntax we have been using in our models
  @property
  def nbits(self):
    return self.width

  def __repr__(self):
    return "Bits(w={0},v={1})".format(self.width, self._uint)

  def __str__(self):
    num_chars = (((self.width-1)/4)+1)
    str = "{:x}".format(self._uint).zfill(num_chars)
    return str[-num_chars:len(str)]

  def bin_str(self):
    str = "{:b}".format(self._uint).zfill(self.width)
    return str

  #------------------------------------------------------------------------
  # Bitwise Access
  #------------------------------------------------------------------------

  def __getitem__(self, addr):
    """Bitfield reads ([])."""
    # TODO: clean up this logic!
    if isinstance(addr, slice):
      start = addr.start
      stop = addr.stop
      # special case open-ended ranges [:], [N:], and [:N]
      if start is None and stop is None:
        return Bits(self.width,self._uint)
      elif start is None:
        start = 0
      elif stop is None:
        stop = self.width
      # Make sure our ranges are sane
      assert start < stop
      assert stop <= self.width
      width = stop - start
      mask  = (1 << width) - 1
      return Bits( width, (self._uint & (mask << start)) >> start )
    else:
      assert addr < self.width
      return Bits( 1, (self._uint & (1 << addr)) >> addr )

  def __setitem__(self, addr, value):
    """Bitfield writes([])."""
    if isinstance(value, Bits):
      value = value._uint
    # TODO: clean up this logic!
    if isinstance(addr, slice):
      start = addr.start
      stop = addr.stop
      # special case open-ended ranges [:], [N:], and [:N]
      if start is None and stop is None:
        # TODO: optimize and uncomment!!!!
        #assert self.width >= _num_bits(value)
        self._uint = value
        return
      elif start is None:
        start = 0
      elif stop is None:
        stop = self.width
      # Make sure our ranges are sane
      assert start < stop
      assert stop <= self.width
      width = stop - start
      # This assert fires if the value you are trying to store is wider
      # than the bitwidth of the slice you are writing to!
      # TODO: optimize and uncomment!!!!
      #assert width >= _num_bits(value)
      # Clear the bits we want to set
      ones  = (1 << width) - 1
      mask = ~(ones << start)
      cleared_val = self._uint & mask
      # Set the bits
      # TODO: anding with ones to ensure negative value assign works!
      #       do we want this behavior?
      self._uint = cleared_val | ((value & ones) << start)
    else:
      assert addr < self.width
      assert 0 <= value <= 1
      # Clear the bits we want to set
      mask = ~(1 << addr)
      cleared_val = self._uint & mask
      # Set the bits
      self._uint = cleared_val | (value << addr)

  #------------------------------------------------------------------------
  # Arithmetic Operators
  #------------------------------------------------------------------------
  # For now, let's make the width equal to the max of the widths of the
  # two operands. This is verilog semantics:
  #  http://www1.pldworld.com/@xilinx/html/technote/TOOL/MANUAL/21i_doc/data/fndtn/ver/ver4_4.htm

  # TODO: reflected operands?
  def __invert__(self):
    return Bits(self.width, ~self._uint, trunc=True )

  def __add__(self, other):
    if not isinstance(other, Bits):
      other = Bits( _num_bits(other), other )
    return Bits( max( self.width, other.width ),
                 self._uint + other._uint, trunc=True )

  def __sub__(self, other):
    if not isinstance(other, Bits):
      other = Bits( _num_bits(other), other )
    return Bits( max( self.width, other.width ),
                 self._uint - other._uint, trunc=True )

  # TODO: what about multiplying Bits object with an object of other type
  # where the bitwidth of the other type is larger than the bitwidth of the
  # Bits object? ( applies to every other oeprator as well.... )
  def __mul__(self, other):
    if isinstance(other, int):
      return Bits(2*self.width, self._uint * other)
    else:
      assert self.width == other.width
      return Bits(2*self.width, self._uint * other._uint)

  # TODO: implement these?
  #def __floordiv__(self, other)
  #def __mod__(self, other)
  #def __divmod__(self, other)
  #def __pow__(self, other[, modulo])

  #------------------------------------------------------------------------
  # Shift Operators
  #------------------------------------------------------------------------

  def __lshift__(self, other):
    # TODO: best way to handle large shift amounts?
    if isinstance(other, int):
      #assert other <= self.width
      shift_val = Bits( self.shift_trunc, other, trunc=True )
      return Bits( self.width, self._uint << shift_val._uint, trunc=True )
      #return Bits( self.width, self.uint << other, trunc=True )
    else:
      #assert other.uint <= self.width
      shift_val = Bits( self.shift_trunc, other._uint, trunc=True )
      return Bits( self.width, self._uint << shift_val._uint, trunc=True )
      #return Bits( self.width, self.uint << other.uint, trunc=True )

  def __rshift__(self, other):
    if isinstance(other, int):
      #assert other <= self.width
      return Bits(self.width, self._uint >> other)
    else:
      #assert other.uint <= self.width
      return Bits(self.width, self._uint >> other._uint)

  #------------------------------------------------------------------------
  # Bitwise Operators
  #------------------------------------------------------------------------

  def __and__(self, other):
    if isinstance(other, Bits):
      other = other._uint
    assert other >= 0
    return Bits( max( self.width, _num_bits(other) ),
                 self._uint & other)

  def __xor__(self, other):
    if isinstance(other, Bits):
      other = other._uint
    assert other >= 0
    return Bits( max( self.width, _num_bits(other) ),
                 self._uint ^ other)

  def __or__(self, other):
    if isinstance(other, Bits):
      other = other._uint
    assert other >= 0
    return Bits( max( self.width, _num_bits(other) ),
                 self._uint | other)

  #------------------------------------------------------------------------
  # Comparison Operators
  #------------------------------------------------------------------------

  def __nonzero__(self):
    return self._uint != 0

  def __eq__(self,other):
    """Equality operator, special case for comparisons with integers."""
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    #assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint == other

  def __ne__(self,other):
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint != other

  def __lt__(self,other):
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint < other

  def __le__(self,other):
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint <= other

  def __gt__(self,other):
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint > other

  def __ge__(self,other):
    if isinstance(other, Bits):
      assert self.width == other.width
      other = other._uint
    assert other >= 0   # TODO: allow comparison with negative numbers?
    return self._uint >= other

  #------------------------------------------------------------------------
  # Extension
  #------------------------------------------------------------------------

  def zext( self, new_width ):
    return Bits( new_width, self._uint )

  def sext( self, new_width ):
    return Bits( new_width, self.int )

#--------------------------------------------------------------------------
# Helper functions
#--------------------------------------------------------------------------

def concat( bits_list ):

  # First figure total new bitwidth

  nbits = 0
  for bits in bits_list:
    nbits += bits.nbits

  # Create new Bits and add each bits from bits_list to it

  concat_bits = Bits( nbits )

  begin = 0
  for bits in reversed(bits_list):
    concat_bits[ begin : begin+bits.nbits ] = bits
    begin += bits.nbits

  return concat_bits

