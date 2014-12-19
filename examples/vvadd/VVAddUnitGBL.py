#=========================================================================
# VVAddUnitGBL
#=========================================================================
# This model implements a hardware unit that does an element-wise sum on
# two vectors in memory, storing the result to a third vector in memory.
# We initialize the model with the base addresses and the length.
# Eventually we could add a message based interface to configure the unit
# and then to read out the result.
#
# We use an elegant combination of a basic function implementation with a
# port-based wrapper based on greenlets to enable interfacing with a
# split-phase memory request/response interface.

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from GreenletWrapper  import GreenletWrapper
from ListMemPortProxy import ListMemPortProxy

#-------------------------------------------------------------------------
# Function Implementation
#-------------------------------------------------------------------------
# This is a plain function implementation of the desired vector-vector
# add behavior.

def vvadd( dest, src0, src1 ):

  for i in xrange(len(dest)):
    dest[i] = src0[i] + src1[i]

#-------------------------------------------------------------------------
# Port-Based Wrapper
#-------------------------------------------------------------------------
# We can use greenlets to wrap the plain function implementation so that
# it can correctly interact with the split-phase memory interface.

class VVAddUnitGBL (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params,
                dest_addr, src0_addr, src1_addr, size ):

    # Short names

    mreq_p  = memreq_params
    mresp_p = memresp_params

    # Memory request/response ports

    s.memreq  = InValRdyBundle  ( mreq_p.nbits  )
    s.memresp = OutValRdyBundle ( mresp_p.nbits )

    # ListMemPortProxy objects

    L = ListMemPortProxy
    s.dest = L( mreq_p, mresp_p, dest_addr, size, s.memreq, s.memresp )
    s.src0 = L( mreq_p, mresp_p, src0_addr, size, s.memreq, s.memresp )
    s.src1 = L( mreq_p, mresp_p, src1_addr, size, s.memreq, s.memresp )

    # Greenlet for functional implementation

    s.vvadd = GreenletWrapper(vvadd)

  #-----------------------------------------------------------------------
  # elaborate_logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    @s.tick
    def logic():

      # This looks like a plain function call, but the greenlets mean
      # that something more sophisticated is going on. The first time we
      # call this wrapper function, the underlying vvadd function will
      # try and access the src0 list. This will get proxied to the dest
      # ListMemPortProxy object which will create a memory request and
      # send it out the memreq port. Since we do not have the data yet,
      # we cannot return the data to the underlying vvadd function so
      # instead we use greenlets to switch back to the tick function. If
      # we had code after this it would be executed. The next time we
      # call tick, we call the wrapper function again, and essentially we
      # jump back into the ListMemPortProxy to see if the response had
      # returned. When the response eventually returns, the
      # ListMemPortProxy object will return the data and the underlying
      # vvadd function will move onto src1.

      s.vvadd( s.dest, s.src0, s.src1 )

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):

    # GreenletWrapper objects include a done method which indicates when
    # they underlying vvadd function has completely finished its
    # execution.

    return s.vvadd.done()

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.dest.line_trace() + " " + \
           s.src0.line_trace() + " " + \
           s.src1.line_trace()

