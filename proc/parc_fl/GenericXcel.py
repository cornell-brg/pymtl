#=========================================================================
# Generic Xcel FL Model
#=========================================================================
# Generic accelerator that simply has 32 accelerator registers and
# enables another model to read/write these registeres using XcelReqMsgs.
# The accelerator also has an interface to memory, even though it doesn't
# use this interface.

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import XcelReqMsg, XcelRespMsg
from pclib.ifcs import MemMsg
from pclib.fl   import InValRdyQueueAdapter, OutValRdyQueueAdapter
from pclib.fl   import ListMemPortAdapter

class GenericXcelFL( Model ):

  # Constructor

  def __init__( s, mem_ifc_types=MemMsg(32,32) ):

    # Interface

    s.xcelreq   = InValRdyBundle  ( XcelReqMsg()  )
    s.xcelresp  = OutValRdyBundle ( XcelRespMsg() )

    #s.memreq    = InValRdyBundle  ( mem_ifc_types.req  )
    #s.memresp   = OutValRdyBundle ( mem_ifc_types.resp )

    # Adapters

    s.xcelreq_q  = InValRdyQueueAdapter  ( s.xcelreq  )
    s.xcelresp_q = OutValRdyQueueAdapter ( s.xcelresp )

    # Accelerator registers

    s.xregs = [ Bits(32,0) for _ in xrange(32) ]

    # Concurrent block

    @s.tick_fl
    def block():

      # We loop forever handling accelerator requests.

      while True:

        xcelreq_msg = s.xcelreq_q.popleft()

        if xcelreq_msg.type_ == XcelReqMsg.TYPE_READ:
          data = s.xregs[xcelreq_msg.raddr]
          s.xcelresp_q.append( XcelRespMsg().mk_rd( data ) )
        else:
          s.xregs[xcelreq_msg.raddr] = xcelreq_msg.data
          s.xcelresp_q.append( XcelRespMsg().mk_wr() )

  # Line tracing

  def line_trace( s ):
    return "{}(){}".format( s.xcelreq, s.xcelresp )

