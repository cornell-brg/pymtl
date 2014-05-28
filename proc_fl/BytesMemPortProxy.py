#=========================================================================
# BytesMemPortProxy
#=========================================================================
# These classes provides the Bytes interface, but the implementation
# essentially turns reads/writes into memory requests sent over a
# port-based memory interface. We use greenlets to enable us to wait
# until the response has come back before returning to the function
# accessing the list.

from greenlet import greenlet

class BytesMemPortProxy (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params, memreq, memresp ):

    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

    # Shorter names

    s.mk_req         = s.memreq_params.mk_req
    s.mk_resp        = s.memresp_params.mk_resp
    s.rd             = s.memreq_params.type_read
    s.wr             = s.memresp_params.type_write
    s.data_slice     = s.memresp_params.data_slice
    s.data_nbytes    = s.memreq_params.data_nbits/8

    # References to the memory request and response ports

    s.memreq         = memreq
    s.memresp        = memresp

    s.trace          = " "

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------

  def __getitem__( s, key ):

    # Calculate base address and length for request

    if isinstance( key, slice ):
      addr   = int(key.start)
      nbytes = int(key.stop) - int(key.start)
    else:
      addr   = int(key)
      nbytes = 1

    len_ = nbytes if nbytes < s.data_nbytes else 0

    # Create a memory request to send out memory request port

    s.trace = "r"
    s.memreq.msg.next  = s.mk_req( s.rd, addr, len_, 0 )
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, return the corresponding data

    s.trace = " "
    s.memreq.val.next  = 0
    s.memresp.rdy.next = 0
    return s.memresp.msg[ s.data_slice ][0:nbytes*8]

  #-----------------------------------------------------------------------
  # __setitem__
  #-----------------------------------------------------------------------

  def __setitem__( s, key, value ):

    # Calculate base address and length for request

    if isinstance( key, slice ):
      addr   = int(key.start)
      nbytes = int(key.stop) - int(key.start)
    else:
      addr   = int(key)
      nbytes = 1

    len_ = nbytes if nbytes < s.data_nbytes else 0

    # Create a memory request to send out memory request port

    s.trace = "w"
    s.memreq.msg.next  = s.mk_req( s.wr, addr, len_, value )
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, then we are done

    s.trace = " "
    s.memreq.val.next  = 0
    s.memresp.rdy.next = 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

