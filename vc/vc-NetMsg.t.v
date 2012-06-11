//=========================================================================
// Unit Tests: Network Message
//=========================================================================

`include "vc-NetMsg.v"
`include "vc-Test.v"

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-NetMsg" )

  //-----------------------------------------------------------------------
  // TestBasic_p32_q3
  //-----------------------------------------------------------------------

  reg  [`VC_NET_MSG_SZ( 32, 3 )-1:0] t0_msg_test;
  reg  [`VC_NET_MSG_SZ( 32, 3 )-1:0] t0_msg_ref;
  wire      [`VC_NET_MSG_STR_SZ-1:0] t0_str;

  vc_NetMsgToStr#(32,3) t0_to_str
  (
    .msg (t0_msg_test),
    .str (t0_str)
  );

  task t0_do_test
  (
    input    [`VC_NET_MSG_DEST_SZ( 32, 3 )-1:0] dest,
    input     [`VC_NET_MSG_SRC_SZ( 32, 3 )-1:0] src,
    input [`VC_NET_MSG_PAYLOAD_SZ( 32, 3 )-1:0] payload
  );
  begin

    t0_msg_test[`VC_NET_MSG_DEST_FIELD( 32, 3 )]    = dest;
    t0_msg_test[`VC_NET_MSG_SRC_FIELD( 32, 3 )]     = src;
    t0_msg_test[`VC_NET_MSG_PAYLOAD_FIELD( 32, 3 )] = payload;

    t0_msg_ref = { dest, src, payload };

    #1;
    `VC_TEST_EQ( t0_str, t0_msg_test, t0_msg_ref )
    #9;

  end
  endtask

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_p32_q3" )
  begin
    t0_do_test( 3'h0, 3'h0, 32'h00000000 );
    t0_do_test( 3'h4, 3'h1, 32'h00000000 );
    t0_do_test( 3'h2, 3'h2, 32'h00000000 );
    t0_do_test( 3'h1, 3'h6, 32'h00000000 );
    t0_do_test( 3'h5, 3'h7, 32'ha0a0a0a0 );
    t0_do_test( 3'h6, 3'h5, 32'hc2c2c2c2 );
    t0_do_test( 3'h7, 3'h4, 32'hdededede );
    t0_do_test( 3'h3, 3'h3, 32'h12345678 );
  end
  `VC_TEST_CASE_END

  //-----------------------------------------------------------------------
  // TestBasic_p64_q7
  //-----------------------------------------------------------------------

  reg  [`VC_NET_MSG_SZ( 64, 7 )-1:0] t1_msg_test;
  reg  [`VC_NET_MSG_SZ( 64, 7 )-1:0] t1_msg_ref;
  wire      [`VC_NET_MSG_STR_SZ-1:0] t1_str;

  vc_NetMsgToStr#(64,7) t1_to_str
  (
    .msg (t1_msg_test),
    .str (t1_str)
  );

  task t1_do_test
  (
    input    [`VC_NET_MSG_DEST_SZ( 64, 7 )-1:0] dest,
    input     [`VC_NET_MSG_SRC_SZ( 64, 7 )-1:0] src,
    input [`VC_NET_MSG_PAYLOAD_SZ( 64, 7 )-1:0] payload
  );
  begin

    t1_msg_test[`VC_NET_MSG_DEST_FIELD( 64, 7 )]    = dest;
    t1_msg_test[`VC_NET_MSG_SRC_FIELD( 64, 7 )]     = src;
    t1_msg_test[`VC_NET_MSG_PAYLOAD_FIELD( 64, 7 )] = payload;

    t1_msg_ref = { dest, src, payload };

    #1;
    `VC_TEST_EQ( t1_str, t1_msg_test, t1_msg_ref )
    #9;

  end
  endtask

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_p64_q7" )
  begin
    t1_do_test( 7'h00, 7'h70, 64'h0000000000000000 );
    t1_do_test( 7'h14, 7'h6b, 64'h0000000000000000 );
    t1_do_test( 7'h2a, 7'h52, 64'h0000000000000000 );
    t1_do_test( 7'h31, 7'h48, 64'h0000000000000000 );
    t1_do_test( 7'h4c, 7'h37, 64'ha0a0a0a0a0a0a0a0 );
    t1_do_test( 7'h5e, 7'h25, 64'hc2c2c2c2c2c2c2c2 );
    t1_do_test( 7'h6f, 7'h19, 64'hdededededededede );
    t1_do_test( 7'h73, 7'h0c, 64'h0123456789abcdef );
  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule
