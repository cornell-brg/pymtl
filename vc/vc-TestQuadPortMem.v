//========================================================================
// Verilog Components: Test Memory
//========================================================================
// This is dual-ported test memory that can handles almost arbitrary
// memory request messages and returns memory response messages.

`ifndef VC_TEST_QUAD_PORT_MEM_V
`define VC_TEST_QUAD_PORT_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Assert.v"
`include "vc-Queues.v"

//------------------------------------------------------------------------
// Quad port test memory
//------------------------------------------------------------------------

module vc_TestQuadPortMem
#(
  parameter p_mem_sz  = 1024, // size of physical memory in bytes
  parameter p_addr_sz = 8,    // size of mem message address in bits
  parameter p_data_sz = 32,   // size of mem message data in bits

  // Local constants not meant to be set from outside the module
  parameter c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz)
)(
  input clk,
  input reset,

  // Memory request port 0 interface

  input                      memreq0_val,
  output                     memreq0_rdy,
  input  [c_req_msg_sz-1:0]  memreq0_msg,

  // Memory response port 0 interface

  output                     memresp0_val,
  input                      memresp0_rdy,
  output [c_resp_msg_sz-1:0] memresp0_msg,

  // Memory request port 1 interface

  input                      memreq1_val,
  output                     memreq1_rdy,
  input  [c_req_msg_sz-1:0]  memreq1_msg,

  // Memory response port 1 interface

  output                     memresp1_val,
  input                      memresp1_rdy,
  output [c_resp_msg_sz-1:0] memresp1_msg,

  // Memory request port 2 interface

  input                      memreq2_val,
  output                     memreq2_rdy,
  input  [c_req_msg_sz-1:0]  memreq2_msg,

  // Memory response port 2 interface

  output                     memresp2_val,
  input                      memresp2_rdy,
  output [c_resp_msg_sz-1:0] memresp2_msg,

  // Memory request port 3 interface

  input                      memreq3_val,
  output                     memreq3_rdy,
  input  [c_req_msg_sz-1:0]  memreq3_msg,

  // Memory response port 3 interface

  output                     memresp3_val,
  input                      memresp3_rdy,
  output [c_resp_msg_sz-1:0] memresp3_msg
);

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  // Size of a physical address for the memory in bits

  localparam c_physical_addr_sz = $clog2(p_mem_sz);

  // Size of data entry in bytes

  localparam c_data_byte_sz = (p_data_sz/8);

  // Number of data entries in memory

  localparam c_num_blocks = p_mem_sz/c_data_byte_sz;

  // Size of block address in bits

  localparam c_physical_block_addr_sz = $clog2(c_num_blocks);

  // Size of block offset in bits

  localparam c_block_offset_sz = $clog2(c_data_byte_sz);

  // Shorthand for the message types

  localparam c_read  = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_write = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TYPE_AMOOR;

  // Shorthand for the message field sizes

  localparam c_req_msg_type_sz  = `VC_MEM_REQ_MSG_TYPE_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_addr_sz  = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_data_sz);

  localparam c_resp_msg_type_sz = `VC_MEM_RESP_MSG_TYPE_SZ(p_data_sz);
  localparam c_resp_msg_len_sz  = `VC_MEM_RESP_MSG_LEN_SZ(p_data_sz);
  localparam c_resp_msg_data_sz = `VC_MEM_RESP_MSG_DATA_SZ(p_data_sz);

  //----------------------------------------------------------------------
  // Unpack the request message
  //----------------------------------------------------------------------

  // Port 0

  wire [c_req_msg_type_sz-1:0] memreq0_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq0_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq0_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq0_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq0_msg_from_bits
  (
    .bits (memreq0_msg),
    .type (memreq0_msg_type),
    .addr (memreq0_msg_addr),
    .len  (memreq0_msg_len),
    .data (memreq0_msg_data)
  );

  // Port 1

  wire [c_req_msg_type_sz-1:0] memreq1_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq1_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq1_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq1_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq1_msg_from_bits
  (
    .bits (memreq1_msg),
    .type (memreq1_msg_type),
    .addr (memreq1_msg_addr),
    .len  (memreq1_msg_len),
    .data (memreq1_msg_data)
  );

  // Port 2

  wire [c_req_msg_type_sz-1:0] memreq2_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq2_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq2_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq2_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq2_msg_from_bits
  (
    .bits (memreq2_msg),
    .type (memreq2_msg_type),
    .addr (memreq2_msg_addr),
    .len  (memreq2_msg_len),
    .data (memreq2_msg_data)
  );

  // Port 3

  wire [c_req_msg_type_sz-1:0] memreq3_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq3_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq3_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq3_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq3_msg_from_bits
  (
    .bits (memreq3_msg),
    .type (memreq3_msg_type),
    .addr (memreq3_msg_addr),
    .len  (memreq3_msg_len),
    .data (memreq3_msg_data)
  );

  //----------------------------------------------------------------------
  // Memory request buffers
  //----------------------------------------------------------------------

  reg                         memreq0_val_M;
  reg [c_req_msg_type_sz-1:0] memreq0_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq0_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq0_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq0_msg_data_M;

  reg                         memreq1_val_M;
  reg [c_req_msg_type_sz-1:0] memreq1_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq1_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq1_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq1_msg_data_M;

  reg                         memreq2_val_M;
  reg [c_req_msg_type_sz-1:0] memreq2_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq2_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq2_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq2_msg_data_M;

  reg                         memreq3_val_M;
  reg [c_req_msg_type_sz-1:0] memreq3_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq3_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq3_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq3_msg_data_M;

  always @( posedge clk ) begin

    // Ensure that the valid bit is reset appropriately

    if ( reset ) begin
      memreq0_val_M <= 1'b0;
      memreq1_val_M <= 1'b0;
      memreq2_val_M <= 1'b0;
      memreq3_val_M <= 1'b0;
    end else begin
      //if ( memresp0_rdy )
      if ( memreq0_rdy )
        memreq0_val_M <= memreq0_val;
      //if ( memresp1_rdy )
      if ( memreq1_rdy )
        memreq1_val_M <= memreq1_val;
      //if ( memresp2_rdy )
      if ( memreq2_rdy )
        memreq2_val_M <= memreq2_val;
      //if ( memresp3_rdy )
      if ( memreq3_rdy )
        memreq3_val_M <= memreq3_val;
    end

    // Stall the pipeline if the response interface is not ready

    //if ( memresp0_rdy ) begin
    if ( memreq0_rdy ) begin
      memreq0_msg_type_M <= memreq0_msg_type;
      memreq0_msg_addr_M <= memreq0_msg_addr;
      memreq0_msg_len_M  <= memreq0_msg_len;
      memreq0_msg_data_M <= memreq0_msg_data;
    end

    //if ( memresp1_rdy ) begin
    if ( memreq1_rdy ) begin
      memreq1_msg_type_M <= memreq1_msg_type;
      memreq1_msg_addr_M <= memreq1_msg_addr;
      memreq1_msg_len_M  <= memreq1_msg_len;
      memreq1_msg_data_M <= memreq1_msg_data;
    end

    //if ( memresp2_rdy ) begin
    if ( memreq2_rdy ) begin
      memreq2_msg_type_M <= memreq2_msg_type;
      memreq2_msg_addr_M <= memreq2_msg_addr;
      memreq2_msg_len_M  <= memreq2_msg_len;
      memreq2_msg_data_M <= memreq2_msg_data;
    end

    //if ( memresp3_rdy ) begin
    if ( memreq3_rdy ) begin
      memreq3_msg_type_M <= memreq3_msg_type;
      memreq3_msg_addr_M <= memreq3_msg_addr;
      memreq3_msg_len_M  <= memreq3_msg_len;
      memreq3_msg_data_M <= memreq3_msg_data;
    end

  end

  // Create a strict pipeline such that the whole pipelipe stalls if the
  // reponse interface is not ready. We do this by disabling the write of
  // the request buffer above if the response interface is not ready, and
  // we also directly wire the response ready signal to the request ready
  // signal.

  //assign memreq0_rdy = memresp0_rdy;
  //assign memreq1_rdy = memresp1_rdy;
  //assign memreq2_rdy = memresp2_rdy;
  //assign memreq3_rdy = memresp3_rdy;

  //----------------------------------------------------------------------
  // Actual memory array
  //----------------------------------------------------------------------

  reg [p_data_sz-1:0] m[c_num_blocks-1:0];

  //----------------------------------------------------------------------
  // Handle request and create response
  //----------------------------------------------------------------------

  // Handle case where length is zero which actually represents a full
  // width access.

  wire [c_req_msg_len_sz:0] memreq0_msg_len_modified_M
    = ( memreq0_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq0_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq1_msg_len_modified_M
    = ( memreq1_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq1_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq2_msg_len_modified_M
    = ( memreq2_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq2_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq3_msg_len_modified_M
    = ( memreq3_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq3_msg_len_M;

  // Caculate the physical byte address for the request. Notice that we
  // truncate the higher order bits that are beyond the size of the
  // physical memory.

  wire [c_physical_addr_sz-1:0] physical_byte_addr0_M
    = memreq0_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr1_M
    = memreq1_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr2_M
    = memreq2_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr3_M
    = memreq3_msg_addr_M[c_physical_addr_sz-1:0];

  // Read the data. We use a behavioral for loop to allow us to flexibly
  // handle arbitrary alignment and lengths. This is a combinational
  // always block so that we can immediately readout the results.
  // We always read out the appropriate block combinationally and shift
  // according to the number of bytes we want to read from the block
  // offset to obtain the read data output.

  wire [c_physical_block_addr_sz-1:0] physical_block_addr0_M
    = physical_byte_addr0_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr1_M
    = physical_byte_addr1_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr2_M
    = physical_byte_addr2_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr3_M
    = physical_byte_addr3_M/c_data_byte_sz;


  wire [c_block_offset_sz-1:0] block_offset0_M
    = physical_byte_addr0_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset1_M
    = physical_byte_addr1_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset2_M
    = physical_byte_addr2_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset3_M
    = physical_byte_addr3_M[c_block_offset_sz-1:0];


  wire [p_data_sz-1:0] read_block0_M
    = m[physical_block_addr0_M];

  wire [p_data_sz-1:0] read_block1_M
    = m[physical_block_addr1_M];

  wire [p_data_sz-1:0] read_block2_M
    = m[physical_block_addr2_M];

  wire [p_data_sz-1:0] read_block3_M
    = m[physical_block_addr3_M];


  wire [c_resp_msg_data_sz-1:0] read_data0_M
    = read_block0_M >> (block_offset0_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data1_M
    = read_block1_M >> (block_offset1_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data2_M
    = read_block2_M >> (block_offset2_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data3_M
    = read_block3_M >> (block_offset3_M*8);

//  reg [c_resp_msg_data_sz-1:0] read_data0_M;
//  reg [c_resp_msg_data_sz-1:0] read_data1_M;
//
//  integer rd0_i;
//  integer rd1_i;
//
//  always @(*) begin
//    for ( rd0_i = 0; rd0_i < memreq0_msg_len_modified_M; rd0_i = rd0_i + 1 ) begin
//      read_data0_M[ (rd0_i*8) +: 8 ] = read_block0_M[ (block_offset0_M*8) + (rd0_i*8) +: 8 ];
//    end
//    for ( rd1_i = 0; rd1_i < memreq1_msg_len_modified_M; rd1_i = rd1_i + 1 ) begin
//      read_data1_M[ (rd1_i*8) +: 8 ] = read_block1_M[ (block_offset1_M*8) + (rd1_i*8) +: 8 ];
//    end
//  end

  // Atomic operations. amo.add, amo.and, and amo.or return the read data
  // pre-modification, but writes the modified data back into memory on
  // the next clock edge. The data field in the memory message is used to
  // specify the data to modify the read data with.
  //
  // Sub-word atomic operations are supported but not used by the
  // ISA. The actual modification is at a block granularity (i.e. for a
  // 32-bit block, the entire 32-bit addition/and/or operation happens),
  // but if the specified length field is not 0, only the corresponding
  // number of bytes will be written back to memory. It might be
  // preferable to allow an amo.add to perform the addition at a sub-word
  // granularity (i.e. a length of 2 will only add the first 2 bytes of
  // the data field to the read data instead of the entire block length),
  // but this is currently not supported.

  // amo.add output

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_amoadd_M
    = read_data0_M + memreq0_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_amoadd_M
    = read_data1_M + memreq1_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_amoadd_M
    = read_data2_M + memreq2_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_amoadd_M
    = read_data3_M + memreq3_msg_data_M;

  // amo.and output

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_amoand_M
    = read_data0_M & memreq0_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_amoand_M
    = read_data1_M & memreq1_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_amoand_M
    = read_data2_M & memreq2_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_amoand_M
    = read_data3_M & memreq3_msg_data_M;

  // amo.or output

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_amoor_M
    = read_data0_M | memreq0_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_amoor_M
    = read_data1_M | memreq1_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_amoor_M
    = read_data2_M | memreq2_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_amoor_M
    = read_data3_M | memreq3_msg_data_M;

  // Modified write data mux

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_modified_M
    = ( memreq0_msg_type_M == c_read   ) ? memreq0_msg_data_M
    : ( memreq0_msg_type_M == c_write  ) ? memreq0_msg_data_M
    : ( memreq0_msg_type_M == c_amoadd ) ? memreq0_msg_data_amoadd_M
    : ( memreq0_msg_type_M == c_amoand ) ? memreq0_msg_data_amoand_M
    : ( memreq0_msg_type_M == c_amoor  ) ? memreq0_msg_data_amoor_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_modified_M
    = ( memreq1_msg_type_M == c_read   ) ? memreq1_msg_data_M
    : ( memreq1_msg_type_M == c_write  ) ? memreq1_msg_data_M
    : ( memreq1_msg_type_M == c_amoadd ) ? memreq1_msg_data_amoadd_M
    : ( memreq1_msg_type_M == c_amoand ) ? memreq1_msg_data_amoand_M
    : ( memreq1_msg_type_M == c_amoor  ) ? memreq1_msg_data_amoor_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_modified_M
    = ( memreq2_msg_type_M == c_read   ) ? memreq2_msg_data_M
    : ( memreq2_msg_type_M == c_write  ) ? memreq2_msg_data_M
    : ( memreq2_msg_type_M == c_amoadd ) ? memreq2_msg_data_amoadd_M
    : ( memreq2_msg_type_M == c_amoand ) ? memreq2_msg_data_amoand_M
    : ( memreq2_msg_type_M == c_amoor  ) ? memreq2_msg_data_amoor_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_modified_M
    = ( memreq3_msg_type_M == c_read   ) ? memreq3_msg_data_M
    : ( memreq3_msg_type_M == c_write  ) ? memreq3_msg_data_M
    : ( memreq3_msg_type_M == c_amoadd ) ? memreq3_msg_data_amoadd_M
    : ( memreq3_msg_type_M == c_amoand ) ? memreq3_msg_data_amoand_M
    : ( memreq3_msg_type_M == c_amoor  ) ? memreq3_msg_data_amoor_M
    :                                      {c_req_msg_data_sz{1'b0}};

  // Write the data if required. Again, we use a behavioral for loop to
  // allow us to flexibly handle arbitrary alignment and lengths. This is
  // a sequential always block so that the write happens on the next edge.

  // TODO: dmlockhart... replace memreq0_val_M with output of queue?

  wire write_en0_M = memreq0_val_M &&
                ( ( memreq0_msg_type_M == c_write  )
                ||( memreq0_msg_type_M == c_amoadd )
                ||( memreq0_msg_type_M == c_amoand )
                ||( memreq0_msg_type_M == c_amoor  ) );

  wire write_en1_M = memreq1_val_M &&
                ( ( memreq1_msg_type_M == c_write  )
                ||( memreq1_msg_type_M == c_amoadd )
                ||( memreq1_msg_type_M == c_amoand )
                ||( memreq1_msg_type_M == c_amoor  ) );

  wire write_en2_M = memreq2_val_M &&
                ( ( memreq2_msg_type_M == c_write  )
                ||( memreq2_msg_type_M == c_amoadd )
                ||( memreq2_msg_type_M == c_amoand )
                ||( memreq2_msg_type_M == c_amoor  ) );

  wire write_en3_M = memreq3_val_M &&
                ( ( memreq3_msg_type_M == c_write  )
                ||( memreq3_msg_type_M == c_amoadd )
                ||( memreq3_msg_type_M == c_amoand )
                ||( memreq3_msg_type_M == c_amoor  ) );

  integer wr0_i;
  integer wr1_i;
  integer wr2_i;
  integer wr3_i;

  always @( posedge clk ) begin
    if ( write_en0_M ) begin
      for ( wr0_i = 0; wr0_i < memreq0_msg_len_modified_M; wr0_i = wr0_i + 1 ) begin
        m[physical_block_addr0_M][ (block_offset0_M*8) + (wr0_i*8) +: 8 ] <= memreq0_msg_data_modified_M[ (wr0_i*8) +: 8 ];
      end
    end
    if ( write_en1_M ) begin
      for ( wr1_i = 0; wr1_i < memreq1_msg_len_modified_M; wr1_i = wr1_i + 1 ) begin
        m[physical_block_addr1_M][ (block_offset1_M*8) + (wr1_i*8) +: 8 ] <= memreq1_msg_data_modified_M[ (wr1_i*8) +: 8 ];
      end
    end
    if ( write_en2_M ) begin
      for ( wr2_i = 0; wr2_i < memreq2_msg_len_modified_M; wr2_i = wr2_i + 1 ) begin
        m[physical_block_addr2_M][ (block_offset2_M*8) + (wr2_i*8) +: 8 ] <= memreq2_msg_data_modified_M[ (wr2_i*8) +: 8 ];
      end
    end
    if ( write_en3_M ) begin
      for ( wr3_i = 0; wr3_i < memreq3_msg_len_modified_M; wr3_i = wr3_i + 1 ) begin
        m[physical_block_addr3_M][ (block_offset3_M*8) + (wr3_i*8) +: 8 ] <= memreq3_msg_data_modified_M[ (wr3_i*8) +: 8 ];
      end
    end
  end

  // Create response

  wire [c_resp_msg_type_sz-1:0] memresp0_msg_type_M = memreq0_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp0_msg_len_M  = memreq0_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp0_msg_data_M = read_data0_M;

  wire [c_resp_msg_type_sz-1:0] memresp1_msg_type_M = memreq1_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp1_msg_len_M  = memreq1_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp1_msg_data_M = read_data1_M;

  wire [c_resp_msg_type_sz-1:0] memresp2_msg_type_M = memreq2_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp2_msg_len_M  = memreq2_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp2_msg_data_M = read_data2_M;

  wire [c_resp_msg_type_sz-1:0] memresp3_msg_type_M = memreq3_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp3_msg_len_M  = memreq3_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp3_msg_data_M = read_data3_M;

  // Response is valid if the request in the request buffer is valid

  //assign memresp0_val = memreq0_val_M;
  //assign memresp1_val = memreq1_val_M;
  //assign memresp2_val = memreq2_val_M;
  //assign memresp3_val = memreq3_val_M;

  //----------------------------------------------------------------------
  // Bypass Queue on the Output
  //----------------------------------------------------------------------
  // This is necessary to prevent deadlock when hooked up directly
  // to the direct mapped cache!
 
  wire [c_resp_msg_sz-1:0] memresp0_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp1_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp2_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp3_queue_msg;
 
  // Uncomment these lines and comment out the queues if you want to
  // configure the memory to have no bypass queues (for testing).
  //assign memresp0_msg = memresp0_queue_msg;
  //assign memresp0_val = memreq0_val_M;
  //assign memreq0_rdy  = memresp0_rdy;
 
  //assign memresp1_msg = memresp1_queue_msg;
  //assign memresp1_val = memreq1_val_M;
  //assign memreq1_rdy  = memresp1_rdy;
 
  //assign memresp2_msg = memresp2_queue_msg;
  //assign memresp2_val = memreq2_val_M;
  //assign memreq2_rdy  = memresp2_rdy;
 
  //assign memresp3_msg = memresp3_queue_msg;
  //assign memresp3_val = memreq3_val_M;
  //assign memreq3_rdy  = memresp3_rdy;
 
  // 16 = number of queue entries, 4 = number of bits needed to
  // index 16 entries... make sure you change that field if
  // you change the number of queue entries! So dumb.
 
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,16,4) memresp0_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp0_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq0_val_M),      // Wire up to req_val output
    .enq_rdy  (memreq0_rdy),        // Wire up directly to req_rdy output
 
    // Wire up deq to the resp output ports
 
    .deq_bits (memresp0_msg),
    .deq_val  (memresp0_val),
    .deq_rdy  (memresp0_rdy)
  );
 
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,16,4) memresp1_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp1_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq1_val_M),      // Wire up to req_val output
    .enq_rdy  (memreq1_rdy),        // Wire up directly to req_rdy output
 
    // Wire up deq to the resp output ports
 
    .deq_bits (memresp1_msg),
    .deq_val  (memresp1_val),
    .deq_rdy  (memresp1_rdy)
  );
 
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,16,4) memresp2_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp2_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq2_val_M),     // Wire up to req_val output
    .enq_rdy  (memreq2_rdy),       // Wire up directly to req_rdy output
 
    // Wire up deq to the resp output ports
 
    .deq_bits (memresp2_msg),
    .deq_val  (memresp2_val),
    .deq_rdy  (memresp2_rdy)
  );
 
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,16,4) memresp3_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp3_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq3_val_M),      // Wire up to req_val output
    .enq_rdy  (memreq3_rdy),        // Wire up directly to req_rdy output
 
    // Wire up deq to the resp output ports
 
    .deq_bits (memresp3_msg),
    .deq_val  (memresp3_val),
    .deq_rdy  (memresp3_rdy)
  );

  //----------------------------------------------------------------------
  // Pack the response message
  //----------------------------------------------------------------------

  vc_MemRespMsgToBits#(p_data_sz) memresp0_msg_to_bits
  (
    .type (memresp0_msg_type_M),
    .len  (memresp0_msg_len_M),
    .data (memresp0_msg_data_M),
    //.bits (memresp0_msg)
    .bits (memresp0_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp1_msg_to_bits
  (
    .type (memresp1_msg_type_M),
    .len  (memresp1_msg_len_M),
    .data (memresp1_msg_data_M),
    //.bits (memresp1_msg)
    .bits (memresp1_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp2_msg_to_bits
  (
    .type (memresp2_msg_type_M),
    .len  (memresp2_msg_len_M),
    .data (memresp2_msg_data_M),
    //.bits (memresp2_msg)
    .bits (memresp2_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp3_msg_to_bits
  (
    .type (memresp3_msg_type_M),
    .len  (memresp3_msg_len_M),
    .data (memresp3_msg_data_M),
    //.bits (memresp3_msg)
    .bits (memresp3_queue_msg)
  );

  //----------------------------------------------------------------------
  // General assertions
  //----------------------------------------------------------------------

  // val/rdy signals should never be x's

  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq0_val,  "memreq0_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp0_rdy, "memresp0_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq1_val,  "memreq1_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp1_rdy, "memresp1_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq2_val,  "memreq2_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp2_rdy, "memresp2_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq3_val,  "memreq3_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp3_rdy, "memresp3_rdy" );

  // Failsafe counter, automatically terminate program if multiple
  // invalid requests are detected.

  wire memreq_x = ( memreq0_val === 1'bx )
               || ( memreq1_val === 1'bx )
               || ( memreq2_val === 1'bx )
               || ( memreq3_val === 1'bx );

  reg [1:0] counter;

  always @ ( posedge clk ) begin
    if ( reset ) begin
      counter <= 2'b0;
    end
    else if ( counter == 2'b11 ) begin
      $finish;
    end
    else if ( memreq_x ) begin
      counter <= counter + 1;
    end
  end

endmodule

`endif /* VC_TEST_QUAD_PORT_MEM_V */

