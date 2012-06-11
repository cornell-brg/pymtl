//========================================================================
// Test Sink with Random Delays
//========================================================================

`ifndef VC_TEST_RAND_DELAY_SINK_V
`define VC_TEST_RAND_DELAY_SINK_V

`include "vc-TestSink.v"
`include "vc-TestRandDelay.v"

module vc_TestRandDelaySink
#(
  parameter p_msg_sz    = 1,    // size of message to store in sink
  parameter p_mem_sz    = 1024, // size of memory that stores the messages
  parameter p_max_delay = 0     // max number of cycles to delay messages
)(
  input  clk,
  input  reset,

  // Sink message interface

  input                 val,
  output                rdy,
  input  [p_msg_sz-1:0] msg,

  // Goes high once all sink data has been received

  output done
);

  //----------------------------------------------------------------------
  // Test random delay
  //----------------------------------------------------------------------

  wire                sink_val;
  wire                sink_rdy;
  wire [p_msg_sz-1:0] sink_msg;

  vc_TestRandDelay#(p_msg_sz,p_max_delay) rand_delay
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (val),
    .in_rdy  (rdy),
    .in_msg  (msg),

    .out_val (sink_val),
    .out_rdy (sink_rdy),
    .out_msg (sink_msg)
  );

  //----------------------------------------------------------------------
  // Test sink
  //----------------------------------------------------------------------

  vc_TestSink#(p_msg_sz,p_mem_sz) sink
  (
    .clk     (clk),
    .reset   (reset),

    .val     (sink_val),
    .rdy     (sink_rdy),
    .msg     (sink_msg),

    .done    (done)
  );

endmodule

`endif

