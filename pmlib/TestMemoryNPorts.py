#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports and includes random
# delays.

from pymtl import *
import pmlib
import mem_msgs

from TestSimpleMemoryNPorts import TestSimpleMemoryNPorts
from TestRandomDelay        import TestRandomDelay

class TestMemoryNPorts (Model):

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

    # delay requests

    self.delay_reqs  = [ TestRandomDelay( memreq_params.nbits,
                                          max_mem_delay )
                         for x in xrange( nports ) ]

    # delay responses

    self.delay_resps = [ TestRandomDelay( memresp_params.nbits,
                                          max_mem_delay )
                         for x in xrange( nports ) ]

    # simple test memory with no delays

    self.mem = TestSimpleMemoryNPorts( memreq_params, memresp_params,
                                       nports, mem_nbytes )

    # Connect

    for i in xrange( nports ):

      # Connect input requests to random delays

      connect( self.memreq_msg[i],          self.delay_reqs[i].in_msg )
      connect( self.memreq_val[i],          self.delay_reqs[i].in_val )
      connect( self.memreq_rdy[i],          self.delay_reqs[i].in_rdy )

      # Connect random delays to memory inputs

      connect( self.delay_reqs[i].out_msg,  self.mem.memreq_msg[i] )
      connect( self.delay_reqs[i].out_val,  self.mem.memreq_val[i] )
      connect( self.delay_reqs[i].out_rdy,  self.mem.memreq_rdy[i] )

      # Connect memory outputs to random delays

      connect( self.mem.memresp_msg[i],     self.delay_resps[i].in_msg )
      connect( self.mem.memresp_val[i],     self.delay_resps[i].in_val )
      connect( self.mem.memresp_rdy[i],     self.delay_resps[i].in_rdy )

      # Connect random delays to memory outputs

      connect( self.delay_resps[i].out_msg, self.memresp_msg[i] )
      connect( self.delay_resps[i].out_val, self.memresp_val[i] )
      connect( self.delay_resps[i].out_rdy, self.memresp_rdy[i] )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):
    return self.mem.line_trace()
