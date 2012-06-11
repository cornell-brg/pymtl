//========================================================================
// Unit Tests: Syscall Message
//========================================================================

`include "vc-SyscMsg.v"
`include "vc-Test.v"

module tester;
  `VC_TEST_SUITE_BEGIN( "vc-SyscMsg" )

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  localparam c_head   = `VC_SYSC_MSG_HEADER_HEAD;
  localparam c_body   = `VC_SYSC_MSG_HEADER_BODY;

  //----------------------------------------------------------------------
  // TestFullStr_payload64
  //----------------------------------------------------------------------

  reg [`VC_SYSC_MSG_SZ(64)-1:0] t1_msg_test;
  reg [`VC_SYSC_MSG_SZ(64)-1:0] t1_msg_ref;

  vc_SyscMsgToStr#(64) t1_sysc_msg_to_str( t1_msg_test );

  task t1_do_test
  (
    input [`VC_SYSC_MSG_HEADER_SZ(64)-1:0]  header,
    input [`VC_SYSC_MSG_LEN_SZ(64)-1:0]     len,
    input [`VC_SYSC_MSG_PAYLOAD_SZ(64)-1:0] payload
  );
  begin

    // Create a wire and set msg fields using `defines

    t1_msg_test[`VC_SYSC_MSG_HEADER_FIELD(64)]  = header;
    t1_msg_test[`VC_SYSC_MSG_LEN_FIELD(64)]     = len;
    t1_msg_test[`VC_SYSC_MSG_PAYLOAD_FIELD(64)] = payload;

    // Create a wire and set msg fields using concatentation

    t1_msg_ref = { header, len, payload };

    // Check that both msgs are the same

    #1;
    `VC_TEST_EQ( t1_sysc_msg_to_str.full_str, t1_msg_test, t1_msg_ref )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 1, "TestFullStr_payload64" )
  begin

    // Create head messages

    t1_do_test( c_head, 3'd4, { 32'd0, 32'd128 } );
    t1_do_test( c_head, 3'd2, { 32'd1, 32'd256 } );
    t1_do_test( c_head, 3'd0, { 32'd2, 32'd512 } );

    // Create body messages

    t1_do_test( c_body, 3'd4, 64'hf0f0f0f0f0f0f0f0 );
    t1_do_test( c_body, 3'd2, 64'h00ff00ff00ff00ff );
    t1_do_test( c_body, 3'd0, 64'hff00ff00ff00ff00 );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestTinyStr_addr32_data32
  //----------------------------------------------------------------------

  reg [`VC_SYSC_MSG_SZ(64)-1:0] t2_msg_test;
  reg [`VC_SYSC_MSG_SZ(64)-1:0] t2_msg_ref;

  vc_SyscMsgToStr#(64) t2_sysc_msg_to_str( t2_msg_test );

  task t2_do_test
  (
    input [`VC_SYSC_MSG_HEADER_SZ(64)-1:0]  header,
    input [`VC_SYSC_MSG_LEN_SZ(64)-1:0]     len,
    input [`VC_SYSC_MSG_PAYLOAD_SZ(64)-1:0] payload
  );
  begin

    // Create a wire and set msg fields using `defines

    t2_msg_test[`VC_SYSC_MSG_HEADER_FIELD(64)]  = header;
    t2_msg_test[`VC_SYSC_MSG_LEN_FIELD(64)]     = len;
    t2_msg_test[`VC_SYSC_MSG_PAYLOAD_FIELD(64)] = payload;

    // Create a wire and set msg fields using concatentation

    t1_msg_ref = { header, len, payload };

    // Check that both msgs are the same

    #1;
    `VC_TEST_EQ( t2_sysc_msg_to_str.tiny_str, t2_msg_test, t2_msg_ref )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 2, "TestTinyStr_payload128" )
  begin

    // Create head messages

    t1_do_test( c_head, 3'd4, { 32'd0, 32'd128 } );
    t1_do_test( c_head, 3'd2, { 32'd1, 32'd256 } );
    t1_do_test( c_head, 3'd0, { 32'd2, 32'd512 } );

    // Create body messages

    t1_do_test( c_body, 3'd4, 64'hf0f0f0f0f0f0f0f0 );
    t1_do_test( c_body, 3'd2, 64'h00ff00ff00ff00ff );
    t1_do_test( c_body, 3'd0, 64'hff00ff00ff00ff00 );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule

