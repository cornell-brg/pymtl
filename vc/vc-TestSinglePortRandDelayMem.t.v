//========================================================================
// Unit Tests: Test Source/Sink
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelaySink.v"
`include "vc-TestSinglePortRandDelayMem.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_mem_sz  = 1024,    // size of physical memory in bytes
  parameter p_addr_sz = 8,       // size of mem message address in bits
  parameter p_data_sz = 32,      // size of mem message data in bits
  parameter p_src_max_delay = 0, // max random delay for source
  parameter p_mem_max_delay = 0, // max random delay for memory
  parameter p_sink_max_delay = 0 // max random delay for sink
)(
  input  clk,
  input  reset,
  output done
);

  // Local parameters

  localparam c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz);
  localparam c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz);

  // Test source

  wire                    memreq_val;
  wire                    memreq_rdy;
  wire [c_req_msg_sz-1:0] memreq_msg;

  wire                    src_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq_val),
    .rdy         (memreq_rdy),
    .msg         (memreq_msg),

    .done        (src_done)
  );

  // Test memory

  wire                     memresp_val;
  wire                     memresp_rdy;
  wire [c_resp_msg_sz-1:0] memresp_msg;

  vc_TestSinglePortRandDelayMem#(p_mem_sz,p_addr_sz,p_data_sz,p_mem_max_delay) mem
  (
    .clk         (clk),
    .reset       (reset),

    .memreq_val  (memreq_val),
    .memreq_rdy  (memreq_rdy),
    .memreq_msg  (memreq_msg),

    .memresp_val (memresp_val),
    .memresp_rdy (memresp_rdy),
    .memresp_msg (memresp_msg)
  );

  // Test sink

  wire sink_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp_val),
    .rdy   (memresp_rdy),
    .msg   (memresp_msg),

    .done  (sink_done)
  );

  // Done when both source and sink are done

  assign done = src_done & sink_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestSinglePortRandDelayMem" )

  //----------------------------------------------------------------------
  // localparams
  //----------------------------------------------------------------------

  localparam c_req_rd  = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_req_wr  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_req_ad  = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_req_an  = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_req_or  = `VC_MEM_REQ_MSG_TYPE_AMOOR;

  localparam c_resp_rd = `VC_MEM_RESP_MSG_TYPE_READ;
  localparam c_resp_wr = `VC_MEM_RESP_MSG_TYPE_WRITE;
  localparam c_resp_ad = `VC_MEM_RESP_MSG_TYPE_AMOADD;
  localparam c_resp_an = `VC_MEM_RESP_MSG_TYPE_AMOAND;
  localparam c_resp_or = `VC_MEM_RESP_MSG_TYPE_AMOOR;

  //----------------------------------------------------------------------
  // TestBasic_srcdelay0_memdelay0_sinkdelay0
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (0),
    .p_mem_max_delay  (0),
    .p_sink_max_delay (0)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req;
  reg [`VC_MEM_RESP_MSG_SZ(32)-1:0]   t0_resp;

  task t0_mk_req_resp
  (
    input [1023:0] index,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t0_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t0_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t0_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t0_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t0.src.src.m[index]   = t0_req;
    t0.sink.sink.m[index] = t0_resp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_srcdelay0_memdelay0_sinkdelay0" )
  begin

    //                  ----------- memory request -----------  ------ memory response -------
    //              idx type      addr      len   data          type       len   data

    t0_mk_req_resp( 0,  c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t0_mk_req_resp( 1,  c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t0_mk_req_resp( 2,  c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t0_mk_req_resp( 3,  c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t0_mk_req_resp( 4,  c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t0_mk_req_resp( 5,  c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t0_mk_req_resp( 6,  c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t0_mk_req_resp( 7,  c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t0_mk_req_resp( 8,  c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t0_mk_req_resp( 9,  c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t0_mk_req_resp(10,  c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t0_mk_req_resp(11,  c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t0_mk_req_resp(12,  c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t0_mk_req_resp(13,  c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    t0_mk_req_resp(14,  c_req_wr, 16'h0010, 2'd0, 32'h12345678, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0010
    t0_mk_req_resp(15,  c_req_ad, 16'h0010, 2'd0, 32'h87654321, c_resp_ad, 2'd0, 32'h12345678 ); // a.add word  0x0010
    t0_mk_req_resp(16,  c_req_an, 16'h0010, 2'd0, 32'hff00ff00, c_resp_an, 2'd0, 32'h99999999 ); // a.and word  0x0010
    t0_mk_req_resp(17,  c_req_or, 16'h0010, 2'd0, 32'h00be00ef, c_resp_or, 2'd0, 32'h99009900 ); // a.or  word  0x0010
    t0_mk_req_resp(18,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h99be99ef ); // read  word  0x0010

    #1;   t0_reset = 1'b1;
    #20;  t0_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay3_memdelay2_sinkdelay10
  //----------------------------------------------------------------------

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (3),
    .p_mem_max_delay  (2),
    .p_sink_max_delay (10)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req;
  reg [`VC_MEM_RESP_MSG_SZ(32)-1:0]   t1_resp;

  task t1_mk_req_resp
  (
    input [1023:0] index,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t1_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t1_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t1_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t1_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t1.src.src.m[index]   = t1_req;
    t1.sink.sink.m[index] = t1_resp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_srcdelay3_memdelay2_sinkdelay10" )
  begin

    //                  ----------- memory request -----------  ------ memory response -------
    //              idx type      addr      len   data          type       len   data

    t1_mk_req_resp( 0,  c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t1_mk_req_resp( 1,  c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t1_mk_req_resp( 2,  c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t1_mk_req_resp( 3,  c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t1_mk_req_resp( 4,  c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t1_mk_req_resp( 5,  c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t1_mk_req_resp( 6,  c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t1_mk_req_resp( 7,  c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t1_mk_req_resp( 8,  c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t1_mk_req_resp( 9,  c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t1_mk_req_resp(10,  c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t1_mk_req_resp(11,  c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t1_mk_req_resp(12,  c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t1_mk_req_resp(13,  c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    t1_mk_req_resp(14,  c_req_wr, 16'h0010, 2'd0, 32'h12345678, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0010
    t1_mk_req_resp(15,  c_req_ad, 16'h0010, 2'd0, 32'h87654321, c_resp_ad, 2'd0, 32'h12345678 ); // a.add word  0x0010
    t1_mk_req_resp(16,  c_req_an, 16'h0010, 2'd0, 32'hff00ff00, c_resp_an, 2'd0, 32'h99999999 ); // a.and word  0x0010
    t1_mk_req_resp(17,  c_req_or, 16'h0010, 2'd0, 32'h00be00ef, c_resp_or, 2'd0, 32'h99009900 ); // a.or  word  0x0010
    t1_mk_req_resp(18,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h99be99ef ); // read  word  0x0010

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay8_memdelay4_sinkdelay2
  //----------------------------------------------------------------------

  wire t2_done;
  reg  t2_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (8),
    .p_mem_max_delay  (4),
    .p_sink_max_delay (2)
  )
  t2
  (
    .clk   (clk),
    .reset (t2_reset),
    .done  (t2_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t2_req;
  reg [`VC_MEM_RESP_MSG_SZ(32)-1:0]   t2_resp;

  task t2_mk_req_resp
  (
    input [1023:0] index,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t2_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t2_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t2_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t2_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t2_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t2_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t2_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t2.src.src.m[index]   = t2_req;
    t2.sink.sink.m[index] = t2_resp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 3, "TestBasic_srcdelay8_memdelay4_sinkdelay2" )
  begin

    //                  ----------- memory request -----------  ------ memory response -------
    //              idx type      addr      len   data          type       len   data

    t2_mk_req_resp( 0,  c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t2_mk_req_resp( 1,  c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t2_mk_req_resp( 2,  c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t2_mk_req_resp( 3,  c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t2_mk_req_resp( 4,  c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t2_mk_req_resp( 5,  c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t2_mk_req_resp( 6,  c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t2_mk_req_resp( 7,  c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t2_mk_req_resp( 8,  c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t2_mk_req_resp( 9,  c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t2_mk_req_resp(10,  c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t2_mk_req_resp(11,  c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t2_mk_req_resp(12,  c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t2_mk_req_resp(13,  c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    t2_mk_req_resp(14,  c_req_wr, 16'h0010, 2'd0, 32'h12345678, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0010
    t2_mk_req_resp(15,  c_req_ad, 16'h0010, 2'd0, 32'h87654321, c_resp_ad, 2'd0, 32'h12345678 ); // a.add word  0x0010
    t2_mk_req_resp(16,  c_req_an, 16'h0010, 2'd0, 32'hff00ff00, c_resp_an, 2'd0, 32'h99999999 ); // a.and word  0x0010
    t2_mk_req_resp(17,  c_req_or, 16'h0010, 2'd0, 32'h00be00ef, c_resp_or, 2'd0, 32'h99009900 ); // a.or  word  0x0010
    t2_mk_req_resp(18,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h99be99ef ); // read  word  0x0010

    #1;   t2_reset = 1'b1;
    #20;  t2_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t2_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay1_memdelay8_sinkdelay1
  //----------------------------------------------------------------------

  wire t3_done;
  reg  t3_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (1),
    .p_mem_max_delay  (8),
    .p_sink_max_delay (1)
  )
  t3
  (
    .clk   (clk),
    .reset (t3_reset),
    .done  (t3_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t3_req;
  reg [`VC_MEM_RESP_MSG_SZ(32)-1:0]   t3_resp;

  task t3_mk_req_resp
  (
    input [1023:0] index,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t3_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t3_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t3_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t3_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t3_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t3_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t3_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t3.src.src.m[index]   = t3_req;
    t3.sink.sink.m[index] = t3_resp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 4, "TestBasic_srcdelay1_memdelay8_sinkdelay1" )
  begin

    //                  ----------- memory request -----------  ------ memory response -------
    //              idx type      addr      len   data          type       len   data

    t3_mk_req_resp( 0,  c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t3_mk_req_resp( 1,  c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t3_mk_req_resp( 2,  c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t3_mk_req_resp( 3,  c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t3_mk_req_resp( 4,  c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t3_mk_req_resp( 5,  c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t3_mk_req_resp( 6,  c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t3_mk_req_resp( 7,  c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t3_mk_req_resp( 8,  c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t3_mk_req_resp( 9,  c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t3_mk_req_resp(10,  c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t3_mk_req_resp(11,  c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t3_mk_req_resp(12,  c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t3_mk_req_resp(13,  c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    t3_mk_req_resp(14,  c_req_wr, 16'h0010, 2'd0, 32'h12345678, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0010
    t3_mk_req_resp(15,  c_req_ad, 16'h0010, 2'd0, 32'h87654321, c_resp_ad, 2'd0, 32'h12345678 ); // a.add word  0x0010
    t3_mk_req_resp(16,  c_req_an, 16'h0010, 2'd0, 32'hff00ff00, c_resp_an, 2'd0, 32'h99999999 ); // a.and word  0x0010
    t3_mk_req_resp(17,  c_req_or, 16'h0010, 2'd0, 32'h00be00ef, c_resp_or, 2'd0, 32'h99009900 ); // a.or  word  0x0010
    t3_mk_req_resp(18,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h99be99ef ); // read  word  0x0010

    #1;   t3_reset = 1'b1;
    #20;  t3_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t3_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 4 )
endmodule

