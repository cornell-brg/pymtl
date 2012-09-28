#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports and includes random
# delays for responses.

from pymtl import *
import pmlib
import mem_msgs

from TestSimpleMemory import TestSimpleMemory
from TestRandomDelay  import TestRandomDelay

class TestMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, memreq_params, memresp_params, nports,
                max_mem_delay = 0, mem_nbytes=2**20 ):

    # Local constant - store the number of ports

    self.nports = nports

    # List of memory request msg, val, rdy ports

    self.memreq_msg  = [ InPort  ( memreq_params.nbits ) for x in
                         xrange( nports ) ]
    self.memreq_val  = [ InPort  ( 1 ) for x in xrange( nports ) ]
    self.memreq_rdy  = [ OutPort ( 1 ) for x in xrange( nports ) ]

    # List of memory response msg, val, rdy ports

    self.memresp_msg = [ OutPort ( memresp_params.nbits ) for x in
                         xrange( nports ) ]
    self.memresp_val = [ OutPort ( 1 ) for x in xrange( nports ) ]
    self.memresp_rdy = [ InPort  ( 1 ) for x in xrange( nports ) ]

    # delay responses

    self.delay_resps = [ TestRandomDelay( memresp_params.nbits,
                                          max_mem_delay )
                         for x in xrange( nports ) ]

    # simple test memory with no delays

    self.mem = TestSimpleMemory( memreq_params, memresp_params,
                                 nports, mem_nbytes )
    # List of Unpack models

    self.memreq = [ mem_msgs.MemReqFromBits( memreq_params ) for x in
                    xrange( nports ) ]

    # Connect memreq_msg port list to Unpack port list

    for i in xrange( nports ):
      connect( self.memreq_msg[i], self.memreq[i].bits )

    # List of Pack models

    self.memresp = [ mem_msgs.MemRespToBits( memresp_params ) for x in
                     xrange( nports ) ]

    # Connect memresp_msg port list to Pack port list

    for i in xrange( nports ):
      connect( self.delay_resps[i].out_msg, self.memresp[i].bits )

    # Connect

    for i in xrange( nports ):

      # Connect memory inputs

      connect( self.memreq_msg[i],  self.mem.memreq_msg[i] )
      connect( self.memreq_val[i],  self.mem.memreq_val[i] )
      connect( self.memreq_rdy[i],  self.mem.memreq_rdy[i] )

      # Connect memory outputs to random delays

      connect( self.mem.memresp_msg[i],     self.delay_resps[i].in_msg )
      connect( self.mem.memresp_val[i],     self.delay_resps[i].in_val )
      connect( self.mem.memresp_rdy[i],     self.delay_resps[i].in_rdy )

      # Connect random delays to memory outputs

      connect( self.delay_resps[i].out_msg, self.memresp_msg[i] )
      connect( self.delay_resps[i].out_val, self.memresp_val[i] )
      connect( self.delay_resps[i].out_rdy, self.memresp_rdy[i] )

  #-----------------------------------------------------------------------
  # load memory function
  #-----------------------------------------------------------------------
  # load memory function accepts a section address and a list of bytes to
  # load the memory data structure.
  # section_len, section_addr, section_data encapsulated in a helper
  # function?

  def load_memory( self, section_list ):

    self.mem.load_memory( section_list )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    memreq_str   = ''
    memresp_str  = ''
    memtrace_str = ''

    for i in xrange( self.nports ):
      memreq_str  = \
        pmlib.valrdy.valrdy_to_str( self.memreq[i].line_trace(),
          self.memreq_val[i].value, self.memreq_rdy[i].value )

      memresp_str = \
        pmlib.valrdy.valrdy_to_str( self.memresp[i].line_trace(),
          self.memresp_val[i].value, self.memresp_rdy[i].value )

      memtrace_str += "|{} () {}" \
        .format( memreq_str, memresp_str )

    return memtrace_str
