//========================================================================
// Unit Tests: Test Network-Memory Interface Adapter
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelaySink.v"
`include "vc-NetMsg.v"
`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-TestSinglePortRandDelayMem.v"
`include "vc-NetMemAdapter.v"
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
  parameter p_sink_max_delay = 0, // max random delay for sink
  parameter p_num_nodes = 4       // max random delay for sink
)(
  input  clk,
  input  reset,
  output done
);

  // Local parameters

  localparam c_srcdest_sz      = $clog2(p_num_nodes);
  localparam c_memreq_msg_sz   = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz);
  localparam c_memresp_msg_sz  = `VC_MEM_RESP_MSG_SZ(p_data_sz);
  localparam c_reqnet_msg_sz   = `VC_NET_MSG_SZ(c_memreq_msg_sz,c_srcdest_sz);
  localparam c_respnet_msg_sz  = `VC_NET_MSG_SZ(c_memresp_msg_sz,c_srcdest_sz);

  // Test source for network output port

  wire                       netout_val;
  wire                       netout_rdy;
  wire [c_reqnet_msg_sz-1:0] netout_msg;

  wire                       netout_done;

  vc_TestRandDelaySource#(c_reqnet_msg_sz,1024,p_src_max_delay)src
  (
    .clk         (clk),
    .reset       (reset),

    .val         (netout_val),
    .rdy         (netout_rdy),
    .msg         (netout_msg),

    .done        (netout_done)
  );

  // Test sink for network input port

  wire                        netin_val;
  wire                        netin_rdy;
  wire [c_respnet_msg_sz-1:0] netin_msg;

  wire                        netin_done;

  vc_TestRandDelaySink#(c_respnet_msg_sz,1024,p_sink_max_delay) sink
  (
    .clk   (clk),
    .reset (reset),

    .val   (netin_val),
    .rdy   (netin_rdy),
    .msg   (netin_msg),

    .done  (netin_done)
  );

  // Test adapter

  wire                        memreq_val;
  wire                        memreq_rdy;
  wire [c_memreq_msg_sz-1:0]  memreq_msg;

  wire                        memresp_val;
  wire                        memresp_rdy;
  wire [c_memresp_msg_sz-1:0] memresp_msg;

  vc_NetMemAdapter#( p_num_nodes, p_addr_sz, p_data_sz ) adapter
  (
    .clk         (clk),
    .reset       (reset),

    .netout_msg  (netout_msg),
    .netout_val  (netout_val),
    .netout_rdy  (netout_rdy),

    .memreq_msg  (memreq_msg),
    .memreq_val  (memreq_val),
    .memreq_rdy  (memreq_rdy),

    .memresp_msg (memresp_msg),
    .memresp_val (memresp_val),
    .memresp_rdy (memresp_rdy),

    .netin_msg   (netin_msg),
    .netin_val   (netin_val),
    .netin_rdy   (netin_rdy)
  );

  // Test memory

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

  assign done = netout_done & netin_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-NetMemAdapter" )

  //----------------------------------------------------------------------
  // localparams
  //----------------------------------------------------------------------

  localparam c_req_rd  = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_req_wr  = `VC_MEM_REQ_MSG_TYPE_WRITE;

  localparam c_resp_rd = `VC_MEM_RESP_MSG_TYPE_READ;
  localparam c_resp_wr = `VC_MEM_RESP_MSG_TYPE_WRITE;
  localparam c_num_nodes = 4;
  localparam c_srcdest_sz = $clog2(c_num_nodes);
  localparam c_memreq_sz  = `VC_MEM_REQ_MSG_SZ(16,32);
  localparam c_memresp_sz = `VC_MEM_RESP_MSG_SZ(32);

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
    .p_sink_max_delay (0),
    .p_num_nodes      (c_num_nodes)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  // Helper tasks

  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]  t0_req;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0] t0_resp;

  task t0_mk_req_resp
  (
    input [1023:0] index,

    input [c_srcdest_sz-1:0] req_src,
    input [c_srcdest_sz-1:0] req_dest,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t0_req[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t0_req[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t0_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t0_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_resp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t0_resp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
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

    //                            ----------- memory request -----------  ------ memory response -------
    //              idx src dst  type      addr      len   data          type       len   data

    t0_mk_req_resp( 0,    0,  4, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t0_mk_req_resp( 1,    1,  4, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t0_mk_req_resp( 2,    2,  4, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t0_mk_req_resp( 3,    3,  4, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t0_mk_req_resp( 4,    1,  4, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t0_mk_req_resp( 5,    2,  4, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t0_mk_req_resp( 6,    3,  4, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t0_mk_req_resp( 7,    4,  4, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t0_mk_req_resp( 8,    1,  4, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t0_mk_req_resp( 9,    2,  4, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t0_mk_req_resp(10,    3,  4, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t0_mk_req_resp(11,    4,  4, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t0_mk_req_resp(12,    1,  4, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t0_mk_req_resp(13,    2,  4, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

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
    .p_sink_max_delay (10),
    .p_num_nodes      (c_num_nodes)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  // Helper tasks

  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]  t1_req;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0] t1_resp;

  task t1_mk_req_resp
  (
    input [1023:0] index,

    input [c_srcdest_sz-1:0] req_src,
    input [c_srcdest_sz-1:0] req_dest,

    input [`VC_MEM_REQ_MSG_TYPE_SZ(16,32)-1:0] req_type,
    input [`VC_MEM_REQ_MSG_ADDR_SZ(16,32)-1:0] req_addr,
    input [`VC_MEM_REQ_MSG_LEN_SZ(16,32)-1:0]  req_len,
    input [`VC_MEM_REQ_MSG_DATA_SZ(16,32)-1:0] req_data,

    input [`VC_MEM_RESP_MSG_TYPE_SZ(32)-1:0]   resp_type,
    input [`VC_MEM_RESP_MSG_LEN_SZ(32)-1:0]    resp_len,
    input [`VC_MEM_RESP_MSG_DATA_SZ(32)-1:0]   resp_data
  );
  begin
    t1_req[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t1_req[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t1_req[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t1_req[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_resp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t1_resp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
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

    //                          ----------- memory request -----------  ------ memory response -------
    //              idx src dst type      addr      len   data          type       len   data

    t1_mk_req_resp( 0,   4,  3, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t1_mk_req_resp( 1,   3,  3, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t1_mk_req_resp( 2,   2,  3, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t1_mk_req_resp( 3,   1,  3, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t1_mk_req_resp( 4,   4,  3, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t1_mk_req_resp( 5,   3,  3, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t1_mk_req_resp( 6,   2,  3, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t1_mk_req_resp( 7,   1,  3, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t1_mk_req_resp( 8,   4,  3, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t1_mk_req_resp( 9,   3,  3, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t1_mk_req_resp(10,   2,  3, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t1_mk_req_resp(11,   1,  3, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t1_mk_req_resp(12,   4,  3, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t1_mk_req_resp(13,   3,  3, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END


  `VC_TEST_SUITE_END( 2 )
endmodule
