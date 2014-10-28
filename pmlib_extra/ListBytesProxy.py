#=========================================================================
# ListBytesProxy
#=========================================================================
# This class provides a standard Python list-based interface, but the
# implementation essentially turns accesses to getitem/setitem into a
# Bytes object. Assumes that the elements are all 4B

from pymtl import Bits

class ListBytesProxy:

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem, base_addr, size ):
    s.mem       = mem
    s.base_addr = base_addr
    s.size      = size

  #-----------------------------------------------------------------------
  # __len__
  #-----------------------------------------------------------------------

  def __len__( s ):
    return int(s.size)

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------

  def __getitem__( s, idx ):

    if idx >= s.size:
      raise StopIteration

    addr = s.base_addr + 4*idx
    return s.mem[addr:addr+4].int()

  #-----------------------------------------------------------------------
  # __setitem__
  #-----------------------------------------------------------------------

  def __setitem__( s, idx, value ):

    if idx >= s.size:
      raise StopIteration

    addr = s.base_addr + 4*idx;
    s.mem[addr:addr+4] = Bits( 32, value )

