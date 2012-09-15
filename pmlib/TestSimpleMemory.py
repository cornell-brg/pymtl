#=========================================================================
# TestMemory
#=========================================================================

from pymtl import *
import pmlib
import mem_msgs

class TestSimpleMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, memreq_params, memresp_params, mem_nbytes=2**20 ):

    self.memreq_msg  = InPort  ( memreq_params.nbits )
    self.memreq_val  = InPort  ( 1 )
    self.memreq_rdy  = OutPort ( 1 )

    self.memresp_msg = OutPort ( memresp_params.nbits )
    self.memresp_val = OutPort ( 1 )
    self.memresp_rdy = InPort  ( 1 )

    # Memory message parameters

    self.memreq_params  = memreq_params
    self.memresp_params = memresp_params

    # Checks

    assert self.memreq_params.data_nbits  % 8 == 0
    assert self.memresp_params.data_nbits % 8 == 0

    # Unpack/pack models

    self.memreq = mem_msgs.MemReqFromBits( memreq_params )
    connect( self.memreq_msg, self.memreq.bits )

    self.memresp = mem_msgs.MemRespToBits( memresp_params )
    connect( self.memresp_msg, self.memresp.bits )

    # Buffer to hold memory request message

    self.memreq_type = 0
    self.memreq_addr = 0
    self.memreq_len  = 0
    self.memreq_data = 0
    self.memreq_full = False

    # Actual memory

    self.mem = bytearray( mem_nbytes )

    # Connect ready signal to input to ensure pipeline behavior

    connect( self.memreq_rdy, self.memresp_rdy )

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # At the end of the cycle, we AND together the val/rdy bits to
    # determine if the request/memresp message transactions occured.

    memreq_go  = self.memreq_val.value  and self.memreq_rdy.value
    memresp_go = self.memresp_val.value and self.memresp_rdy.value

    # If the memresp transaction occured, then clear the buffer full bit.
    # Note that we do this _first_ before we process the request
    # transaction so we can essentially pipeline this control logic.

    if memresp_go:
      self.memreq_full = False

    # If the request transaction occured, then write the request message
    # into our internal buffer and update the buffer full bit

    if memreq_go:
      self.memreq_type = self.memreq.type_.value.uint
      self.memreq_addr = self.memreq.addr.value.uint
      self.memreq_len  = self.memreq.len_.value.uint
      self.memreq_data = self.memreq.data.value[:]
      self.memreq_full = True

    # When len is zero, then we use all of the data

    nbytes = self.memreq_len
    if self.memreq_len == 0:
      nbytes = self.memreq_params.data_nbits/8

    # Handle a read request

    if self.memreq_type == self.memreq_params.type_read:

      # Copy the bytes from the bytearray into read data bits

      read_data = Bits( self.memreq_params.data_nbits )
      for i in xrange( nbytes ):
        read_data[i*8:i*8+8] = self.mem[ self.memreq_addr + i ]

      # Create the response message

      self.memresp.type_.next = self.memresp_params.type_read
      self.memresp.len_.next  = self.memreq_len
      self.memresp.data.next  = read_data

    # Handle a write request

    elif self.memreq_type == self.memreq_params.type_write:

      # Copy write data bits into bytearray

      write_data = self.memreq_data
      for i in xrange( nbytes ):
        self.mem[ self.memreq_addr + i ] = write_data[i*8:i*8+8].uint

      # Create the response message

      self.memresp.type_.next = self.memresp_params.type_write
      self.memresp.len_.next  = 0
      self.memresp.data.next  = 0

    # For some reason this is causing an assert in PyMTL?
    #
    # else:
    #   assert True, "Unrecognized request message type! {}" \
    #     .format( self.memreq_type )

    # The memresp message if valid if the buffer is full

    self.memresp_val.next = self.memreq_full

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    memreq_str = \
      pmlib.valrdy.valrdy_to_str( self.memreq.line_trace(),
        self.memreq_val.value, self.memreq_rdy.value )

    memresp_str = \
      pmlib.valrdy.valrdy_to_str( self.memresp.line_trace(),
        self.memresp_val.value, self.memresp_rdy.value )

    return "{} () {}".format( memreq_str, memresp_str )

