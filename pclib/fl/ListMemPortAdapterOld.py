#=========================================================================
# ListMemPortAdapterOld
#=========================================================================
# These classes provides a list interface, but the implementation
# essentially turns reads/writes into memory requests sent over a
# port-based memory interface. We use greenlets to enable us to wait
# until the response has come back before returning to the function
# accessing the list.
#
# This is the old version of this adapter which works with a
# ParentReqRespBundle. Unfortunately, our current version of these
# ReqRespBundles is not very clean since we do not support nested port
# bundles. So we should either add support for nested port bundles, or
# change the users of this adapter so they no longer use ReqRespBundles.
#

from greenlet import greenlet

from pclib.ifcs import MemReqMsg, MemRespMsg

#-------------------------------------------------------------------------
# ListMemPortAdapterOld
#-------------------------------------------------------------------------

class ListMemPortAdapterOld (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memifc ):

    # Shorter names

    s.MemReqMsgType  = memifc.req_msg.msg_type
    s.MemRespMsgType = memifc.resp_msg.msg_type

    # References to the memory request and response ports

    s.memifc = memifc

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

    len_ = nbytes if nbytes < s.memifc.req_msg.data.nbits/8 else 0

    # Create a memory request to send out memory request port

    s.trace = "r"

    memreq_msg = s.MemReqMsgType()
    memreq_msg.type_ = MemReqMsg.TYPE_READ
    memreq_msg.addr  = s.base + 4 * addr
    memreq_msg.len   = len_

    s.memifc.req_msg.next  = memreq_msg
    s.memifc.req_val.next  = 1
    s.memifc.resp_rdy.next = 1

    # Yield so we wait at least one cycle for the ready/response

    greenlet.getcurrent().parent.switch(0)

    # If memory request is not ready yet then yeild

    s.memifc.req_val.next  = 1
    s.memifc.resp_rdy.next = 1

    while not s.memifc.req_rdy:
      s.trace = ";"
      greenlet.getcurrent().parent.switch(0)

    # If memory response has not arrived, then yield

    s.memifc.req_val.next  = 0
    s.memifc.resp_rdy.next = 1

    while not s.memifc.resp_val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, return the corresponding data

    s.trace = " "
    s.memifc.req_val.next  = 0
    s.memifc.resp_rdy.next = 0
    return s.memifc.resp_msg.data[0:nbytes*8].int()

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

    len_ = nbytes if nbytes < s.memifc.req_msg.data.nbits/8 else 0

    # Create a memory request to send out memory request port

    s.trace = "w"

    memreq_msg = s.MemReqMsgType()
    memreq_msg.type_ = MemReqMsg.TYPE_WRITE
    memreq_msg.addr  = s.base + 4 * addr
    memreq_msg.len   = len_
    memreq_msg.data  = value

    s.memifc.req_msg.next  = memreq_msg
    s.memifc.req_val.next  = 1
    s.memifc.resp_rdy.next = 1

    # Yield so we wait at least one cycle for the response

    greenlet.getcurrent().parent.switch(0)

    # If memory request is not ready yet then yeild

    s.memifc.req_val.next  = 1
    s.memifc.resp_rdy.next = 1

    while not s.memifc.req_rdy:
      s.trace = ";"
      greenlet.getcurrent().parent.switch(0)

    # If memory response has not arrived, then yield

    s.memifc.req_val.next  = 0
    s.memifc.resp_rdy.next = 1

    while not s.memifc.resp_val:
      s.trace = ":"
      greenlet.getcurrent().parent.switch(0)

    # When memory response has arrived, then we are done

    s.trace = " "
    s.memifc.req_val.next  = 0
    s.memifc.resp_rdy.next = 0

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

