#=========================================================================
# MatrixVecProxy
#=========================================================================
# Same interface as MatrixVec except that it proxies the commands to a
# port based interface.

from greenlet import greenlet
from pymtl    import Bits
from pclib.fl import OutQueuePortProxy

class MatrixVecProxy (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, to_cp2, from_cp2 ):

    s.to_cp2       = to_cp2
    s.to_cp2_queue = OutQueuePortProxy( to_cp2 )
    s.from_cp2     = from_cp2
    s.trace        = " "

  #-----------------------------------------------------------------------
  # Helper
  #-----------------------------------------------------------------------

  @staticmethod
  def mk_msg( addr, data ):
    msg = Bits(37)
    msg[32:37] = addr
    msg[ 0:32] = data
    return msg

  #-----------------------------------------------------------------------
  # Configuration
  #-----------------------------------------------------------------------

  def set_size( s, size ):
    s.to_cp2_queue.append( MatrixVecProxy.mk_msg( 0x1, size ) )

  def set_src0_addr( s, src0_addr ):
    s.to_cp2_queue.append( MatrixVecProxy.mk_msg( 0x2, src0_addr ) )

  def set_src1_addr( s, src1_addr ):
    s.to_cp2_queue.append( MatrixVecProxy.mk_msg( 0x3, src1_addr ) )

  def set_dest_addr( s, dest_addr ):
    s.to_cp2_queue.append( MatrixVecProxy.mk_msg( 0x4, dest_addr ) )

  #-----------------------------------------------------------------------
  # go
  #-----------------------------------------------------------------------

  def go( s ):

    s.trace = " "

    s.to_cp2_queue.append( MatrixVecProxy.mk_msg( 0x0, 0x1 ) )

    # Wait at least one cycle

    greenlet.getcurrent().parent.switch(0)

    # If cp2 not done then yield

    while s.from_cp2.done != 1:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # cp2 is done

    s.trace = " "

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "(" + s.trace + s.to_cp2_queue.line_trace() + ")"

