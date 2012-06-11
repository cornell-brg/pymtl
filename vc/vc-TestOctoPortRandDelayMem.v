//========================================================================
// Verilog Components: Test Memory with Random Delays
//========================================================================

`ifndef VC_TEST_OCTO_PORT_RAND_DELAY_MEM_V
`define VC_TEST_OCTO_PORT_RAND_DELAY_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-TestOctoPortMem.v"
`include "vc-TestRandDelay.v"

module vc_TestOctoPortRandDelayMem
#(
  parameter p_mem_sz    = 1024, // size of physical memory in bytes
  parameter p_addr_sz   = 8,    // size of mem message address in bits
  parameter p_data_sz   = 32,   // size of mem message data in bits
  parameter p_max_delay = 0,    // max number of cycles to delay messages

  // Local constants not meant to be set from outside the module
  parameter c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter c_req_pyifc_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,32),
  parameter c_resp_pyifc_sz = `VC_MEM_RESP_MSG_SZ(32)
)(
  input clk,
  input reset,

  // Memory request interface port 0

  input                      memreq0_val,
  output                     memreq0_rdy,
  input  [c_req_msg_sz-1:0]  memreq0_msg,

  // Memory response interface port 0

  output                     memresp0_val,
  input                      memresp0_rdy,
  output [c_resp_msg_sz-1:0] memresp0_msg,

  // Memory request interface port 1

  input                      memreq1_val,
  output                     memreq1_rdy,
  input  [c_req_msg_sz-1:0]  memreq1_msg,

  // Memory response interface port 1

  output                     memresp1_val,
  input                      memresp1_rdy,
  output [c_resp_msg_sz-1:0] memresp1_msg,

  // Memory request interface port 2

  input                      memreq2_val,
  output                     memreq2_rdy,
  input  [c_req_msg_sz-1:0]  memreq2_msg,

  // Memory response interface port 2

  output                     memresp2_val,
  input                      memresp2_rdy,
  output [c_resp_msg_sz-1:0] memresp2_msg,

  // Memory request interface port 3

  input                      memreq3_val,
  output                     memreq3_rdy,
  input  [c_req_msg_sz-1:0]  memreq3_msg,

  // Memory response interface port 3

  output                     memresp3_val,
  input                      memresp3_rdy,
  output [c_resp_msg_sz-1:0] memresp3_msg,

  // Memory request interface port 4

  input                      memreq4_val,
  output                     memreq4_rdy,
  input  [c_req_msg_sz-1:0]  memreq4_msg,

  // Memory response interface port 4

  output                     memresp4_val,
  input                      memresp4_rdy,
  output [c_resp_msg_sz-1:0] memresp4_msg,

  // Memory request interface port 5

  input                      memreq5_val,
  output                     memreq5_rdy,
  input  [c_req_msg_sz-1:0]  memreq5_msg,

  // Memory response interface port 5

  output                     memresp5_val,
  input                      memresp5_rdy,
  output [c_resp_msg_sz-1:0] memresp5_msg,

  // Memory request interface port 6

  input                      memreq6_val,
  output                     memreq6_rdy,
  input  [c_req_msg_sz-1:0]  memreq6_msg,

  // Memory response interface port 6

  output                     memresp6_val,
  input                      memresp6_rdy,
  output [c_resp_msg_sz-1:0] memresp6_msg,

  // Memory request interface port 7

  input                        memreq7_val,
  output                       memreq7_rdy,
  input  [c_req_pyifc_sz-1:0]  memreq7_msg,

  // Memory response interface port 7

  output                       memresp7_val,
  input                        memresp7_rdy,
  output [c_resp_pyifc_sz-1:0] memresp7_msg
);

  //------------------------------------------------------------------------
  // Single port test memory with random delay
  //------------------------------------------------------------------------

  wire                     mem_memresp0_val;
  wire                     mem_memresp0_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp0_msg;

  wire                     mem_memresp1_val;
  wire                     mem_memresp1_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp1_msg;

  wire                     mem_memresp2_val;
  wire                     mem_memresp2_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp2_msg;

  wire                     mem_memresp3_val;
  wire                     mem_memresp3_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp3_msg;

  wire                     mem_memresp4_val;
  wire                     mem_memresp4_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp4_msg;

  wire                     mem_memresp5_val;
  wire                     mem_memresp5_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp5_msg;

  wire                     mem_memresp6_val;
  wire                     mem_memresp6_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp6_msg;

  wire                       mem_memresp7_val;
  wire                       mem_memresp7_rdy;
  wire [c_resp_pyifc_sz-1:0] mem_memresp7_msg;

  vc_TestOctoPortMem#(p_mem_sz,p_addr_sz,p_data_sz) mem
  (
    .clk         (clk),
    .reset       (reset),

    .memreq0_val  (memreq0_val),
    .memreq0_rdy  (memreq0_rdy),
    .memreq0_msg  (memreq0_msg),

    .memresp0_val (mem_memresp0_val),
    .memresp0_rdy (mem_memresp0_rdy),
    .memresp0_msg (mem_memresp0_msg),

    .memreq1_val  (memreq1_val),
    .memreq1_rdy  (memreq1_rdy),
    .memreq1_msg  (memreq1_msg),

    .memresp1_val (mem_memresp1_val),
    .memresp1_rdy (mem_memresp1_rdy),
    .memresp1_msg (mem_memresp1_msg),

    .memreq2_val  (memreq2_val),
    .memreq2_rdy  (memreq2_rdy),
    .memreq2_msg  (memreq2_msg),

    .memresp2_val (mem_memresp2_val),
    .memresp2_rdy (mem_memresp2_rdy),
    .memresp2_msg (mem_memresp2_msg),

    .memreq3_val  (memreq3_val),
    .memreq3_rdy  (memreq3_rdy),
    .memreq3_msg  (memreq3_msg),

    .memresp3_val (mem_memresp3_val),
    .memresp3_rdy (mem_memresp3_rdy),
    .memresp3_msg (mem_memresp3_msg),

    .memreq4_val  (memreq4_val),
    .memreq4_rdy  (memreq4_rdy),
    .memreq4_msg  (memreq4_msg),

    .memresp4_val (mem_memresp4_val),
    .memresp4_rdy (mem_memresp4_rdy),
    .memresp4_msg (mem_memresp4_msg),

    .memreq5_val  (memreq5_val),
    .memreq5_rdy  (memreq5_rdy),
    .memreq5_msg  (memreq5_msg),

    .memresp5_val (mem_memresp5_val),
    .memresp5_rdy (mem_memresp5_rdy),
    .memresp5_msg (mem_memresp5_msg),

    .memreq6_val  (memreq6_val),
    .memreq6_rdy  (memreq6_rdy),
    .memreq6_msg  (memreq6_msg),

    .memresp6_val (mem_memresp6_val),
    .memresp6_rdy (mem_memresp6_rdy),
    .memresp6_msg (mem_memresp6_msg),

    .memreq7_val  (memreq7_val),
    .memreq7_rdy  (memreq7_rdy),
    .memreq7_msg  (memreq7_msg),

    .memresp7_val (mem_memresp7_val),
    .memresp7_rdy (mem_memresp7_rdy),
    .memresp7_msg (mem_memresp7_msg)
  );

  //------------------------------------------------------------------------
  // Test random delay
  //------------------------------------------------------------------------

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay0
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp0_val),
    .in_rdy  (mem_memresp0_rdy),
    .in_msg  (mem_memresp0_msg),

    .out_val (memresp0_val),
    .out_rdy (memresp0_rdy),
    .out_msg (memresp0_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay1
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp1_val),
    .in_rdy  (mem_memresp1_rdy),
    .in_msg  (mem_memresp1_msg),

    .out_val (memresp1_val),
    .out_rdy (memresp1_rdy),
    .out_msg (memresp1_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay2
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp2_val),
    .in_rdy  (mem_memresp2_rdy),
    .in_msg  (mem_memresp2_msg),

    .out_val (memresp2_val),
    .out_rdy (memresp2_rdy),
    .out_msg (memresp2_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay3
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp3_val),
    .in_rdy  (mem_memresp3_rdy),
    .in_msg  (mem_memresp3_msg),

    .out_val (memresp3_val),
    .out_rdy (memresp3_rdy),
    .out_msg (memresp3_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay4
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp4_val),
    .in_rdy  (mem_memresp4_rdy),
    .in_msg  (mem_memresp4_msg),

    .out_val (memresp4_val),
    .out_rdy (memresp4_rdy),
    .out_msg (memresp4_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay5
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp5_val),
    .in_rdy  (mem_memresp5_rdy),
    .in_msg  (mem_memresp5_msg),

    .out_val (memresp5_val),
    .out_rdy (memresp5_rdy),
    .out_msg (memresp5_msg)
  );

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay6
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp6_val),
    .in_rdy  (mem_memresp6_rdy),
    .in_msg  (mem_memresp6_msg),

    .out_val (memresp6_val),
    .out_rdy (memresp6_rdy),
    .out_msg (memresp6_msg)
  );

  vc_TestRandDelay#(c_resp_pyifc_sz,p_max_delay) rand_delay7
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp7_val),
    .in_rdy  (mem_memresp7_rdy),
    .in_msg  (mem_memresp7_msg),

    .out_val (memresp7_val),
    .out_rdy (memresp7_rdy),
    .out_msg (memresp7_msg)
  );

endmodule

`endif /* VC_TEST_OCTO_PORT_RAND_DELAY_MEM_V */

