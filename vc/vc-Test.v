//========================================================================
// Macros for unit tests
//========================================================================
// This file contains various macros to help write unit tests for
// small verilog blocks. Here is a simple example of a test harness
// for a two input mux.
//
// `include "vc-Test.v"
//
// module tester;
//
//  reg clk = 1;
//  always #5 clk = ~clk;
//
//  `VC_TEST_SUITE_BEGIN( "vc_Muxes" );
//
//  reg  [31:0] mux2_in0, mux2_in1;
//  reg         mux2_sel;
//  wire [31:0] mux2_out;
//
//  vc_Mux2#(32) mux2( mux2_in0, mux2_in1, mux2_sel, mux2_out );
//
//  `VC_TEST_CASE_BEGIN( 0, "vc_Mux2" )
//  begin
//
//    mux2_in0 = 32'h0a0a0a0a;
//    mux2_in1 = 32'hb0b0b0b0;
//
//    mux2_sel = 1'd0; #25;
//    `VC_TEST_EQ( "sel == 0", mux2_out, 32'h0a0a0a0a )
//
//   mux2_sel = 1'd1; #25;
//    `VC_TEST_EQ( "sel == 1", mux2_out, 32'hb0b0b0b0 )
//
//  end
//  `VC_TEST_CASE_END
//
//  `VC_TEST_SUITE_END( 1 )
// endmodule
//
// Note that you need a clk even if you are only testing a
// combinational block since the test infrastructure includes a
// clocked state element. Each of the macros are discussed in more
// detail below.
//
// By default only checks which fail are displayed. The user can
// specify verbose output using the +verbose=1 command line parameter.
// When verbose output is enabled, all checks are displayed regardless
// of whether or not they pass or fail.

`ifndef VC_TEST_V
`define VC_TEST_V

//------------------------------------------------------------------------
// VC_TEST_SUITE_BEGIN( suite-name )
//------------------------------------------------------------------------
// The single parameter should be a quoted string indicating the name of
// the test suite.

`define VC_TEST_SUITE_BEGIN( name )                                     \
  reg          clk = 1;                                                 \
  reg    [1:0] verbose;                                                 \
  reg [1023:0] test_case_num = 0;                                       \
  reg [1023:0] next_test_case_num = 0;                                  \
  initial begin                                                         \
    if ( !$value$plusargs( "verbose=%d", verbose ) ) begin              \
      verbose = 0;                                                      \
    end                                                                 \
    $display("");                                                       \
    $display(" Entering Test Suite: %s", name );                        \
  end                                                                   \
  always #5 clk = ~clk;                                                 \
  always @(*)                                                           \
    if ( test_case_num == 0 )                                           \
    begin                                                               \
      #100;                                                             \
      next_test_case_num = test_case_num + 1;                           \
    end                                                                 \
  always @( posedge clk )                                               \
    test_case_num <= next_test_case_num;

//------------------------------------------------------------------------
// VC_TEST_SUITE_END( total-num-test-cases )
//------------------------------------------------------------------------
// You must include this macro at the end of the tester module right
// before endmodule. The single parameter should be the number of test
// cases in the suite. Note that a very common mistake is to not put
// the right number here - double check!

`define VC_TEST_SUITE_END( finalnum )                                   \
  always @(*)                                                           \
    if ( test_case_num == (finalnum+1) )                                \
    begin #25;                                                          \
      $display("");                                                     \
      $finish;                                                          \
    end

//------------------------------------------------------------------------
// VC_TEST_CASE_BEGIN( test-case-num, test-case-name )
//------------------------------------------------------------------------
// This should directly proceed a begin-end block which contains the
// actual test case code. The test-case-num must be an increasing
// number and it must be unique. It is very easy to accidently reuse a
// test case number and this will cause multiple test cases to run
// concurrently jumbling the corresponding output.

`define VC_TEST_CASE_BEGIN( num, name )                                 \
  always @(*) begin                                                     \
    if ( test_case_num == num ) begin                                   \
      $display( "  + Running Test Case: %s", name );

//------------------------------------------------------------------------
// VC_TEST_CASE_END
//------------------------------------------------------------------------
// This should directly follow the begin-end block for the test case.

`define VC_TEST_CASE_END                                                \
      next_test_case_num = test_case_num + 1;                           \
    end                                                                 \
  end

//------------------------------------------------------------------------
// VC_TEST_NOTE( msg )
//------------------------------------------------------------------------
// Output some text only if verbose

`define VC_TEST_NOTE( msg )                                             \
  if ( verbose > 0 )                                                    \
    $display( "     [ -note- ] %s", msg );

//------------------------------------------------------------------------
// VC_TEST_CHECK( check-name, test )
//------------------------------------------------------------------------
// This macro is used to check that some condition is true. The name
// is used in the test output. It should be unique to help make it
// easier to debug test failures.

`define VC_TEST_CHECK( name, boolean )                                  \
   if ( boolean )                                                       \
     begin                                                              \
       if ( verbose > 1 )                                               \
         $display( "     [ passed ] Test ( %s ) succeeded ", name );    \
     end                                                                \
   else                                                                 \
     $display( "     [ FAILED ] Test ( %s ) failed", name );

