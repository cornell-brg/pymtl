

class Bits(object):
  """Class emulating limited precision values of a set bitwidth."""

  def __init__(self, width, value=0):
    self.width = width
    self.wmask = (1 << self.width) - 1
    self._value = value & self.wmask

  @property
  def value(self):
    """Return the unsigned integer representation of the bits."""
    return self._value
  @value.setter
  def value(self, value):
    self._value = (value & self.wmask)

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
        return self.value
      elif start is None:
        start = 0
      elif stop is None:
        stop = self.width
      # Make sure our ranges are sane
      assert start < stop
      assert stop <= self.width
      width = stop - start
      mask  = (1 << width) - 1
      return (self.value & (mask << start)) >> start
    else:
      assert addr < self.width
      return (self.value & (1 << addr)) >> addr

  def __setitem__(self, addr, value):
    """Bitfield writes([])."""
    # TODO: clean up this logic!
    if isinstance(addr, slice):
      print "BEGIN", addr, bin(value)
      start = addr.start
      stop = addr.stop
      # special case open-ended ranges [:], [N:], and [:N]
      if start is None and stop is None:
        self.value = value
        return
      elif start is None:
        start = 0
      elif stop is None:
        stop = self.width
      # Make sure our ranges are sane
      assert start < stop
      assert stop <= self.width
      width = stop - start
      # Clear the bits we want to set
      ones  = (1 << width) - 1
      mask = ~(ones << start)
      self.value &= mask
      # Set the bits
      self.value |= (value << start)
    else:
      assert addr < self.width
      assert 0 <= value <= 1
      # Clear the bits we want to set
      mask = ~(1 << addr)
      self.value &= mask
      # Set the bits
      self.value |= (value << addr)

  #------------------------------------------------------------------------
  # Arithmetic Operators
  #------------------------------------------------------------------------

  # TODO: reflected operands?
  def __invert__(self):
    return Bits(self.width, ~self.value)

  def __add__(self, other):
    #TODO: width of returned bits?
    #      check widths?
    if isinstance(other, int):
      return Bits(self.width, self.value + other)
    else:
      assert self.width == other.width
      return Bits(self.width, self.value + other.value)

  def __sub__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value - other)
    else:
      assert self.width == other.width
      return Bits(self.width, self.value - other.value)

  def __lshift__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value << other)
    else:
      return Bits(self.width, self.value << other.value)

  def __rshift__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value >> other)
    else:
      return Bits(self.width, self.value >> other.value)

  def __and__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value & other)
    else:
      return Bits(self.width, self.value & other.value)

  def __xor__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value ^ other)
    else:
      return Bits(self.width, self.value ^ other.value)

  def __or__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.value | other)
    else:
      return Bits(self.width, self.value | other.value)

  # TODO: what about multiplying Bits object with an object of other type
  # where the bitwidth of the other type is larger than the bitwidth of the
  # Bits object? ( applies to every other oeprator as well.... )
  def __mul__(self, other):
    if isinstance(other, int):
      return Bits(2*self.width, self.value * other)
    else:
      assert self.width == other.width
      return Bits(2*self.width, self.value * other.value)

  # TODO: implement these?
  #def __floordiv__(self, other)
  #def __mod__(self, other)
  #def __divmod__(self, other)
  #def __pow__(self, other[, modulo])

  #------------------------------------------------------------------------
  # Comparison Operators
  #------------------------------------------------------------------------

  def __eq__(self,other):
    """Equality operator, special case for comparisons with integers."""
    if isinstance(other, int):
      return self.value == other
    else:
      return id(self) == id(other)

  def __ne__(self,other):
    if isinstance(other, int):
      return self.value != other
    else:
      return id(self) != id(other)

  def __lt__(self,other):
    if isinstance(other, int):
      return self.value < other
    # TODO: default return?

  def __le__(self,other):
    if isinstance(other, int):
      return self.value <= other
    # TODO: default return?

  def __gt__(self,other):
    if isinstance(other, int):
      return self.value > other
    # TODO: default return?

  def __ge__(self,other):
    if isinstance(other, int):
      return self.value >= other
    # TODO: default return?
