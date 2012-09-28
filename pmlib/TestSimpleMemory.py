#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports.

from pymtl import *
import pmlib
import mem_msgs

class TestSimpleMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, memreq_params, memresp_params, nports,
                mem_nbytes=2**20 ):

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


    # Memory message parameters

    self.memreq_params  = memreq_params
    self.memresp_params = memresp_params

    # Checks

    assert self.memreq_params.data_nbits  % 8 == 0
    assert self.memresp_params.data_nbits % 8 == 0

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
      connect( self.memresp_msg[i], self.memresp[i].bits )

    # Buffers to hold memory request messages

    self.memreq_type = [ 0 for x in xrange( nports ) ]
    self.memreq_addr = [ 0 for x in xrange( nports ) ]
    self.memreq_len  = [ 0 for x in xrange( nports ) ]
    self.memreq_data = [ 0 for x in xrange( nports ) ]
    self.memreq_full = [ False for x in xrange( nports ) ]

    # Input Output Transaction Signals

    self.memreq_go  = [0]*self.nports
    self.memresp_go = [0]*self.nports

    # Actual memory

    self.mem = bytearray( mem_nbytes )

    # Connect ready signals to inputs to ensure pipeline behavior

    #for i in xrange( nports ):
    #  connect( self.memreq_rdy[i], self.memresp_rdy[i] )

  #-----------------------------------------------------------------------
  # load memory function
  #-----------------------------------------------------------------------
  # load memory function accepts a section address and a list of bytes to
  # load the memory data structure.
  # section_len, section_addr, section_data encapsulated in a helper
  # function?

  def load_memory( self, section_list ):

    section_addr = section_list[0]
    section_data = section_list[1]
    section_len  = len( section_data )

    assert len(self.mem) > (section_addr + section_len)
    self.mem[ section_addr : section_addr + section_len ] = section_data

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @posedge_clk
  def tick( self ):

    # Iterate over the port list

    for i in xrange( self.nports ):

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the request/memresp message transactions occured.

      self.memreq_go[i]  = self.memreq_val[i].value  and self.memreq_rdy[i].value
      self.memresp_go[i] = self.memresp_val[i].value and self.memresp_rdy[i].value

      # If the memresp transaction occured, then clear the buffer full bit.
      # Note that we do this _first_ before we process the request
      # transaction so we can essentially pipeline this control logic.

      if self.memresp_go[i]:
        self.memreq_full[i] = False

      # If the request transaction occured, then write the request message
      # into our internal buffer and update the buffer full bit

      if self.memreq_go[i]:
        self.memreq_type[i] = self.memreq[i].type_.value.uint
        self.memreq_addr[i] = self.memreq[i].addr.value.uint
        self.memreq_len[i]  = self.memreq[i].len_.value.uint
        self.memreq_data[i] = self.memreq[i].data.value[:]
        self.memreq_full[i] = True

      # When len is zero, then we use all of the data

      nbytes = self.memreq_len[i]
      if self.memreq_len[i] == 0:
        nbytes = self.memreq_params.data_nbits/8

      # Handle a read request

      if self.memreq_type[i] == self.memreq_params.type_read:

        # Copy the bytes from the bytearray into read data bits

        read_data = Bits( self.memreq_params.data_nbits )
        for j in xrange( nbytes ):
          read_data[j*8:j*8+8] = self.mem[ self.memreq_addr[i] + j ]

        # Create the response message

        self.memresp[i].type_.next = self.memresp_params.type_read
        self.memresp[i].len_.next  = self.memreq_len[i]
        self.memresp[i].data.next  = read_data

      # Handle a write request

      elif self.memreq_type[i] == self.memreq_params.type_write:

        # Copy write data bits into bytearray

        write_data = self.memreq_data[i]
        for j in xrange( nbytes ):
          self.mem[ self.memreq_addr[i] + j ] = write_data[j*8:j*8+8].uint

        # Create the response message

        self.memresp[i].type_.next = self.memresp_params.type_write
        self.memresp[i].len_.next  = 0
        self.memresp[i].data.next  = 0

      # For some reason this is causing an assert in PyMTL?
      #
      # else:
      #   assert True, "Unrecognized request message type! {}" \
      #     .format( self.memreq_type[i] )

      # The memresp message if valid if the buffer is full

      self.memresp_val[i].next = self.memreq_full[i]

  #-----------------------------------------------------------------------
  # Combinational Logic
  #-----------------------------------------------------------------------
  # We model the TestSimpleMemory to behave like a normal queue. Instead of
  # combinationally hooking up the memresp_rdy to memreq_rdy, we see if
  # there is anything present in the buffer or not, to calculate request
  # ready signal.

  @combinational
  def comb( self ):

    # Iterate over the port list

    for i in xrange( self.nports ):

      self.memreq_rdy[i].value = ( not self.memreq_full[i] or
                                       self.memresp_rdy[i].value )

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

