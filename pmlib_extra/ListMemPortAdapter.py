#=========================================================================
# BytesMemPortProxy
#=========================================================================
# These classes provides the Bytes interface, but the implementation
# essentially turns reads/writes into memory requests sent over a
# port-based memory interface. We use greenlets to enable us to wait
# until the response has come back before returning to the function
# accessing the list.

from greenlet import greenlet

class ListMemPortAdapter (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, parent ):

    # Shorter names

    s.mk_req         = parent.req.mk_msg
    s.mk_resp        = parent.resp.mk_resp
    s.rd             = 0
    s.wr             = 1

    # References to the memory request and response ports

    s.memreq         = parent
    s.memresp        = parent

    s.size = 0
    s.base = 0
    s.base_set = False
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
      nbytes = 4

    len_ = nbytes if nbytes < s.memreq.req.data.nbits/8 else 0

    # Create a memory request to send out memory request port

    s.trace = "r"
    s.memreq.req_msg.next  = s.mk_req( s.rd, s.base + 4 * addr, len_, 0 )
    s.memreq.req_val.next  = 1
    s.memresp.resp_rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.req_val.next  = 0
    s.memresp.resp_rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.resp_val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, return the corresponding data

    s.trace = " "
    s.memreq.req_val.next  = 0
    s.memresp.resp_rdy.next = 0
    return s.memresp.resp_msg.data[0:nbytes*8]

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
      nbytes = 4

    len_ = nbytes if nbytes < s.data_nbytes else 0

    # Create a memory request to send out memory request port

    s.trace = "w"
    s.memreq.req_msg.next  = s.mk_msg( s.wr, s.base + 4 * addr, len_, value )
    s.memreq.req_val.next  = 1
    s.memresp.resp_rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    s.memreq.req_val.next  = 0
    s.memresp.resp_rdy.next = 1

    # If memory response has not arrived, then yield

    while not s.memresp.resp_val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, then we are done

    s.trace = " "
    s.memreq.req_val.next  = 0
    s.memresp.resp_rdy.next = 0

  def set_base( s, addr ):
    s.base = addr
    s.base_set = True

  def set_size( s, size):
    s.size = size

  def __len__( s ):
    return s.size

  def __iter__( s ):
    for x in range(s.size):
      yield s[x]


  def is_rdy( s ):
    return s.base_set and s.mod.size > 0
  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

