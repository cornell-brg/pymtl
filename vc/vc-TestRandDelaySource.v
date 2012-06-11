//========================================================================
// Test Source with Random Delays
//========================================================================

`ifndef VC_TEST_RAND_DELAY_SOURCE_V
`define VC_TEST_RAND_DELAY_SOURCE_V

`include "vc-TestSource.v"
`include "vc-TestRandDelay.v"

module vc_TestRandDelaySource
#(
  parameter p_msg_sz    = 1,    // size of message to store in source
  parameter p_mem_sz    = 1024, // size of memory that stores the messages
  parameter p_max_delay = 0     // max number of cycles to delay messages
)(
  input  clk,
  input  reset,

  // Source message interface

  output                val,
  input                 rdy,
  output [p_msg_sz-1:0] msg,

  // Goes high once all source data has been issued

  output done
);

  //----------------------------------------------------------------------
  // Test source
  //----------------------------------------------------------------------

  wire                src_val;
  wire                src_rdy;
  wire [p_msg_sz-1:0] src_msg;

  vc_TestSource#(p_msg_sz,p_mem_sz) src
  (
    .clk     (clk),
    .reset   (reset),

    .val     (src_val),
    .rdy     (src_rdy),
    .msg     (src_msg),

    .done    (done)
  );

  //----------------------------------------------------------------------
  // Test random delay
  //----------------------------------------------------------------------

  vc_TestRandDelay#(p_msg_sz,p_max_delay) rand_delay
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (src_val),
    .in_rdy  (src_rdy),
    .in_msg  (src_msg),

    .out_val (val),
    .out_rdy (rdy),
    .out_msg (msg)
  );

endmodule

`endif

