//========================================================================
// Unit Tests: Memory Request Message
//========================================================================

`include "vc-MemReqMsgTag.v"
`include "vc-Test.v"

module tester;
  `VC_TEST_SUITE_BEGIN( "vc-MemReqTagMsg" )

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  localparam c_read   = `VC_MEM_REQ_MSG_TAG_TYPE_READ;
  localparam c_write  = `VC_MEM_REQ_MSG_TAG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TAG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TAG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TAG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_REQ_MSG_TAG_TYPE_AMOXCH;

  //----------------------------------------------------------------------
  // TestFullStr_addr32_data32_tag2
  //----------------------------------------------------------------------

  reg [`VC_MEM_REQ_MSG_TAG_SZ(32,32,2)-1:0] t1_msg_test;
  reg [`VC_MEM_REQ_MSG_TAG_SZ(32,32,2)-1:0] t1_msg_ref;

  vc_MemReqMsgTagToStr#(32,32,2) t1_mem_req_msg_to_str( t1_msg_test );

  task t1_do_test
  (
    input [`VC_MEM_REQ_MSG_TAG_TAG_SZ(32,32,2)-1:0]  tag,
    input [`VC_MEM_REQ_MSG_TAG_TYPE_SZ(32,32,2)-1:0] type,
    input [`VC_MEM_REQ_MSG_TAG_ADDR_SZ(32,32,2)-1:0] addr,
    input [`VC_MEM_REQ_MSG_TAG_LEN_SZ(32,32,2)-1:0]  len,
    input [`VC_MEM_REQ_MSG_TAG_DATA_SZ(32,32,2)-1:0] data
  );
  begin

    // Create a wire and set msg fields using `defines

    t1_msg_test[`VC_MEM_REQ_MSG_TAG_TAG_FIELD(32,32,2)]  = tag;
    t1_msg_test[`VC_MEM_REQ_MSG_TAG_TYPE_FIELD(32,32,2)] = type;
    t1_msg_test[`VC_MEM_REQ_MSG_TAG_ADDR_FIELD(32,32,2)] = addr;
    t1_msg_test[`VC_MEM_REQ_MSG_TAG_LEN_FIELD(32,32,2)]  = len;
    t1_msg_test[`VC_MEM_REQ_MSG_TAG_DATA_FIELD(32,32,2)] = data;

    // Create a wire and set msg fields using concatentation

    t1_msg_ref = { tag, type, addr, len, data };

    // Check that both msgs are the same

    #1;
    `VC_TEST_EQ( t1_mem_req_msg_to_str.full_str, t1_msg_test, t1_msg_ref )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 1, "TestFullStr_addr32_data32" )
  begin

    // Create read messages

    t1_do_test( c_read, 2'd0,  32'h10000100, 2'd1, 32'hxxxxxxxx );
    t1_do_test( c_read, 2'd1,  32'h01000100, 2'd2, 32'hxxxxxxxx );
    t1_do_test( c_read, 2'd2,  32'h00100100, 2'd0, 32'hxxxxxxxx );

    // Create write messages

    t1_do_test( c_write, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t1_do_test( c_write, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t1_do_test( c_write, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic add messages

    t1_do_test( c_amoadd, 2'd0, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t1_do_test( c_amoadd, 2'd1, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t1_do_test( c_amoadd, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic and messages

    t1_do_test( c_amoand, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t1_do_test( c_amoand, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t1_do_test( c_amoand, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic or messages

    t1_do_test( c_amoor, 2'd0, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t1_do_test( c_amoor, 2'd1, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t1_do_test( c_amoor, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic exchange messages

    t1_do_test( c_amoxch, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t1_do_test( c_amoxch, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t1_do_test( c_amoxch, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestTinyStr_addr32_data32
  //----------------------------------------------------------------------

  reg [`VC_MEM_REQ_MSG_TAG_SZ(32,32,2)-1:0] t2_msg_test;
  reg [`VC_MEM_REQ_MSG_TAG_SZ(32,32,2)-1:0] t2_msg_ref;

  vc_MemReqMsgTagToStr#(32,32,2) t2_mem_req_msg_to_str( t2_msg_test );

  task t2_do_test
  (
    input [`VC_MEM_REQ_MSG_TAG_TAG_SZ(32,32,2)-1:0]  tag,
    input [`VC_MEM_REQ_MSG_TAG_TYPE_SZ(32,32,2)-1:0] type,
    input [`VC_MEM_REQ_MSG_TAG_ADDR_SZ(32,32,2)-1:0] addr,
    input [`VC_MEM_REQ_MSG_TAG_LEN_SZ(32,32,2)-1:0]  len,
    input [`VC_MEM_REQ_MSG_TAG_DATA_SZ(32,32,2)-1:0] data
  );
  begin

    // Create a wire and set msg fields using `defines
    t2_msg_test[`VC_MEM_REQ_MSG_TAG_TAG_FIELD(32,32,2)]  = tag;
    t2_msg_test[`VC_MEM_REQ_MSG_TAG_TYPE_FIELD(32,32,2)] = type;
    t2_msg_test[`VC_MEM_REQ_MSG_TAG_ADDR_FIELD(32,32,2)] = addr;
    t2_msg_test[`VC_MEM_REQ_MSG_TAG_LEN_FIELD(32,32,2)]  = len;
    t2_msg_test[`VC_MEM_REQ_MSG_TAG_DATA_FIELD(32,32,2)] = data;

    // Create a wire and set msg fields using concatentation

    t2_msg_ref = { tag, type, addr, len, data };

    // Check that both msgs are the same

    #1;
    `VC_TEST_EQ( t2_mem_req_msg_to_str.tiny_str, t2_msg_test, t2_msg_ref )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 2, "TestTinyStr_addr32_data32" )
  begin

    // Create read messages

    t2_do_test( c_read, 2'd0,  32'h10000100, 2'd1, 32'hxxxxxxxx );
    t2_do_test( c_read, 2'd1,  32'h01000100, 2'd2, 32'hxxxxxxxx );
    t2_do_test( c_read, 2'd2,  32'h00100100, 2'd0, 32'hxxxxxxxx );

    // Create write messages

    t2_do_test( c_write, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t2_do_test( c_write, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t2_do_test( c_write, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic add messages

    t2_do_test( c_amoadd, 2'd0, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t2_do_test( c_amoadd, 2'd1, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t2_do_test( c_amoadd, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic and messages

    t2_do_test( c_amoand, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t2_do_test( c_amoand, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t2_do_test( c_amoand, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic or messages

    t2_do_test( c_amoor, 2'd0, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t2_do_test( c_amoor, 2'd1, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t2_do_test( c_amoor, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

    // Create atomic exchange messages

    t2_do_test( c_amoxch, 2'd1, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t2_do_test( c_amoxch, 2'd0, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t2_do_test( c_amoxch, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestFullStr_addr16_data64
  //----------------------------------------------------------------------

  reg [`VC_MEM_REQ_MSG_TAG_SZ(16,64,2)-1:0] t3_msg_test;
  reg [`VC_MEM_REQ_MSG_TAG_SZ(16,64,2)-1:0] t3_msg_ref;

  vc_MemReqMsgTagToStr#(16,64) t3_mem_req_msg_to_str( t3_msg_test );

  task t3_do_test
  (
    input [`VC_MEM_REQ_MSG_TAG_TAG_SZ(16,64,2)-1:0]  tag,
    input [`VC_MEM_REQ_MSG_TAG_TYPE_SZ(16,64,2)-1:0] type,
    input [`VC_MEM_REQ_MSG_TAG_ADDR_SZ(16,64,2)-1:0] addr,
    input [`VC_MEM_REQ_MSG_TAG_LEN_SZ(16,64,2)-1:0]  len,
    input [`VC_MEM_REQ_MSG_TAG_DATA_SZ(16,64,2)-1:0] data
  );
  begin

    // Create a wire and set msg fields using `defines

    t3_msg_test[`VC_MEM_REQ_MSG_TAG_TAG_FIELD(16,64,2)]  = tag;
    t3_msg_test[`VC_MEM_REQ_MSG_TAG_TYPE_FIELD(16,64,2)] = type;
    t3_msg_test[`VC_MEM_REQ_MSG_TAG_ADDR_FIELD(16,64,2)] = addr;
    t3_msg_test[`VC_MEM_REQ_MSG_TAG_LEN_FIELD(16,64,2)]  = len;
    t3_msg_test[`VC_MEM_REQ_MSG_TAG_DATA_FIELD(16,64,2)] = data;

    // Create a wire and set msg fields using concatentation

    t3_msg_ref = { tag, type, addr, len, data };

    // Check that both msgs are the same

    #1;
    `VC_TEST_EQ( t3_mem_req_msg_to_str.full_str, t3_msg_test, t3_msg_ref )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 3, "TestFullStr_addr16_data64" )
  begin

    // Create read messages

    t3_do_test( c_read, 2'd0,  16'h0100, 2'd1, 64'h_xxxxxxxx_xxxxxxxx );
    t3_do_test( c_read, 2'd1,  16'h0100, 2'd2, 64'h_xxxxxxxx_xxxxxxxx );
    t3_do_test( c_read, 2'd2,  16'h0100, 2'd0, 64'h_xxxxxxxx_xxxxxxxx );

    // Create write messages

    t3_do_test( c_write, 2'd0, 16'h0100, 2'd1, 64'h_0a0b0c0d_0a0b0c0d );
    t3_do_test( c_write, 2'd1, 16'h0100, 2'd2, 64'h_0b0c0d0e_0b0c0d0e );
    t3_do_test( c_write, 2'd2, 16'h0100, 2'd0, 64'h_0c0d0e0f_0c0d0e0f );

    // Create atomic add messages

    t3_do_test( c_amoadd, 2'd0, 16'h0100, 2'd1, 64'h_0a0b0c0d_0a0b0c0d );
    t3_do_test( c_amoadd, 2'd1, 16'h0100, 2'd2, 64'h_0b0c0d0e_0b0c0d0e );
    t3_do_test( c_amoadd, 2'd2, 16'h0100, 2'd0, 64'h_0c0d0e0f_0c0d0e0f );

    // Create atomic and messages

    t3_do_test( c_amoand, 2'd0, 16'h0100, 2'd1, 64'h_0a0b0c0d_0a0b0c0d );
    t3_do_test( c_amoand, 2'd1, 16'h0100, 2'd2, 64'h_0b0c0d0e_0b0c0d0e );
    t3_do_test( c_amoand, 2'd2, 16'h0100, 2'd0, 64'h_0c0d0e0f_0c0d0e0f );

    // Create atomic or messages

    t3_do_test( c_amoor, 2'd0, 16'h0100, 2'd1, 64'h_0a0b0c0d_0a0b0c0d );
    t3_do_test( c_amoor, 2'd1, 16'h0100, 2'd2, 64'h_0b0c0d0e_0b0c0d0e );
    t3_do_test( c_amoor, 2'd2, 16'h0100, 2'd0, 64'h_0c0d0e0f_0c0d0e0f );

    // Create atomic exchange messages

    t3_do_test( c_amoxch, 2'd0, 32'h10000100, 2'd1, 32'h0a0b0c0d );
    t3_do_test( c_amoxch, 2'd1, 32'h01000100, 2'd2, 32'h0b0c0d0e );
    t3_do_test( c_amoxch, 2'd2, 32'h00100100, 2'd0, 32'h0c0d0e0f );

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 3 )
endmodule

