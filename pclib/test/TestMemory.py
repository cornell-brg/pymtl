#=======================================================================
# TestMemory
#=======================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test import TestRandomDelay

from TestSimpleMemory import TestSimpleMemory

import pclib.ifcs.valrdy   as valrdy
import pclib.ifcs.mem_msgs as mem_msgs

#-----------------------------------------------------------------------
# TestMemory
#-----------------------------------------------------------------------
class TestMemory( Model ):

  def __init__( s, memreq_params, memresp_params, nports,
                   max_mem_delay = 0, mem_nbytes=2**20 ):

    req_dtype  = memreq_params.nbits
    resp_dtype = memresp_params.nbits

    # List of memory request port bundles

    s.reqs  = [ InValRdyBundle( req_dtype )   for _ in range( nports ) ]

    # List of memory response msg, val, rdy ports

    s.resps = [ OutValRdyBundle( resp_dtype ) for _ in range( nports ) ]

    # delay responses

    s.delay_resps = [ TestRandomDelay( resp_dtype, max_mem_delay )
                      for x in range( nports ) ]

    # simple test memory with no delays

    s.mem = TestSimpleMemory(memreq_params, memresp_params, nports, mem_nbytes)

    # Connect

    for i in range( nports ):

      # Connect memory inputs

      s.connect( s.reqs[i],  s.mem.reqs[i] )

      # Connect memory outputs to random delays

      s.connect( s.mem.resps[i], s.delay_resps[i].in_ )

      # Connect random delays to memory outputs

      s.connect( s.delay_resps[i].out, s.resps[i] )

    # Config constants

    s.nports = nports

  #---------------------------------------------------------------------
  # load_memory
  #---------------------------------------------------------------------
  def load_memory( s, section_list ):
    '''Accepts a section address and a list of bytes to load the memory.

    section_len, section_addr, section_data encapsulated in a helper
    function?
    '''
    s.mem.load_memory( section_list )

  #---------------------------------------------------------------------
  # line_tracing
  #---------------------------------------------------------------------
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
