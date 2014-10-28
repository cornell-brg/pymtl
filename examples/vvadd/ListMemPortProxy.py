#=========================================================================
# ListProxy
#=========================================================================
# This class provides a standard Python list-based interface, but the
# implementation essentially turns accesses to getitem/setitem into
# memory requests sent over a port-based memory interface. We use
# greenlets to enable us to wait until the response has come back before
# returning to the function accessing the list.

from greenlet import greenlet

class ListMemPortProxy:

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params, base_addr, size,
                memreq, memresp ):

    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params
    s.base_addr      = base_addr
    s.size           = size

    # Shorter names

    s.mk_req         = s.memreq_params.mk_req
    s.mk_resp        = s.memresp_params.mk_resp
    s.rd             = s.memreq_params.type_read
    s.wr             = s.memresp_params.type_write
    s.data_slice     = s.memresp_params.data_slice

    # References to the memory request and response ports

    s.memreq         = memreq
    s.memresp        = memresp

    s.trace          = " "

  #-----------------------------------------------------------------------
  # __len__
  #-----------------------------------------------------------------------

  def __len__( s ):
    return s.size

  #-----------------------------------------------------------------------
  # __getitem__
  #-----------------------------------------------------------------------

  def __getitem__( s, idx ):

    if idx >= s.size:
      raise StopIteration

    # Create a memory request to send out memory request port

    s.trace = "r"
    r_addr = s.base_addr + (idx * 4)
    s.memreq.msg.next  = s.mk_req( s.rd, r_addr, 0, 0 )
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.val or not s.memresp.rdy:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, return the corresponding data

    s.trace = " "
    s.memreq.val.next  = 0
    s.memresp.rdy.next = 0
    return s.memresp.msg[ s.data_slice ].uint()

  #-----------------------------------------------------------------------
  # __setitem__
  #-----------------------------------------------------------------------

  def __setitem__( s, idx, value ):

    if idx >= s.size:
      raise StopIteration

    # Create a memory request to send out memory request port

    s.trace = "w"
    r_addr = s.base_addr + (idx * 4)
    s.memreq.msg.next  = s.mk_req( s.wr, r_addr, 0, value )
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.val or not s.memresp.rdy:
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

