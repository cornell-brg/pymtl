//========================================================================
// Tests for Arithmetic Components
//========================================================================

`include "vc-Arith.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Arith" )

  //----------------------------------------------------------------------
  // Test vc_Adder
  //----------------------------------------------------------------------

  reg  [31:0] t0_in0, t0_in1;
  reg         t0_cin;
  wire [31:0] t0_out;
  wire        t0_cout;

  vc_Adder#(32) t0_dut
  (
    .in0  (t0_in0),
    .in1  (t0_in1),
    .cin  (t0_cin),
    .out  (t0_out),
    .cout (t0_cout)
  );

  `VC_TEST_CASE_BEGIN( 1, "vc_Adder_w32" )
  begin

    t0_cin = 0;
    t0_in0 = 32'h000fffff;
    t0_in1 = 32'h0000ffff;

    #25;
    `VC_TEST_EQ( "0x000fffff + 0x0000ffff",        t0_out,  32'h0010fffe )
    `VC_TEST_EQ( "0x000fffff + 0x0000ffff (cout)", t0_cout, 1'b0 )

    t0_cin = 0;
    t0_in0 = 32'hffffffff;
    t0_in1 = 32'h0000ffff;

    #25;
    `VC_TEST_EQ( "0x000fffff + 0x0000ffff",        t0_out,  32'h0000fffe )
    `VC_TEST_EQ( "0x000fffff + 0x0000ffff (cout)", t0_cout, 1'b1 )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Inc_w5
  //----------------------------------------------------------------------

  reg  [4:0] t1_in;
  wire [4:0] t1_out;

  vc_Inc#(5,5'd4) t1_dut
  (
    .in  (t1_in),
    .out (t1_out)
  );

  `VC_TEST_CASE_BEGIN( 2, "vc_Inc_w5" )
  begin

    t1_in = 5'd5; #25;
    `VC_TEST_EQ( "5 + 4", t1_out, 5'd9 )

    t1_in = 5'd3; #25;
    `VC_TEST_EQ( "3 + 4", t1_out, 5'd7 )

    t1_in = 5'd9; #25;
    `VC_TEST_EQ( "9 + 4", t1_out, 5'd13 )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_ZeroExtend_w32
  //----------------------------------------------------------------------

  reg  [15:0] t2_in;
  wire [31:0] t2_out;

  vc_ZeroExtend#(16,32) t2_dut
  (
    .in  (t2_in),
    .out (t2_out)
  );

  `VC_TEST_CASE_BEGIN( 3, "vc_ZeroExtend_w32" )
  begin

    t2_in = 16'h0fff; #25;
    `VC_TEST_EQ( "zeroExtend(16'h0fff)", t2_out, 32'h00000fff )

    t2_in = 16'hffff; #25;
    `VC_TEST_EQ( "zeroExtend(16'hffff)", t2_out, 32'h0000ffff )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_SignExtend_w32
  //----------------------------------------------------------------------

  reg  [15:0] t3_in;
  wire [31:0] t3_out;

  vc_SignExtend#(16,32) t3_dut
  (
    .in  (t3_in),
    .out (t3_out)
  );

  `VC_TEST_CASE_BEGIN( 4, "vc_SignExtend_w32" )
  begin

    t3_in = 16'h0fff; #25;
    `VC_TEST_EQ( "signExtend(16'h0fff)", t3_out, 32'h00000fff )

    t3_in = 16'hffff; #25;
    `VC_TEST_EQ( "signExtend(16'hffff)", t3_out, 32'hffffffff )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 4 )
endmodule

