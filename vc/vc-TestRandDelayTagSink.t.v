//========================================================================
// Unit Tests: Test Tag Source with Random Delay
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelayTagSink.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_msg_nbits   = 1,
  parameter p_num_entries = 1024,
  parameter p_tag_nbits   = 1,
  parameter p_tag_offset  = 0,
  parameter p_max_delay   = 0
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

  vc_TestRandDelaySource
  #(
    p_msg_nbits,
    p_num_entries,
    p_max_delay
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

  vc_TestRandDelayTagSink
  #(
    p_msg_nbits,
    p_num_entries,
    p_tag_nbits,
    p_tag_offset,
    p_max_delay
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

  `VC_TEST_SUITE_BEGIN( "vc-TestRandDelayTagSink" )

  //----------------------------------------------------------------------
  // TestBasic_msg10_rdelay0
  //----------------------------------------------------------------------

  // Helper task

  reg [9:0] t0_req_msg_shifted;
  reg [1:0] t0_req_tag;

  task t0_mk_req_resp
  (
    input [3:0] req_index,
    input [9:0] req_msg,
    input [3:0] resp_index
  );
  begin
    t0.src.src.m[req_index] = req_msg;

    t0_req_msg_shifted = ( req_msg >> 8 );
    t0_req_tag = t0_req_msg_shifted[1:0];

    t0.sink.sink.m[ { t0_req_tag, resp_index } ] = req_msg;
  end
  endtask

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_msg_nbits   (10),
    .p_num_entries (16),
    .p_tag_nbits   (2),
    .p_tag_offset  (8),
    .p_max_delay   (0)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_msg10_rdelay0" )
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

  //----------------------------------------------------------------------
  // TestBasic_msg10_rdelay1
  //----------------------------------------------------------------------

  // Helper task

  reg [9:0] t1_req_msg_shifted;
  reg [1:0] t1_req_tag;

  task t1_mk_req_resp
  (
    input [3:0] req_index,
    input [9:0] req_msg,
    input [3:0] resp_index
  );
  begin
    t1.src.src.m[req_index] = req_msg;

    t1_req_msg_shifted = ( req_msg >> 8 );
    t1_req_tag = t1_req_msg_shifted[1:0];

    t1.sink.sink.m[ { t1_req_tag, resp_index } ] = req_msg;
  end
  endtask

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    .p_msg_nbits   (10),
    .p_num_entries (16),
    .p_tag_nbits   (2),
    .p_tag_offset  (8),
    .p_max_delay   (1)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_msg10_rdelay1" )
  begin

    t1_mk_req_resp(  0, 10'h0aa,  0 );
    t1_mk_req_resp(  1, 10'h1bb,  0 );
    t1_mk_req_resp(  2, 10'h2cc,  0 );
    t1_mk_req_resp(  3, 10'h3dd,  0 );
    t1_mk_req_resp(  4, 10'h0ee,  1 );
    t1_mk_req_resp(  5, 10'h1ff,  1 );
    t1_mk_req_resp(  6, 10'h2ab,  1 );
    t1_mk_req_resp(  7, 10'h3cd,  1 );

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_msg10_rdelay2
  //----------------------------------------------------------------------

  // Helper task

  reg [9:0] t2_req_msg_shifted;
  reg [1:0] t2_req_tag;

  task t2_mk_req_resp
  (
    input [3:0] req_index,
    input [9:0] req_msg,
    input [3:0] resp_index
  );
  begin
    t2.src.src.m[req_index] = req_msg;

    t2_req_msg_shifted = ( req_msg >> 8 );
    t2_req_tag = t2_req_msg_shifted[1:0];

    t2.sink.sink.m[ { t2_req_tag, resp_index } ] = req_msg;
  end
  endtask

  wire t2_done;
  reg  t2_reset = 1;

  TestHarness
  #(
    .p_msg_nbits   (10),
    .p_num_entries (16),
    .p_tag_nbits   (2),
    .p_tag_offset  (8),
    .p_max_delay   (2)
  )
  t2
  (
    .clk   (clk),
    .reset (t2_reset),
    .done  (t2_done)
  );

  `VC_TEST_CASE_BEGIN( 3, "TestBasic_msg10_rdelay2" )
  begin

    t2_mk_req_resp(  0, 10'h0aa,  0 );
    t2_mk_req_resp(  1, 10'h1bb,  0 );
    t2_mk_req_resp(  2, 10'h2cc,  0 );
    t2_mk_req_resp(  3, 10'h3dd,  0 );
    t2_mk_req_resp(  4, 10'h0ee,  1 );
    t2_mk_req_resp(  5, 10'h1ff,  1 );
    t2_mk_req_resp(  6, 10'h2ab,  1 );
    t2_mk_req_resp(  7, 10'h3cd,  1 );

    #1;   t2_reset = 1'b1;
    #20;  t2_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t2_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 3 )

endmodule

