//========================================================================
// Unit Tests: Memory Port Width Adapter
//========================================================================

`include "vc-MemPortWidthAdapter.v"
`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Test.v"

module tester;
  `VC_TEST_SUITE_BEGIN( "vc-MemPortWidthAdapter" )

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  localparam c_read   = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_write  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_REQ_MSG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_REQ_MSG_TYPE_AMOXCH;

  localparam c_addr_sz  = 16;
  localparam c_pdata_sz = 16;
  localparam c_mdata_sz = 64;

  //----------------------------------------------------------------------
  // Some Test
  //----------------------------------------------------------------------

  reg [`VC_MEM_REQ_MSG_SZ(c_addr_sz,c_mdata_sz)-1:0] mreq_msg_ref;
  reg [`VC_MEM_RESP_MSG_SZ(c_pdata_sz)-1:0] presp_msg_ref;

  reg  [`VC_MEM_REQ_MSG_SZ(c_addr_sz,c_pdata_sz)-1:0] preq_msg;
  reg  preq_val;
  wire preq_rdy;
  wire [`VC_MEM_REQ_MSG_SZ(c_addr_sz,c_mdata_sz)-1:0] mreq_msg;
  wire mreq_val;
  reg  mreq_rdy;

  reg  [`VC_MEM_RESP_MSG_SZ(c_mdata_sz)-1:0] mresp_msg;
  reg  mresp_val;
  wire mresp_rdy;
  wire [`VC_MEM_RESP_MSG_SZ(c_pdata_sz)-1:0] presp_msg;
  wire presp_val;
  reg  presp_rdy;

  vc_MemPortWidthAdapter#(c_addr_sz,c_pdata_sz,c_mdata_sz) adapter
  (
    .procreq_val    (preq_val),
    .procreq_rdy    (preq_rdy),
    .procreq_msg    (preq_msg),
    .procresp_val   (presp_val),
    .procresp_rdy   (presp_rdy),
    .procresp_msg   (presp_msg),
    .memreq_val     (mreq_val),
    .memreq_rdy     (mreq_rdy),
    .memreq_msg     (mreq_msg),
    .memresp_val    (mresp_val),
    .memresp_rdy    (mresp_rdy),
    .memresp_msg    (mresp_msg)
  );

  task t1_do_test
  (
    input [`VC_MEM_REQ_MSG_TYPE_SZ(c_addr_sz,c_pdata_sz)-1:0] type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(c_addr_sz,c_pdata_sz)-1:0] addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(c_addr_sz,c_pdata_sz)-1:0]  len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(c_addr_sz,c_pdata_sz)-1:0] data,
    input                                                    val,
    input                                                    rdy,
    input [`VC_MEM_REQ_MSG_LEN_SZ(c_addr_sz,c_mdata_sz)-1:0]  exp_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(c_addr_sz,c_mdata_sz)-1:0] exp_data
  );
  begin

    preq_msg[`VC_MEM_REQ_MSG_TYPE_FIELD(c_addr_sz,c_pdata_sz)] = type;
    preq_msg[`VC_MEM_REQ_MSG_ADDR_FIELD(c_addr_sz,c_pdata_sz)] = addr;
    preq_msg[`VC_MEM_REQ_MSG_LEN_FIELD(c_addr_sz,c_pdata_sz)]  = len;
    preq_msg[`VC_MEM_REQ_MSG_DATA_FIELD(c_addr_sz,c_pdata_sz)] = data;
    preq_val = val;
    mreq_rdy = rdy;

    // Check that both msgs are the same
    #1;
    `VC_TEST_EQ( "type", mreq_msg[`VC_MEM_REQ_MSG_TYPE_FIELD(c_addr_sz,c_mdata_sz)], type )
    `VC_TEST_EQ( "addr", mreq_msg[`VC_MEM_REQ_MSG_ADDR_FIELD(c_addr_sz,c_mdata_sz)], addr )
    `VC_TEST_EQ( "len",  mreq_msg[`VC_MEM_REQ_MSG_LEN_FIELD(c_addr_sz,c_mdata_sz)],  exp_len )
    `VC_TEST_EQ( "data", mreq_msg[`VC_MEM_REQ_MSG_DATA_FIELD(c_addr_sz,c_mdata_sz)], exp_data )
    `VC_TEST_EQ( "val",  mreq_val, preq_val )
    `VC_TEST_EQ( "rdy",  mreq_rdy, preq_rdy )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 1, "Test_Req16_Req64" )
  begin

    // Create read messages

    t1_do_test( c_read,   16'h1000, 1'd1, 16'hxxxx, 1'b1, 1'b0, 4'd1, 64'hzzzzzzzz );
    t1_do_test( c_read,   16'h0100, 1'd0, 16'hxxxx, 1'b1, 1'b0, 4'd2, 64'hzzzzzzzz );
    t1_do_test( c_read,   16'h0010, 1'd0, 16'hxxxx, 1'b1, 1'b0, 4'd2, 64'hzzzzzzzz );

    // Create write messages

    t1_do_test( c_write,  16'h1000, 1'd1, 16'h0c0d, 1'b1, 1'b1, 4'd1, 64'h00000c0d );
    t1_do_test( c_write,  16'h0100, 1'd0, 16'h0d0e, 1'b1, 1'b1, 4'd2, 64'h00000d0e );
    t1_do_test( c_write,  16'h0010, 1'd0, 16'h0e0f, 1'b1, 1'b1, 4'd2, 64'h00000e0f );

    // Create atomic add messages

    t1_do_test( c_amoadd, 16'h1000, 1'd1, 16'h0a0b, 1'b0, 1'b1, 4'd1, 64'h00000a0b );
    t1_do_test( c_amoadd, 16'h0100, 1'd0, 16'h0b0c, 1'b0, 1'b1, 4'd2, 64'h00000b0c );
    t1_do_test( c_amoadd, 16'h0010, 1'd0, 16'h0c0d, 1'b0, 1'b1, 4'd2, 64'h00000c0d );

    // Create atomic and messages

    t1_do_test( c_amoand, 16'h0100, 1'd1, 16'hb0c0, 1'b0, 1'b0, 4'd1, 64'h0000b0c0 );
    t1_do_test( c_amoand, 16'h0100, 1'd0, 16'hc0d0, 1'b0, 1'b0, 4'd2, 64'h0000c0d0 );
    t1_do_test( c_amoand, 16'h0100, 1'd0, 16'hd0e0, 1'b0, 1'b0, 4'd2, 64'h0000d0e0 );

    // Create atomic or messages

    t1_do_test( c_amoor,  16'h0100, 1'd1, 16'h0c0d, 1'b1, 1'b0, 4'd1, 64'h00000c0d );
    t1_do_test( c_amoor,  16'h0100, 1'd0, 16'h0d0e, 1'b1, 1'b0, 4'd2, 64'h00000d0e );
    t1_do_test( c_amoor,  16'h0100, 1'd0, 16'h0e0f, 1'b1, 1'b0, 4'd2, 64'h00000e0f );

    // Create atomic exchange messages

    t1_do_test( c_amoxch, 16'h0100, 1'd1, 16'h0a00, 1'b1, 1'b0, 4'd1, 64'h00000a00 );
    t1_do_test( c_amoxch, 16'h0100, 1'd0, 16'h0b00, 1'b1, 1'b0, 4'd2, 64'h00000b00 );
    t1_do_test( c_amoxch, 16'h0100, 1'd0, 16'h0c00, 1'b1, 1'b0, 4'd2, 64'h00000c00 );

  end
  `VC_TEST_CASE_END


  task t2_do_test
  (
    input [`VC_MEM_RESP_MSG_TYPE_SZ(c_mdata_sz)-1:0] type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(c_mdata_sz)-1:0]  len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(c_mdata_sz)-1:0] data,
    input [`VC_MEM_RESP_MSG_LEN_SZ(c_pdata_sz)-1:0]  exp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(c_pdata_sz)-1:0] exp_data,
    input                                            val,
    input                                            rdy
  );
  begin

    mresp_msg[`VC_MEM_RESP_MSG_TYPE_FIELD(c_mdata_sz)] = type;
    mresp_msg[`VC_MEM_RESP_MSG_LEN_FIELD(c_mdata_sz)]  = len;
    mresp_msg[`VC_MEM_RESP_MSG_DATA_FIELD(c_mdata_sz)] = data;
    mresp_val = val;
    presp_rdy = rdy;

    // Check that both msgs are the same
    #1;
    `VC_TEST_EQ( "type", presp_msg[`VC_MEM_RESP_MSG_TYPE_FIELD(c_pdata_sz)], type )
    `VC_TEST_EQ( "len",  presp_msg[`VC_MEM_RESP_MSG_LEN_FIELD(c_pdata_sz)],  exp_len )
    `VC_TEST_EQ( "data", presp_msg[`VC_MEM_RESP_MSG_DATA_FIELD(c_pdata_sz)], exp_data )
    `VC_TEST_EQ( "val",  presp_val, mresp_val )
    `VC_TEST_EQ( "rdy",  presp_rdy, mresp_rdy )
    #9;
  end
  endtask

  `VC_TEST_CASE_BEGIN( 2, "Test_Resp64_Resp16" )
  begin

    // Create read messages

    t2_do_test( c_read,   4'd1, 64'hzzzzzzzz, 1'd1, 16'hxxxx, 1'b1, 1'b0 );
    t2_do_test( c_read,   4'd2, 64'hzzzzzzzz, 1'd0, 16'hxxxx, 1'b1, 1'b0 );
    t2_do_test( c_read,   4'd2, 64'hzzzzzzzz, 1'd0, 16'hxxxx, 1'b1, 1'b0 );

    // Create write messages

    t2_do_test( c_write,  4'd1, 64'h00000c0d, 1'd1, 16'h0c0d, 1'b1, 1'b1 );
    t2_do_test( c_write,  4'd2, 64'h00000d0e, 1'd0, 16'h0d0e, 1'b1, 1'b1 );
    t2_do_test( c_write,  4'd2, 64'h00000e0f, 1'd0, 16'h0e0f, 1'b1, 1'b1 );

    // Create atomic add messages

    t2_do_test( c_amoadd, 4'd1, 64'h00000a0b, 1'd1, 16'h0a0b, 1'b0, 1'b1 );
    t2_do_test( c_amoadd, 4'd2, 64'h00000b0c, 1'd0, 16'h0b0c, 1'b0, 1'b1 );
    t2_do_test( c_amoadd, 4'd2, 64'h00000c0d, 1'd0, 16'h0c0d, 1'b0, 1'b1 );

    // Create atomic and messages

    t2_do_test( c_amoand, 4'd1, 64'h0000b0c0, 1'd1, 16'hb0c0, 1'b0, 1'b0 );
    t2_do_test( c_amoand, 4'd2, 64'h0000c0d0, 1'd0, 16'hc0d0, 1'b0, 1'b0 );
    t2_do_test( c_amoand, 4'd2, 64'h0000d0e0, 1'd0, 16'hd0e0, 1'b0, 1'b0 );

    // Create atomic or messages

    t2_do_test( c_amoor,  4'd1, 64'h00000c0d, 1'd1, 16'h0c0d, 1'b1, 1'b0 );
    t2_do_test( c_amoor,  4'd2, 64'h00000d0e, 1'd0, 16'h0d0e, 1'b1, 1'b0 );
    t2_do_test( c_amoor,  4'd2, 64'h00000e0f, 1'd0, 16'h0e0f, 1'b1, 1'b0 );

    // Create atomic exchange messages

    t2_do_test( c_amoxch, 4'd1, 64'h00000a00, 1'd1, 16'h0a00, 1'b1, 1'b0 );
    t2_do_test( c_amoxch, 4'd2, 64'h00000b00, 1'd0, 16'h0b00, 1'b1, 1'b0 );
    t2_do_test( c_amoxch, 4'd2, 64'h00000c00, 1'd0, 16'h0c00, 1'b1, 1'b0 );

  end
  `VC_TEST_CASE_END



  `VC_TEST_SUITE_END( 2 )
endmodule

