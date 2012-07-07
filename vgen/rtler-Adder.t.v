`include "rtler-Adder.v"
`include "vc-Test.v"

module FullAdder
(
  output sum,
  input  in0,
  input  in1,
  input  cin,
  output cout
);
  assign sum = (in0 ^ in1) ^ cin;
  assign cout = (in0 && in1) || (in0 && cin) || (in1 && cin);
endmodule


module tester;

  `VC_TEST_SUITE_BEGIN( "rtler-Adder" )

  reg  [3:0] t1_in0 = 4'd0;
  reg  [3:0] t1_in1 = 4'd0;
  wire [3:0] t1_sum;

  RippleCarryAdder t1_adder
  (
    .in0 (t1_in0),
    .in1 (t1_in1),
    .sum (t1_sum)
  );

  // Helper tasks

  task t1_do_test
  (
    input [8*8-1:0] test_case_str,
    input [3:0]     in1,
    input [3:0]     in2,
    input [3:0]     expected_sum
  );
  begin
    t1_in0 = in1;
    t1_in1 = in2;
    #1;
    `VC_TEST_EQ( test_case_str, t1_sum, expected_sum)
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_Mux2_w32" )
  begin
    t1_do_test( "0+1", 4'd0, 4'd1, 4'd1);
    t1_do_test( "1+0", 4'd1, 4'd0, 4'd1);
    t1_do_test( "1+1", 4'd1, 4'd1, 4'd2);
    t1_do_test( "2+1", 4'd2, 4'd1, 4'd3);
    t1_do_test( "8+7", 4'd8, 4'd7, 4'd15);
    t1_do_test( "8+8", 4'd8, 4'd8, 4'd1);
  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule
