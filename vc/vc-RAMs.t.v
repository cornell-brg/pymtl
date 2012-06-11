//========================================================================
// Tests for RAMs
//========================================================================

`include "vc-RAMs.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-RAMs" )

  //----------------------------------------------------------------------
  // Test vc_RAM_rst_1w1r_pf
  //----------------------------------------------------------------------

  reg  t0_reset = 1;
  wire t0_reset_int;

  vc_DFF_pf#(1) t0_reset_reg
  (
    .clk   (clk),
    .d_p   (t0_reset),
    .q_np  (t0_reset_int)
  );

  reg  [3:0] t0_raddr;
  wire [1:0] t0_rdata;
  reg        t0_wen;
  reg  [3:0] t0_waddr;
  reg  [1:0] t0_wdata;

  vc_RAM_rst_1w1r_pf#(2,16,4,2'b10) t0_ram
  (
    .clk      (clk),
    .reset_p  (t0_reset_int),
    .raddr    (t0_raddr),
    .rdata    (t0_rdata),
    .wen_p    (t0_wen),
    .waddr_p  (t0_waddr),
    .wdata_p  (t0_wdata)
  );

  `VC_TEST_CASE_BEGIN( 1, "vc-RAM_rst_1w1r_pf" )
  begin

    #1;
    t0_reset = 1'b1;
    t0_raddr = 4'd0;
    t0_wen   = 1'b0;
    t0_waddr = 4'd0;
    t0_wdata = 2'b00;

    #20;
    t0_reset = 1'b0;

    #10;
    `VC_TEST_EQ( "Reset data correct?", t0_rdata, 2'b10  )

    #10;
    t0_wen   = 1'b1;
    t0_waddr = 4'd0;
    t0_wdata = 2'b01;

    #10;
    t0_wen   = 1'b0;
    t0_raddr = 4'd0;
    #1;
    `VC_TEST_EQ( "Read data correct?", t0_rdata, 2'b01  )

    #9;
    t0_wen   = 1'b1;
    t0_waddr = 4'd4;
    t0_wdata = 2'b11;

    #10;
    t0_wen   = 1'b0;
    t0_raddr = 4'd4;
    #1;
    `VC_TEST_EQ( "Read data correct?", t0_rdata, 2'b11  )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule

