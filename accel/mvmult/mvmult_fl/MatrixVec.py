#=========================================================================
# MatrixVec
#=========================================================================
# Functional implementation of our matrix-vector multiplication unit.

from pclib.fl import ListBytesProxy

class MatrixVec (object):

  #-----------------------------------------------------------------------
  # Pure-Python Implementation
  #-----------------------------------------------------------------------

  @staticmethod
  def mvmult( dest, src0, src1 ):

    result = 0
    for i in xrange(len(src0)):
      result += src0[i] * src1[i]

    dest[0] = result

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem ):
    s.size      = 0
    s.src0_addr = 0x0000
    s.src0_addr = 0x0000
    s.dest_addr = 0x0000
    s.mem       = mem

  #-----------------------------------------------------------------------
  # Configuration
  #-----------------------------------------------------------------------

  def set_size( s, size ):
    s.size = size

  def set_src0_addr( s, src0_addr ):
    s.src0_addr = src0_addr

  def set_src1_addr( s, src1_addr ):
    s.src1_addr = src1_addr

  def set_dest_addr( s, dest_addr ):
    s.dest_addr = dest_addr

  #-----------------------------------------------------------------------
  # go
  #-----------------------------------------------------------------------

  def go( s ):

    src0 = ListBytesProxy( s.mem, s.src0_addr, s.size )
    src1 = ListBytesProxy( s.mem, s.src1_addr, s.size )
    dest = ListBytesProxy( s.mem, s.dest_addr, 1      )

    MatrixVec.mvmult( dest, src0, src1 )

