//========================================================================
// Unit Tests: Test Random Delay Module
//========================================================================

`include "vc-TestSource.v"
`include "vc-TestSink.v"
`include "vc-TestRandDelay.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_msg_sz    = 1,
  parameter p_mem_sz    = 1024,
  parameter p_max_delay = 0
)(
  input  clk,
  input  reset,
  output done
);

  wire                src_val;
  wire                src_rdy;
  wire [p_msg_sz-1:0] src_msg;
  wire                src_done;

  vc_TestSource#(p_msg_sz,p_mem_sz) src
  (
    .clk     (clk),
    .reset   (reset),

    .val     (src_val),
    .rdy     (src_rdy),
    .msg     (src_msg),

    .done    (src_done)
  );

  wire                sink_val;
  wire                sink_rdy;
  wire [p_msg_sz-1:0] sink_msg;

  vc_TestRandDelay#(p_msg_sz,p_max_delay) rand_delay
  (
    .clk     (clk),
    .reset   (reset),

    .in_val  (src_val),
    .in_rdy  (src_rdy),
    .in_msg  (src_msg),

    .out_val (sink_val),
    .out_rdy (sink_rdy),
    .out_msg (sink_msg)
  );

  wire sink_done;

  vc_TestSink#(p_msg_sz,p_mem_sz) sink
  (
    .clk     (clk),
    .reset   (reset),

    .val     (sink_val),
    .rdy     (sink_rdy),
    .msg     (sink_msg),

    .done    (sink_done)
  );

  assign done = src_done & sink_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestRandDelay" )

  //----------------------------------------------------------------------
  // TestBasic_rdelay0
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_msg_sz    (8),
    .p_mem_sz    (32),
    .p_max_delay (0)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_rdelay0" )
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
  // TestBasic_rdelay1
  //----------------------------------------------------------------------

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    .p_msg_sz    (8),
    .p_mem_sz    (32),
    .p_max_delay (0)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_rdelay1" )
  begin

    t1.src.m[0] = 8'haa; t1.sink.m[0] = 8'haa;
    t1.src.m[1] = 8'hbb; t1.sink.m[1] = 8'hbb;
    t1.src.m[2] = 8'hcc; t1.sink.m[2] = 8'hcc;
    t1.src.m[3] = 8'hdd; t1.sink.m[3] = 8'hdd;
    t1.src.m[4] = 8'hee; t1.sink.m[4] = 8'hee;
    t1.src.m[5] = 8'hff; t1.sink.m[5] = 8'hff;

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_rdelay2
  //----------------------------------------------------------------------

  wire t2_done;
  reg  t2_reset = 1;

  TestHarness
  #(
    .p_msg_sz    (8),
    .p_mem_sz    (32),
    .p_max_delay (2)
  )
  t2
  (
    .clk   (clk),
    .reset (t2_reset),
    .done  (t2_done)
  );

  `VC_TEST_CASE_BEGIN( 3, "TestBasic_rdelay2" )
  begin

    t2.src.m[0] = 8'haa; t2.sink.m[0] = 8'haa;
    t2.src.m[1] = 8'hbb; t2.sink.m[1] = 8'hbb;
    t2.src.m[2] = 8'hcc; t2.sink.m[2] = 8'hcc;
    t2.src.m[3] = 8'hdd; t2.sink.m[3] = 8'hdd;
    t2.src.m[4] = 8'hee; t2.sink.m[4] = 8'hee;
    t2.src.m[5] = 8'hff; t2.sink.m[5] = 8'hff;

    #1;   t2_reset = 1'b1;
    #20;  t2_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t2_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_rdelay10
  //----------------------------------------------------------------------

  wire t3_done;
  reg  t3_reset = 1;

  TestHarness
  #(
    .p_msg_sz    (8),
    .p_mem_sz    (32),
    .p_max_delay (2)
  )
  t3
  (
    .clk   (clk),
    .reset (t3_reset),
    .done  (t3_done)
  );

  `VC_TEST_CASE_BEGIN( 4, "TestBasic_rdelay10" )
  begin

    t3.src.m[0] = 8'haa; t3.sink.m[0] = 8'haa;
    t3.src.m[1] = 8'hbb; t3.sink.m[1] = 8'hbb;
    t3.src.m[2] = 8'hcc; t3.sink.m[2] = 8'hcc;
    t3.src.m[3] = 8'hdd; t3.sink.m[3] = 8'hdd;
    t3.src.m[4] = 8'hee; t3.sink.m[4] = 8'hee;
    t3.src.m[5] = 8'hff; t3.sink.m[5] = 8'hff;

    #1;   t3_reset = 1'b1;
    #20;  t3_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t3_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 4 )
endmodule

