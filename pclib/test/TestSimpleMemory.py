#=========================================================================
# TestMemory with Multiple Ports
#=========================================================================
# This model implements a behavioral Test Memory which is parameterized
# based on the number of memory request/response ports.

from __future__ import print_function

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

import pclib.ifcs.valrdy   as valrdy
import pclib.ifcs.mem_msgs as mem_msgs

class TestSimpleMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, memreq_params, memresp_params, nports,
                mem_nbytes=2**20 ):

    # Local constant - store the number of ports

    req_nbits  = memreq_params.nbits
    resp_nbits = memresp_params.nbits

    # List of memory request ports

    s.reqs  = [ InValRdyBundle( req_nbits )   for _ in range( nports ) ]

    # List of memory response ports

    s.resps = [ OutValRdyBundle( resp_nbits ) for _ in range( nports ) ]

    # Memory message parameters

    s.memreq_params  = memreq_params
    s.memresp_params = memresp_params

    # Checks

    assert s.memreq_params.data_nbits  % 8 == 0
    assert s.memresp_params.data_nbits % 8 == 0

    # List of Unpack models

    s.memreq = [ mem_msgs.MemReqFromBits( memreq_params ) for _ in
                    range( nports ) ]

    # List of Pack models

    s.memresp = [ mem_msgs.MemRespToBits( memresp_params ) for _ in
                     range( nports ) ]

    s.mem_nbytes = mem_nbytes

    #---------------------------------------------------------------------
    # Connectivity and Logic
    #---------------------------------------------------------------------

    # Buffers to hold memory request messages

    s.memreq_type = [ Bits( 1) for _ in range( nports ) ]
    s.memreq_addr = [ Bits(32) for _ in range( nports ) ]
    s.memreq_len  = [ Bits( 2) for _ in range( nports ) ]
    s.memreq_data = [ Bits(32) for _ in range( nports ) ]

    s.memreq_full = [ Wire(1) for _ in range( nports ) ]

    # Actual memory
    s.mem = bytearray( s.mem_nbytes )

    # Connect memreq_msg port list to Unpack port list
    for i in range( nports ):
      s.connect( s.reqs[i].msg, s.memreq[i].bits )


    # Connect memresp_msg port list to Pack port list
    for i in range( nports ):
      s.connect( s.resps[i].msg, s.memresp[i].bits )

    #-----------------------------------------------------------------------
    # Tick
    #-----------------------------------------------------------------------

    @s.posedge_clk
    def tick():

      # Iterate over the port list

      for i in range( nports ):

        # At the end of the cycle, we AND together the val/rdy bits to
        # determine if the request/memresp message transactions occured.

        s.memreq_go  = s.reqs[i].val  and s.reqs[i].rdy
        s.memresp_go = s.resps[i].val and s.resps[i].rdy

        # If the memresp transaction occured, then clear the buffer full bit.
        # Note that we do this _first_ before we process the request
        # transaction so we can essentially pipeline this control logic.

        if s.memresp_go:
          s.memreq_full[i].next = 0

        # If the request transaction occured, then write the request message
        # into our internal buffer and update the buffer full bit

        if s.memreq_go:

          s.memreq_full[i].next = 1

          s.memreq_type[i] = s.memreq[i].type_
          s.memreq_addr[i] = s.memreq[i].addr
          s.memreq_len[i]  = s.memreq[i].len_
          s.memreq_data[i] = s.memreq[i].data[:]

          # When len is zero, then we use all of the data

          nbytes = s.memreq_len[i]
          if s.memreq_len[i] == 0:
            nbytes = s.memreq_params.data_nbits/8

          # Handle a read request

          if s.memreq_type[i] == s.memreq_params.type_read:

            # Copy the bytes from the bytearray into read data bits

            read_data = Bits( s.memreq_params.data_nbits )
            for j in range( nbytes ):
              read_data[j*8:j*8+8] = s.mem[ s.memreq_addr[i] + j ]

            # Create the response message

            s.memresp[i].type_.next = s.memresp_params.type_read
            s.memresp[i].len_ .next  = s.memreq_len[i]
            s.memresp[i].data .next  = read_data

          # Handle a write request

          elif s.memreq_type[i] == s.memreq_params.type_write:

            # Copy write data bits into bytearray

            write_data = s.memreq_data[i]
            for j in range( nbytes ):
              s.mem[ s.memreq_addr[i] + j ] = write_data[j*8:j*8+8].uint()

            # Create the response message

            s.memresp[i].type_.next = s.memresp_params.type_write
            s.memresp[i].len_ .next  = 0
            s.memresp[i].data .next  = 0

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

      for i in range( nports ):

        s.reqs[i].rdy.value  = ( not s.memreq_full[i] or s.resps[i].rdy )
        s.resps[i].val.value = s.memreq_full[i]

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    memtrace_str = ''

    for req, resp in zip( s.reqs, s.resps ):
      memtrace_str += "|{} () {}".format( req, resp )

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
