//========================================================================
// Verilog Components: Test Memory with Random Delays
//========================================================================
// This is dual ported test memory with random delay that can handle
// arbitrary memory request messages and returns memory response
// messages.

`ifndef VC_TEST_DUAL_PORT_RAND_DELAY_MEM_V
`define VC_TEST_DUAL_PORT_RAND_DELAY_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-TestDualPortMem.v"
`include "vc-TestRandDelay.v"

module vc_TestDualPortRandDelayMem
#(
  parameter p_mem_sz    = 1024, // size of physical memory in bytes
  parameter p_addr_sz   = 8,    // size of mem message address in bits
  parameter p_data_sz   = 32,   // size of mem message data in bits
  parameter p_max_delay = 0,    // max number of cycles to delay messages

  // Local constants not meant to be set from outside the module
  parameter c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz)
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
  output [c_resp_msg_sz-1:0] memresp1_msg
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

  vc_TestDualPortMem#(p_mem_sz,p_addr_sz,p_data_sz) mem
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
    .memresp1_msg (mem_memresp1_msg)
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

endmodule

`endif /* VC_TEST_DUAL_PORT_RAND_DELAY_MEM_V */

