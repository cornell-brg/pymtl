//========================================================================
// Tests for SRAMs
//========================================================================

`include "vc-SRAMs.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-SRAMs" )

  //----------------------------------------------------------------------
  // Test vc_SRAM_1rw
  //----------------------------------------------------------------------

  reg         t0_en;
  reg         t0_write_en;
  reg   [3:0] t0_byte_en;
  reg   [4:0] t0_addr;
  reg  [31:0] t0_write_data;
  wire [31:0] t0_read_data;

  vc_SRAM_1rw#(32,32) t0_sram
  (
    .clk        (clk),
    .en         (t0_en),
    .write_en   (t0_write_en),
    .byte_en    (t0_byte_en),
    .addr       (t0_addr),
    .write_data (t0_write_data),
    .read_data  (t0_read_data)
 );

  `VC_TEST_CASE_BEGIN( 1, "vc-SRAM-1rw" )
  begin

    #1;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b1111;
    t0_addr       = 5'd0;
    t0_write_data = 32'h00000000;

    #10;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'h00000000 )

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b0001;
    t0_addr       = 5'd0;
    t0_write_data = 32'hdeadbeef;

    #10;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'h000000ef )

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b0110;
    t0_addr       = 5'd0;
    t0_write_data = 32'habcdefab;

    #10;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'h00cdefef )

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b1011;
    t0_addr       = 5'd0;
    t0_write_data = 32'hff000000;

    #10;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'hffcd0000 )

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b1111;
    t0_addr       = 5'd0;
    t0_write_data = 32'hdeadbeef;

    #10;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'hdeadbeef )

    // Try disabling SRAM, write should not occur

    #10;
    t0_en         = 1'b0;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b1111;
    t0_addr       = 5'd0;
    t0_write_data = 32'hffffffff;

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'hdeadbeef )

    // Enable write then disable read, should be old data

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b1;
    t0_byte_en    = 4'b1111;
    t0_addr       = 5'd0;
    t0_write_data = 32'hffffffff;

    #10;
    t0_en         = 1'b0;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'hdeadbeef )

    // Read newly written data

    #10;
    t0_en         = 1'b1;
    t0_write_en   = 1'b0;

    #10;
    `VC_TEST_EQ( "Read data correct?", t0_read_data, 32'hffffffff )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule

