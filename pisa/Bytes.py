#=========================================================================
# Bytes
#=========================================================================
# Simple class that encapsulates a byte array but with extra support for
# reading and writing Bits.
#
# Author : Christopher Batten
# Date   : May 26, 2014

from new_pymtl import Bits
import struct
import binascii

class Bytes (object):

  def __init__( self, size ):
    self.mem  = bytearray(size)

  def __setitem__( self, key, value ):

    if isinstance( value, bytearray ) or isinstance( value, str ):

      start_addr = 0
      stop_addr  = 0

      if isinstance( key, slice ):
        start_addr = int(key.start)
        stop_addr  = int(key.stop)
      elif isinstance( key, int ):
        start_addr = key
        stop_addr  = key+1
      elif isinstance( key, Bits ):
        start_addr = int(key)
      else:
        raise TypeError( "Invalid key type" )

      self.mem[start_addr:stop_addr] = value

    elif isinstance( value, Bits ):

      assert value.nbits % 8 == 0

      start_addr = 0
      num_bytes  = 0

      if isinstance( key, slice ):
        start_addr = int(key.start)
        num_bytes  = int(key.stop) - int(key.start)
      elif isinstance( key, int ):
        start_addr = key
        num_bytes  = 1
      elif isinstance( key, Bits ):
        start_addr = int(key)
        num_bytes  = 1
      else:
        raise TypeError( "Invalid key type" )

      for i in xrange(num_bytes):
        self.mem[start_addr+i] = value[i*8:i*8+8]

    else:
      raise TypeError( "Invalid value type" )

  def __getitem__( self, key ):

    if isinstance( key, slice ):

      start_addr = int(key.start)
      num_bytes = int(key.stop) - int(key.start)
      bits = Bits( 8*num_bytes )

      for i in xrange(num_bytes):
        bits[i*8:i*8+8] = \
          struct.unpack_from("<B",buffer(self.mem,start_addr+i,1))[0]

      return bits

    elif isinstance( key, int ):
      return Bits( 8, struct.unpack_from("<B",buffer(self.mem,key,1))[0] )

    elif isinstance( key, Bits ):
      idx = int(key)
      return Bits( 8, struct.unpack_from("<B",buffer(self.mem,idx,1))[0] )

    else:
      raise TypeError( "Invalid key type" )

  def __eq__( self, other ):
    return self.mem == other.mem

  def __str__( self ):
    return binascii.hexlify(self.mem)

