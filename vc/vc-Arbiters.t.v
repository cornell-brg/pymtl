//========================================================================
// Tests for vc-Arbiters
//========================================================================

`include "vc-Arbiters.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Arbiters" )

  //--------------------------------------------------------------------
  // Test vc_FixedArb
  //--------------------------------------------------------------------

  reg        t1_kin;
  reg  [3:0] t1_reqs;
  wire [3:0] t1_grants;
  wire       t1_kout;

  vc_FixedArbChain#(4) t1_arb
  (
    .kin    (t1_kin),
    .reqs   (t1_reqs),
    .grants (t1_grants),
    .kout   (t1_kout)
  );

  // Helper tasks

  task t1_do_test
  (
    input [4*8-1:0] test_case_str,
    input           kin,
    input [3:0]     reqs,
    input [3:0]     correct_grants,
    input           correct_kout
  );
  begin
    t1_kin  = kin;
    t1_reqs = reqs;
    #1;
    `VC_TEST_EQ( ({test_case_str," grants"}), t1_grants, correct_grants )
    `VC_TEST_EQ( ({test_case_str," kout  "}), t1_kout,   correct_kout   )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_FixedArb" )
  begin

    t1_do_test( "0000", 1, 4'b0000, 4'b0000, 1 );
    t1_do_test( "1111", 1, 4'b1111, 4'b0000, 1 );

    t1_do_test( "0000", 0, 4'b0000, 4'b0000, 0 );

    t1_do_test( "1000", 0, 4'b1000, 4'b1000, 1 );
    t1_do_test( "0100", 0, 4'b0100, 4'b0100, 1 );
    t1_do_test( "0010", 0, 4'b0010, 4'b0010, 1 );
    t1_do_test( "0001", 0, 4'b0001, 4'b0001, 1 );

    t1_do_test( "1100", 0, 4'b1100, 4'b0100, 1 );
    t1_do_test( "1010", 0, 4'b1010, 4'b0010, 1 );
    t1_do_test( "1001", 0, 4'b1001, 4'b0001, 1 );
    t1_do_test( "0110", 0, 4'b0110, 4'b0010, 1 );
    t1_do_test( "0101", 0, 4'b0101, 4'b0001, 1 );
    t1_do_test( "0011", 0, 4'b0011, 4'b0001, 1 );

    t1_do_test( "1110", 0, 4'b1110, 4'b0010, 1 );
    t1_do_test( "1101", 0, 4'b1101, 4'b0001, 1 );
    t1_do_test( "1011", 0, 4'b1011, 4'b0001, 1 );
    t1_do_test( "0111", 0, 4'b0111, 4'b0001, 1 );

    t1_do_test( "1111", 0, 4'b1111, 4'b0001, 1 );

  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_VariableArb
  //--------------------------------------------------------------------

  reg        t2_kin;
  reg  [3:0] t2_priority;
  reg  [3:0] t2_reqs;
  wire [3:0] t2_grants;
  wire       t2_kout;

  vc_VariableArbChain#(4) t2_arb
  (
    .kin      (t2_kin),
    .priority (t2_priority),
    .reqs     (t2_reqs),
    .grants   (t2_grants),
    .kout     (t2_kout)
  );

  // Helper tasks

  task t2_do_test
  (
    input [6*8-1:0] test_case_str,
    input           kin,
    input [3:0]     priority,
    input [3:0]     reqs,
    input [3:0]     correct_grants,
    input           correct_kout
  );
  begin
    t2_kin      = kin;
    t2_priority = priority;
    t2_reqs     = reqs;
    #1;
    `VC_TEST_EQ( ({test_case_str," grants"}), t2_grants, correct_grants )
    `VC_TEST_EQ( ({test_case_str," kout  "}), t2_kout,   correct_kout   )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "vc_VariableArb" )
  begin

    // Test kin = 1

    t2_do_test( "0 0000", 1, 4'b0001, 4'b0000, 4'b0000, 1 );
    t2_do_test( "0 1111", 1, 4'b0001, 4'b1111, 4'b0000, 1 );
    t2_do_test( "1 0000", 1, 4'b0010, 4'b0000, 4'b0000, 1 );
    t2_do_test( "1 1111", 1, 4'b0010, 4'b1111, 4'b0000, 1 );
    t2_do_test( "2 0000", 1, 4'b0100, 4'b0000, 4'b0000, 1 );
    t2_do_test( "2 1111", 1, 4'b0100, 4'b1111, 4'b0000, 1 );
    t2_do_test( "3 0000", 1, 4'b1000, 4'b0000, 4'b0000, 1 );
    t2_do_test( "3 1111", 1, 4'b1000, 4'b1111, 4'b0000, 1 );

    // Test when requester 0 has highest priority

    t2_do_test( "0 0000", 0, 4'b0001, 4'b0000, 4'b0000, 0 );

    t2_do_test( "0 1000", 0, 4'b0001, 4'b1000, 4'b1000, 1 );
    t2_do_test( "0 0100", 0, 4'b0001, 4'b0100, 4'b0100, 1 );
    t2_do_test( "0 0010", 0, 4'b0001, 4'b0010, 4'b0010, 1 );
    t2_do_test( "0 0001", 0, 4'b0001, 4'b0001, 4'b0001, 1 );

    t2_do_test( "0 1100", 0, 4'b0001, 4'b1100, 4'b0100, 1 );
    t2_do_test( "0 1010", 0, 4'b0001, 4'b1010, 4'b0010, 1 );
    t2_do_test( "0 1001", 0, 4'b0001, 4'b1001, 4'b0001, 1 );
    t2_do_test( "0 0110", 0, 4'b0001, 4'b0110, 4'b0010, 1 );
    t2_do_test( "0 0101", 0, 4'b0001, 4'b0101, 4'b0001, 1 );
    t2_do_test( "0 0011", 0, 4'b0001, 4'b0011, 4'b0001, 1 );

    t2_do_test( "0 1110", 0, 4'b0001, 4'b1110, 4'b0010, 1 );
    t2_do_test( "0 1101", 0, 4'b0001, 4'b1101, 4'b0001, 1 );
    t2_do_test( "0 1011", 0, 4'b0001, 4'b1011, 4'b0001, 1 );
    t2_do_test( "0 0111", 0, 4'b0001, 4'b0111, 4'b0001, 1 );

    t2_do_test( "0 1111", 0, 4'b0001, 4'b1111, 4'b0001, 1 );

    // Test when requester 1 has highest priority

    t2_do_test( "1 0000", 0, 4'b0010, 4'b0000, 4'b0000, 0 );

    t2_do_test( "1 1000", 0, 4'b0010, 4'b1000, 4'b1000, 1 );
    t2_do_test( "1 0100", 0, 4'b0010, 4'b0100, 4'b0100, 1 );
    t2_do_test( "1 0010", 0, 4'b0010, 4'b0010, 4'b0010, 1 );
    t2_do_test( "1 0001", 0, 4'b0010, 4'b0001, 4'b0001, 1 );

    t2_do_test( "1 1100", 0, 4'b0010, 4'b1100, 4'b0100, 1 );
    t2_do_test( "1 1010", 0, 4'b0010, 4'b1010, 4'b0010, 1 );
    t2_do_test( "1 1001", 0, 4'b0010, 4'b1001, 4'b1000, 1 );
    t2_do_test( "1 0110", 0, 4'b0010, 4'b0110, 4'b0010, 1 );
    t2_do_test( "1 0101", 0, 4'b0010, 4'b0101, 4'b0100, 1 );
    t2_do_test( "1 0011", 0, 4'b0010, 4'b0011, 4'b0010, 1 );

    t2_do_test( "1 1110", 0, 4'b0010, 4'b1110, 4'b0010, 1 );
    t2_do_test( "1 1101", 0, 4'b0010, 4'b1101, 4'b0100, 1 );
    t2_do_test( "1 1011", 0, 4'b0010, 4'b1011, 4'b0010, 1 );
    t2_do_test( "1 0111", 0, 4'b0010, 4'b0111, 4'b0010, 1 );

    t2_do_test( "1 1111", 0, 4'b0010, 4'b1111, 4'b0010, 1 );

    // Test when requester 2 has highest priority

    t2_do_test( "2 0000", 0, 4'b0100, 4'b0000, 4'b0000, 0 );

    t2_do_test( "2 1000", 0, 4'b0100, 4'b1000, 4'b1000, 1 );
    t2_do_test( "2 0100", 0, 4'b0100, 4'b0100, 4'b0100, 1 );
    t2_do_test( "2 0010", 0, 4'b0100, 4'b0010, 4'b0010, 1 );
    t2_do_test( "2 0001", 0, 4'b0100, 4'b0001, 4'b0001, 1 );

    t2_do_test( "2 1100", 0, 4'b0100, 4'b1100, 4'b0100, 1 );
    t2_do_test( "2 1010", 0, 4'b0100, 4'b1010, 4'b1000, 1 );
    t2_do_test( "2 1001", 0, 4'b0100, 4'b1001, 4'b1000, 1 );
    t2_do_test( "2 0110", 0, 4'b0100, 4'b0110, 4'b0100, 1 );
    t2_do_test( "2 0101", 0, 4'b0100, 4'b0101, 4'b0100, 1 );
    t2_do_test( "2 0011", 0, 4'b0100, 4'b0011, 4'b0001, 1 );

    t2_do_test( "2 1110", 0, 4'b0100, 4'b1110, 4'b0100, 1 );
    t2_do_test( "2 1101", 0, 4'b0100, 4'b1101, 4'b0100, 1 );
    t2_do_test( "2 1011", 0, 4'b0100, 4'b1011, 4'b1000, 1 );
    t2_do_test( "2 0111", 0, 4'b0100, 4'b0111, 4'b0100, 1 );

    t2_do_test( "2 1111", 0, 4'b0100, 4'b1111, 4'b0100, 1 );

    // Test when requester 3 has highest priority

    t2_do_test( "3 0000", 0, 4'b1000, 4'b0000, 4'b0000, 0 );

    t2_do_test( "3 1000", 0, 4'b1000, 4'b1000, 4'b1000, 1 );
    t2_do_test( "3 0100", 0, 4'b1000, 4'b0100, 4'b0100, 1 );
    t2_do_test( "3 0010", 0, 4'b1000, 4'b0010, 4'b0010, 1 );
    t2_do_test( "3 0001", 0, 4'b1000, 4'b0001, 4'b0001, 1 );

    t2_do_test( "3 1100", 0, 4'b1000, 4'b1100, 4'b1000, 1 );
    t2_do_test( "3 1010", 0, 4'b1000, 4'b1010, 4'b1000, 1 );
    t2_do_test( "3 1001", 0, 4'b1000, 4'b1001, 4'b1000, 1 );
    t2_do_test( "3 0110", 0, 4'b1000, 4'b0110, 4'b0010, 1 );
    t2_do_test( "3 0101", 0, 4'b1000, 4'b0101, 4'b0001, 1 );
    t2_do_test( "3 0011", 0, 4'b1000, 4'b0011, 4'b0001, 1 );

    t2_do_test( "3 1110", 0, 4'b1000, 4'b1110, 4'b1000, 1 );
    t2_do_test( "3 1101", 0, 4'b1000, 4'b1101, 4'b1000, 1 );
    t2_do_test( "3 1011", 0, 4'b1000, 4'b1011, 4'b1000, 1 );
    t2_do_test( "3 0111", 0, 4'b1000, 4'b0111, 4'b0001, 1 );

    t2_do_test( "3 1111", 0, 4'b1000, 4'b1111, 4'b1000, 1 );

  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_RoundRobinArb
  //--------------------------------------------------------------------

  reg        t3_reset = 1'b1;
  reg        t3_kin   = 1'b0;
  reg  [3:0] t3_reqs  = 4'b0;
  wire [3:0] t3_grants;
  wire       t3_kout;

  vc_RoundRobinArbChain#(4) t3_arb
  (
    .clk    (clk),
    .reset  (t3_reset),
    .kin    (t3_kin),
    .reqs   (t3_reqs),
    .grants (t3_grants),
    .kout   (t3_kout)
  );

  // Helper tasks

  task t3_do_test
  (
    input [4*8-1:0] test_case_str,
    input           kin,
    input [3:0]     reqs,
    input [3:0]     correct_grants,
    input           correct_kout
  );
  begin
    t3_kin  = kin;
    t3_reqs = reqs;
    #1;
    `VC_TEST_EQ( ({test_case_str," grants"}), t3_grants, correct_grants )
    `VC_TEST_EQ( ({test_case_str," kout  "}), t3_kout,   correct_kout   )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 3, "vc_RoundRobinArb" )
  begin

    #1;  t3_reset = 1'b1;
    #20; t3_reset = 1'b0;

    t3_do_test( "0000", 1, 4'b0000, 4'b0000, 1 );
    t3_do_test( "1111", 1, 4'b1111, 4'b0000, 1 );

    t3_do_test( "0000", 0, 4'b0000, 4'b0000, 0 );

    t3_do_test( "0001", 0, 4'b0001, 4'b0001, 1 );
    t3_do_test( "0010", 0, 4'b0010, 4'b0010, 1 );
    t3_do_test( "0100", 0, 4'b0100, 4'b0100, 1 );
    t3_do_test( "1000", 0, 4'b1000, 4'b1000, 1 );

    t3_do_test( "1111", 0, 4'b1111, 4'b0001, 1 );
    t3_do_test( "1111", 0, 4'b1111, 4'b0010, 1 );
    t3_do_test( "1111", 0, 4'b1111, 4'b0100, 1 );
    t3_do_test( "1111", 0, 4'b1111, 4'b1000, 1 );
    t3_do_test( "1111", 0, 4'b1111, 4'b0001, 1 );

    t3_do_test( "1100", 0, 4'b1100, 4'b0100, 1 );
    t3_do_test( "1010", 0, 4'b1010, 4'b1000, 1 );
    t3_do_test( "1001", 0, 4'b1001, 4'b0001, 1 );
    t3_do_test( "0110", 0, 4'b0110, 4'b0010, 1 );
    t3_do_test( "0101", 0, 4'b0101, 4'b0100, 1 );
    t3_do_test( "0011", 0, 4'b0011, 4'b0001, 1 );

    t3_do_test( "1110", 0, 4'b1110, 4'b0010, 1 );
    t3_do_test( "1101", 0, 4'b1101, 4'b0100, 1 );
    t3_do_test( "1011", 0, 4'b1011, 4'b1000, 1 );
    t3_do_test( "0111", 0, 4'b0111, 4'b0001, 1 );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 3 )
endmodule

