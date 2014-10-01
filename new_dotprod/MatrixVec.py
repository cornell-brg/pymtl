#=========================================================================
# MatrixVec
#=========================================================================
# Functional implementation of our matrix-vector multiplication unit.

from pmlib_extra import ListBytesProxy

class MatrixVec (object):

  #-----------------------------------------------------------------------
  # Pure-Python Implementation
  #-----------------------------------------------------------------------

  @staticmethod
  def mvmult(src0, src1 ):

    result = 0
    for i in xrange(len(src0)):
      result += src0[i] * src1[i]

    return result

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem ):
    s.size      = 0
    s.src0_addr = 0x0000
    s.src0_addr = 0x0000
    s.mem       = mem
    s.valid = [False] * 3

  #-----------------------------------------------------------------------
  # Configuration
  #-----------------------------------------------------------------------

  def set_size( s, size ):
    s.size = size
    s.valid[0] = True

  def set_src0( s, src0_addr ):
    s.src0_addr = src0_addr
    s.valid[1] = True

  def set_src1( s, src1_addr ):
    s.src1_addr = src1_addr
    s.valid[2] = True

  def is_valid( s ):
    return s.valid[0] and s.valid[1] and s.valid[2]

  #-----------------------------------------------------------------------
  # go
  #-----------------------------------------------------------------------

  def go( s ):

    src0 = ListBytesProxy( s.mem, s.src0_addr, s.size )
    src1 = ListBytesProxy( s.mem, s.src1_addr, s.size )

    result = MatrixVec.mvmult(src0, src1 )

    s.valid = [False] * 3

    return result
