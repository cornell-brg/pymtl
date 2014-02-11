#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports.

from new_pymtl import *
from new_pmlib.ValRdyBundle import InValRdyBundle, OutValRdyBundle
import new_pmlib
import mem_msgs

class TestSimpleMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params, nports,
                mem_nbytes=2**20 ):

    # Local constant - store the number of ports

    s.nports = nports

    # List of memory request ports

    s.reqs = [ InValRdyBundle( memreq_params.nbits ) for x in
                      xrange( nports ) ]

    # List of memory response ports

    s.resps = [ OutValRdyBundle( memresp_params.nbits ) for x in
                      xrange( nports ) ]

    # Memory message parameters

    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

    # Checks

    assert s.memreq_params.data_nbits  % 8 == 0
    assert s.memresp_params.data_nbits % 8 == 0

    # List of Unpack models

    s.memreq = [ mem_msgs.MemReqFromBits( memreq_params ) for x in
                    xrange( nports ) ]

    # List of Pack models

    s.memresp = [ mem_msgs.MemRespToBits( memresp_params ) for x in
                     xrange( nports ) ]

    s.mem_nbytes = mem_nbytes
  #-----------------------------------------------------------------------
  # Connectivity and Logic
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):
    # Buffers to hold memory request messages

    #s.memreq_type = [ 0 for x in xrange( s.nports ) ]
    #s.memreq_addr = [ 0 for x in xrange( s.nports ) ]
    #s.memreq_len  = [ 0 for x in xrange( s.nports ) ]
    #s.memreq_data = [ 0 for x in xrange( s.nports ) ]
    s.memreq_type = [ Wire(1) for x in xrange( s.nports ) ]
    s.memreq_addr = [ Wire(32) for x in xrange( s.nports ) ]
    s.memreq_len  = [ Wire(2) for x in xrange( s.nports ) ]
    s.memreq_data = [ Wire(32) for x in xrange( s.nports ) ]
    #s.memreq_full = [ False for x in xrange( s.nports ) ]
    s.memreq_full = [ Wire(1) for x in xrange( s.nports ) ]

    # Input Output Transaction Signals

    #s.memreq_go  = [0]*s.nports
    #s.memresp_go = [0]*s.nports

    # Actual memory
    s.mem = bytearray( s.mem_nbytes )

    # Connect memreq_msg port list to Unpack port list
    for i in xrange( s.nports ):
      s.connect( s.reqs[i].msg, s.memreq[i].bits )


    # Connect memresp_msg port list to Pack port list
    for i in xrange( s.nports ):
      s.connect( s.resps[i].msg, s.memresp[i].bits )

    #-----------------------------------------------------------------------
    # Tick
    #-----------------------------------------------------------------------

    @s.posedge_clk
    def tick():

      # Iterate over the port list

      for i in xrange( s.nports ):

        # At the end of the cycle, we AND together the val/rdy bits to
        # determine if the request/memresp message transactions occured.

        s.memreq_go  = s.reqs[i].val  and s.reqs[i].rdy
        s.memresp_go = s.resps[i].val and s.resps[i].rdy

        # If the memresp transaction occured, then clear the buffer full bit.
        # Note that we do this _first_ before we process the request
        # transaction so we can essentially pipeline this control logic.

        #if s.memresp_go[i]:
        if s.memresp_go:
          #s.memreq_full[i] = False
          s.memreq_full[i].next = 0

        # If the request transaction occured, then write the request message
        # into our internal buffer and update the buffer full bit

        if s.memreq_go:
          s.memreq_type[i] = s.memreq[i].type_.value#.uint()
          s.memreq_addr[i] = s.memreq[i].addr.value#.uint()
          s.memreq_len[i]  = s.memreq[i].len_.value#.uint()
          s.memreq_data[i] = s.memreq[i].data.value[:]
          #s.memreq_full[i] = True
          s.memreq_full[i].next = 1

          # When len is zero, then we use all of the data

          nbytes = s.memreq_len[i]
          if s.memreq_len[i] == 0:
            nbytes = s.memreq_params.data_nbits/8

          # Handle a read request

          if s.memreq_type[i] == s.memreq_params.type_read:

            # Copy the bytes from the bytearray into read data bits

            read_data = Bits( s.memreq_params.data_nbits )
            for j in xrange( nbytes ):
              read_data[j*8:j*8+8] = s.mem[ s.memreq_addr[i] + j ]

            # Create the response message

            s.memresp[i].type_.next = s.memresp_params.type_read
            s.memresp[i].len_.next  = s.memreq_len[i]
            s.memresp[i].data.next  = read_data

          # Handle a write request

          elif s.memreq_type[i] == s.memreq_params.type_write:

            # Copy write data bits into bytearray

            write_data = s.memreq_data[i]
            for j in xrange( nbytes ):
              s.mem[ s.memreq_addr[i] + j ] = write_data[j*8:j*8+8].uint()

            # Create the response message

            s.memresp[i].type_.next = s.memresp_params.type_write
            s.memresp[i].len_.next  = 0
            s.memresp[i].data.next  = 0

          # For some reason this is causing an assert in PyMTL?
          #
          # else:
          #   assert True, "Unrecognized request message type! {}" \
          #     .format( s.memreq_type[i] )


    #-----------------------------------------------------------------------
    # Combinational Logic
    #-----------------------------------------------------------------------
    # We model the TestSimpleMemory to behave like a normal queue. Instead of
    # combinationally hooking up the memresp_rdy to memreq_rdy, we see if
    # there is anything present in the buffer or not, to calculate request
    # ready signal.

    @s.combinational
    def comb():

      # Iterate over the port list

      for i in xrange( s.nports ):

        s.reqs[i].rdy.value  = ( not s.memreq_full[i] or s.resps[i].rdy )
        s.resps[i].val.value = s.memreq_full[i]

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    memreq_str   = ''
    memresp_str  = ''
    memtrace_str = ''

    for i in xrange( s.nports ):
      memreq_str  = \
        new_pmlib.valrdy.valrdy_to_str( s.memreq[i].line_trace(),
          s.reqs[i].val, s.reqs[i].rdy )

      memresp_str = \
        new_pmlib.valrdy.valrdy_to_str( s.memresp[i].line_trace(),
          s.resps[i].val, s.resps[i].rdy )

      memtrace_str += "|{} () {}" \
        .format( memreq_str, memresp_str )

    return memtrace_str

  #-----------------------------------------------------------------------
  # load memory function
  #-----------------------------------------------------------------------
  # load memory function accepts a section address and a list of bytes to
  # load the memory data structure.
  # section_len, section_addr, section_data encapsulated in a helper
  # function?

  def load_memory( s, section_list ):

    section_addr = section_list[0]
    section_data = section_list[1]
    section_len  = len( section_data )

    #print(section_addr)
    #print(section_data)
    #print(section_len)

    assert len(s.mem) > (section_addr + section_len)
    s.mem[ section_addr : section_addr + section_len ] = section_data
