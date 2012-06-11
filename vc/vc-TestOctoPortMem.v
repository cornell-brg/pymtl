//========================================================================
// Verilog Components: Test Memory
//========================================================================

`ifndef VC_TEST_OCTO_PORT_MEM_V
`define VC_TEST_OCTO_PORT_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Assert.v"
`include "vc-Queues.v"
`include "vc-TestMemReqRespPort.v"

`include "vc-Arbiters.v"

//------------------------------------------------------------------------
// Quad port test memory
//------------------------------------------------------------------------

module vc_TestOctoPortMem
#(
  parameter p_mem_sz  = 1024, // size of physical memory in bytes
  parameter p_addr_sz = 8,    // size of mem message address in bits
  parameter p_data_sz = 32,   // size of mem message data in bits

  // Local constants not meant to be set from outside the module
  parameter c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter p_pydata_sz = 32,
  parameter c_req_pyifc_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_pydata_sz),
  parameter c_resp_pyifc_sz = `VC_MEM_RESP_MSG_SZ(p_pydata_sz)
)(
  input clk,
  input reset,

  // Memory request ports

  input                      memreq0_val,
  output                     memreq0_rdy,
  input  [c_req_msg_sz-1:0]  memreq0_msg,
  input                      memreq1_val,
  output                     memreq1_rdy,
  input  [c_req_msg_sz-1:0]  memreq1_msg,
  input                      memreq2_val,
  output                     memreq2_rdy,
  input  [c_req_msg_sz-1:0]  memreq2_msg,
  input                      memreq3_val,
  output                     memreq3_rdy,
  input  [c_req_msg_sz-1:0]  memreq3_msg,
  input                      memreq4_val,
  output                     memreq4_rdy,
  input  [c_req_msg_sz-1:0]  memreq4_msg,
  input                      memreq5_val,
  output                     memreq5_rdy,
  input  [c_req_msg_sz-1:0]  memreq5_msg,
  input                      memreq6_val,
  output                     memreq6_rdy,
  input  [c_req_msg_sz-1:0]  memreq6_msg,
  // Specially sized port
  input                        memreq7_val,
  output                       memreq7_rdy,
  input  [c_req_pyifc_sz-1:0]  memreq7_msg,


  // Memory response ports

  output                     memresp0_val,
  input                      memresp0_rdy,
  output [c_resp_msg_sz-1:0] memresp0_msg,
  output                     memresp1_val,
  input                      memresp1_rdy,
  output [c_resp_msg_sz-1:0] memresp1_msg,
  output                     memresp2_val,
  input                      memresp2_rdy,
  output [c_resp_msg_sz-1:0] memresp2_msg,
  output                     memresp3_val,
  input                      memresp3_rdy,
  output [c_resp_msg_sz-1:0] memresp3_msg,
  output                     memresp4_val,
  input                      memresp4_rdy,
  output [c_resp_msg_sz-1:0] memresp4_msg,
  output                     memresp5_val,
  input                      memresp5_rdy,
  output [c_resp_msg_sz-1:0] memresp5_msg,
  output                     memresp6_val,
  input                      memresp6_rdy,
  output [c_resp_msg_sz-1:0] memresp6_msg,
  // Specially sized port
  output                       memresp7_val,
  input                        memresp7_rdy,
  output [c_resp_pyifc_sz-1:0] memresp7_msg

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

  // Shorthand for the message field sizes

  localparam c_req_msg_type_sz  = `VC_MEM_REQ_MSG_TYPE_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_addr_sz  = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_data_sz);
  localparam c_req_msg_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_data_sz);

  localparam c_resp_msg_type_sz = `VC_MEM_RESP_MSG_TYPE_SZ(p_data_sz);
  localparam c_resp_msg_len_sz  = `VC_MEM_RESP_MSG_LEN_SZ(p_data_sz);
  localparam c_resp_msg_data_sz = `VC_MEM_RESP_MSG_DATA_SZ(p_data_sz);

  localparam c_req_pyifc_type_sz  = `VC_MEM_REQ_MSG_TYPE_SZ(p_addr_sz,p_pydata_sz);
  localparam c_req_pyifc_addr_sz  = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_pydata_sz);
  localparam c_req_pyifc_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_pydata_sz);
  localparam c_req_pyifc_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_pydata_sz);

  localparam c_resp_pyifc_type_sz = `VC_MEM_RESP_MSG_TYPE_SZ(p_pydata_sz);
  localparam c_resp_pyifc_len_sz  = `VC_MEM_RESP_MSG_LEN_SZ(p_pydata_sz);
  localparam c_resp_pyifc_data_sz = `VC_MEM_RESP_MSG_DATA_SZ(p_pydata_sz);

  //----------------------------------------------------------------------
  // Declare Wires to Port Modules
  //----------------------------------------------------------------------

  wire [c_physical_block_addr_sz-1:0] physical_block_addr0_M;
  wire                                write_en0_M;
  wire [c_req_msg_len_sz:0]           memreq0_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset0_M;
  wire [c_req_msg_data_sz-1:0]        memreq0_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr1_M;
  wire                                write_en1_M;
  wire [c_req_msg_len_sz:0]           memreq1_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset1_M;
  wire [c_req_msg_data_sz-1:0]        memreq1_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr2_M;
  wire                                write_en2_M;
  wire [c_req_msg_len_sz:0]           memreq2_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset2_M;
  wire [c_req_msg_data_sz-1:0]        memreq2_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr3_M;
  wire                                write_en3_M;
  wire [c_req_msg_len_sz:0]           memreq3_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset3_M;
  wire [c_req_msg_data_sz-1:0]        memreq3_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr4_M;
  wire                                write_en4_M;
  wire [c_req_msg_len_sz:0]           memreq4_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset4_M;
  wire [c_req_msg_data_sz-1:0]        memreq4_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr5_M;
  wire                                write_en5_M;
  wire [c_req_msg_len_sz:0]           memreq5_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset5_M;
  wire [c_req_msg_data_sz-1:0]        memreq5_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr6_M;
  wire                                write_en6_M;
  wire [c_req_msg_len_sz:0]           memreq6_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset6_M;
  wire [c_req_msg_data_sz-1:0]        memreq6_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr7_M;
  wire                                write_en7_M;
  wire [c_req_pyifc_len_sz:0]           memreq7_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset7_M;
  wire [c_req_pyifc_data_sz-1:0]        memreq7_msg_data_modified_M;

  wire arb_amo_en0;
  wire arb_amo_en1;
  wire arb_amo_en2;
  wire arb_amo_en3;
  wire arb_amo_en4;
  wire arb_amo_en5;
  wire arb_amo_en6;
  wire arb_amo_en7;
  wire [7:0] amo_grants;

  //----------------------------------------------------------------------
  // Actual memory array
  //----------------------------------------------------------------------

  reg [p_data_sz-1:0] m[c_num_blocks-1:0];

  //----------------------------------------------------------------------
  // Read the data
  //----------------------------------------------------------------------

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


  //----------------------------------------------------------------------
  // Instantiate the Ports
  //----------------------------------------------------------------------

  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port0
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq0_val),
    .memreq_rdy                 (memreq0_rdy),
    .memreq_msg                 (memreq0_msg),

    .memresp_val                (memresp0_val),
    .memresp_rdy                (memresp0_rdy),
    .memresp_msg                (memresp0_msg),

    .physical_block_addr_M      (physical_block_addr0_M),
    .read_block_M               (read_block0_M),

    .write_en_M                 (write_en0_M),
    .memreq_msg_len_modified_M  (memreq0_msg_len_modified_M),
    .block_offset_M             (block_offset0_M),
    .memreq_msg_data_modified_M (memreq0_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en0),
    .amo_grant                  (amo_grants[0])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port1
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq1_val),
    .memreq_rdy                 (memreq1_rdy),
    .memreq_msg                 (memreq1_msg),

    .memresp_val                (memresp1_val),
    .memresp_rdy                (memresp1_rdy),
    .memresp_msg                (memresp1_msg),

    .physical_block_addr_M      (physical_block_addr1_M),
    .read_block_M               (read_block1_M),

    .write_en_M                 (write_en1_M),
    .memreq_msg_len_modified_M  (memreq1_msg_len_modified_M),
    .block_offset_M             (block_offset1_M),
    .memreq_msg_data_modified_M (memreq1_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en1),
    .amo_grant                  (amo_grants[1])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port2
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq2_val),
    .memreq_rdy                 (memreq2_rdy),
    .memreq_msg                 (memreq2_msg),

    .memresp_val                (memresp2_val),
    .memresp_rdy                (memresp2_rdy),
    .memresp_msg                (memresp2_msg),

    .physical_block_addr_M      (physical_block_addr2_M),
    .read_block_M               (read_block2_M),

    .write_en_M                 (write_en2_M),
    .memreq_msg_len_modified_M  (memreq2_msg_len_modified_M),
    .block_offset_M             (block_offset2_M),
    .memreq_msg_data_modified_M (memreq2_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en2),
    .amo_grant                  (amo_grants[2])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port3
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq3_val),
    .memreq_rdy                 (memreq3_rdy),
    .memreq_msg                 (memreq3_msg),

    .memresp_val                (memresp3_val),
    .memresp_rdy                (memresp3_rdy),
    .memresp_msg                (memresp3_msg),

    .physical_block_addr_M      (physical_block_addr3_M),
    .read_block_M               (read_block3_M),

    .write_en_M                 (write_en3_M),
    .memreq_msg_len_modified_M  (memreq3_msg_len_modified_M),
    .block_offset_M             (block_offset3_M),
    .memreq_msg_data_modified_M (memreq3_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en3),
    .amo_grant                  (amo_grants[3])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port4
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq4_val),
    .memreq_rdy                 (memreq4_rdy),
    .memreq_msg                 (memreq4_msg),

    .memresp_val                (memresp4_val),
    .memresp_rdy                (memresp4_rdy),
    .memresp_msg                (memresp4_msg),

    .physical_block_addr_M      (physical_block_addr4_M),
    .read_block_M               (read_block4_M),

    .write_en_M                 (write_en4_M),
    .memreq_msg_len_modified_M  (memreq4_msg_len_modified_M),
    .block_offset_M             (block_offset4_M),
    .memreq_msg_data_modified_M (memreq4_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en4),
    .amo_grant                  (amo_grants[4])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port5
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq5_val),
    .memreq_rdy                 (memreq5_rdy),
    .memreq_msg                 (memreq5_msg),

    .memresp_val                (memresp5_val),
    .memresp_rdy                (memresp5_rdy),
    .memresp_msg                (memresp5_msg),

    .physical_block_addr_M      (physical_block_addr5_M),
    .read_block_M               (read_block5_M),

    .write_en_M                 (write_en5_M),
    .memreq_msg_len_modified_M  (memreq5_msg_len_modified_M),
    .block_offset_M             (block_offset5_M),
    .memreq_msg_data_modified_M (memreq5_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en5),
    .amo_grant                  (amo_grants[5])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port6
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq6_val),
    .memreq_rdy                 (memreq6_rdy),
    .memreq_msg                 (memreq6_msg),

    .memresp_val                (memresp6_val),
    .memresp_rdy                (memresp6_rdy),
    .memresp_msg                (memresp6_msg),

    .physical_block_addr_M      (physical_block_addr6_M),
    .read_block_M               (read_block6_M),

    .write_en_M                 (write_en6_M),
    .memreq_msg_len_modified_M  (memreq6_msg_len_modified_M),
    .block_offset_M             (block_offset6_M),
    .memreq_msg_data_modified_M (memreq6_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en6),
    .amo_grant                  (amo_grants[6])
  );

  //----------------------------------------------------------------------
  // PyParc Mem Interface Port
  //----------------------------------------------------------------------
  // TODO: this port is a different size than the rest, and I haven't
  //       figured out how to make it work correctly when instantiating
  //       a TestReqRespMemPort.  FIX, and remote all this!

  wire [c_req_pyifc_type_sz-1:0] memreq7_msg_type;
  wire [c_req_pyifc_addr_sz-1:0] memreq7_msg_addr;
  wire [c_req_pyifc_len_sz-1:0]  memreq7_msg_len;
  wire [c_req_pyifc_data_sz-1:0] memreq7_msg_data;
  vc_MemReqMsgFromBits#(p_addr_sz,32) memreq7_msg_from_bits
  (
    .bits (memreq7_msg),
    .type (memreq7_msg_type),
    .addr (memreq7_msg_addr),
    .len  (memreq7_msg_len),
    .data (memreq7_msg_data)
  );
  reg                           memreq7_val_M;
  reg [c_req_pyifc_type_sz-1:0] memreq7_msg_type_M;
  reg [c_req_pyifc_addr_sz-1:0] memreq7_msg_addr_M;
  reg [c_req_pyifc_len_sz-1:0]  memreq7_msg_len_M;
  reg [c_req_pyifc_data_sz-1:0] memreq7_msg_data_M;
  wire memreq7_go = memreq7_val && memreq7_rdy;

  always @( posedge clk ) begin
    // Ensure that the valid bit is reset appropriately
    if ( reset ) begin
      memreq7_val_M <= 1'b0;
    end else begin
      memreq7_val_M <= memreq7_go;
    end
    if ( memreq7_rdy ) begin
      memreq7_msg_type_M <= memreq7_msg_type;
      memreq7_msg_addr_M <= memreq7_msg_addr;
      memreq7_msg_len_M  <= memreq7_msg_len;
      memreq7_msg_data_M <= memreq7_msg_data;
    end
  end
  assign memreq7_msg_len_modified_M
    = ( memreq7_msg_len_M == 0 ) ? (c_req_pyifc_data_sz/8)
    :                              memreq7_msg_len_M;
  wire [c_physical_addr_sz-1:0] physical_byte_addr7_M
    = memreq7_msg_addr_M[c_physical_addr_sz-1:0];
  assign physical_block_addr7_M
    = physical_byte_addr7_M/c_data_byte_sz;
  assign block_offset7_M
    = physical_byte_addr7_M[c_block_offset_sz-1:0];
  //assign [p_data_sz-1:0] read_block7_M
  //  = m[physical_block_addr7_M];
  wire [c_resp_pyifc_data_sz-1:0] read_data7_M
    = read_block7_M >> (block_offset7_M*8);
  wire [c_req_pyifc_data_sz-1:0] memreq7_msg_data_amoadd_M
    = read_data7_M + memreq7_msg_data_M;
  wire [c_req_pyifc_data_sz-1:0] memreq7_msg_data_amoand_M
    = read_data7_M & memreq7_msg_data_M;
  wire [c_req_pyifc_data_sz-1:0] memreq7_msg_data_amoor_M
    = read_data7_M | memreq7_msg_data_M;
  localparam c_read   = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_write  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_REQ_MSG_TYPE_AMOXCH;
  assign memreq7_msg_data_modified_M
    = ( memreq7_msg_type_M == c_read   ) ? memreq7_msg_data_M
    : ( memreq7_msg_type_M == c_write  ) ? memreq7_msg_data_M
    : ( memreq7_msg_type_M == c_amoadd ) ? memreq7_msg_data_amoadd_M
    : ( memreq7_msg_type_M == c_amoand ) ? memreq7_msg_data_amoand_M
    : ( memreq7_msg_type_M == c_amoor  ) ? memreq7_msg_data_amoor_M
    : ( memreq7_msg_type_M == c_amoxch ) ? memreq7_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};
  assign write_en7_M = memreq7_val_M &&
                ( ( memreq7_msg_type_M == c_write  )
                ||( memreq7_msg_type_M == c_amoadd )
                ||( memreq7_msg_type_M == c_amoand )
                ||( memreq7_msg_type_M == c_amoor  )
                ||( memreq7_msg_type_M == c_amoxch ) );
  wire [c_resp_pyifc_type_sz-1:0] memresp7_msg_type_M = memreq7_msg_type_M;
  wire [c_resp_pyifc_len_sz-1:0]  memresp7_msg_len_M  = memreq7_msg_len_M;
  wire [c_resp_pyifc_data_sz-1:0] memresp7_msg_data_M = read_data7_M;
  wire [c_resp_pyifc_sz-1:0] memresp7_queue_msg;
  wire enq_memreq7_rdy;
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_pyifc_sz,32,5) memresp7_queue
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
  assign arb_amo_en7 = memreq7_val
                  && ( ( memreq7_msg_type == c_amoadd )
                    || ( memreq7_msg_type == c_amoand )
                    || ( memreq7_msg_type == c_amoor  )
                    || ( memreq7_msg_type == c_amoxch ) );
  assign memreq7_rdy = ( arb_amo_en7 ) ? amo_grants[7] && enq_memreq7_rdy : enq_memreq7_rdy;
  vc_MemRespMsgToBits#(32) memresp7_msg_to_bits
  (
    .type (memresp7_msg_type_M),
    .len  (memresp7_msg_len_M),
    .data (memresp7_msg_data_M),
    //.bits (memresp7_msg)
    .bits (memresp7_queue_msg)
  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq7_val,  "memreq7_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp7_rdy, "memresp7_rdy" );

  //----------------------------------------------------------------------
  // Write the data
  //----------------------------------------------------------------------

  integer wr0_i;
  integer wr1_i;
  integer wr2_i;
  integer wr3_i;
  integer wr4_i;
  integer wr5_i;
  integer wr6_i;
  integer wr7_i;

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
  end

  //----------------------------------------------------------------------
  // Atomic op grants arbiter
  //----------------------------------------------------------------------

  wire [7:0] amo_reqs = { arb_amo_en7, arb_amo_en6, arb_amo_en5, arb_amo_en4,
                          arb_amo_en3, arb_amo_en2, arb_amo_en1, arb_amo_en0 };
  vc_RoundRobinArb
  #(
    .NUM_REQS (8)
  )
  arb
  (
    .clk    (clk),
    .reset  (reset),
    .reqs   (amo_reqs),
    .grants (amo_grants)
  );

endmodule

`endif /* VC_TEST_OCTO_PORT_MEM_V */

