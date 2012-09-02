

class Bits(object):
  """Class emulating limited precision values of a set bitwidth."""

  def __init__(self, width, value=0):
    assert width > 0
    self.width = width
    self.wmask = (1 << self.width) - 1
    if value is not None:
      self._uint = value & self.wmask
    else:
      self._uint = None

  @property
  def uint(self):
    """Return the unsigned integer representation of the bits."""
    if self._uint == None:
      return 0
    return self._uint
  @uint.setter
  def uint(self, value):
    self._uint = (value & self.wmask)

  def __repr__(self):
    return "Bits(w={0},v={1})".format(self.width, self.uint)

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
        return self.uint
      elif start is None:
        start = 0
      elif stop is None:
        stop = self.width
      # Make sure our ranges are sane
      assert start < stop
      assert stop <= self.width
      width = stop - start
      mask  = (1 << width) - 1
      return (self.uint & (mask << start)) >> start
    else:
      assert addr < self.width
      return (self.uint & (1 << addr)) >> addr

  def __setitem__(self, addr, value):
    """Bitfield writes([])."""
    if isinstance(value, Bits):
      value = value.uint
    # TODO: clean up this logic!
    if isinstance(addr, slice):
      start = addr.start
      stop = addr.stop
      # special case open-ended ranges [:], [N:], and [:N]
      if start is None and stop is None:
        self.uint = value
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
      self.uint &= mask
      # Set the bits
      self.uint |= (value << start)
    else:
      assert addr < self.width
      assert 0 <= value <= 1
      # Clear the bits we want to set
      mask = ~(1 << addr)
      self.uint &= mask
      # Set the bits
      self.uint |= (value << addr)

  #------------------------------------------------------------------------
  # Arithmetic Operators
  #------------------------------------------------------------------------

  # TODO: reflected operands?
  def __invert__(self):
    return Bits(self.width, ~self.uint)

  def __add__(self, other):
    #TODO: width of returned bits?
    #      check widths?
    if isinstance(other, int):
      return Bits(self.width, self.uint + other)
    else:
      assert self.width == other.width
      return Bits(self.width, self.uint + other.uint)

  def __sub__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint - other)
    else:
      assert self.width == other.width
      return Bits(self.width, self.uint - other.uint)

  def __lshift__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint << other)
    else:
      return Bits(self.width, self.uint << other.uint)

  def __rshift__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint >> other)
    else:
      return Bits(self.width, self.uint >> other.uint)

  def __and__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint & other)
    else:
      return Bits(self.width, self.uint & other.uint)

  def __xor__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint ^ other)
    else:
      return Bits(self.width, self.uint ^ other.uint)

  def __or__(self, other):
    if isinstance(other, int):
      return Bits(self.width, self.uint | other)
    else:
      return Bits(self.width, self.uint | other.uint)

  # TODO: what about multiplying Bits object with an object of other type
  # where the bitwidth of the other type is larger than the bitwidth of the
  # Bits object? ( applies to every other oeprator as well.... )
  def __mul__(self, other):
    if isinstance(other, int):
      return Bits(2*self.width, self.uint * other)
    else:
      assert self.width == other.width
      return Bits(2*self.width, self.uint * other.uint)

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
      return self.uint == other
    elif isinstance(other, Bits):
      assert self.width == other.width
      return self.uint == other.uint
    else:
      return False

  def __ne__(self,other):
    if isinstance(other, int):
      return self.uint != other
    elif isinstance(other, Bits):
      assert self.width == other.width
      return self.uint != other.uint
    else:
      return False

  def __lt__(self,other):
    if isinstance(other, int):
      return self.uint < other
    # TODO: default return?

  def __le__(self,other):
    if isinstance(other, int):
      return self.uint <= other
    # TODO: default return?

  def __gt__(self,other):
    if isinstance(other, int):
      return self.uint > other
    # TODO: default return?

  def __ge__(self,other):
    if isinstance(other, int):
      return self.uint >= other
    # TODO: default return?
