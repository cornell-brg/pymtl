//========================================================================
// Tests for vc-Misc
//========================================================================

`include "vc-Misc.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Misc" )

  //----------------------------------------------------------------------
  // Test vc_PartitionedTriBuf
  //----------------------------------------------------------------------

  wire [31:0] t1_tribuf_in = { 8'h0A, 8'h0B, 8'h0C, 8'h0D };
  reg  [ 3:0] t1_tribuf_oe;
  wire [ 7:0] t1_tribuf_out;

  vc_PartitionedTriBuf#(32,8) t1_tribuf
  (
    .in  (t1_tribuf_in),
    .oe  (t1_tribuf_oe),
    .out (t1_tribuf_out)
  );

  // Helper tasks

  task t1_do_test
  (
    input [4*8-1:0] test_case_str,
    input [3:0]     tribuf_oe,
    input [7:0]     correct_tribuf_out
  );
  begin
    t1_tribuf_oe = tribuf_oe;
    #1;
    `VC_TEST_EQ( test_case_str, t1_tribuf_out, correct_tribuf_out )
    #10;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_PartitionedTriBuf" )
  begin
    t1_do_test( "0000", 4'b0000, 8'hzz );
    t1_do_test( "0001", 4'b0001, 8'h0D );
    t1_do_test( "0010", 4'b0010, 8'h0C );
    t1_do_test( "0100", 4'b0100, 8'h0B );
    t1_do_test( "1000", 4'b1000, 8'h0A );
  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_Counter
  //--------------------------------------------------------------------

  reg        t2_reset;
  reg        t2_init_count_val;
  reg  [1:0] t2_init_count;
  reg        t2_increment;
  reg        t2_decrement;
  wire [1:0] t2_count_next;
  wire [1:0] t2_count;

  vc_Counter_pf#(2,0) t2_counter
  (
    .clk              (clk),
    .reset_p          (t2_reset),
    .init_count_val_p (t2_init_count_val),
    .init_count_p     (t2_init_count),
    .increment_p      (t2_increment),
    .decrement_p      (t2_decrement),
    .count_next       (t2_count_next),
    .count_np         (t2_count)
  );

  // Helper tasks

  task t2_do_test
  (
    input [7*8-1:0] test_case_str,
    input           init_count_val,
    input [1:0]     init_count,
    input           increment,
    input           decrement,
    input [1:0]     correct_count_next,
    input [1:0]     correct_count
  );
  begin
    t2_init_count_val = init_count_val;
    t2_init_count     = init_count;
    t2_increment      = increment;
    t2_decrement      = decrement;
    #1;

    `VC_TEST_EQ( ({test_case_str," : next count "}),
                  t2_count_next, correct_count_next )

    `VC_TEST_EQ( ({test_case_str," : count      "}),
                  t2_count,      correct_count      )

    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "vc_Counter" )
  begin

    #0;  t2_reset = 1;
    #21; t2_reset = 0;

    //                     init_count  inc   dec    next  count

    t2_do_test( "load 3 ", 1'b1, 2'd3, 1'b0, 1'b0, 2'd3,  2'd0 );
    t2_do_test( "none   ", 1'b1, 2'd3, 1'b0, 1'b0, 2'd3,  2'd3 );
    t2_do_test( "dec    ", 1'b0, 2'dx, 1'b0, 1'b1, 2'd2,  2'd3 );
    t2_do_test( "dec    ", 1'b0, 2'dx, 1'b0, 1'b1, 2'd1,  2'd2 );
    t2_do_test( "dec    ", 1'b0, 2'dx, 1'b0, 1'b1, 2'd0,  2'd1 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'd0,  2'd0 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b1, 1'b0, 2'd1,  2'd0 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b1, 1'b0, 2'd2,  2'd1 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b1, 1'b0, 2'd3,  2'd2 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b1, 1'b0, 2'd0,  2'd3 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b1, 1'b0, 2'd1,  2'd0 );
    t2_do_test( "inc    ", 1'b0, 2'dx, 1'b0, 1'b0, 2'd1,  2'd1 );
    t2_do_test( "dec/inc", 1'b0, 2'dx, 1'b1, 1'b1, 2'd1,  2'd1 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'd1,  2'd1 );
    t2_do_test( "load 0 ", 1'b1, 2'd0, 1'b1, 1'b1, 2'd0,  2'd1 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'd0,  2'd0 );

    t2_do_test( "val = x", 1'bx, 2'dx, 1'b0, 1'b0, 2'dx,  2'd0 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'dx,  2'dx );
    t2_do_test( "load 0 ", 1'b1, 2'd0, 1'b0, 1'b0, 2'd0,  2'dx );

    t2_do_test( "inc = x", 1'b0, 2'dx, 1'bx, 1'b0, 2'b0x, 2'b00 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'b0x, 2'b0x );
    t2_do_test( "load 0 ", 1'b1, 2'd0, 1'b0, 1'b0, 2'b00, 2'b0x );

    t2_do_test( "dec = x", 1'b0, 2'dx, 1'b0, 1'bx, 2'bxx, 2'b00 );
    t2_do_test( "none   ", 1'b0, 2'dx, 1'b0, 1'b0, 2'bxx, 2'bxx );
    t2_do_test( "load 0 ", 1'b1, 2'd0, 1'b0, 1'b0, 2'b00, 2'bxx );

  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_Decoder(2)
  //--------------------------------------------------------------------

  reg  [1:0] t3_in;
  wire [3:0] t3_out;

  vc_Decoder#(2,4) t3_decoder
  (
    .in  (t3_in),
    .out (t3_out)
  );

  // Helper tasks

  task t3_do_test
  (
    input [5*8-1:0] test_case_str,
    input [1:0]     in,
    input [3:0]     correct_out
  );
  begin
    t3_in = in;
    #1;
    `VC_TEST_EQ( test_case_str, t3_out, correct_out )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 3, "vc_Decoder(2)" )
  begin
    t3_do_test( "2'd0 ", 2'd0,  4'b0001 );
    t3_do_test( "2'd1 ", 2'd1,  4'b0010 );
    t3_do_test( "2'd2 ", 2'd2,  4'b0100 );
    t3_do_test( "2'd3 ", 2'd3,  4'b1000 );

    t3_do_test( "2'b0x", 2'b0x, 4'b00xx );
    t3_do_test( "2'b1x", 2'b1x, 4'bxx00 );
    t3_do_test( "2'bx0", 2'bx0, 4'b0x0x );
    t3_do_test( "2'bx1", 2'bx1, 4'bx0x0 );
    t3_do_test( "2'bxx", 2'bxx, 4'bxxxx );
  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_Decoder(2,3)
  //--------------------------------------------------------------------

  reg  [1:0] t4_in;
  wire [2:0] t4_out;

  vc_Decoder#(2,3) t4_decoder
  (
    .in  (t4_in),
    .out (t4_out)
  );

  // Helper tasks

  task t4_do_test
  (
    input [5*8-1:0] test_case_str,
    input [1:0]     in,
    input [2:0]     correct_out
  );
  begin
    t4_in = in;
    #1;
    `VC_TEST_EQ( test_case_str, t4_out, correct_out )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 4, "vc_Decoder(2,3)" )
  begin
    t4_do_test( "2'd0 ", 2'd0,  3'b001 );
    t4_do_test( "2'd1 ", 2'd1,  3'b010 );
    t4_do_test( "2'd2 ", 2'd2,  3'b100 );
    t4_do_test( "2'd3 ", 2'd3,  3'b000 );

    t4_do_test( "2'b0x", 2'b0x, 3'b0xx );
    t4_do_test( "2'b1x", 2'b1x, 3'bx00 );
    t4_do_test( "2'bx0", 2'bx0, 3'bx0x );
    t4_do_test( "2'bx1", 2'bx1, 3'b0x0 );
    t4_do_test( "2'bxx", 2'bxx, 3'bxxx );
  end
  `VC_TEST_CASE_END

  //--------------------------------------------------------------------
  // Test vc_RandomNumberGenerator
  //--------------------------------------------------------------------

  reg        t5_reset = 1;
  reg        t5_next  = 0;
  wire [4:0] t5_out;

  vc_RandomNumberGenerator#(5,32'hB9B9B9B9) t5_rng
  (
    .clk     (clk),
    .reset_p (t5_reset),
    .next_p  (t5_next),
    .out_np  (t5_out)
  );

  task t5_do_test;
  begin
    #10;
    if ( verbose )
      $display( "     [ -note- ] Random number = %x", t5_out );
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 5, "vc_RandomNumberGenerator" )
  begin

    #0;  t5_reset = 1;
    #21; t5_reset = 0;

    t5_next = 1'b1;

    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();
    t5_do_test();

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 5 )
endmodule

