#=========================================================================
# Bytes
#=========================================================================
# Simple class that encapsulates a byte array but with extra support for
# reading and writing Bits.
#
# Author : Christopher Batten
# Date   : May 26, 2014

from pymtl import Bits
import struct
import binascii

class Bytes (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, size ):
    self.mem = bytearray(size)

  #-----------------------------------------------------------------------
  # setitem
  #-----------------------------------------------------------------------

  def __setitem__( self, key, value ):

    if isinstance( value, bytearray ) or isinstance( value, str ):

      start_addr = 0
      stop_addr  = 0

      if isinstance( key, slice ):
        start_addr = int(key.start)
        stop_addr  = int(key.stop)
      else:
        start_addr = int(key)
        stop_addr  = int(key)+1

      self.mem[start_addr:stop_addr] = value

    else:

      start_addr = 0
      num_bytes  = 0

      if isinstance( key, slice ):
        start_addr = int(key.start)
        num_bytes  = int(key.stop) - int(key.start)
      else:
        start_addr = int(key)
        num_bytes  = 1

      if isinstance( value, Bits ):
        bits = value
        assert value.nbits % 8 == 0
      else:
        bits = Bits( num_bytes*8, value )

      for i in range(num_bytes):
        self.mem[start_addr+i] = bits[i*8:i*8+8]

  #-----------------------------------------------------------------------
  # getitem
  #-----------------------------------------------------------------------

  def __getitem__( self, key ):

    if isinstance( key, slice ):

      start_addr = int(key.start)
      num_bytes = int(key.stop) - int(key.start)
      bits = Bits( 8*num_bytes )

      for i in range(num_bytes):
        bits[i*8:i*8+8] = \
          struct.unpack_from("<B",buffer(self.mem,start_addr+i,1))[0]

      return bits

    else:
      idx = int(key)
      return Bits( 8, struct.unpack_from("<B",buffer(self.mem,idx,1))[0] )

  #-----------------------------------------------------------------------
  # eq
  #-----------------------------------------------------------------------

  def __eq__( self, other ):
    return self.mem == other.mem

  #-----------------------------------------------------------------------
  # str
  #-----------------------------------------------------------------------

  def __str__( self ):
    return binascii.hexlify(self.mem)

