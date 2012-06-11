//========================================================================
// Test Tag Sink with Random Delays
//========================================================================

`ifndef VC_TEST_RAND_DELAY_TAG_SINK_V
`define VC_TEST_RAND_DELAY_TAG_SINK_V

`include "vc-TestTagSink.v"
`include "vc-TestRandDelay.v"

module vc_TestRandDelayTagSink
#(
  parameter p_msg_nbits   = 1,    // size of message to store in sink
  parameter p_num_entries = 1024, // size of memory that stores the messages
  parameter p_tag_nbits   = 1,    // size of tag in bits
  parameter p_tag_offset  = 0,    // offset to tag field in message in bits
  parameter p_max_delay   = 0     // max number of cycles to delay messages
)(
  input  clk,
  input  reset,

  // Sink message interface

  input                    val,
  output                   rdy,
  input  [p_msg_nbits-1:0] msg,

  // Goes high once all sink data has been received

  output done
);

  //----------------------------------------------------------------------
  // Test random delay
  //----------------------------------------------------------------------

  wire                   sink_val;
  wire                   sink_rdy;
  wire [p_msg_nbits-1:0] sink_msg;

  vc_TestRandDelay
  #(
    p_msg_nbits,
    p_max_delay
  )
  rand_delay
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

  vc_TestTagSink
  #(
    p_msg_nbits,
    p_num_entries,
    p_tag_nbits,
    p_tag_offset
  )
  sink
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

