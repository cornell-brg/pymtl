//========================================================================
// Tests for State Elements
//========================================================================

`include "vc-StateElements.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-StateElements" )

  //--------------------------------------------------------------------
  // Test vcDFF_pf
  //--------------------------------------------------------------------

  reg  [31:0] vc_DFF_test_d_p;
  wire [31:0] vc_DFF_test_q_np;

  vc_DFF_pf#(32) vc_DFF_test_pf
  (
    .clk  (clk),
    .d_p  (vc_DFF_test_d_p),
    .q_np (vc_DFF_test_q_np)
  );

  `VC_TEST_CASE_BEGIN( 1, "vc_DFF_pf" )
  begin

    #1;

    vc_DFF_test_d_p = 1'b0;
    #10; `VC_TEST_EQ( "#1", vc_DFF_test_q_np, 1'b0  )

    vc_DFF_test_d_p = 1'b1;
    #0;  `VC_TEST_EQ( "#2", vc_DFF_test_q_np, 1'b0  )
    #10; `VC_TEST_EQ( "#3", vc_DFF_test_q_np, 1'b1  )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule

