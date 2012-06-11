//========================================================================
// Verilog Components: Test Memory with Random Delays
//========================================================================
// This is single ported test memory with random delay that can handle
// arbitrary memory request messages and returns memory response
// messages.

`ifndef VC_TEST_SINGLE_PORT_RAND_DELAY_MEM_V
`define VC_TEST_SINGLE_PORT_RAND_DELAY_MEM_V

`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-TestSinglePortMem.v"
`include "vc-TestRandDelay.v"

module vc_TestSinglePortRandDelayMem
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

  // Memory request interface

  input                      memreq_val,
  output                     memreq_rdy,
  input  [c_req_msg_sz-1:0]  memreq_msg,

  // Memory response interface

  output                     memresp_val,
  input                      memresp_rdy,
  output [c_resp_msg_sz-1:0] memresp_msg
);

  //------------------------------------------------------------------------
  // Single port test memory with random delay
  //------------------------------------------------------------------------

  wire                     mem_memresp_val;
  wire                     mem_memresp_rdy;
  wire [c_resp_msg_sz-1:0] mem_memresp_msg;

  vc_TestSinglePortMem#(p_mem_sz,p_addr_sz,p_data_sz) mem
  (
    .clk         (clk),
    .reset       (reset),

    .memreq_val  (memreq_val),
    .memreq_rdy  (memreq_rdy),
    .memreq_msg  (memreq_msg),

    .memresp_val (mem_memresp_val),
    .memresp_rdy (mem_memresp_rdy),
    .memresp_msg (mem_memresp_msg)
  );

  //------------------------------------------------------------------------
  // Test random delay
  //------------------------------------------------------------------------

  vc_TestRandDelay#(c_resp_msg_sz,p_max_delay) rand_delay
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (mem_memresp_val),
    .in_rdy  (mem_memresp_rdy),
    .in_msg  (mem_memresp_msg),

    .out_val (memresp_val),
    .out_rdy (memresp_rdy),
    .out_msg (memresp_msg)
  );

endmodule

`endif /* VC_TEST_SINGLE_PORT_RAND_DELAY_MEM_V */

