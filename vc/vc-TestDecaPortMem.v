//========================================================================
// Verilog Components: Test Memory
//========================================================================

`ifndef VC_TEST_DECA_PORT_MEM_V
`define VC_TEST_DECA_PORT_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Assert.v"
`include "vc-Queues.v"

`include "vc-Arbiters.v"

//------------------------------------------------------------------------
// Deca port test memory
//------------------------------------------------------------------------

module vc_TestDecaPortMem
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
  output [c_resp_msg_sz-1:0] memresp3_msg,

  // Memory request port 4 interface

  input                      memreq4_val,
  output                     memreq4_rdy,
  input  [c_req_msg_sz-1:0]  memreq4_msg,

  // Memory response port 4 interface

  output                     memresp4_val,
  input                      memresp4_rdy,
  output [c_resp_msg_sz-1:0] memresp4_msg,

  // Memory request port 5 interface

  input                      memreq5_val,
  output                     memreq5_rdy,
  input  [c_req_msg_sz-1:0]  memreq5_msg,

  // Memory response port 5 interface

  output                     memresp5_val,
  input                      memresp5_rdy,
  output [c_resp_msg_sz-1:0] memresp5_msg,

  // Memory request port 6 interface

  input                      memreq6_val,
  output                     memreq6_rdy,
  input  [c_req_msg_sz-1:0]  memreq6_msg,

  // Memory response port 6 interface

  output                     memresp6_val,
  input                      memresp6_rdy,
  output [c_resp_msg_sz-1:0] memresp6_msg,

  // Memory request port 7 interface

  input                      memreq7_val,
  output                     memreq7_rdy,
  input  [c_req_msg_sz-1:0]  memreq7_msg,

  // Memory response port 7 interface

  output                     memresp7_val,
  input                      memresp7_rdy,
  output [c_resp_msg_sz-1:0] memresp7_msg,

  // Memory request port 8 interface

  input                      memreq8_val,
  output                     memreq8_rdy,
  input  [c_req_msg_sz-1:0]  memreq8_msg,

  // Memory response port 8 interface

  output                     memresp8_val,
  input                      memresp8_rdy,
  output [c_resp_msg_sz-1:0] memresp8_msg,

  // Memory request port 9 interface

  input                      memreq9_val,
  output                     memreq9_rdy,
  input  [c_req_msg_sz-1:0]  memreq9_msg,

  // Memory response port 9 interface

  output                     memresp9_val,
  input                      memresp9_rdy,
  output [c_resp_msg_sz-1:0] memresp9_msg


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

  localparam c_read   = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_write  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_REQ_MSG_TYPE_AMOXCH;

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

  // Port 4

  wire [c_req_msg_type_sz-1:0] memreq4_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq4_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq4_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq4_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq4_msg_from_bits
  (
    .bits (memreq4_msg),
    .type (memreq4_msg_type),
    .addr (memreq4_msg_addr),
    .len  (memreq4_msg_len),
    .data (memreq4_msg_data)
  );

  // Port 5

  wire [c_req_msg_type_sz-1:0] memreq5_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq5_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq5_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq5_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq5_msg_from_bits
  (
    .bits (memreq5_msg),
    .type (memreq5_msg_type),
    .addr (memreq5_msg_addr),
    .len  (memreq5_msg_len),
    .data (memreq5_msg_data)
  );

  // Port 6

  wire [c_req_msg_type_sz-1:0] memreq6_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq6_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq6_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq6_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq6_msg_from_bits
  (
    .bits (memreq6_msg),
    .type (memreq6_msg_type),
    .addr (memreq6_msg_addr),
    .len  (memreq6_msg_len),
    .data (memreq6_msg_data)
  );

  // Port 7

  wire [c_req_msg_type_sz-1:0] memreq7_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq7_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq7_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq7_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq7_msg_from_bits
  (
    .bits (memreq7_msg),
    .type (memreq7_msg_type),
    .addr (memreq7_msg_addr),
    .len  (memreq7_msg_len),
    .data (memreq7_msg_data)
  );

  // Port 8

  wire [c_req_msg_type_sz-1:0] memreq8_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq8_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq8_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq8_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq8_msg_from_bits
  (
    .bits (memreq8_msg),
    .type (memreq8_msg_type),
    .addr (memreq8_msg_addr),
    .len  (memreq8_msg_len),
    .data (memreq8_msg_data)
  );

  // Port 9

  wire [c_req_msg_type_sz-1:0] memreq9_msg_type;
  wire [c_req_msg_addr_sz-1:0] memreq9_msg_addr;
  wire [c_req_msg_len_sz-1:0]  memreq9_msg_len;
  wire [c_req_msg_data_sz-1:0] memreq9_msg_data;

  vc_MemReqMsgFromBits#(p_addr_sz,p_data_sz) memreq9_msg_from_bits
  (
    .bits (memreq9_msg),
    .type (memreq9_msg_type),
    .addr (memreq9_msg_addr),
    .len  (memreq9_msg_len),
    .data (memreq9_msg_data)
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

  reg                         memreq4_val_M;
  reg [c_req_msg_type_sz-1:0] memreq4_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq4_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq4_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq4_msg_data_M;

  reg                         memreq5_val_M;
  reg [c_req_msg_type_sz-1:0] memreq5_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq5_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq5_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq5_msg_data_M;

  reg                         memreq6_val_M;
  reg [c_req_msg_type_sz-1:0] memreq6_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq6_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq6_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq6_msg_data_M;

  reg                         memreq7_val_M;
  reg [c_req_msg_type_sz-1:0] memreq7_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq7_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq7_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq7_msg_data_M;

  reg                         memreq8_val_M;
  reg [c_req_msg_type_sz-1:0] memreq8_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq8_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq8_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq8_msg_data_M;

  reg                         memreq9_val_M;
  reg [c_req_msg_type_sz-1:0] memreq9_msg_type_M;
  reg [c_req_msg_addr_sz-1:0] memreq9_msg_addr_M;
  reg [c_req_msg_len_sz-1:0]  memreq9_msg_len_M;
  reg [c_req_msg_data_sz-1:0] memreq9_msg_data_M;

  wire memreq0_go = memreq0_val && memreq0_rdy;
  wire memreq1_go = memreq1_val && memreq1_rdy;
  wire memreq2_go = memreq2_val && memreq2_rdy;
  wire memreq3_go = memreq3_val && memreq3_rdy;
  wire memreq4_go = memreq4_val && memreq4_rdy;
  wire memreq5_go = memreq5_val && memreq5_rdy;
  wire memreq6_go = memreq6_val && memreq6_rdy;
  wire memreq7_go = memreq7_val && memreq7_rdy;
  wire memreq8_go = memreq8_val && memreq8_rdy;
  wire memreq9_go = memreq9_val && memreq9_rdy;

  always @( posedge clk ) begin

    // Ensure that the valid bit is reset appropriately

    if ( reset ) begin
      memreq0_val_M <= 1'b0;
      memreq1_val_M <= 1'b0;
      memreq2_val_M <= 1'b0;
      memreq3_val_M <= 1'b0;
      memreq4_val_M <= 1'b0;
      memreq5_val_M <= 1'b0;
      memreq6_val_M <= 1'b0;
      memreq7_val_M <= 1'b0;
      memreq8_val_M <= 1'b0;
      memreq9_val_M <= 1'b0;
    end else begin
//      if ( memreq0_rdy )
//        memreq0_val_M <= memreq0_val;
//      if ( memreq1_rdy )
//        memreq1_val_M <= memreq1_val;
//      if ( memreq2_rdy )
//        memreq2_val_M <= memreq2_val;
//      if ( memreq3_rdy )
//        memreq3_val_M <= memreq3_val;
//      if ( memreq4_rdy )
//        memreq4_val_M <= memreq4_val;
//      if ( memreq5_rdy )
//        memreq5_val_M <= memreq5_val;
//      if ( memreq6_rdy )
//        memreq6_val_M <= memreq6_val;
//      if ( memreq7_rdy )
//        memreq7_val_M <= memreq7_val;
      memreq0_val_M <= memreq0_go;
      memreq1_val_M <= memreq1_go;
      memreq2_val_M <= memreq2_go;
      memreq3_val_M <= memreq3_go;
      memreq4_val_M <= memreq4_go;
      memreq5_val_M <= memreq5_go;
      memreq6_val_M <= memreq6_go;
      memreq7_val_M <= memreq7_go;
      memreq8_val_M <= memreq8_go;
      memreq9_val_M <= memreq9_go;
    end

    // Stall the pipeline if the response interface is not ready

    if ( memreq0_rdy ) begin
      memreq0_msg_type_M <= memreq0_msg_type;
      memreq0_msg_addr_M <= memreq0_msg_addr;
      memreq0_msg_len_M  <= memreq0_msg_len;
      memreq0_msg_data_M <= memreq0_msg_data;
    end

    if ( memreq1_rdy ) begin
      memreq1_msg_type_M <= memreq1_msg_type;
      memreq1_msg_addr_M <= memreq1_msg_addr;
      memreq1_msg_len_M  <= memreq1_msg_len;
      memreq1_msg_data_M <= memreq1_msg_data;
    end

    if ( memreq2_rdy ) begin
      memreq2_msg_type_M <= memreq2_msg_type;
      memreq2_msg_addr_M <= memreq2_msg_addr;
      memreq2_msg_len_M  <= memreq2_msg_len;
      memreq2_msg_data_M <= memreq2_msg_data;
    end

    if ( memreq3_rdy ) begin
      memreq3_msg_type_M <= memreq3_msg_type;
      memreq3_msg_addr_M <= memreq3_msg_addr;
      memreq3_msg_len_M  <= memreq3_msg_len;
      memreq3_msg_data_M <= memreq3_msg_data;
    end

    if ( memreq4_rdy ) begin
      memreq4_msg_type_M <= memreq4_msg_type;
      memreq4_msg_addr_M <= memreq4_msg_addr;
      memreq4_msg_len_M  <= memreq4_msg_len;
      memreq4_msg_data_M <= memreq4_msg_data;
    end

    if ( memreq5_rdy ) begin
      memreq5_msg_type_M <= memreq5_msg_type;
      memreq5_msg_addr_M <= memreq5_msg_addr;
      memreq5_msg_len_M  <= memreq5_msg_len;
      memreq5_msg_data_M <= memreq5_msg_data;
    end

    if ( memreq6_rdy ) begin
      memreq6_msg_type_M <= memreq6_msg_type;
      memreq6_msg_addr_M <= memreq6_msg_addr;
      memreq6_msg_len_M  <= memreq6_msg_len;
      memreq6_msg_data_M <= memreq6_msg_data;
    end

    if ( memreq7_rdy ) begin
      memreq7_msg_type_M <= memreq7_msg_type;
      memreq7_msg_addr_M <= memreq7_msg_addr;
      memreq7_msg_len_M  <= memreq7_msg_len;
      memreq7_msg_data_M <= memreq7_msg_data;
    end

    if ( memreq8_rdy ) begin
      memreq8_msg_type_M <= memreq8_msg_type;
      memreq8_msg_addr_M <= memreq8_msg_addr;
      memreq8_msg_len_M  <= memreq8_msg_len;
      memreq8_msg_data_M <= memreq8_msg_data;
    end

    if ( memreq9_rdy ) begin
      memreq9_msg_type_M <= memreq9_msg_type;
      memreq9_msg_addr_M <= memreq9_msg_addr;
      memreq9_msg_len_M  <= memreq9_msg_len;
      memreq9_msg_data_M <= memreq9_msg_data;
    end

  end

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

  wire [c_req_msg_len_sz:0] memreq4_msg_len_modified_M
    = ( memreq4_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq4_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq5_msg_len_modified_M
    = ( memreq5_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq5_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq6_msg_len_modified_M
    = ( memreq6_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq6_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq7_msg_len_modified_M
    = ( memreq7_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq7_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq8_msg_len_modified_M
    = ( memreq8_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq8_msg_len_M;

  wire [c_req_msg_len_sz:0] memreq9_msg_len_modified_M
    = ( memreq9_msg_len_M == 0 ) ? (c_req_msg_data_sz/8)
    :                              memreq9_msg_len_M;

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

  wire [c_physical_addr_sz-1:0] physical_byte_addr4_M
    = memreq4_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr5_M
    = memreq5_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr6_M
    = memreq6_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr7_M
    = memreq7_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr8_M
    = memreq8_msg_addr_M[c_physical_addr_sz-1:0];

  wire [c_physical_addr_sz-1:0] physical_byte_addr9_M
    = memreq9_msg_addr_M[c_physical_addr_sz-1:0];

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

  wire [c_physical_block_addr_sz-1:0] physical_block_addr4_M
    = physical_byte_addr4_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr5_M
    = physical_byte_addr5_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr6_M
    = physical_byte_addr6_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr7_M
    = physical_byte_addr7_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr8_M
    = physical_byte_addr8_M/c_data_byte_sz;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr9_M
    = physical_byte_addr9_M/c_data_byte_sz;


  wire [c_block_offset_sz-1:0] block_offset0_M
    = physical_byte_addr0_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset1_M
    = physical_byte_addr1_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset2_M
    = physical_byte_addr2_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset3_M
    = physical_byte_addr3_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset4_M
    = physical_byte_addr4_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset5_M
    = physical_byte_addr5_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset6_M
    = physical_byte_addr6_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset7_M
    = physical_byte_addr7_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset8_M
    = physical_byte_addr8_M[c_block_offset_sz-1:0];

  wire [c_block_offset_sz-1:0] block_offset9_M
    = physical_byte_addr9_M[c_block_offset_sz-1:0];


  wire [p_data_sz-1:0] read_block0_M
    = m[physical_block_addr0_M];

  wire [p_data_sz-1:0] read_block1_M
    = m[physical_block_addr1_M];

  wire [p_data_sz-1:0] read_block2_M
    = m[physical_block_addr2_M];

  wire [p_data_sz-1:0] read_block3_M
    = m[physical_block_addr3_M];

  wire [p_data_sz-1:0] read_block4_M
    = m[physical_block_addr4_M];

  wire [p_data_sz-1:0] read_block5_M
    = m[physical_block_addr5_M];

  wire [p_data_sz-1:0] read_block6_M
    = m[physical_block_addr6_M];

  wire [p_data_sz-1:0] read_block7_M
    = m[physical_block_addr7_M];

  wire [p_data_sz-1:0] read_block8_M
    = m[physical_block_addr8_M];

  wire [p_data_sz-1:0] read_block9_M
    = m[physical_block_addr9_M];


  wire [c_resp_msg_data_sz-1:0] read_data0_M
    = read_block0_M >> (block_offset0_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data1_M
    = read_block1_M >> (block_offset1_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data2_M
    = read_block2_M >> (block_offset2_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data3_M
    = read_block3_M >> (block_offset3_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data4_M
    = read_block4_M >> (block_offset4_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data5_M
    = read_block5_M >> (block_offset5_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data6_M
    = read_block6_M >> (block_offset6_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data7_M
    = read_block7_M >> (block_offset7_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data8_M
    = read_block8_M >> (block_offset8_M*8);

  wire [c_resp_msg_data_sz-1:0] read_data9_M
    = read_block9_M >> (block_offset9_M*8);

  // Atomic operations. amo.add, amo.and, amo.or, and amo.xchg return the
  // read data pre-modification, but writes the modified data back into
  // memory on the next clock edge. The data field in the memory message is
  // used to specify the data to modify the read data with.
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

  wire [c_req_msg_data_sz-1:0] memreq4_msg_data_amoadd_M
    = read_data4_M + memreq4_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq5_msg_data_amoadd_M
    = read_data5_M + memreq5_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq6_msg_data_amoadd_M
    = read_data6_M + memreq6_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq7_msg_data_amoadd_M
    = read_data7_M + memreq7_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq8_msg_data_amoadd_M
    = read_data8_M + memreq8_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq9_msg_data_amoadd_M
    = read_data9_M + memreq9_msg_data_M;

  // amo.and output

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_amoand_M
    = read_data0_M & memreq0_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_amoand_M
    = read_data1_M & memreq1_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_amoand_M
    = read_data2_M & memreq2_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_amoand_M
    = read_data3_M & memreq3_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq4_msg_data_amoand_M
    = read_data4_M & memreq4_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq5_msg_data_amoand_M
    = read_data5_M & memreq5_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq6_msg_data_amoand_M
    = read_data6_M & memreq6_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq7_msg_data_amoand_M
    = read_data7_M & memreq7_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq8_msg_data_amoand_M
    = read_data8_M & memreq8_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq9_msg_data_amoand_M
    = read_data9_M & memreq9_msg_data_M;

  // amo.or output

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_amoor_M
    = read_data0_M | memreq0_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_amoor_M
    = read_data1_M | memreq1_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_amoor_M
    = read_data2_M | memreq2_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_amoor_M
    = read_data3_M | memreq3_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq4_msg_data_amoor_M
    = read_data4_M | memreq4_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq5_msg_data_amoor_M
    = read_data5_M | memreq5_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq6_msg_data_amoor_M
    = read_data6_M | memreq6_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq7_msg_data_amoor_M
    = read_data7_M | memreq7_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq8_msg_data_amoor_M
    = read_data8_M | memreq8_msg_data_M;

  wire [c_req_msg_data_sz-1:0] memreq9_msg_data_amoor_M
    = read_data9_M | memreq9_msg_data_M;

  // Modified write data mux

  wire [c_req_msg_data_sz-1:0] memreq0_msg_data_modified_M
    = ( memreq0_msg_type_M == c_read   ) ? memreq0_msg_data_M
    : ( memreq0_msg_type_M == c_write  ) ? memreq0_msg_data_M
    : ( memreq0_msg_type_M == c_amoadd ) ? memreq0_msg_data_amoadd_M
    : ( memreq0_msg_type_M == c_amoand ) ? memreq0_msg_data_amoand_M
    : ( memreq0_msg_type_M == c_amoor  ) ? memreq0_msg_data_amoor_M
    : ( memreq0_msg_type_M == c_amoxch ) ? memreq0_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq1_msg_data_modified_M
    = ( memreq1_msg_type_M == c_read   ) ? memreq1_msg_data_M
    : ( memreq1_msg_type_M == c_write  ) ? memreq1_msg_data_M
    : ( memreq1_msg_type_M == c_amoadd ) ? memreq1_msg_data_amoadd_M
    : ( memreq1_msg_type_M == c_amoand ) ? memreq1_msg_data_amoand_M
    : ( memreq1_msg_type_M == c_amoor  ) ? memreq1_msg_data_amoor_M
    : ( memreq1_msg_type_M == c_amoxch ) ? memreq1_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq2_msg_data_modified_M
    = ( memreq2_msg_type_M == c_read   ) ? memreq2_msg_data_M
    : ( memreq2_msg_type_M == c_write  ) ? memreq2_msg_data_M
    : ( memreq2_msg_type_M == c_amoadd ) ? memreq2_msg_data_amoadd_M
    : ( memreq2_msg_type_M == c_amoand ) ? memreq2_msg_data_amoand_M
    : ( memreq2_msg_type_M == c_amoor  ) ? memreq2_msg_data_amoor_M
    : ( memreq2_msg_type_M == c_amoxch ) ? memreq2_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq3_msg_data_modified_M
    = ( memreq3_msg_type_M == c_read   ) ? memreq3_msg_data_M
    : ( memreq3_msg_type_M == c_write  ) ? memreq3_msg_data_M
    : ( memreq3_msg_type_M == c_amoadd ) ? memreq3_msg_data_amoadd_M
    : ( memreq3_msg_type_M == c_amoand ) ? memreq3_msg_data_amoand_M
    : ( memreq3_msg_type_M == c_amoor  ) ? memreq3_msg_data_amoor_M
    : ( memreq3_msg_type_M == c_amoxch ) ? memreq3_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq4_msg_data_modified_M
    = ( memreq4_msg_type_M == c_read   ) ? memreq4_msg_data_M
    : ( memreq4_msg_type_M == c_write  ) ? memreq4_msg_data_M
    : ( memreq4_msg_type_M == c_amoadd ) ? memreq4_msg_data_amoadd_M
    : ( memreq4_msg_type_M == c_amoand ) ? memreq4_msg_data_amoand_M
    : ( memreq4_msg_type_M == c_amoor  ) ? memreq4_msg_data_amoor_M
    : ( memreq4_msg_type_M == c_amoxch ) ? memreq4_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq5_msg_data_modified_M
    = ( memreq5_msg_type_M == c_read   ) ? memreq5_msg_data_M
    : ( memreq5_msg_type_M == c_write  ) ? memreq5_msg_data_M
    : ( memreq5_msg_type_M == c_amoadd ) ? memreq5_msg_data_amoadd_M
    : ( memreq5_msg_type_M == c_amoand ) ? memreq5_msg_data_amoand_M
    : ( memreq5_msg_type_M == c_amoor  ) ? memreq5_msg_data_amoor_M
    : ( memreq5_msg_type_M == c_amoxch ) ? memreq5_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq6_msg_data_modified_M
    = ( memreq6_msg_type_M == c_read   ) ? memreq6_msg_data_M
    : ( memreq6_msg_type_M == c_write  ) ? memreq6_msg_data_M
    : ( memreq6_msg_type_M == c_amoadd ) ? memreq6_msg_data_amoadd_M
    : ( memreq6_msg_type_M == c_amoand ) ? memreq6_msg_data_amoand_M
    : ( memreq6_msg_type_M == c_amoor  ) ? memreq6_msg_data_amoor_M
    : ( memreq6_msg_type_M == c_amoxch ) ? memreq6_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq7_msg_data_modified_M
    = ( memreq7_msg_type_M == c_read   ) ? memreq7_msg_data_M
    : ( memreq7_msg_type_M == c_write  ) ? memreq7_msg_data_M
    : ( memreq7_msg_type_M == c_amoadd ) ? memreq7_msg_data_amoadd_M
    : ( memreq7_msg_type_M == c_amoand ) ? memreq7_msg_data_amoand_M
    : ( memreq7_msg_type_M == c_amoor  ) ? memreq7_msg_data_amoor_M
    : ( memreq7_msg_type_M == c_amoxch ) ? memreq7_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq8_msg_data_modified_M
    = ( memreq8_msg_type_M == c_read   ) ? memreq8_msg_data_M
    : ( memreq8_msg_type_M == c_write  ) ? memreq8_msg_data_M
    : ( memreq8_msg_type_M == c_amoadd ) ? memreq8_msg_data_amoadd_M
    : ( memreq8_msg_type_M == c_amoand ) ? memreq8_msg_data_amoand_M
    : ( memreq8_msg_type_M == c_amoor  ) ? memreq8_msg_data_amoor_M
    : ( memreq8_msg_type_M == c_amoxch ) ? memreq8_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  wire [c_req_msg_data_sz-1:0] memreq9_msg_data_modified_M
    = ( memreq9_msg_type_M == c_read   ) ? memreq9_msg_data_M
    : ( memreq9_msg_type_M == c_write  ) ? memreq9_msg_data_M
    : ( memreq9_msg_type_M == c_amoadd ) ? memreq9_msg_data_amoadd_M
    : ( memreq9_msg_type_M == c_amoand ) ? memreq9_msg_data_amoand_M
    : ( memreq9_msg_type_M == c_amoor  ) ? memreq9_msg_data_amoor_M
    : ( memreq9_msg_type_M == c_amoxch ) ? memreq9_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};

  // Write the data if required. Again, we use a behavioral for loop to
  // allow us to flexibly handle arbitrary alignment and lengths. This is
  // a sequential always block so that the write happens on the next edge.

  // TODO: dmlockhart... replace memreq0_val_M with output of queue?

  wire write_en0_M = memreq0_val_M &&
                ( ( memreq0_msg_type_M == c_write  )
                ||( memreq0_msg_type_M == c_amoadd )
                ||( memreq0_msg_type_M == c_amoand )
                ||( memreq0_msg_type_M == c_amoor  )
                ||( memreq0_msg_type_M == c_amoxch ) );

  wire write_en1_M = memreq1_val_M &&
                ( ( memreq1_msg_type_M == c_write  )
                ||( memreq1_msg_type_M == c_amoadd )
                ||( memreq1_msg_type_M == c_amoand )
                ||( memreq1_msg_type_M == c_amoor  )
                ||( memreq1_msg_type_M == c_amoxch ) );

  wire write_en2_M = memreq2_val_M &&
                ( ( memreq2_msg_type_M == c_write  )
                ||( memreq2_msg_type_M == c_amoadd )
                ||( memreq2_msg_type_M == c_amoand )
                ||( memreq2_msg_type_M == c_amoor  )
                ||( memreq2_msg_type_M == c_amoxch ) );

  wire write_en3_M = memreq3_val_M &&
                ( ( memreq3_msg_type_M == c_write  )
                ||( memreq3_msg_type_M == c_amoadd )
                ||( memreq3_msg_type_M == c_amoand )
                ||( memreq3_msg_type_M == c_amoor  )
                ||( memreq3_msg_type_M == c_amoxch ) );

  wire write_en4_M = memreq4_val_M &&
                ( ( memreq4_msg_type_M == c_write  )
                ||( memreq4_msg_type_M == c_amoadd )
                ||( memreq4_msg_type_M == c_amoand )
                ||( memreq4_msg_type_M == c_amoor  )
                ||( memreq4_msg_type_M == c_amoxch ) );

  wire write_en5_M = memreq5_val_M &&
                ( ( memreq5_msg_type_M == c_write  )
                ||( memreq5_msg_type_M == c_amoadd )
                ||( memreq5_msg_type_M == c_amoand )
                ||( memreq5_msg_type_M == c_amoor  )
                ||( memreq5_msg_type_M == c_amoxch ) );

  wire write_en6_M = memreq6_val_M &&
                ( ( memreq6_msg_type_M == c_write  )
                ||( memreq6_msg_type_M == c_amoadd )
                ||( memreq6_msg_type_M == c_amoand )
                ||( memreq6_msg_type_M == c_amoor  )
                ||( memreq6_msg_type_M == c_amoxch ) );

  wire write_en7_M = memreq7_val_M &&
                ( ( memreq7_msg_type_M == c_write  )
                ||( memreq7_msg_type_M == c_amoadd )
                ||( memreq7_msg_type_M == c_amoand )
                ||( memreq7_msg_type_M == c_amoor  )
                ||( memreq7_msg_type_M == c_amoxch ) );

  wire write_en8_M = memreq8_val_M &&
                ( ( memreq8_msg_type_M == c_write  )
                ||( memreq8_msg_type_M == c_amoadd )
                ||( memreq8_msg_type_M == c_amoand )
                ||( memreq8_msg_type_M == c_amoor  )
                ||( memreq8_msg_type_M == c_amoxch ) );

  wire write_en9_M = memreq9_val_M &&
                ( ( memreq9_msg_type_M == c_write  )
                ||( memreq9_msg_type_M == c_amoadd )
                ||( memreq9_msg_type_M == c_amoand )
                ||( memreq9_msg_type_M == c_amoor  )
                ||( memreq9_msg_type_M == c_amoxch ) );

  integer wr0_i;
  integer wr1_i;
  integer wr2_i;
  integer wr3_i;
  integer wr4_i;
  integer wr5_i;
  integer wr6_i;
  integer wr7_i;
  integer wr8_i;
  integer wr9_i;

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
    if ( write_en4_M ) begin
      for ( wr4_i = 0; wr4_i < memreq4_msg_len_modified_M; wr4_i = wr4_i + 1 ) begin
        m[physical_block_addr4_M][ (block_offset4_M*8) + (wr4_i*8) +: 8 ] <= memreq4_msg_data_modified_M[ (wr4_i*8) +: 8 ];
      end
    end
    if ( write_en5_M ) begin
      for ( wr5_i = 0; wr5_i < memreq5_msg_len_modified_M; wr5_i = wr5_i + 1 ) begin
        m[physical_block_addr5_M][ (block_offset5_M*8) + (wr5_i*8) +: 8 ] <= memreq5_msg_data_modified_M[ (wr5_i*8) +: 8 ];
      end
    end
    if ( write_en6_M ) begin
      for ( wr6_i = 0; wr6_i < memreq6_msg_len_modified_M; wr6_i = wr6_i + 1 ) begin
        m[physical_block_addr6_M][ (block_offset6_M*8) + (wr6_i*8) +: 8 ] <= memreq6_msg_data_modified_M[ (wr6_i*8) +: 8 ];
      end
    end
    if ( write_en7_M ) begin
      for ( wr7_i = 0; wr7_i < memreq7_msg_len_modified_M; wr7_i = wr7_i + 1 ) begin
        m[physical_block_addr7_M][ (block_offset7_M*8) + (wr7_i*8) +: 8 ] <= memreq7_msg_data_modified_M[ (wr7_i*8) +: 8 ];
      end
    end
    if ( write_en8_M ) begin
      for ( wr8_i = 0; wr8_i < memreq8_msg_len_modified_M; wr8_i = wr8_i + 1 ) begin
        m[physical_block_addr8_M][ (block_offset8_M*8) + (wr8_i*8) +: 8 ] <= memreq8_msg_data_modified_M[ (wr8_i*8) +: 8 ];
      end
    end
    if ( write_en9_M ) begin
      for ( wr9_i = 0; wr9_i < memreq9_msg_len_modified_M; wr9_i = wr9_i + 1 ) begin
        m[physical_block_addr9_M][ (block_offset9_M*8) + (wr9_i*8) +: 8 ] <= memreq9_msg_data_modified_M[ (wr9_i*8) +: 8 ];
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

  wire [c_resp_msg_type_sz-1:0] memresp4_msg_type_M = memreq4_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp4_msg_len_M  = memreq4_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp4_msg_data_M = read_data4_M;

  wire [c_resp_msg_type_sz-1:0] memresp5_msg_type_M = memreq5_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp5_msg_len_M  = memreq5_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp5_msg_data_M = read_data5_M;

  wire [c_resp_msg_type_sz-1:0] memresp6_msg_type_M = memreq6_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp6_msg_len_M  = memreq6_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp6_msg_data_M = read_data6_M;

  wire [c_resp_msg_type_sz-1:0] memresp7_msg_type_M = memreq7_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp7_msg_len_M  = memreq7_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp7_msg_data_M = read_data7_M;

  wire [c_resp_msg_type_sz-1:0] memresp8_msg_type_M = memreq8_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp8_msg_len_M  = memreq8_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp8_msg_data_M = read_data8_M;

  wire [c_resp_msg_type_sz-1:0] memresp9_msg_type_M = memreq9_msg_type_M;
  wire [c_resp_msg_len_sz-1:0]  memresp9_msg_len_M  = memreq9_msg_len_M;
  wire [c_resp_msg_data_sz-1:0] memresp9_msg_data_M = read_data9_M;

  //----------------------------------------------------------------------
  // Bypass Queue on the Output
  //----------------------------------------------------------------------
  // This is necessary to prevent deadlock when hooked up directly
  // to the direct mapped cache!

  wire [c_resp_msg_sz-1:0] memresp0_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp1_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp2_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp3_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp4_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp5_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp6_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp7_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp8_queue_msg;
  wire [c_resp_msg_sz-1:0] memresp9_queue_msg;

  // Response queue enqueue ready signals

  wire enq_memreq0_rdy;
  wire enq_memreq1_rdy;
  wire enq_memreq2_rdy;
  wire enq_memreq3_rdy;
  wire enq_memreq4_rdy;
  wire enq_memreq5_rdy;
  wire enq_memreq6_rdy;
  wire enq_memreq7_rdy;
  wire enq_memreq8_rdy;
  wire enq_memreq9_rdy;

  // 16 = number of queue entries, 4 = number of bits needed to
  // index 16 entries... make sure you change that field if
  // you change the number of queue entries! So dumb.

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp0_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp0_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq0_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq0_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp0_msg),
    .deq_val  (memresp0_val),
    .deq_rdy  (memresp0_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp1_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp1_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq1_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq1_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp1_msg),
    .deq_val  (memresp1_val),
    .deq_rdy  (memresp1_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp2_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp2_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq2_val_M),     // Wire up to req_val output
    .enq_rdy  (enq_memreq2_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp2_msg),
    .deq_val  (memresp2_val),
    .deq_rdy  (memresp2_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp3_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp3_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq3_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq3_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp3_msg),
    .deq_val  (memresp3_val),
    .deq_rdy  (memresp3_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp4_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp4_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq4_val_M),     // Wire up to req_val output
    .enq_rdy  (enq_memreq4_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp4_msg),
    .deq_val  (memresp4_val),
    .deq_rdy  (memresp4_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp5_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp5_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq5_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq5_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp5_msg),
    .deq_val  (memresp5_val),
    .deq_rdy  (memresp5_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp6_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp6_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq6_val_M),     // Wire up to req_val output
    .enq_rdy  (enq_memreq6_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp6_msg),
    .deq_val  (memresp6_val),
    .deq_rdy  (memresp6_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp7_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp7_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq7_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq7_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp7_msg),
    .deq_val  (memresp7_val),
    .deq_rdy  (memresp7_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp8_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp8_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq8_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq8_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp8_msg),
    .deq_val  (memresp8_val),
    .deq_rdy  (memresp8_rdy)
  );

  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_msg_sz,32,5) memresp9_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp9_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq9_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq9_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp9_msg),
    .deq_val  (memresp9_val),
    .deq_rdy  (memresp9_rdy)
  );

  //----------------------------------------------------------------------
  // Atomic operation logic
  //----------------------------------------------------------------------
  // We need to serialize atomic memory requests when multiple arrive
  // across all the ports in a single cycle. An arbiter is used to grant
  // one port access to atomically modify memory. Only this port sets its
  // rdy signal high, the other requests must wait. Note that the rdy
  // signal is only dependent on the arbiter grants if there are
  // simultaneous atomics requests, otherwise it is only dependent on
  // whether or not there is room in the response queues.

  wire arb_amo_en0 = memreq0_val
                  && ( ( memreq0_msg_type == c_amoadd )
                    || ( memreq0_msg_type == c_amoand )
                    || ( memreq0_msg_type == c_amoor  )
                    || ( memreq0_msg_type == c_amoxch ) );

  wire arb_amo_en1 = memreq1_val
                  && ( ( memreq1_msg_type == c_amoadd )
                    || ( memreq1_msg_type == c_amoand )
                    || ( memreq1_msg_type == c_amoor  )
                    || ( memreq1_msg_type == c_amoxch ) );

  wire arb_amo_en2 = memreq2_val
                  && ( ( memreq2_msg_type == c_amoadd )
                    || ( memreq2_msg_type == c_amoand )
                    || ( memreq2_msg_type == c_amoor  )
                    || ( memreq2_msg_type == c_amoxch ) );

  wire arb_amo_en3 = memreq3_val
                  && ( ( memreq3_msg_type == c_amoadd )
                    || ( memreq3_msg_type == c_amoand )
                    || ( memreq3_msg_type == c_amoor  )
                    || ( memreq3_msg_type == c_amoxch ) );

  wire arb_amo_en4 = memreq4_val
                  && ( ( memreq4_msg_type == c_amoadd )
                    || ( memreq4_msg_type == c_amoand )
                    || ( memreq4_msg_type == c_amoor  )
                    || ( memreq4_msg_type == c_amoxch ) );

  wire arb_amo_en5 = memreq5_val
                  && ( ( memreq5_msg_type == c_amoadd )
                    || ( memreq5_msg_type == c_amoand )
                    || ( memreq5_msg_type == c_amoor  )
                    || ( memreq5_msg_type == c_amoxch ) );

  wire arb_amo_en6 = memreq6_val
                  && ( ( memreq6_msg_type == c_amoadd )
                    || ( memreq6_msg_type == c_amoand )
                    || ( memreq6_msg_type == c_amoor  )
                    || ( memreq6_msg_type == c_amoxch ) );

  wire arb_amo_en7 = memreq7_val
                  && ( ( memreq7_msg_type == c_amoadd )
                    || ( memreq7_msg_type == c_amoand )
                    || ( memreq7_msg_type == c_amoor  )
                    || ( memreq7_msg_type == c_amoxch ) );

  wire arb_amo_en8 = memreq8_val
                  && ( ( memreq8_msg_type == c_amoadd )
                    || ( memreq8_msg_type == c_amoand )
                    || ( memreq8_msg_type == c_amoor  )
                    || ( memreq8_msg_type == c_amoxch ) );

  wire arb_amo_en9 = memreq9_val
                  && ( ( memreq9_msg_type == c_amoadd )
                    || ( memreq9_msg_type == c_amoand )
                    || ( memreq9_msg_type == c_amoor  )
                    || ( memreq9_msg_type == c_amoxch ) );

  // Atomic op grants arbiter

  wire [9:0] amo_reqs = { arb_amo_en9, arb_amo_en8, arb_amo_en7, arb_amo_en6, 
                          arb_amo_en5, arb_amo_en4, arb_amo_en3, arb_amo_en2, 
                          arb_amo_en1, arb_amo_en0 };

  wire [9:0] amo_grants;

  vc_RoundRobinArb
  #(
    .NUM_REQS (10)
  )
  arb
  (
    .clk    (clk),
    .reset  (reset),
    .reqs   (amo_reqs),
    .grants (amo_grants)
  );

  // Set memreq rdy signals based on atomic requests

  assign memreq0_rdy = ( arb_amo_en0 ) ? amo_grants[0] && enq_memreq0_rdy : enq_memreq0_rdy;
  assign memreq1_rdy = ( arb_amo_en1 ) ? amo_grants[1] && enq_memreq1_rdy : enq_memreq1_rdy;
  assign memreq2_rdy = ( arb_amo_en2 ) ? amo_grants[2] && enq_memreq2_rdy : enq_memreq2_rdy;
  assign memreq3_rdy = ( arb_amo_en3 ) ? amo_grants[3] && enq_memreq3_rdy : enq_memreq3_rdy;
  assign memreq4_rdy = ( arb_amo_en4 ) ? amo_grants[4] && enq_memreq4_rdy : enq_memreq4_rdy;
  assign memreq5_rdy = ( arb_amo_en5 ) ? amo_grants[5] && enq_memreq5_rdy : enq_memreq5_rdy;
  assign memreq6_rdy = ( arb_amo_en6 ) ? amo_grants[6] && enq_memreq6_rdy : enq_memreq6_rdy;
  assign memreq7_rdy = ( arb_amo_en7 ) ? amo_grants[7] && enq_memreq7_rdy : enq_memreq7_rdy;
  assign memreq8_rdy = ( arb_amo_en8 ) ? amo_grants[8] && enq_memreq8_rdy : enq_memreq8_rdy;
  assign memreq9_rdy = ( arb_amo_en9 ) ? amo_grants[9] && enq_memreq9_rdy : enq_memreq9_rdy;

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

  vc_MemRespMsgToBits#(p_data_sz) memresp4_msg_to_bits
  (
    .type (memresp4_msg_type_M),
    .len  (memresp4_msg_len_M),
    .data (memresp4_msg_data_M),
    //.bits (memresp4_msg)
    .bits (memresp4_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp5_msg_to_bits
  (
    .type (memresp5_msg_type_M),
    .len  (memresp5_msg_len_M),
    .data (memresp5_msg_data_M),
    //.bits (memresp5_msg)
    .bits (memresp5_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp6_msg_to_bits
  (
    .type (memresp6_msg_type_M),
    .len  (memresp6_msg_len_M),
    .data (memresp6_msg_data_M),
    //.bits (memresp6_msg)
    .bits (memresp6_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp7_msg_to_bits
  (
    .type (memresp7_msg_type_M),
    .len  (memresp7_msg_len_M),
    .data (memresp7_msg_data_M),
    //.bits (memresp7_msg)
    .bits (memresp7_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp8_msg_to_bits
  (
    .type (memresp8_msg_type_M),
    .len  (memresp8_msg_len_M),
    .data (memresp8_msg_data_M),
    //.bits (memresp8_msg)
    .bits (memresp8_queue_msg)
  );

  vc_MemRespMsgToBits#(p_data_sz) memresp9_msg_to_bits
  (
    .type (memresp9_msg_type_M),
    .len  (memresp9_msg_len_M),
    .data (memresp9_msg_data_M),
    //.bits (memresp9_msg)
    .bits (memresp9_queue_msg)
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
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq4_val,  "memreq4_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp4_rdy, "memresp4_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq5_val,  "memreq5_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp5_rdy, "memresp5_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq6_val,  "memreq6_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp6_rdy, "memresp6_rdy" );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq7_val,  "memreq7_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq8_val,  "memreq8_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq9_val,  "memreq9_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp9_rdy, "memresp9_rdy" );

endmodule

`endif /* VC_TEST_DECA_PORT_MEM_V */

