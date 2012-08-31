

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

  def __getitem__(self, addr):
    """Bitfield reads ([])."""
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

  def __invert__(self):
    return Bits(self.width, ~self.value)

  #def __eq__(self,other):
  #  if isinstance(other, int):
  #    return self.value == other
