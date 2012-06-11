//========================================================================
// Unit Tests: Test Tag Source/Sink
//========================================================================

`include "vc-TestSource.v"
`include "vc-TestTagSink.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_msg_nbits    = 1,
  parameter p_num_entries  = 1024,
  parameter p_tag_nbits    = 1,
  parameter p_tag_offset   = 0
)(
  input  clk,
  input  reset,
  output done
);

  wire                   val;
  wire                   rdy;
  wire [p_msg_nbits-1:0] msg;

  wire                   src_done;
  wire                   sink_done;

  vc_TestSource
  #(
    p_msg_nbits,
    p_num_entries
  )
  src
  (
    .clk   (clk),
    .reset (reset),
    .val   (val),
    .rdy   (rdy),
    .msg   (msg),
    .done  (src_done)
  );

  vc_TestTagSink
  #(
    p_msg_nbits,
    p_num_entries,
    p_tag_nbits,
    p_tag_offset
  )
  sink
  (
    .clk   (clk),
    .reset (reset),
    .val   (val),
    .rdy   (rdy),
    .msg   (msg),
    .done  (sink_done)
  );

  assign done = src_done & sink_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestTagSink" )

  //----------------------------------------------------------------------
  // Helper task
  //----------------------------------------------------------------------

  reg [9:0] req_msg_shifted;
  reg [1:0] req_tag;

  task t0_mk_req_resp
  (
    input [3:0] req_index,
    input [9:0] req_msg,
    input [3:0] resp_index
  );
  begin
    t0.src.m[req_index] = req_msg;

    req_msg_shifted = ( req_msg >> 8 );
    req_tag = req_msg_shifted[1:0];

    t0.sink.m[ { req_tag, resp_index } ] = req_msg;
  end
  endtask

  //----------------------------------------------------------------------
  // TestBasic_msg10
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_msg_nbits   (10),
    .p_num_entries (16),
    .p_tag_nbits   (2),
    .p_tag_offset  (8)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_msg10" )
  begin

    t0_mk_req_resp(  0, 10'h0aa,  0 );
    t0_mk_req_resp(  1, 10'h1bb,  0 );
    t0_mk_req_resp(  2, 10'h2cc,  0 );
    t0_mk_req_resp(  3, 10'h3dd,  0 );
    t0_mk_req_resp(  4, 10'h0ee,  1 );
    t0_mk_req_resp(  5, 10'h1ff,  1 );
    t0_mk_req_resp(  6, 10'h2ab,  1 );
    t0_mk_req_resp(  7, 10'h3cd,  1 );

    #1;   t0_reset = 1'b1;
    #20;  t0_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )

endmodule

