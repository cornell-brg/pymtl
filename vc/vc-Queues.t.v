//========================================================================
// Tests for Queues
//========================================================================

`include "vc-Queues.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Queues" )

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(NORMAL,1)
  //----------------------------------------------------------------------

  reg        t1_reset = 1;
  reg  [7:0] t1_enq_bits;
  reg        t1_enq_val = 0;
  wire       t1_enq_rdy;
  wire [7:0] t1_deq_bits;
  wire       t1_deq_val;
  reg        t1_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_NORMAL,8,1) t1_queue
  (
    .clk      (clk),
    .reset    (t1_reset),
    .enq_bits (t1_enq_bits),
    .enq_val  (t1_enq_val),
    .enq_rdy  (t1_enq_rdy),
    .deq_bits (t1_deq_bits),
    .deq_val  (t1_deq_val),
    .deq_rdy  (t1_deq_rdy)
  );

  // Task to perform test and verify results

  task t1_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t1_enq_bits = enq_bits; t1_enq_val = enq_val; t1_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t1_enq_rdy, enq_rdy,
                  t1_deq_bits, deq_bits, t1_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_Queue_pf(NORMAL,1)" )
  begin

    #1;  t1_reset = 1'b1;
    #20; t1_reset = 1'b0;

    // Enque one element and then dequeue it

    t1_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1 );
    t1_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 0,  8'h01, 1, 1 );
    t1_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 0 );

    // Fill queue and then do enq/deq at same time

    t1_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0 );
    t1_do_test( "[03]    Q(1) [02]   ", 8'h03, 1, 0,  8'h02, 1, 0 );
    t1_do_test( "[  ]    Q(1) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t1_do_test( "[03]    Q(1) [02] ->", 8'h03, 1, 0,  8'h02, 1, 1 );
    t1_do_test( "[03] -> Q(0) [02]   ", 8'h03, 1, 1,  8'h??, 0, 1 );
    t1_do_test( "[04]    Q(1) [03] ->", 8'h04, 1, 0,  8'h03, 1, 1 );
    t1_do_test( "[04] -> Q(0) [03]   ", 8'h04, 1, 1,  8'h??, 0, 1 );
    t1_do_test( "[  ]    Q(1) [04] ->", 8'hxx, 0, 0,  8'h04, 1, 1 );
    t1_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(PIPE,1)
  //----------------------------------------------------------------------

  reg        t2_reset = 1;
  reg  [7:0] t2_enq_bits;
  reg        t2_enq_val = 0;
  wire       t2_enq_rdy;
  wire [7:0] t2_deq_bits;
  wire       t2_deq_val;
  reg        t2_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_PIPE,8,1) t2_queue
  (
    .clk      (clk),
    .reset    (t2_reset),
    .enq_bits (t2_enq_bits),
    .enq_val  (t2_enq_val),
    .enq_rdy  (t2_enq_rdy),
    .deq_bits (t2_deq_bits),
    .deq_val  (t2_deq_val),
    .deq_rdy  (t2_deq_rdy)
  );

  // Task to perform test and verify results

  task t2_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t2_enq_bits = enq_bits; t2_enq_val = enq_val; t2_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t2_enq_rdy, enq_rdy,
                  t2_deq_bits, deq_bits, t2_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "vc_Queue_pf(PIPE,1)" )
  begin

    #1;  t2_reset = 1'b1;
    #20; t2_reset = 1'b0;

    // Enque one element and then dequeue it

    t2_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1 );
    t2_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 1,  8'h01, 1, 1 );
    t2_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 0 );

    // Fill queue and then do enq/deq at same time

    t2_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0 );
    t2_do_test( "[03]    Q(1) [02]   ", 8'h03, 1, 0,  8'h02, 1, 0 );
    t2_do_test( "[  ]    Q(1) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t2_do_test( "[03] -> Q(1) [02] ->", 8'h03, 1, 1,  8'h02, 1, 1 );
    t2_do_test( "[04] -> Q(1) [03] ->", 8'h04, 1, 1,  8'h03, 1, 1 );
    t2_do_test( "[  ]    Q(1) [04] ->", 8'hxx, 0, 1,  8'h04, 1, 1 );
    t2_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(BYPASS,1)
  //----------------------------------------------------------------------

  reg        t3_reset = 1;
  reg  [7:0] t3_enq_bits;
  reg        t3_enq_val = 0;
  wire       t3_enq_rdy;
  wire [7:0] t3_deq_bits;
  wire       t3_deq_val;
  reg        t3_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_BYPASS,8,1) t3_queue
  (
    .clk      (clk),
    .reset    (t3_reset),
    .enq_bits (t3_enq_bits),
    .enq_val  (t3_enq_val),
    .enq_rdy  (t3_enq_rdy),
    .deq_bits (t3_deq_bits),
    .deq_val  (t3_deq_val),
    .deq_rdy  (t3_deq_rdy)
  );

  // Task to perform test and verify results

  task t3_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t3_enq_bits = enq_bits; t3_enq_val = enq_val; t3_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t3_enq_rdy, enq_rdy,
                  t3_deq_bits, deq_bits, t3_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 3, "vc_Queue_pf(BYPASS,1)" )
  begin

    #1;  t3_reset = 1'b1;
    #20; t3_reset = 1'b0;

    // Enque one element and then dequeue it

    t3_do_test( "[01] -> Q(0) [01] ->", 8'h01, 1, 1,  8'h01, 1, 1 );
    t3_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'hxx, 0, 0 );

    // Fill queue and then do enq/deq at same time

    t3_do_test( "[02] -> Q(0) [02]   ", 8'h02, 1, 1,  8'h02, 1, 0 );
    t3_do_test( "[03]    Q(1) [02]   ", 8'h03, 1, 0,  8'h02, 1, 0 );
    t3_do_test( "[  ]    Q(1) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t3_do_test( "[03]    Q(1) [02] ->", 8'h03, 1, 0,  8'h02, 1, 1 );
    t3_do_test( "[03] -> Q(0) [03] ->", 8'h03, 1, 1,  8'h03, 1, 1 );
    t3_do_test( "[04] -> Q(0) [04] ->", 8'h04, 1, 1,  8'h04, 1, 1 );
    t3_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(NORMAL,3)
  //----------------------------------------------------------------------

  reg        t4_reset = 1;
  reg  [7:0] t4_enq_bits;
  reg        t4_enq_val = 0;
  wire       t4_enq_rdy;
  wire [7:0] t4_deq_bits;
  wire       t4_deq_val;
  reg        t4_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_NORMAL,8,3,2) t4_queue
  (
    .clk      (clk),
    .reset    (t4_reset),
    .enq_bits (t4_enq_bits),
    .enq_val  (t4_enq_val),
    .enq_rdy  (t4_enq_rdy),
    .deq_bits (t4_deq_bits),
    .deq_val  (t4_deq_val),
    .deq_rdy  (t4_deq_rdy)
  );

  // Task to perform test and verify results

  task t4_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t4_enq_bits = enq_bits; t4_enq_val = enq_val; t4_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t4_enq_rdy, enq_rdy,
                  t4_deq_bits, deq_bits, t4_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 4, "vc_Queue_pf(NORMAL,3)" )
  begin

    #1;  t4_reset = 1'b1;
    #20; t4_reset = 1'b0;

    // Enque one element and then dequeue it

    t4_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1 );
    t4_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 1,  8'h01, 1, 1 );
    t4_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 0 );

    // Fill queue and then do enq/deq at same time

    t4_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0 );
    t4_do_test( "[03] -> Q(1) [02]   ", 8'h03, 1, 1,  8'h02, 1, 0 );
    t4_do_test( "[04] -> Q(2) [02]   ", 8'h04, 1, 1,  8'h02, 1, 0 );
    t4_do_test( "[05]    Q(3) [02]   ", 8'h05, 1, 0,  8'h02, 1, 0 );
    t4_do_test( "[  ]    Q(3) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t4_do_test( "[05]    Q(3) [02] ->", 8'h05, 1, 0,  8'h02, 1, 1 );
    t4_do_test( "[05] -> Q(2) [03] ->", 8'h05, 1, 1,  8'h03, 1, 1 );
    t4_do_test( "[06] -> Q(2) [04] ->", 8'h06, 1, 1,  8'h04, 1, 1 );
    t4_do_test( "[07] -> Q(2) [05] ->", 8'h07, 1, 1,  8'h05, 1, 1 );
    t4_do_test( "[  ]    Q(2) [06] ->", 8'hxx, 0, 1,  8'h06, 1, 1 );
    t4_do_test( "[  ]    Q(1) [07] ->", 8'hxx, 0, 1,  8'h07, 1, 1 );
    t4_do_test( "[  ]    Q(0) [  ] ->", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(PIPE,3)
  //----------------------------------------------------------------------

  reg        t5_reset = 1;
  reg  [7:0] t5_enq_bits;
  reg        t5_enq_val = 0;
  wire       t5_enq_rdy;
  wire [7:0] t5_deq_bits;
  wire       t5_deq_val;
  reg        t5_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_PIPE,8,3,2) t5_queue
  (
    .clk      (clk),
    .reset    (t5_reset),
    .enq_bits (t5_enq_bits),
    .enq_val  (t5_enq_val),
    .enq_rdy  (t5_enq_rdy),
    .deq_bits (t5_deq_bits),
    .deq_val  (t5_deq_val),
    .deq_rdy  (t5_deq_rdy)
  );

  // Task to perform test and verify results

  task t5_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t5_enq_bits = enq_bits; t5_enq_val = enq_val; t5_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t5_enq_rdy, enq_rdy,
                  t5_deq_bits, deq_bits, t5_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 5, "vc_Queue_pf(PIPE,3)" )
  begin

    #1;  t5_reset = 1'b1;
    #20; t5_reset = 1'b0;

    // Enque one element and then dequeue it

    t5_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1 );
    t5_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 1,  8'h01, 1, 1 );
    t5_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1 );

    // Fill queue and then do enq/deq at same time

    t5_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0 );
    t5_do_test( "[03] -> Q(1) [02]   ", 8'h03, 1, 1,  8'h02, 1, 0 );
    t5_do_test( "[04] -> Q(2) [02]   ", 8'h04, 1, 1,  8'h02, 1, 0 );
    t5_do_test( "[05]    Q(3) [02]   ", 8'h05, 1, 0,  8'h02, 1, 0 );
    t5_do_test( "[  ]    Q(3) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t5_do_test( "[05] -> Q(3) [02] ->", 8'h05, 1, 1,  8'h02, 1, 1 );
    t5_do_test( "[06] -> Q(3) [03] ->", 8'h06, 1, 1,  8'h03, 1, 1 );
    t5_do_test( "[07] -> Q(3) [04] ->", 8'h07, 1, 1,  8'h04, 1, 1 );
    t5_do_test( "[  ] -> Q(3) [05] ->", 8'hxx, 0, 1,  8'h05, 1, 1 );
    t5_do_test( "[  ]    Q(2) [06] ->", 8'hxx, 0, 1,  8'h06, 1, 1 );
    t5_do_test( "[  ]    Q(1) [07] ->", 8'hxx, 0, 1,  8'h07, 1, 1 );
    t5_do_test( "[  ]    Q(0) [  ] ->", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_Queue_pf(BYPASS,3)
  //----------------------------------------------------------------------

  reg        t6_reset = 1;
  reg  [7:0] t6_enq_bits;
  reg        t6_enq_val = 0;
  wire       t6_enq_rdy;
  wire [7:0] t6_deq_bits;
  wire       t6_deq_val;
  reg        t6_deq_rdy = 0;

  vc_Queue_pf#(`VC_QUEUE_BYPASS,8,3,2) t6_queue
  (
    .clk      (clk),
    .reset    (t6_reset),
    .enq_bits (t6_enq_bits),
    .enq_val  (t6_enq_val),
    .enq_rdy  (t6_enq_rdy),
    .deq_bits (t6_deq_bits),
    .deq_val  (t6_deq_val),
    .deq_rdy  (t6_deq_rdy)
  );

  // Task to perform test and verify results

  task t6_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy
  );
  begin
    t6_enq_bits = enq_bits; t6_enq_val = enq_val; t6_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ3( test_case_str, t6_enq_rdy, enq_rdy,
                  t6_deq_bits, deq_bits, t6_deq_val, deq_val )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 6, "vc_Queue_pf(BYPASS,3)" )
  begin

    #1;  t6_reset = 1'b1;
    #20; t6_reset = 1'b0;

    // Enque one element and then dequeue it

    t6_do_test( "[01] -> Q(0) [01]   ", 8'h01, 1, 1,  8'h01, 1, 1 );
    t6_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1 );

    // Fill queue and then do enq/deq at same time

    t6_do_test( "[02] -> Q(0) [02]   ", 8'h02, 1, 1,  8'h02, 1, 0 );
    t6_do_test( "[03] -> Q(1) [02]   ", 8'h03, 1, 1,  8'h02, 1, 0 );
    t6_do_test( "[04] -> Q(2) [02]   ", 8'h04, 1, 1,  8'h02, 1, 0 );
    t6_do_test( "[05]    Q(3) [02]   ", 8'h05, 1, 0,  8'h02, 1, 0 );
    t6_do_test( "[  ]    Q(3) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0 );
    t6_do_test( "[05] -> Q(3) [02] ->", 8'h05, 1, 0,  8'h02, 1, 1 );
    t6_do_test( "[06] -> Q(3) [03] ->", 8'h05, 1, 1,  8'h03, 1, 1 );
    t6_do_test( "[07] -> Q(3) [04] ->", 8'h06, 1, 1,  8'h04, 1, 1 );
    t6_do_test( "[  ] -> Q(3) [05] ->", 8'h07, 1, 1,  8'h05, 1, 1 );
    t6_do_test( "[  ]    Q(2) [06] ->", 8'hxx, 0, 1,  8'h06, 1, 1 );
    t6_do_test( "[  ]    Q(1) [07] ->", 8'hxx, 0, 1,  8'h07, 1, 1 );
    t6_do_test( "[  ]    Q(0) [  ] ->", 8'hxx, 0, 1,  8'h??, 0, 1 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_SkidQueue_pf(NORMAL,3)
  //----------------------------------------------------------------------

  reg        t7_reset = 1;
  reg  [7:0] t7_enq_bits;
  reg        t7_enq_val = 0;
  wire       t7_enq_rdy;
  wire [7:0] t7_deq_bits;
  wire       t7_deq_val;
  reg        t7_deq_rdy = 0;
  wire [2:0] t7_num_free_entries;

  vc_SkidQueue_pf#(`VC_QUEUE_NORMAL,8,3,2) t7_queue
  (
    .clk              (clk),
    .reset            (t7_reset),
    .enq_bits         (t7_enq_bits),
    .enq_val          (t7_enq_val),
    .enq_rdy          (t7_enq_rdy),
    .deq_bits         (t7_deq_bits),
    .deq_val          (t7_deq_val),
    .deq_rdy          (t7_deq_rdy),
    .num_free_entries (t7_num_free_entries)
  );

  // Task to perform test and verify results

  task t7_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy,
    input [2:0] num_free_entries
  );
  begin
    t7_enq_bits = enq_bits; t7_enq_val = enq_val; t7_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ4( test_case_str, t7_enq_rdy, enq_rdy,
                  t7_deq_bits, deq_bits, t7_deq_val, deq_val,
                  t7_num_free_entries, num_free_entries )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 7, "vc_SkidQueue_pf(NORMAL,3)" )
  begin

    #1;  t7_reset = 1'b1;
    #20; t7_reset = 1'b0;

    // Enque one element and then dequeue it

    t7_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1,  3 );
    t7_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 1,  8'h01, 1, 1,  2 );
    t7_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 0,  3 );

    // Fill queue and then do enq/deq at same time

    t7_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0,  3 );
    t7_do_test( "[03] -> Q(1) [02]   ", 8'h03, 1, 1,  8'h02, 1, 0,  2 );
    t7_do_test( "[04] -> Q(2) [02]   ", 8'h04, 1, 1,  8'h02, 1, 0,  1 );
    t7_do_test( "[05]    Q(3) [02]   ", 8'h05, 1, 0,  8'h02, 1, 0,  0 );
    t7_do_test( "[  ]    Q(3) [02]   ", 8'hxx, 0, 0,  8'h02, 1, 0,  0 );
    t7_do_test( "[05]    Q(3) [02] ->", 8'h05, 1, 0,  8'h02, 1, 1,  0 );
    t7_do_test( "[05] -> Q(2) [03] ->", 8'h05, 1, 1,  8'h03, 1, 1,  1 );
    t7_do_test( "[06] -> Q(2) [04] ->", 8'h06, 1, 1,  8'h04, 1, 1,  1 );
    t7_do_test( "[07] -> Q(2) [05] ->", 8'h07, 1, 1,  8'h05, 1, 1,  1 );
    t7_do_test( "[  ]    Q(2) [06] ->", 8'hxx, 0, 1,  8'h06, 1, 1,  1 );
    t7_do_test( "[  ]    Q(1) [07] ->", 8'hxx, 0, 1,  8'h07, 1, 1,  2 );
    t7_do_test( "[  ]    Q(0) [  ] ->", 8'hxx, 0, 1,  8'h??, 0, 1,  3 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // Test vc_DelaySkidQueue_pf(5,NORMAL,3)
  //----------------------------------------------------------------------

  reg        t8_reset = 1;
  reg  [7:0] t8_enq_bits;
  reg        t8_enq_val = 0;
  wire       t8_enq_rdy;
  wire [7:0] t8_deq_bits;
  wire       t8_deq_val;
  reg        t8_deq_rdy = 0;
  wire [2:0] t8_num_free_entries;

  vc_DelaySkidQueue_pf
  #(
    .DELAY     (5),
    .TYPE      (`VC_QUEUE_NORMAL),
    .DATA_SZ   (8),
    .ENTRIES   (3),
    .ADDR_SZ   (2)
  )
  t8_queue
  (
    .clk              (clk),
    .reset            (t8_reset),
    .enq_bits         (t8_enq_bits),
    .enq_val          (t8_enq_val),
    .enq_rdy          (t8_enq_rdy),
    .deq_bits         (t8_deq_bits),
    .deq_val          (t8_deq_val),
    .deq_rdy          (t8_deq_rdy),
    .num_free_entries (t8_num_free_entries)
  );

  // Task to perform test and verify results

  task t8_do_test
  (
    input [20*8-1:0] test_case_str,
    input [7:0] enq_bits, input enq_val, input enq_rdy,
    input [7:0] deq_bits, input deq_val, input deq_rdy,
    input [2:0] num_free_entries
  );
  begin
    t8_enq_bits = enq_bits; t8_enq_val = enq_val; t8_deq_rdy = deq_rdy;
    #1;
    `VC_TEST_EQ4( test_case_str, t8_enq_rdy, enq_rdy,
                  t8_deq_bits, deq_bits, t8_deq_val, deq_val,
                  t8_num_free_entries, num_free_entries )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 8, "vc_DelaySkidQueue_pf(5,NORMAL,3)" )
  begin

    #1;  t8_reset = 1'b1;
    #20; t8_reset = 1'b0;

    // Enque one element and then dequeue it

    t8_do_test( "[01] -> Q(0) [  ]   ", 8'h01, 1, 1,  8'h??, 0, 1,  3 );
    t8_do_test( "[  ]    Q(1) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1,  2 );
    t8_do_test( "[  ]    Q(1) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1,  2 );
    t8_do_test( "[  ]    Q(1) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1,  2 );
    t8_do_test( "[  ]    Q(1) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1,  2 );
    t8_do_test( "[  ]    Q(1) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 1,  2 );
    t8_do_test( "[  ]    Q(1) [01] ->", 8'hxx, 0, 1,  8'h01, 1, 1,  2 );
    t8_do_test( "[  ]    Q(0) [  ]   ", 8'hxx, 0, 1,  8'h??, 0, 0,  3 );

    // Fill queue and then do enq/deq at same time

    t8_do_test( "[02] -> Q(0) [  ]   ", 8'h02, 1, 1,  8'h??, 0, 0,  3 );
    t8_do_test( "[03] -> Q(1) [  ]   ", 8'h03, 1, 1,  8'h??, 0, 0,  2 );
    t8_do_test( "[04] -> Q(2) [  ]   ", 8'h04, 1, 1,  8'h??, 0, 0,  1 );
    t8_do_test( "[05]    Q(3) [  ]   ", 8'h05, 1, 0,  8'h??, 0, 0,  0 );
    t8_do_test( "[  ]    Q(3) [  ]   ", 8'hxx, 0, 0,  8'h??, 0, 0,  0 );
    t8_do_test( "[  ]    Q(3) [  ]   ", 8'hxx, 0, 0,  8'h??, 0, 0,  0 );
    t8_do_test( "[05]    Q(3) [02] ->", 8'h05, 1, 0,  8'h02, 1, 1,  0 );
    t8_do_test( "[05] -> Q(2) [  ]   ", 8'h05, 1, 1,  8'h??, 0, 1,  1 );
    t8_do_test( "[06]    Q(3) [  ]   ", 8'h06, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[06]    Q(3) [  ]   ", 8'h06, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[06]    Q(3) [  ]   ", 8'h06, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[06]    Q(3) [  ]   ", 8'h06, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[06]    Q(3) [03] ->", 8'h06, 1, 0,  8'h03, 1, 1,  0 );
    t8_do_test( "[06] -> Q(2) [  ]   ", 8'h06, 1, 1,  8'h??, 0, 1,  1 );
    t8_do_test( "[07]    Q(3) [  ]   ", 8'h07, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[07]    Q(3) [  ]   ", 8'h07, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[07]    Q(3) [  ]   ", 8'h07, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[07]    Q(3) [  ]   ", 8'h07, 1, 0,  8'h??, 0, 1,  0 );
    t8_do_test( "[07]    Q(3) [04] ->", 8'h07, 1, 0,  8'h04, 1, 1,  0 );
    t8_do_test( "[07] -> Q(2) [  ]   ", 8'h07, 1, 1,  8'h??, 0, 1,  1 );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 8 )
endmodule

