#=========================================================================
# ListMemPortAdapter
#=========================================================================
# These classes provides a list interface, but the implementation
# essentially turns reads/writes into memory requests sent over a
# port-based memory interface. We use greenlets to enable us to wait
# until the response has come back before returning to the function
# accessing the list.

from greenlet import greenlet

from pclib.ifcs import MemReqMsg, MemRespMsg

#-------------------------------------------------------------------------
# ListMemPortAdapter
#-------------------------------------------------------------------------

class ListMemPortAdapter (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq, memresp ):

    # Shorter names

    s.MemReqMsgType  = memreq.msg.msg_type
    s.MemRespMsgType = memresp.msg.msg_type

    # References to the memory request and response ports

    s.memreq  = memreq
    s.memresp = memresp

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

    len_ = nbytes if nbytes < s.memreq.msg.data.nbits/8 else 0

    # Create a memory request to send out memory request port

    s.trace = "r"

    memreq_msg = s.MemReqMsgType()
    memreq_msg.type_ = MemReqMsg.TYPE_READ
    memreq_msg.addr  = s.base + 4 * addr
    memreq_msg.len   = len_

    s.memreq.msg.next  = memreq_msg
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the ready/response

    greenlet.getcurrent().parent.switch(0)

    # If memory request is not ready yet then yeild

    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    while not s.memreq.rdy:
      s.trace = ";"
      greenlet.getcurrent().parent.switch(0)

    # If memory response has not arrived, then yield

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    while not s.memresp.val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, return the corresponding data

    s.trace = " "
    s.memreq.val.next  = 0
    s.memresp.rdy.next = 0
    return s.memresp.msg.data[0:nbytes*8].int()

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

    len_ = nbytes if nbytes < s.memreq.msg.data.nbits/8 else 0

    # Create a memory request to send out memory request port

    s.trace = "w"

    memreq_msg = s.MemReqMsgType()
    memreq_msg.type_ = MemReqMsg.TYPE_WRITE
    memreq_msg.addr  = s.base + 4 * addr
    memreq_msg.len   = len_
    memreq_msg.data  = value

    s.memreq.msg.next  = memreq_msg
    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    # If memory request is not ready yet then yeild

    s.memreq.val.next  = 1
    s.memresp.rdy.next = 1

    while not s.memreq.rdy:
      s.trace = ";"
      greenlet.getcurrent().parent.switch(0)

    # If memory response has not arrived, then yield

    s.memreq.val.next  = 0
    s.memresp.rdy.next = 1

    while not s.memresp.val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, then we are done

    s.trace = " "
    s.memreq.val.next  = 0
    s.memresp.rdy.next = 0

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

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.trace

