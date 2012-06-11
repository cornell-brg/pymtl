//========================================================================
// Tests for Register Files
//========================================================================

`include "vc-Regfiles.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-Regfiles" )

  //----------------------------------------------------------------------
  // Test vcRegfile_1w1r_pf
  //----------------------------------------------------------------------

  localparam T1_DATA_SZ = 8;
  localparam T1_ENTRIES = 5;
  localparam T1_ADDR_SZ = 3;

  reg  [T1_ADDR_SZ-1:0] t1_raddr;
  wire [T1_DATA_SZ-1:0] t1_rdata;
  reg                   t1_wen = 0;
  reg  [T1_ADDR_SZ-1:0] t1_waddr;
  reg  [T1_DATA_SZ-1:0] t1_wdata;

  vc_Regfile_1w1r_pf#(T1_DATA_SZ,T1_ENTRIES,T1_ADDR_SZ) t1_regfile
  (
    .clk     (clk),
    .raddr   (t1_raddr),
    .rdata   (t1_rdata),
    .wen_p   (t1_wen),
    .waddr_p (t1_waddr),
    .wdata_p (t1_wdata)
  );

  // Helper task

  task t1_do_test
  (
    input [22*8-1:0]       test_case_str,
    input [T1_ADDR_SZ-1:0] tst_raddr,
    input [T1_DATA_SZ-1:0] tst_rdata,
    input                  tst_wen,
    input [T1_ADDR_SZ-1:0] tst_waddr,
    input [T1_DATA_SZ-1:0] tst_wdata
  );
  begin
    t1_raddr = tst_raddr;
    t1_wen   = tst_wen;
    t1_waddr = tst_waddr;
    t1_wdata = tst_wdata;
    #1;
    `VC_TEST_NOTE( test_case_str )
    `VC_TEST_EQ( "rdata", t1_rdata, tst_rdata )
    #9;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "vc_Regfile_1w1r_pf" )
  begin

    #1;

    //                                      -- read --  --- write ---
    //                                      addr data   wen addr data

    t1_do_test( "          |           ",   'hx, 'h??,   0, 'hx, 'hxx );

    // Write an entry and read it

    t1_do_test( "          | write 0 aa",   'hx, 'h??,   1,  0,  'haa );
    t1_do_test( "read 0 aa |           ",    0,  'haa,   0, 'hx, 'hxx );

    // Fill with entries then read

    t1_do_test( "          | write 0 aa",   'hx, 'h??,   1,  0,  'haa );
    t1_do_test( "          | write 1 bb",   'hx, 'h??,   1,  1,  'hbb );
    t1_do_test( "          | write 2 cc",   'hx, 'h??,   1,  2,  'hcc );
    t1_do_test( "          | write 3 dd",   'hx, 'h??,   1,  3,  'hdd );
    t1_do_test( "          | write 4 ee",   'hx, 'h??,   1,  4,  'hee );

    t1_do_test( "read 0 aa |           ",    0,  'haa,   0, 'hx, 'hxx );
    t1_do_test( "read 1 bb |           ",    1,  'hbb,   0, 'hx, 'hxx );
    t1_do_test( "read 2 cc |           ",    2,  'hcc,   0, 'hx, 'hxx );
    t1_do_test( "read 3 dd |           ",    3,  'hdd,   0, 'hx, 'hxx );
    t1_do_test( "read 4 ee |           ",    4,  'hee,   0, 'hx, 'hxx );

    // Overwrite entries and read again

    t1_do_test( "          | write 0 00",   'hx, 'h??,   1,  0,  'h00 );
    t1_do_test( "          | write 1 11",   'hx, 'h??,   1,  1,  'h11 );
    t1_do_test( "          | write 2 22",   'hx, 'h??,   1,  2,  'h22 );
    t1_do_test( "          | write 3 33",   'hx, 'h??,   1,  3,  'h33 );
    t1_do_test( "          | write 4 44",   'hx, 'h??,   1,  4,  'h44 );

    t1_do_test( "read 0 00 |           ",    0,  'h00,   0, 'hx, 'hxx );
    t1_do_test( "read 1 11 |           ",    1,  'h11,   0, 'hx, 'hxx );
    t1_do_test( "read 2 22 |           ",    2,  'h22,   0, 'hx, 'hxx );
    t1_do_test( "read 3 33 |           ",    3,  'h33,   0, 'hx, 'hxx );
    t1_do_test( "read 4 44 |           ",    4,  'h44,   0, 'hx, 'hxx );

    // Concurrent read/writes (to different addr)

    t1_do_test( "read 1 11 | write 0 0a",    1,  'h11,   1,  0,  'h0a );
    t1_do_test( "read 2 22 | write 1 1b",    2,  'h22,   1,  1,  'h1b );
    t1_do_test( "read 3 33 | write 2 2c",    3,  'h33,   1,  2,  'h2c );
    t1_do_test( "read 4 44 | write 3 3d",    4,  'h44,   1,  3,  'h3d );
    t1_do_test( "read 0 0a | write 4 4e",    0,  'h0a,   1,  4,  'h4e );

    // Concurrent read/writes (to same addr)

    t1_do_test( "read 0 0a | write 0 5a",    0,  'h0a,   1,  0,  'h5a );
    t1_do_test( "read 1 1b | write 1 6b",    1,  'h1b,   1,  1,  'h6b );
    t1_do_test( "read 2 2c | write 2 7c",    2,  'h2c,   1,  2,  'h7c );
    t1_do_test( "read 3 3d | write 3 8d",    3,  'h3d,   1,  3,  'h8d );
    t1_do_test( "read 4 4e | write 4 9e",    4,  'h4e,   1,  4,  'h9e );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule

