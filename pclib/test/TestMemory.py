#=========================================================================
# TestMemory
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports and includes random
# delays for responses.

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test import TestRandomDelay

from TestSimpleMemory import TestSimpleMemory

import pclib.ifcs.valrdy   as valrdy
import pclib.ifcs.mem_msgs as mem_msgs

class TestMemory( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  def __init__( s, memreq_params, memresp_params, nports,
                max_mem_delay = 0, mem_nbytes=2**20 ):

    # Local constant - store the number of ports

    s.nports         = nports
    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params
    s.max_mem_delay  = max_mem_delay
    s.mem_nbytes     = mem_nbytes
    req_nbits        = memreq_params.nbits
    resp_nbits       = memresp_params.nbits

    # List of memory request port bundles

    s.reqs  = [ InValRdyBundle( req_nbits )   for _ in range( nports ) ]

    # List of memory response msg, val, rdy ports

    s.resps = [ OutValRdyBundle( resp_nbits ) for _ in range( nports ) ]

    # delay responses

    s.delay_resps = [ TestRandomDelay( s.memresp_params.nbits, s.max_mem_delay )
                      for x in range( s.nports ) ]

    # simple test memory with no delays

    s.mem = TestSimpleMemory( s.memreq_params, s.memresp_params,
                                 s.nports, s.mem_nbytes )
    # Connect

    for i in range( s.nports ):

      # Connect memory inputs

      s.connect( s.reqs[i],  s.mem.reqs[i] )

      # Connect memory outputs to random delays

      s.connect( s.mem.resps[i], s.delay_resps[i].in_ )
      #s.connect( s.mem.resps[i], s.resps[i] )

      # Connect random delays to memory outputs

      s.connect( s.delay_resps[i].out, s.resps[i] )


  #-----------------------------------------------------------------------
  # load memory function
  #-----------------------------------------------------------------------
  # load memory function accepts a section address and a list of bytes to
  # load the memory data structure.
  # section_len, section_addr, section_data encapsulated in a helper
  # function?
  def load_memory( s, section_list ):
    s.mem.load_memory( section_list )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------
  def line_trace( s ):

    memreq_str   = ''
    memresp_str  = ''
    memtrace_str = ''

    for i in range( s.nports ):
      memreq_str  = \
        valrdy.valrdy_to_str(
          #  str(s.mem.reqs[i].msg.value.uint()) + s.mem.memreq[i].line_trace(),
          s.mem.memreq[i].line_trace(),
          s.reqs[i].val, s.reqs[i].rdy )

      memresp_str = \
        valrdy.valrdy_to_str(
          #str(s.resps[i].msg.value) + s.mem.memresp[i].line_trace(),
          s.resps[i].msg,
          s.resps[i].val, s.resps[i].rdy )

      memtrace_str += "|{} () {}" \
        .format( memreq_str, memresp_str )

    return memtrace_str