//------------------------------------------------------------------------
// VC_TEST_EQ( check-name, tval, cval )
//------------------------------------------------------------------------
// This macro is used to check that tval == cval. The name is used in
// the test output. It should be unique to help make it easier to
// debug test failures.

`define VC_TEST_EQ( name, tval, cval )                                  \
  casez ( tval )                                                        \
    cval :                                                              \
      if ( verbose > 1 )                                                \
         $display(                                                      \
           "     [ passed ] Test ( %s ) succeeded, [ %x == %x ]",       \
           name, tval, cval );                                          \
    default :                                                           \
     $display(                                                          \
       "     [ FAILED ] Test ( %s ) failed, [ %x != %x ]",              \
       name, tval, cval );                                              \
  endcase

//------------------------------------------------------------------------
// VC_TEST_EQ2( check-name, tval1, cval1, tval2, cval2 )
//------------------------------------------------------------------------
// This macro is used to check that tval1 == cval1, tval2 == cval2. The
// name is used in the test output. It should be unique to help make it
// easier to debug test failures.

`define VC_TEST_EQ2( name, tval1, cval1, tval2, cval2 )                 \
  casez ( { tval1, tval2 } )                                            \
    { cval1, cval2 } :                                                  \
      if ( verbose > 1 )                                                \
        $display(                                                       \
          "     [ passed ] Test ( %s ) succeeded, [ %x == %x | %x == %x ]", \
          name, tval1, cval1, tval2, cval2 );                           \
    default :                                                           \
      $display(                                                         \
        "     [ FAILED ] Test ( %s ) failed,    [ %x != %x | %x != %x ]", \
        name, tval1, cval1, tval2, cval2 );                             \
  endcase

//------------------------------------------------------------------------
// VC_TEST_EQ3( check-name, tval1, cval1, tval2, cval2, tval3, cval3 )
//------------------------------------------------------------------------
// This macro is used to check that tval1 == cval1, tval2 == cval2, etc
// The name is used in the test output. It should be unique to help make
// it easier to debug test failures.

`define VC_TEST_EQ3( name, tval1, cval1, tval2, cval2, tval3, cval3 )   \
  casez ( { tval1, tval2, tval3 } )                                     \
    { cval1, cval2, cval3 } :                                           \
      if ( verbose > 1 )                                                \
        $display(                                                       \
          "     [ passed ] Test ( %s ) succeeded, [ %x == %x | %x == %x | %x == %x ]", \
          name, tval1, cval1, tval2, cval2, tval3, cval3 );             \
    default :                                                           \
      $display(                                                         \
        "     [ FAILED ] Test ( %s ) failed,    [ %x != %x | %x != %x | %x != %x ]", \
          name, tval1, cval1, tval2, cval2, tval3, cval3 );             \
  endcase

//------------------------------------------------------------------------
// VC_TEST_EQ4( check-name, tval1, cval1, tval2, cval2, tval3, cval3, tval4, cval4 )
//------------------------------------------------------------------------
// This macro is used to check that tval1 == cval1, tval2 == cval2, etc
// The name is used in the test output. It should be unique to help make
// it easier to debug test failures.

`define VC_TEST_EQ4( name, tval1, cval1, tval2, cval2, tval3, cval3, tval4, cval4 ) \
  casez ( { tval1, tval2, tval3, tval4 } )                              \
    { cval1, cval2, cval3, cval4 } :                                    \
      if ( verbose > 1 )                                                \
        $display(                                                       \
          "     [ passed ] Test ( %s ) succeeded, [ %x == %x | %x == %x | %x == %x | %x == %x ]", \
          name, tval1, cval1, tval2, cval2, tval3, cval3, tval4, cval4 ); \
    default :                                                           \
      $display(                                                         \
        "     [ FAILED ] Test ( %s ) failed,    [ %x != %x | %x != %x | %x != %x | %x != %x ]", \
        name, tval1, cval1, tval2, cval2, tval3, cval3, tval4, cval4 ); \
  endcase

//------------------------------------------------------------------------
// VC_TEST_NEQ( check-name, tval, cval )
//------------------------------------------------------------------------
// This macro is used to check that tval != cval. The name is used in
// the test output. It should be unique to help make it easier to
// debug test failures.

`define VC_TEST_NEQ( name, tval, cval )                                 \
   if ( tval != cval )                                                  \
     begin                                                              \
       if ( verbose > 1 )                                               \
         $display(                                                      \
           "     [ passed ] Test ( %s ) succeeded, [ %x != %x ]",       \
           name, tval, cval );                                          \
     end                                                                \
   else                                                                 \
     $display(                                                          \
       "     [ FAILED ] Test ( %s ) failed, [ %x == %x ]",              \
       name, tval, cval );

`endif

