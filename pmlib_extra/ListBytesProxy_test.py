#=========================================================================
# ListBytesProxy_test
#=========================================================================

from new_pymtl.Bits import Bits
from Bytes          import Bytes
from ListBytesProxy import ListBytesProxy

#-------------------------------------------------------------------------
# vvadd
#-------------------------------------------------------------------------

def vvadd( dest, src0, src1 ):

  for i in xrange(len(dest)):
    dest[i] = src0[i] + src1[i]

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic():

  data = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 ]
  mem = Bytes(18*4)
  for i in xrange(18):
    mem[i*4:i*4+1] = Bits( 32, data[i] )

  src0 = ListBytesProxy( mem, 0*4, 4 )
  src1 = ListBytesProxy( mem, 4*4, 4 )
  dest = ListBytesProxy( mem, 8*4, 4 )

  vvadd( dest, src0, src1 )

  data_ref = [  0,  1,  2,  3,
                4,  5,  6,  7,
                4,  6,  8, 10,
               12, 13, 14, 15,
               16, 17 ]

  data_ref_bytes = Bytes(18*4)
  for i in xrange(18):
    data_ref_bytes[i*4:i*4+1] = Bits( 32, data_ref[i] )

  assert mem == data_ref_bytes

