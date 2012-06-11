//========================================================================
// Verilog Components: Test Memory
//========================================================================

`ifndef VC_TEST_ICOSA_PORT_MEM_V
`define VC_TEST_ICOSA_PORT_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Assert.v"
`include "vc-Queues.v"
`include "vc-TestMemReqRespPort.v"

`include "vc-Arbiters.v"

//------------------------------------------------------------------------
// Quad port test memory
//------------------------------------------------------------------------

module vc_TestIcosaPortMem
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
  input                      memreq7_val,
  output                     memreq7_rdy,
  input  [c_req_msg_sz-1:0]  memreq7_msg,
  input                      memreq8_val,
  output                     memreq8_rdy,
  input  [c_req_msg_sz-1:0]  memreq8_msg,
  input                      memreq9_val,
  output                     memreq9_rdy,
  input  [c_req_msg_sz-1:0]  memreq9_msg,
  input                      memreq10_val,
  output                     memreq10_rdy,
  input  [c_req_msg_sz-1:0]  memreq10_msg,
  input                      memreq11_val,
  output                     memreq11_rdy,
  input  [c_req_msg_sz-1:0]  memreq11_msg,
  input                      memreq12_val,
  output                     memreq12_rdy,
  input  [c_req_msg_sz-1:0]  memreq12_msg,
  input                      memreq13_val,
  output                     memreq13_rdy,
  input  [c_req_msg_sz-1:0]  memreq13_msg,
  input                      memreq14_val,
  output                     memreq14_rdy,
  input  [c_req_msg_sz-1:0]  memreq14_msg,
  input                      memreq15_val,
  output                     memreq15_rdy,
  input  [c_req_msg_sz-1:0]  memreq15_msg,
  input                      memreq16_val,
  output                     memreq16_rdy,
  input  [c_req_msg_sz-1:0]  memreq16_msg,
  input                      memreq17_val,
  output                     memreq17_rdy,
  input  [c_req_msg_sz-1:0]  memreq17_msg,
  input                      memreq18_val,
  output                     memreq18_rdy,
  input  [c_req_msg_sz-1:0]  memreq18_msg,
  // Specially sized port
  input                        memreq19_val,
  output                       memreq19_rdy,
  input  [c_req_pyifc_sz-1:0]  memreq19_msg,


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
  output                     memresp7_val,
  input                      memresp7_rdy,
  output [c_resp_msg_sz-1:0] memresp7_msg,
  output                     memresp8_val,
  input                      memresp8_rdy,
  output [c_resp_msg_sz-1:0] memresp8_msg,
  output                     memresp9_val,
  input                      memresp9_rdy,
  output [c_resp_msg_sz-1:0] memresp9_msg,
  output                     memresp10_val,
  input                      memresp10_rdy,
  output [c_resp_msg_sz-1:0] memresp10_msg,
  output                     memresp11_val,
  input                      memresp11_rdy,
  output [c_resp_msg_sz-1:0] memresp11_msg,
  output                     memresp12_val,
  input                      memresp12_rdy,
  output [c_resp_msg_sz-1:0] memresp12_msg,
  output                     memresp13_val,
  input                      memresp13_rdy,
  output [c_resp_msg_sz-1:0] memresp13_msg,
  output                     memresp14_val,
  input                      memresp14_rdy,
  output [c_resp_msg_sz-1:0] memresp14_msg,
  output                     memresp15_val,
  input                      memresp15_rdy,
  output [c_resp_msg_sz-1:0] memresp15_msg,
  output                     memresp16_val,
  input                      memresp16_rdy,
  output [c_resp_msg_sz-1:0] memresp16_msg,
  output                     memresp17_val,
  input                      memresp17_rdy,
  output [c_resp_msg_sz-1:0] memresp17_msg,
  output                     memresp18_val,
  input                      memresp18_rdy,
  output [c_resp_msg_sz-1:0] memresp18_msg,
  // Specially sized port
  output                       memresp19_val,
  input                        memresp19_rdy,
  output [c_resp_pyifc_sz-1:0] memresp19_msg

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
  wire [c_req_msg_len_sz:0]           memreq7_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset7_M;
  wire [c_req_msg_data_sz-1:0]        memreq7_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr8_M;
  wire                                write_en8_M;
  wire [c_req_msg_len_sz:0]           memreq8_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset8_M;
  wire [c_req_msg_data_sz-1:0]        memreq8_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr9_M;
  wire                                write_en9_M;
  wire [c_req_msg_len_sz:0]           memreq9_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset9_M;
  wire [c_req_msg_data_sz-1:0]        memreq9_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr10_M;
  wire                                write_en10_M;
  wire [c_req_msg_len_sz:0]           memreq10_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset10_M;
  wire [c_req_msg_data_sz-1:0]        memreq10_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr11_M;
  wire                                write_en11_M;
  wire [c_req_msg_len_sz:0]           memreq11_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset11_M;
  wire [c_req_msg_data_sz-1:0]        memreq11_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr12_M;
  wire                                write_en12_M;
  wire [c_req_msg_len_sz:0]           memreq12_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset12_M;
  wire [c_req_msg_data_sz-1:0]        memreq12_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr13_M;
  wire                                write_en13_M;
  wire [c_req_msg_len_sz:0]           memreq13_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset13_M;
  wire [c_req_msg_data_sz-1:0]        memreq13_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr14_M;
  wire                                write_en14_M;
  wire [c_req_msg_len_sz:0]           memreq14_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset14_M;
  wire [c_req_msg_data_sz-1:0]        memreq14_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr15_M;
  wire                                write_en15_M;
  wire [c_req_msg_len_sz:0]           memreq15_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset15_M;
  wire [c_req_msg_data_sz-1:0]        memreq15_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr16_M;
  wire                                write_en16_M;
  wire [c_req_msg_len_sz:0]           memreq16_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset16_M;
  wire [c_req_msg_data_sz-1:0]        memreq16_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr17_M;
  wire                                write_en17_M;
  wire [c_req_msg_len_sz:0]           memreq17_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset17_M;
  wire [c_req_msg_data_sz-1:0]        memreq17_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr18_M;
  wire                                write_en18_M;
  wire [c_req_msg_len_sz:0]           memreq18_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset18_M;
  wire [c_req_msg_data_sz-1:0]        memreq18_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr19_M;
  wire                                write_en19_M;
  wire [c_req_pyifc_len_sz:0]         memreq19_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset19_M;
  wire [c_req_pyifc_data_sz-1:0]      memreq19_msg_data_modified_M;


  wire arb_amo_en0;
  wire arb_amo_en1;
  wire arb_amo_en2;
  wire arb_amo_en3;
  wire arb_amo_en4;
  wire arb_amo_en5;
  wire arb_amo_en6;
  wire arb_amo_en7;
  wire arb_amo_en8;
  wire arb_amo_en9;
  wire arb_amo_en10;
  wire arb_amo_en11;
  wire arb_amo_en12;
  wire arb_amo_en13;
  wire arb_amo_en14;
  wire arb_amo_en15;
  wire arb_amo_en16;
  wire arb_amo_en17;
  wire arb_amo_en18;
  wire arb_amo_en19;
  wire [19:0] amo_grants;

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

  wire [p_data_sz-1:0] read_block8_M
    = m[physical_block_addr8_M];

  wire [p_data_sz-1:0] read_block9_M
    = m[physical_block_addr9_M];

  wire [p_data_sz-1:0] read_block10_M
    = m[physical_block_addr10_M];

  wire [p_data_sz-1:0] read_block11_M
    = m[physical_block_addr11_M];

  wire [p_data_sz-1:0] read_block12_M
    = m[physical_block_addr12_M];

  wire [p_data_sz-1:0] read_block13_M
    = m[physical_block_addr13_M];

  wire [p_data_sz-1:0] read_block14_M
    = m[physical_block_addr14_M];

  wire [p_data_sz-1:0] read_block15_M
    = m[physical_block_addr15_M];

  wire [p_data_sz-1:0] read_block16_M
    = m[physical_block_addr16_M];

  wire [p_data_sz-1:0] read_block17_M
    = m[physical_block_addr17_M];

  wire [p_data_sz-1:0] read_block18_M
    = m[physical_block_addr18_M];

  wire [p_data_sz-1:0] read_block19_M
    = m[physical_block_addr19_M];

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
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port7
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq7_val),
    .memreq_rdy                 (memreq7_rdy),
    .memreq_msg                 (memreq7_msg),

    .memresp_val                (memresp7_val),
    .memresp_rdy                (memresp7_rdy),
    .memresp_msg                (memresp7_msg),

    .physical_block_addr_M      (physical_block_addr7_M),
    .read_block_M               (read_block7_M),

    .write_en_M                 (write_en7_M),
    .memreq_msg_len_modified_M  (memreq7_msg_len_modified_M),
    .block_offset_M             (block_offset7_M),
    .memreq_msg_data_modified_M (memreq7_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en7),
    .amo_grant                  (amo_grants[7])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port8
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq8_val),
    .memreq_rdy                 (memreq8_rdy),
    .memreq_msg                 (memreq8_msg),

    .memresp_val                (memresp8_val),
    .memresp_rdy                (memresp8_rdy),
    .memresp_msg                (memresp8_msg),

    .physical_block_addr_M      (physical_block_addr8_M),
    .read_block_M               (read_block8_M),

    .write_en_M                 (write_en8_M),
    .memreq_msg_len_modified_M  (memreq8_msg_len_modified_M),
    .block_offset_M             (block_offset8_M),
    .memreq_msg_data_modified_M (memreq8_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en8),
    .amo_grant                  (amo_grants[8])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port9
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq9_val),
    .memreq_rdy                 (memreq9_rdy),
    .memreq_msg                 (memreq9_msg),

    .memresp_val                (memresp9_val),
    .memresp_rdy                (memresp9_rdy),
    .memresp_msg                (memresp9_msg),

    .physical_block_addr_M      (physical_block_addr9_M),
    .read_block_M               (read_block9_M),

    .write_en_M                 (write_en9_M),
    .memreq_msg_len_modified_M  (memreq9_msg_len_modified_M),
    .block_offset_M             (block_offset9_M),
    .memreq_msg_data_modified_M (memreq9_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en9),
    .amo_grant                  (amo_grants[9])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port10
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq10_val),
    .memreq_rdy                 (memreq10_rdy),
    .memreq_msg                 (memreq10_msg),

    .memresp_val                (memresp10_val),
    .memresp_rdy                (memresp10_rdy),
    .memresp_msg                (memresp10_msg),

    .physical_block_addr_M      (physical_block_addr10_M),
    .read_block_M               (read_block10_M),

    .write_en_M                 (write_en10_M),
    .memreq_msg_len_modified_M  (memreq10_msg_len_modified_M),
    .block_offset_M             (block_offset10_M),
    .memreq_msg_data_modified_M (memreq10_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en10),
    .amo_grant                  (amo_grants[10])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port11
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq11_val),
    .memreq_rdy                 (memreq11_rdy),
    .memreq_msg                 (memreq11_msg),

    .memresp_val                (memresp11_val),
    .memresp_rdy                (memresp11_rdy),
    .memresp_msg                (memresp11_msg),

    .physical_block_addr_M      (physical_block_addr11_M),
    .read_block_M               (read_block11_M),

    .write_en_M                 (write_en11_M),
    .memreq_msg_len_modified_M  (memreq11_msg_len_modified_M),
    .block_offset_M             (block_offset11_M),
    .memreq_msg_data_modified_M (memreq11_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en11),
    .amo_grant                  (amo_grants[11])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port12
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq12_val),
    .memreq_rdy                 (memreq12_rdy),
    .memreq_msg                 (memreq12_msg),

    .memresp_val                (memresp12_val),
    .memresp_rdy                (memresp12_rdy),
    .memresp_msg                (memresp12_msg),

    .physical_block_addr_M      (physical_block_addr12_M),
    .read_block_M               (read_block12_M),

    .write_en_M                 (write_en12_M),
    .memreq_msg_len_modified_M  (memreq12_msg_len_modified_M),
    .block_offset_M             (block_offset12_M),
    .memreq_msg_data_modified_M (memreq12_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en12),
    .amo_grant                  (amo_grants[12])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port13
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq13_val),
    .memreq_rdy                 (memreq13_rdy),
    .memreq_msg                 (memreq13_msg),

    .memresp_val                (memresp13_val),
    .memresp_rdy                (memresp13_rdy),
    .memresp_msg                (memresp13_msg),

    .physical_block_addr_M      (physical_block_addr13_M),
    .read_block_M               (read_block13_M),

    .write_en_M                 (write_en13_M),
    .memreq_msg_len_modified_M  (memreq13_msg_len_modified_M),
    .block_offset_M             (block_offset13_M),
    .memreq_msg_data_modified_M (memreq13_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en13),
    .amo_grant                  (amo_grants[13])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port14
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq14_val),
    .memreq_rdy                 (memreq14_rdy),
    .memreq_msg                 (memreq14_msg),

    .memresp_val                (memresp14_val),
    .memresp_rdy                (memresp14_rdy),
    .memresp_msg                (memresp14_msg),

    .physical_block_addr_M      (physical_block_addr14_M),
    .read_block_M               (read_block14_M),

    .write_en_M                 (write_en14_M),
    .memreq_msg_len_modified_M  (memreq14_msg_len_modified_M),
    .block_offset_M             (block_offset14_M),
    .memreq_msg_data_modified_M (memreq14_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en14),
    .amo_grant                  (amo_grants[14])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port15
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq15_val),
    .memreq_rdy                 (memreq15_rdy),
    .memreq_msg                 (memreq15_msg),

    .memresp_val                (memresp15_val),
    .memresp_rdy                (memresp15_rdy),
    .memresp_msg                (memresp15_msg),

    .physical_block_addr_M      (physical_block_addr15_M),
    .read_block_M               (read_block15_M),

    .write_en_M                 (write_en15_M),
    .memreq_msg_len_modified_M  (memreq15_msg_len_modified_M),
    .block_offset_M             (block_offset15_M),
    .memreq_msg_data_modified_M (memreq15_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en15),
    .amo_grant                  (amo_grants[15])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port16
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq16_val),
    .memreq_rdy                 (memreq16_rdy),
    .memreq_msg                 (memreq16_msg),

    .memresp_val                (memresp16_val),
    .memresp_rdy                (memresp16_rdy),
    .memresp_msg                (memresp16_msg),

    .physical_block_addr_M      (physical_block_addr16_M),
    .read_block_M               (read_block16_M),

    .write_en_M                 (write_en16_M),
    .memreq_msg_len_modified_M  (memreq16_msg_len_modified_M),
    .block_offset_M             (block_offset16_M),
    .memreq_msg_data_modified_M (memreq16_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en16),
    .amo_grant                  (amo_grants[16])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port17
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq17_val),
    .memreq_rdy                 (memreq17_rdy),
    .memreq_msg                 (memreq17_msg),

    .memresp_val                (memresp17_val),
    .memresp_rdy                (memresp17_rdy),
    .memresp_msg                (memresp17_msg),

    .physical_block_addr_M      (physical_block_addr17_M),
    .read_block_M               (read_block17_M),

    .write_en_M                 (write_en17_M),
    .memreq_msg_len_modified_M  (memreq17_msg_len_modified_M),
    .block_offset_M             (block_offset17_M),
    .memreq_msg_data_modified_M (memreq17_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en17),
    .amo_grant                  (amo_grants[17])
  );
  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port18
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq18_val),
    .memreq_rdy                 (memreq18_rdy),
    .memreq_msg                 (memreq18_msg),

    .memresp_val                (memresp18_val),
    .memresp_rdy                (memresp18_rdy),
    .memresp_msg                (memresp18_msg),

    .physical_block_addr_M      (physical_block_addr18_M),
    .read_block_M               (read_block18_M),

    .write_en_M                 (write_en18_M),
    .memreq_msg_len_modified_M  (memreq18_msg_len_modified_M),
    .block_offset_M             (block_offset18_M),
    .memreq_msg_data_modified_M (memreq18_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en18),
    .amo_grant                  (amo_grants[18])
  );

  //----------------------------------------------------------------------
  // PyParc Mem Interface Port
  //----------------------------------------------------------------------
  // TODO: this port is a different size than the rest, and I haven't
  //       figured out how to make it work correctly when instantiating
  //       a TestReqRespMemPort.  FIX, and remote all this!

  wire [c_req_pyifc_type_sz-1:0] memreq19_msg_type;
  wire [c_req_pyifc_addr_sz-1:0] memreq19_msg_addr;
  wire [c_req_pyifc_len_sz-1:0]  memreq19_msg_len;
  wire [c_req_pyifc_data_sz-1:0] memreq19_msg_data;
  vc_MemReqMsgFromBits#(p_addr_sz,32) memreq19_msg_from_bits
  (
    .bits (memreq19_msg),
    .type (memreq19_msg_type),
    .addr (memreq19_msg_addr),
    .len  (memreq19_msg_len),
    .data (memreq19_msg_data)
  );
  reg                           memreq19_val_M;
  reg [c_req_pyifc_type_sz-1:0] memreq19_msg_type_M;
  reg [c_req_pyifc_addr_sz-1:0] memreq19_msg_addr_M;
  reg [c_req_pyifc_len_sz-1:0]  memreq19_msg_len_M;
  reg [c_req_pyifc_data_sz-1:0] memreq19_msg_data_M;
  wire memreq19_go = memreq19_val && memreq19_rdy;

  always @( posedge clk ) begin
    // Ensure that the valid bit is reset appropriately
    if ( reset ) begin
      memreq19_val_M <= 1'b0;
    end else begin
      memreq19_val_M <= memreq19_go;
    end
    if ( memreq19_rdy ) begin
      memreq19_msg_type_M <= memreq19_msg_type;
      memreq19_msg_addr_M <= memreq19_msg_addr;
      memreq19_msg_len_M  <= memreq19_msg_len;
      memreq19_msg_data_M <= memreq19_msg_data;
    end
  end
  assign memreq19_msg_len_modified_M
    = ( memreq19_msg_len_M == 0 ) ? (c_req_pyifc_data_sz/8)
    :                              memreq19_msg_len_M;
  wire [c_physical_addr_sz-1:0] physical_byte_addr19_M
    = memreq19_msg_addr_M[c_physical_addr_sz-1:0];
  assign physical_block_addr19_M
    = physical_byte_addr19_M/c_data_byte_sz;
  assign block_offset19_M
    = physical_byte_addr19_M[c_block_offset_sz-1:0];
  //assign [p_data_sz-1:0] read_block19_M
  //  = m[physical_block_addr19_M];
  wire [c_resp_pyifc_data_sz-1:0] read_data19_M
    = read_block19_M >> (block_offset19_M*8);
  wire [c_req_pyifc_data_sz-1:0] memreq19_msg_data_amoadd_M
    = read_data19_M + memreq19_msg_data_M;
  wire [c_req_pyifc_data_sz-1:0] memreq19_msg_data_amoand_M
    = read_data19_M & memreq19_msg_data_M;
  wire [c_req_pyifc_data_sz-1:0] memreq19_msg_data_amoor_M
    = read_data19_M | memreq19_msg_data_M;
  localparam c_read   = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_write  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_REQ_MSG_TYPE_AMOXCH;
  assign memreq19_msg_data_modified_M
    = ( memreq19_msg_type_M == c_read   ) ? memreq19_msg_data_M
    : ( memreq19_msg_type_M == c_write  ) ? memreq19_msg_data_M
    : ( memreq19_msg_type_M == c_amoadd ) ? memreq19_msg_data_amoadd_M
    : ( memreq19_msg_type_M == c_amoand ) ? memreq19_msg_data_amoand_M
    : ( memreq19_msg_type_M == c_amoor  ) ? memreq19_msg_data_amoor_M
    : ( memreq19_msg_type_M == c_amoxch ) ? memreq19_msg_data_M
    :                                      {c_req_msg_data_sz{1'b0}};
  assign write_en19_M = memreq19_val_M &&
                ( ( memreq19_msg_type_M == c_write  )
                ||( memreq19_msg_type_M == c_amoadd )
                ||( memreq19_msg_type_M == c_amoand )
                ||( memreq19_msg_type_M == c_amoor  )
                ||( memreq19_msg_type_M == c_amoxch ) );
  wire [c_resp_pyifc_type_sz-1:0] memresp19_msg_type_M = memreq19_msg_type_M;
  wire [c_resp_pyifc_len_sz-1:0]  memresp19_msg_len_M  = memreq19_msg_len_M;
  wire [c_resp_pyifc_data_sz-1:0] memresp19_msg_data_M = read_data19_M;
  wire [c_resp_pyifc_sz-1:0] memresp19_queue_msg;
  wire enq_memreq19_rdy;
  vc_Queue_pf#(`VC_QUEUE_BYPASS,c_resp_pyifc_sz,32,5) memresp19_queue
  (
    .clk      (clk),
    .reset    (reset),
    .enq_bits (memresp19_queue_msg), // Wire up to MsgToBits output
    .enq_val  (memreq19_val_M),      // Wire up to req_val output
    .enq_rdy  (enq_memreq19_rdy),

    // Wire up deq to the resp output ports

    .deq_bits (memresp19_msg),
    .deq_val  (memresp19_val),
    .deq_rdy  (memresp19_rdy)
  );
  assign arb_amo_en19 = memreq19_val
                  && ( ( memreq19_msg_type == c_amoadd )
                    || ( memreq19_msg_type == c_amoand )
                    || ( memreq19_msg_type == c_amoor  )
                    || ( memreq19_msg_type == c_amoxch ) );
  assign memreq19_rdy = ( arb_amo_en19 ) ? amo_grants[19] && enq_memreq19_rdy : enq_memreq19_rdy;
  vc_MemRespMsgToBits#(32) memresp19_msg_to_bits
  (
    .type (memresp19_msg_type_M),
    .len  (memresp19_msg_len_M),
    .data (memresp19_msg_data_M),
    //.bits (memresp19_msg)
    .bits (memresp19_queue_msg)
  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memreq19_val,  "memreq19_val"  );
  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, memresp19_rdy, "memresp19_rdy" );

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
  integer wr8_i;
  integer wr9_i;
  integer wr10_i;
  integer wr11_i;
  integer wr12_i;
  integer wr13_i;
  integer wr14_i;
  integer wr15_i;
  integer wr16_i;
  integer wr17_i;
  integer wr18_i;
  integer wr19_i;

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
    if ( write_en10_M ) begin
      for ( wr10_i = 0; wr10_i < memreq10_msg_len_modified_M; wr10_i = wr10_i + 1 ) begin
        m[physical_block_addr10_M][ (block_offset10_M*8) + (wr10_i*8) +: 8 ] <= memreq10_msg_data_modified_M[ (wr10_i*8) +: 8 ];
      end
    end
    if ( write_en11_M ) begin
      for ( wr11_i = 0; wr11_i < memreq11_msg_len_modified_M; wr11_i = wr11_i + 1 ) begin
        m[physical_block_addr11_M][ (block_offset11_M*8) + (wr11_i*8) +: 8 ] <= memreq11_msg_data_modified_M[ (wr11_i*8) +: 8 ];
      end
    end
    if ( write_en12_M ) begin
      for ( wr12_i = 0; wr12_i < memreq12_msg_len_modified_M; wr12_i = wr12_i + 1 ) begin
        m[physical_block_addr12_M][ (block_offset12_M*8) + (wr12_i*8) +: 8 ] <= memreq12_msg_data_modified_M[ (wr12_i*8) +: 8 ];
      end
    end
    if ( write_en13_M ) begin
      for ( wr13_i = 0; wr13_i < memreq13_msg_len_modified_M; wr13_i = wr13_i + 1 ) begin
        m[physical_block_addr13_M][ (block_offset13_M*8) + (wr13_i*8) +: 8 ] <= memreq13_msg_data_modified_M[ (wr13_i*8) +: 8 ];
      end
    end
    if ( write_en14_M ) begin
      for ( wr14_i = 0; wr14_i < memreq14_msg_len_modified_M; wr14_i = wr14_i + 1 ) begin
        m[physical_block_addr14_M][ (block_offset14_M*8) + (wr14_i*8) +: 8 ] <= memreq14_msg_data_modified_M[ (wr14_i*8) +: 8 ];
      end
    end
    if ( write_en15_M ) begin
      for ( wr15_i = 0; wr15_i < memreq15_msg_len_modified_M; wr15_i = wr15_i + 1 ) begin
        m[physical_block_addr15_M][ (block_offset15_M*8) + (wr15_i*8) +: 8 ] <= memreq15_msg_data_modified_M[ (wr15_i*8) +: 8 ];
      end
    end
    if ( write_en16_M ) begin
      for ( wr16_i = 0; wr16_i < memreq16_msg_len_modified_M; wr16_i = wr16_i + 1 ) begin
        m[physical_block_addr16_M][ (block_offset16_M*8) + (wr16_i*8) +: 8 ] <= memreq16_msg_data_modified_M[ (wr16_i*8) +: 8 ];
      end
    end
    if ( write_en17_M ) begin
      for ( wr17_i = 0; wr17_i < memreq17_msg_len_modified_M; wr17_i = wr17_i + 1 ) begin
        m[physical_block_addr17_M][ (block_offset17_M*8) + (wr17_i*8) +: 8 ] <= memreq17_msg_data_modified_M[ (wr17_i*8) +: 8 ];
      end
    end
    if ( write_en18_M ) begin
      for ( wr18_i = 0; wr18_i < memreq18_msg_len_modified_M; wr18_i = wr18_i + 1 ) begin
        m[physical_block_addr18_M][ (block_offset18_M*8) + (wr18_i*8) +: 8 ] <= memreq18_msg_data_modified_M[ (wr18_i*8) +: 8 ];
      end
    end
    if ( write_en19_M ) begin
      for ( wr19_i = 0; wr19_i < memreq19_msg_len_modified_M; wr19_i = wr19_i + 1 ) begin
        m[physical_block_addr19_M][ (block_offset19_M*8) + (wr19_i*8) +: 8 ] <= memreq19_msg_data_modified_M[ (wr19_i*8) +: 8 ];
      end
    end
  end

  //----------------------------------------------------------------------
  // Atomic op grants arbiter
  //----------------------------------------------------------------------

  wire [19:0] amo_reqs = {
                          arb_amo_en19, arb_amo_en18,
                          arb_amo_en17, arb_amo_en16, arb_amo_en15, arb_amo_en14,
                          arb_amo_en13, arb_amo_en12, arb_amo_en11, arb_amo_en10,
                          arb_amo_en9, arb_amo_en8,
                          arb_amo_en7, arb_amo_en6, arb_amo_en5, arb_amo_en4,
                          arb_amo_en3, arb_amo_en2, arb_amo_en1, arb_amo_en0
                         };
  vc_RoundRobinArb
  #(
    .NUM_REQS (20)
  )
  arb
  (
    .clk    (clk),
    .reset  (reset),
    .reqs   (amo_reqs),
    .grants (amo_grants)
  );

endmodule

`endif /* VC_TEST_ICOSA_PORT_MEM_V */

