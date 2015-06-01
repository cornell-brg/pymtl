#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports. This version is a
# little different from the one in pclib because we actually use the
# memory messages correctly in the interface.

from __future__ import print_function

from pymtl      import *
from pclib.ifcs import MemMsg, MemReqMsg, MemRespMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.cl   import InValRdyRandStallAdapter
from pclib.cl   import OutValRdyInelasticPipeAdapter

class TestMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem_ifc_types=MemMsg(32,32), nports=1,
                stall_prob=0, latency=0, mem_nbytes=2**20 ):

    # Interface

    xr = range
    s.reqs  = [ InValRdyBundle  ( mem_ifc_types.req  ) for _ in xr(nports) ]
    s.resps = [ OutValRdyBundle ( mem_ifc_types.resp ) for _ in xr(nports) ]

    # Checks

    assert mem_ifc_types.req.data.nbits  % 8 == 0
    assert mem_ifc_types.resp.data.nbits % 8 == 0

    # Buffers to hold memory request/response messages

    s.reqs_q = []
    for req in s.reqs:
      s.reqs_q.append( InValRdyRandStallAdapter( req, stall_prob ) )

    s.resps_q = []
    for resp in s.resps:
      s.resps_q.append( OutValRdyInelasticPipeAdapter( resp, latency ) )

    # Actual memory

    s.mem = bytearray( mem_nbytes )

    # Local constants

    s.mem_ifc_types = mem_ifc_types
    s.nports = nports

    #---------------------------------------------------------------------
    # Tick
    #---------------------------------------------------------------------

    @s.tick_cl
    def tick():

      # Tick adapters

      for req_q, resp_q in zip( s.reqs_q, s.resps_q ):
        req_q.xtick()
        resp_q.xtick()

      # Iterate over input/output queues

      for req_q, resp_q in zip( s.reqs_q, s.resps_q ):

        if not req_q.empty() and not resp_q.full():

          # Dequeue memory request message

          memreq = req_q.deq()

          # When len is zero, then we use all of the data

          nbytes = memreq.len
          if memreq.len == 0:
            nbytes = s.mem_ifc_types.req.data.nbits/8

          # Handle a read request

          if memreq.type_ == MemReqMsg.TYPE_READ:

            # Copy the bytes from the bytearray into read data bits

            read_data = Bits( s.mem_ifc_types.req.data.nbits )
            for j in range( nbytes ):
              read_data[j*8:j*8+8] = s.mem[ memreq.addr + j ]

            # Create and enqueu response message

            memresp = s.mem_ifc_types.resp()
            memresp.type_ = MemRespMsg.TYPE_READ
            memresp.len   = memreq.len
            memresp.data  = read_data

            resp_q.enq( memresp )

          # Handle a write request

          elif memreq.type_ == MemReqMsg.TYPE_WRITE:

            # Copy write data bits into bytearray

            write_data = memreq.data
            for j in range( nbytes ):
              s.mem[ memreq.addr + j ] = write_data[j*8:j*8+8].uint()

            # Create and enqueu response message

            memresp = s.mem_ifc_types.resp()
            memresp.type_ = MemRespMsg.TYPE_WRITE
            memresp.len   = 0
            memresp.data  = 0

            resp_q.enq( memresp )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    trace_str = ""
    for req, resp_q, resp in zip( s.reqs, s.resps_q, s.resps ):
      trace_str += "{}({}){} ".format( req, resp_q, resp )

    return trace_str

  #-----------------------------------------------------------------------
  # write memory function
  #-----------------------------------------------------------------------
  # Writes the list of bytes to the given memory address.

  def write_mem( s, addr, data ):
    assert len(s.mem) > (addr + len(data))
    s.mem[ addr : addr + len(data) ] = data

  #-----------------------------------------------------------------------
  # read memory function
  #-----------------------------------------------------------------------
  # Reads size bytes from the given memory address

  def read_mem( s, addr, size ):
    assert len(s.mem) > (addr + size)
    return s.mem[ addr : addr + size ]

