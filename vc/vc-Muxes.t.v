//========================================================================
// Tests for Muxes
//========================================================================

`include "vc-Muxes.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Muxes" )

  //--------------------------------------------------------------------
  // Test vc_Mux2_w32
  //--------------------------------------------------------------------

  reg  [31:0] t1_mux2_in0 = 32'h0a0a0a0a;
  reg  [31:0] t1_mux2_in1 = 32'hb0b0b0b0;
  reg         t1_mux2_sel;
  wire [31:0] t1_mux2_out;

  vc_Mux2#(32) t1_mux2
  (
    .in0 (t1_mux2_in0),
    .in1 (t1_mux2_in1),
    .sel (t1_mux2_sel),
    .out (t1_mux2_out)
  );

  // Helper tasks

  task t1_do_test
  (
    input [8*8-1:0] test_case_str,
    input           mux2_sel,
    input [31:0]    correct_mux2_out
  );
  begin
    t1_mux2_sel = mux2_sel;
    #1;
    `VC_TEST_EQ( test_case_str, t1_mux2_out, correct_mux2_out )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_Mux2_w32" )
  begin
    t1_do_test( "sel == 0", 1'd0, 32'h0a0a0a0a );
    t1_do_test( "sel == 1", 1'd1, 32'hb0b0b0b0 );
  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_Mux4
  //--------------------------------------------------------------------

  reg  [31:0] t2_mux4_in0 = 32'h0a0a0a0a;
  reg  [31:0] t2_mux4_in1 = 32'hb0b0b0b0;
  reg  [31:0] t2_mux4_in2 = 32'h0c0c0c0c;
  reg  [31:0] t2_mux4_in3 = 32'hd0d0d0d0;
  reg  [ 1:0] t2_mux4_sel;
  wire [31:0] t2_mux4_out;

  vc_Mux4#(32) t2_mux4
  (
    .in0 (t2_mux4_in0),
    .in1 (t2_mux4_in1),
    .in2 (t2_mux4_in2),
    .in3 (t2_mux4_in3),
    .sel (t2_mux4_sel),
    .out (t2_mux4_out)
  );

  // Helper tasks

  task t2_do_test
  (
    input [8*8-1:0] test_case_str,
    input [1:0]     mux4_sel,
    input [31:0]    correct_mux4_out
  );
  begin
    t2_mux4_sel = mux4_sel;
    #1;
    `VC_TEST_EQ( test_case_str, t2_mux4_out, correct_mux4_out )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 2, "vc_Mux4_w32" )
  begin
    t2_do_test( "sel == 0", 2'd0, 32'h0a0a0a0a );
    t2_do_test( "sel == 1", 2'd1, 32'hb0b0b0b0 );
    t2_do_test( "sel == 2", 2'd2, 32'h0c0c0c0c );
    t2_do_test( "sel == 3", 2'd3, 32'hd0d0d0d0 );
  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule
