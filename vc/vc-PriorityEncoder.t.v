//========================================================================
// Tests for Priority Encoders
//========================================================================

`include "vc-PriorityEncoder.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-PriorityEncoder" )

  //----------------------------------------------------------------------
  // Test vc_32_5_PriorityEncoder
  //----------------------------------------------------------------------

  reg  [31:0] t0_in_bits;
  wire        t0_out_val;
  wire  [4:0] t0_out_bits;

  vc_32_5_PriorityEncoder t0_enc
  (
    .in_bits  (t0_in_bits),
    .out_val  (t0_out_val),
    .out_bits (t0_out_bits)
  );

  // Helper tasks

  task t0_do_test
  (
    input [8*8-1:0] test_str,
    input    [31:0] in_bits,
    input           correct_out_val,
    input     [4:0] correct_out_bits
  );
  begin

    t0_in_bits = in_bits;
    #1;
    `VC_TEST_EQ( ({test_str," out_val"}), t0_out_val, correct_out_val )
    `VC_TEST_EQ( ({test_str," out_bits"}), t0_out_bits, correct_out_bits )
    #9;

  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_32_5_PriorityEncoder" )
  begin

    //          test_str    in_bits       out_val out_bits
    t0_do_test( "00000000", 32'h00000000, 1'b0,   5'b?????  );
    t0_do_test( "80000000", 32'h80000000, 1'b1,   5'b11111  );
    t0_do_test( "f0000000", 32'hf0000000, 1'b1,   5'b11111  );
    t0_do_test( "ffffffff", 32'hffffffff, 1'b1,   5'b11111  );
    t0_do_test( "01000000", 32'h01000000, 1'b1,   5'b11000  );
    t0_do_test( "00100000", 32'h00100000, 1'b1,   5'b10100  );
    t0_do_test( "0010dead", 32'h0010dead, 1'b1,   5'b10100  );
    t0_do_test( "00001000", 32'h00001000, 1'b1,   5'b01100  );
    t0_do_test( "10000001", 32'h10000001, 1'b1,   5'b11100  );
    t0_do_test( "00000001", 32'h00000001, 1'b1,   5'b00000  );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_32_5_ReversePriorityEncoder
  //----------------------------------------------------------------------

  reg  [31:0] t1_in_bits;
  wire        t1_out_val;
  wire  [4:0] t1_out_bits;

  vc_32_5_ReversePriorityEncoder t1_enc
  (
    .in_bits  (t1_in_bits),
    .out_val  (t1_out_val),
    .out_bits (t1_out_bits)
  );

  // Helper tasks

  task t1_do_test
  (
    input [8*8-1:0] test_str,
    input    [31:0] in_bits,
    input           correct_out_val,
    input     [4:0] correct_out_bits
  );
  begin

    t1_in_bits = in_bits;
    #1;
    `VC_TEST_EQ( ({test_str," out_val"}), t1_out_val, correct_out_val )
    `VC_TEST_EQ( ({test_str," out_bits"}), t1_out_bits, correct_out_bits )
    #9;

  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "vc_32_5_ReversePriorityEncoder" )
  begin

    //          test_str,   in_bits       out_val out_bits
    t1_do_test( "00000000", 32'h00000000, 1'b0,   5'b?????  );
    t1_do_test( "80000000", 32'h80000000, 1'b1,   5'b11111  );
    t1_do_test( "f0000000", 32'hf0000000, 1'b1,   5'b11100  );
    t1_do_test( "ffffffff", 32'hffffffff, 1'b1,   5'b00000  );
    t1_do_test( "01000000", 32'h01000000, 1'b1,   5'b11000  );
    t1_do_test( "00100000", 32'h00100000, 1'b1,   5'b10100  );
    t1_do_test( "0010dead", 32'h0010dead, 1'b1,   5'b00000  );
    t1_do_test( "f0f0f000", 32'hf0f0f000, 1'b1,   5'b01100  );
    t1_do_test( "10000001", 32'h10000001, 1'b1,   5'b00000  );
    t1_do_test( "dead0010", 32'hdead0010, 1'b1,   5'b00100  );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule
