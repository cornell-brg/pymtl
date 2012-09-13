#=========================================================================
# TestSimpleMemory
#=========================================================================
# This class implements a parameterized magic Test Memory Model.

from pymtl import *
from MemMsg import *

def concat_bytes( byte_list ):
  value = 0
  for i in range( len( byte_list ) ):
    value = value | ( ( byte_list[i] ) << i*8 )
  return value

class TestSimpleMemory (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, nports ):

    # memory size of 1MB
    s.mem = bytearray( 2**20 )

    s.memreq     = [ InPort  ( NREQBITS ) for x in range(nports) ]
    s.memreq_val = [ InPort  ( 1        ) for x in range(nports) ]
    s.memreq_rdy = [ OutPort ( 1        ) for x in range(nports) ]

    s.memresp     = [ OutPort  ( NRESPBITS ) for x in range(nports) ]
    s.memresp_val = [ OutPort  ( 1         ) for x in range(nports) ]
    s.memresp_rdy = [ InPort   ( 1         ) for x in range(nports) ]

    s.nports    = nports

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  @combinational
  def comb( s ):
    for i in range( s.nports ):

      if s.reset.value:
        s.memreq_rdy[i].value = 0
        s.memresp_val[i].value = 0
      s.memreq_rdy[i].value  = s.memresp_rdy[i].value
      if s.memresp_rdy[i].value and s.memreq_val[i].value:
        s.memresp_val[i].value = 1

  @posedge_clk
  def tick( s ):
    for i in range( s.nports ):

      if s.memresp_rdy[i].value and s.memreq_val[i].value:

        msg_len = s.memreq[i].value[REQ_LEN].uint
        if msg_len == 0:
          msg_len = MAX_DATA_BYTES
        write_data = []

        memresp_msg = Bits( NRESPBITS )
        memresp_msg[RESP_TYPE] = s.memreq[i].value[REQ_TYPE].uint
        memresp_msg[RESP_LEN]  = s.memreq[i].value[REQ_LEN].uint

        if s.memreq[i].value[REQ_TYPE]:

          for pos in range( msg_len ):
            write_data.append( s.memreq[i].value[(pos*8):((pos*8) + 8)].uint )

          write_addr = slice( s.memreq[i].value[REQ_ADDR].uint,
                        s.memreq[i].value[REQ_ADDR].uint + msg_len )

          s.mem[write_addr] = write_data

          memresp_msg[RESP_DATA] = 0
          s.memresp[i].value = memresp_msg

        else:

          read_addr = slice( s.memreq[i].value[REQ_ADDR].uint,
                        s.memreq[i].value[REQ_ADDR].uint + msg_len )

          memresp_msg[RESP_DATA] = concat_bytes(s.mem[read_addr])

          s.memresp[i].value = memresp_msg
