//========================================================================
// Unit Tests: Test Network-Memory Interface Adapter
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelaySink.v"
`include "vc-NetMsg.v"
`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-ProcNetAdapter.v"
`include "vc-Test.v"

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_mem_sz  = 1024,    // size of physical memory in bytes
  parameter p_addr_sz = 8,       // size of mem message address in bits
  parameter p_data_sz = 32,      // size of mem message data in bits
  parameter p_dest_offset = 2,   // offset to dest field in bits
  parameter p_src_max_delay = 0, // max random delay for source
  parameter p_mem_max_delay = 0, // max random delay for memory
  parameter p_sink_max_delay = 0,// max random delay for sink
  parameter p_num_nodes = 4,     // number of network nodes
  parameter p_router_id = 1,     // id of the router we're attached to
  parameter p_max_requests = 16  // maximum number of in flight requests
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

  // Test source for processor memory request port

  wire                       memreq_val;
  wire                       memreq_rdy;
  wire [c_memreq_msg_sz-1:0] memreq_msg;

  wire                       memreq_done;

  vc_TestRandDelaySource#(c_memreq_msg_sz,1024,p_src_max_delay) msrc
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq_val),
    .rdy         (memreq_rdy),
    .msg         (memreq_msg),

    .done        (memreq_done)
  );

  // Test sink for network input port

  wire                        netin_val;
  wire                        netin_rdy;
  wire [c_reqnet_msg_sz-1:0]  netin_msg;

  wire                        netin_done;

  vc_TestRandDelaySink#(c_reqnet_msg_sz,1024,p_sink_max_delay) nsink
  (
    .clk   (clk),
    .reset (reset),

    .val   (netin_val),
    .rdy   (netin_rdy),
    .msg   (netin_msg),

    .done  (netin_done)
  );

  // Test source for network output port

  wire                        netout_val;
  wire                        netout_rdy;
  wire [c_respnet_msg_sz-1:0] netout_msg;

  wire                        netout_done;

  vc_TestRandDelaySource#(c_respnet_msg_sz,1024,p_src_max_delay) nsrc
  (
    .clk         (clk),
    .reset       (reset),

    .val         (netout_val),
    .rdy         (netout_rdy),
    .msg         (netout_msg),

    .done        (netout_done)
  );

  // Test sink for processor memory response port

  wire                        memresp_val;
  wire                        memresp_rdy;
  wire [c_memresp_msg_sz-1:0] memresp_msg;

  wire                        memresp_done;

  vc_TestRandDelaySink#(c_memresp_msg_sz,1024,p_sink_max_delay) msink
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp_val),
    .rdy   (memresp_rdy),
    .msg   (memresp_msg),

    .done  (memresp_done)
  );

  // Test adapter

  vc_ProcNetAdapter#( p_router_id, p_num_nodes, p_addr_sz,
                      p_data_sz, p_dest_offset, p_max_requests )
  adapter
  (
    .clk         (clk),
    .reset       (reset),

    .memreq_msg  (memreq_msg),
    .memreq_val  (memreq_val),
    .memreq_rdy  (memreq_rdy),

    .netin_msg   (netin_msg),
    .netin_val   (netin_val),
    .netin_rdy   (netin_rdy),

    .netout_msg  (netout_msg),
    .netout_val  (netout_val),
    .netout_rdy  (netout_rdy),

    .memresp_msg (memresp_msg),
    .memresp_val (memresp_val),
    .memresp_rdy (memresp_rdy)
  );

  assign done = memreq_done & netout_done & netin_done & memresp_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-ProcNetAdapter" )

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
  // TestBasic_srcdelay0_memdelay0_sinkdelay0_maxreq16
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_dest_offset    (2),
    .p_src_max_delay  (0),
    .p_mem_max_delay  (0),
    .p_sink_max_delay (0),
    .p_num_nodes      (c_num_nodes),
    .p_max_requests   (16)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0] t0_memreq;
  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]     t0_netreq;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0]    t0_netresp;
  reg [`VC_MEM_RESP_MSG_SZ(c_memresp_sz)-1:0]            t0_memresp;

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
    t0_memreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_memreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t0_memreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_memreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_netreq[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t0_netreq[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t0_netreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_netreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t0_netreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_netreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_netresp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t0_netresp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
    t0_netresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t0_netresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t0_netresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t0_memresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t0_memresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t0_memresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t0.msrc.src.m[index]   = t0_memreq;
    t0.nsink.sink.m[index] = t0_netreq;
    t0.nsrc.src.m[index]   = t0_netresp;
    t0.msink.sink.m[index] = t0_memresp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_srcdelay0_memdelay0_sinkdelay0_maxreq16" )
  begin

    //                            ----------- memory request -----------  ------ memory response -------
    //              idx src dst  type      addr      len   data          type       len   data

    t0_mk_req_resp( 0,    1,  0, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t0_mk_req_resp( 1,    1,  1, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t0_mk_req_resp( 2,    1,  0, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t0_mk_req_resp( 3,    1,  1, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t0_mk_req_resp( 4,    1,  2, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t0_mk_req_resp( 5,    1,  2, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t0_mk_req_resp( 6,    1,  2, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t0_mk_req_resp( 7,    1,  2, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t0_mk_req_resp( 8,    1,  2, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t0_mk_req_resp( 9,    1,  2, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t0_mk_req_resp(10,    1,  3, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t0_mk_req_resp(11,    1,  3, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t0_mk_req_resp(12,    1,  3, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t0_mk_req_resp(13,    1,  3, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    #1;   t0_reset = 1'b1;
    #20;  t0_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay3_memdelay2_sinkdelay10_maxreq16
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
    .p_num_nodes      (c_num_nodes),
    .p_max_requests   (16)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0] t1_memreq;
  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]     t1_netreq;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0]    t1_netresp;
  reg [`VC_MEM_RESP_MSG_SZ(c_memresp_sz)-1:0]            t1_memresp;

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
    t1_memreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_memreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t1_memreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_memreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_netreq[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t1_netreq[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t1_netreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_netreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t1_netreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_netreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_netresp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t1_netresp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
    t1_netresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t1_netresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t1_netresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t1_memresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t1_memresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t1_memresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t1.msrc.src.m[index]   = t1_memreq;
    t1.nsink.sink.m[index] = t1_netreq;
    t1.nsrc.src.m[index]   = t1_netresp;
    t1.msink.sink.m[index] = t1_memresp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_srcdelay3_memdelay2_sinkdelay10_maxreq16" )
  begin

    //                          ----------- memory request -----------  ------ memory response -------
    //              idx src dst type      addr      len   data          type       len   data

    t1_mk_req_resp( 0,   1,  0, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t1_mk_req_resp( 1,   1,  1, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t1_mk_req_resp( 2,   1,  0, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t1_mk_req_resp( 3,   1,  1, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t1_mk_req_resp( 4,   1,  2, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t1_mk_req_resp( 5,   1,  2, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t1_mk_req_resp( 6,   1,  2, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t1_mk_req_resp( 7,   1,  2, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t1_mk_req_resp( 8,   1,  2, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t1_mk_req_resp( 9,   1,  2, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t1_mk_req_resp(10,   1,  3, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t1_mk_req_resp(11,   1,  3, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t1_mk_req_resp(12,   1,  3, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t1_mk_req_resp(13,   1,  3, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay0_memdelay0_sinkdelay0_maxreq1
  //----------------------------------------------------------------------

  wire t2_done;
  reg  t2_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (0),
    .p_mem_max_delay  (0),
    .p_sink_max_delay (0),
    .p_num_nodes      (c_num_nodes),
    .p_max_requests   (1)
  )
  t2
  (
    .clk   (clk),
    .reset (t2_reset),
    .done  (t2_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0] t2_memreq;
  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]     t2_netreq;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0]    t2_netresp;
  reg [`VC_MEM_RESP_MSG_SZ(c_memresp_sz)-1:0]            t2_memresp;

  task t2_mk_req_resp
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
    t2_memreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t2_memreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t2_memreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t2_memreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t2_netreq[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t2_netreq[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t2_netreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t2_netreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t2_netreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t2_netreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t2_netresp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t2_netresp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
    t2_netresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t2_netresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t2_netresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t2_memresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t2_memresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t2_memresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t2.msrc.src.m[index]   = t2_memreq;
    t2.nsink.sink.m[index] = t2_netreq;
    t2.nsrc.src.m[index]   = t2_netresp;
    t2.msink.sink.m[index] = t2_memresp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 3, "TestBasic_srcdelay0_memdelay0_sinkdelay0_maxreq1" )
  begin

    //                            ----------- memory request -----------  ------ memory response -------
    //              idx src dst  type      addr      len   data          type       len   data

    t2_mk_req_resp( 0,    1,  0, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t2_mk_req_resp( 1,    1,  1, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t2_mk_req_resp( 2,    1,  0, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t2_mk_req_resp( 3,    1,  1, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t2_mk_req_resp( 4,    1,  2, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t2_mk_req_resp( 5,    1,  2, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t2_mk_req_resp( 6,    1,  2, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t2_mk_req_resp( 7,    1,  2, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t2_mk_req_resp( 8,    1,  2, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t2_mk_req_resp( 9,    1,  2, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t2_mk_req_resp(10,    1,  3, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t2_mk_req_resp(11,    1,  3, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t2_mk_req_resp(12,    1,  3, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t2_mk_req_resp(13,    1,  3, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    #1;   t2_reset = 1'b1;
    #20;  t2_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t2_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay3_memdelay2_sinkdelay10
  //----------------------------------------------------------------------

  wire t3_done;
  reg  t3_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (3),
    .p_mem_max_delay  (2),
    .p_sink_max_delay (10),
    .p_num_nodes      (c_num_nodes),
    .p_max_requests   (1)
  )
  t3
  (
    .clk   (clk),
    .reset (t3_reset),
    .done  (t3_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0] t3_memreq;
  reg [`VC_NET_MSG_SZ(c_memreq_sz,c_srcdest_sz)-1:0]     t3_netreq;
  reg [`VC_NET_MSG_SZ(c_memresp_sz,c_srcdest_sz)-1:0]    t3_netresp;
  reg [`VC_MEM_RESP_MSG_SZ(c_memresp_sz)-1:0]            t3_memresp;

  task t3_mk_req_resp
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
    t3_memreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t3_memreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t3_memreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t3_memreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t3_netreq[`VC_NET_MSG_DEST_FIELD(c_memreq_sz,c_srcdest_sz)] = req_dest;
    t3_netreq[`VC_NET_MSG_SRC_FIELD(c_memreq_sz,c_srcdest_sz)]  = req_src;
    t3_netreq[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t3_netreq[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t3_netreq[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t3_netreq[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t3_netresp[`VC_NET_MSG_DEST_FIELD(c_memresp_sz,c_srcdest_sz)] = req_src;
    t3_netresp[`VC_NET_MSG_SRC_FIELD(c_memresp_sz,c_srcdest_sz)]  = req_dest;
    t3_netresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t3_netresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t3_netresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t3_memresp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t3_memresp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t3_memresp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    t3.msrc.src.m[index]   = t3_memreq;
    t3.nsink.sink.m[index] = t3_netreq;
    t3.nsrc.src.m[index]   = t3_netresp;
    t3.msink.sink.m[index] = t3_memresp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 4, "TestBasic_srcdelay3_memdelay2_sinkdelay10_maxreq1" )
  begin

    //                          ----------- memory request -----------  ------ memory response -------
    //              idx src dst type      addr      len   data          type       len   data

    t3_mk_req_resp( 0,   1,  0, c_req_wr, 16'h0000, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0000
    t3_mk_req_resp( 1,   1,  1, c_req_wr, 16'h0004, 2'd0, 32'h0e0f0102, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0004

    t3_mk_req_resp( 2,   1,  0, c_req_rd, 16'h0000, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0a0b0c0d ); // read  word  0x0000
    t3_mk_req_resp( 3,   1,  1, c_req_rd, 16'h0004, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'h0e0f0102 ); // read  word  0x0004

    t3_mk_req_resp( 4,   1,  2, c_req_wr, 16'h0008, 2'd0, 32'h0a0b0c0d, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x0008
    t3_mk_req_resp( 5,   1,  2, c_req_wr, 16'h0008, 2'd1, 32'hdeadbeef, c_resp_wr, 2'd1, 32'h???????? ); // write byte  0x0008
    t3_mk_req_resp( 6,   1,  2, c_req_rd, 16'h0008, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????ef ); // read  byte  0x0008
    t3_mk_req_resp( 7,   1,  2, c_req_rd, 16'h0009, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0c ); // read  byte  0x0009
    t3_mk_req_resp( 8,   1,  2, c_req_rd, 16'h000a, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0b ); // read  byte  0x000a
    t3_mk_req_resp( 9,   1,  2, c_req_rd, 16'h000b, 2'd1, 32'hxxxxxxxx, c_resp_rd, 2'd1, 32'h??????0a ); // read  byte  0x000b

    t3_mk_req_resp(10,   1,  3, c_req_wr, 16'h000c, 2'd0, 32'h01020304, c_resp_wr, 2'd0, 32'h???????? ); // write word  0x000c
    t3_mk_req_resp(11,   1,  3, c_req_wr, 16'h000c, 2'd2, 32'hdeadbeef, c_resp_wr, 2'd2, 32'h???????? ); // write hword 0x000c
    t3_mk_req_resp(12,   1,  3, c_req_rd, 16'h000c, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????beef ); // read  hword 0x000c
    t3_mk_req_resp(13,   1,  3, c_req_rd, 16'h000e, 2'd2, 32'hxxxxxxxx, c_resp_rd, 2'd2, 32'h????0102 ); // read  hword 0x000e

    #1;   t3_reset = 1'b1;
    #20;  t3_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t3_done )

  end
  `VC_TEST_CASE_END


  `VC_TEST_SUITE_END( 4 )
endmodule
