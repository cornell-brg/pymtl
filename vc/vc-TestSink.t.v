//========================================================================
// Unit Tests: Test Source/Sink
//========================================================================

`include "vc-TestSource.v"
`include "vc-TestSink.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_msg_sz = 1,
  parameter p_mem_sz = 1024
)(
  input  clk,
  input  reset,
  output done
);

  wire                val;
  wire                rdy;
  wire [p_msg_sz-1:0] msg;

  wire                src_done;
  wire                sink_done;

  vc_TestSource#(p_msg_sz,p_mem_sz) src
  (
    .clk   (clk),
    .reset (reset),
    .val   (val),
    .rdy   (rdy),
    .msg   (msg),
    .done  (src_done)
  );

  vc_TestSink#(p_msg_sz,p_mem_sz) sink
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
// // Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestSink" )

  //----------------------------------------------------------------------
  // TestBasic_msg8
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_msg_sz (8),
    .p_mem_sz (64)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_msg8" )
  begin

    t0.src.m[0] = 8'haa; t0.sink.m[0] = 8'haa;
    t0.src.m[1] = 8'hbb; t0.sink.m[1] = 8'hbb;
    t0.src.m[2] = 8'hcc; t0.sink.m[2] = 8'hcc;
    t0.src.m[3] = 8'hdd; t0.sink.m[3] = 8'hdd;
    t0.src.m[4] = 8'hee; t0.sink.m[4] = 8'hee;
    t0.src.m[5] = 8'hff; t0.sink.m[5] = 8'hff;

    #1;   t0_reset = 1'b1;
    #20;  t0_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_msg13
  //----------------------------------------------------------------------

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    .p_msg_sz (13),
    .p_mem_sz (64)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_msg13" )
  begin

    t1.src.m[0] = 13'h11aa; t1.sink.m[0] = 13'h11aa;
    t1.src.m[1] = 13'h02bb; t1.sink.m[1] = 13'h02bb;
    t1.src.m[2] = 13'h13cc; t1.sink.m[2] = 13'h13cc;
    t1.src.m[3] = 13'h04dd; t1.sink.m[3] = 13'h04dd;
    t1.src.m[4] = 13'h15ee; t1.sink.m[4] = 13'h15ee;
    t1.src.m[5] = 13'h06ff; t1.sink.m[5] = 13'h06ff;

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule

