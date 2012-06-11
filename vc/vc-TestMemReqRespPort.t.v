//========================================================================
// Unit Tests: Test Source/Sink
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelaySink.v"
//`include "vc-TestDualPortMem.v"
`include "vc-TestMemReqRespPort.v"
`include "vc-Test.v"
`include "vc-Arbiters.v"


module vc_TestComposition
#(
  parameter p_mem_sz  = 1024,    // size of physical memory in bytes
  parameter p_addr_sz = 16,      // size of mem message address in bits
  parameter p_data_sz = 32,      // size of mem message data in bits

  parameter c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter c_data_byte_sz = (p_data_sz/8),
  parameter c_num_blocks = p_mem_sz/c_data_byte_sz,
  parameter c_physical_block_addr_sz = $clog2(c_num_blocks),
  parameter c_block_offset_sz = $clog2(c_data_byte_sz),
  parameter c_req_msg_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_data_sz),
  parameter c_req_msg_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_data_sz)
)(

  input clk,
  input reset,

  // Memory request port interface

  input                      memreq0_val,
  output                     memreq0_rdy,
  input  [c_req_msg_sz-1:0]  memreq0_msg,
  input                      memreq1_val,
  output                     memreq1_rdy,
  input  [c_req_msg_sz-1:0]  memreq1_msg,

  // Memory response port interface

  output                     memresp0_val,
  input                      memresp0_rdy,
  output [c_resp_msg_sz-1:0] memresp0_msg,
  output                     memresp1_val,
  input                      memresp1_rdy,
  output [c_resp_msg_sz-1:0] memresp1_msg

);

  wire [c_physical_block_addr_sz-1:0] physical_block_addr0_M;
  wire [p_data_sz-1:0]                read_block0_M;

  wire                                write_en0_M;
  // Intentionally not [c_req_msg_len_sz-1:0]
  wire [c_req_msg_len_sz:0]         memreq0_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset0_M;
  wire [c_req_msg_data_sz-1:0]        memreq0_msg_data_modified_M;

  wire [c_physical_block_addr_sz-1:0] physical_block_addr1_M;
  wire [p_data_sz-1:0]                read_block1_M;

  wire                                write_en1_M;
  // Intentionally not [c_req_msg_len_sz-1:0]
  wire [c_req_msg_len_sz:0]         memreq1_msg_len_modified_M;
  wire [c_block_offset_sz-1:0]        block_offset1_M;
  wire [c_req_msg_data_sz-1:0]        memreq1_msg_data_modified_M;

  wire arb_amo_en0;
  wire arb_amo_en1;
  wire [1:0] amo_grants;

  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port0
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq0_val),
    .memreq_rdy                 (memreq0_rdy),
    .memreq_msg                 (memreq0_msg),

    .memresp_val                (memresp0_val),
    .memresp_rdy                (memresp0_rdy),
    .memresp_msg                (memresp0_msg),

    .physical_block_addr_M      (physical_block_addr0_M),
    .read_block_M               (read_block0_M),

    .write_en_M                 (write_en0_M),
    .memreq_msg_len_modified_M  (memreq0_msg_len_modified_M),
    .block_offset_M             (block_offset0_M),
    .memreq_msg_data_modified_M (memreq0_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en0),
    .amo_grant                  (amo_grants[0])
  );

  vc_TestReqRespMemPort#(p_mem_sz, p_addr_sz, p_data_sz) port1
  (
    .clk                        (clk),
    .reset                      (reset),

    .memreq_val                 (memreq1_val),
    .memreq_rdy                 (memreq1_rdy),
    .memreq_msg                 (memreq1_msg),

    .memresp_val                (memresp1_val),
    .memresp_rdy                (memresp1_rdy),
    .memresp_msg                (memresp1_msg),

    .physical_block_addr_M      (physical_block_addr1_M),
    .read_block_M               (read_block1_M),

    .write_en_M                 (write_en1_M),
    .memreq_msg_len_modified_M  (memreq1_msg_len_modified_M),
    .block_offset_M             (block_offset1_M),
    .memreq_msg_data_modified_M (memreq1_msg_data_modified_M),

    .arb_amo_en                 (arb_amo_en1),
    .amo_grant                  (amo_grants[1])
  );

  reg [p_data_sz-1:0] m[c_num_blocks-1:0];

  assign read_block0_M = m[physical_block_addr0_M];

  assign read_block1_M = m[physical_block_addr1_M];

  integer wr0_i;
  integer wr1_i;

  always @( posedge clk ) begin

    if ( write_en0_M ) begin
      for ( wr0_i = 0; wr0_i < memreq0_msg_len_modified_M; wr0_i = wr0_i + 1 ) begin
        m[physical_block_addr0_M][ (block_offset0_M*8) + (wr0_i*8) +: 8 ]
          <= memreq0_msg_data_modified_M[ (wr0_i*8) +: 8 ];
      end
    end

    if ( write_en1_M ) begin
      for ( wr1_i = 0; wr1_i < memreq1_msg_len_modified_M; wr1_i = wr1_i + 1 ) begin
        m[physical_block_addr1_M][ (block_offset1_M*8) + (wr1_i*8) +: 8 ]
          <= memreq1_msg_data_modified_M[ (wr1_i*8) +: 8 ];
      end
    end

  end

  // Atomic op grants arbiter

  wire [1:0] amo_reqs = { arb_amo_en1, arb_amo_en0 };

  vc_RoundRobinArb
  #(
    .NUM_REQS (2)
  )
  arb
  (
    .clk    (clk),
    .reset  (reset),
    .reqs   (amo_reqs),
    .grants (amo_grants)
  );


endmodule


//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

module TestHarness
#(
  parameter p_mem_sz  = 1024,    // size of physical memory in bytes
  parameter p_addr_sz = 16,       // size of mem message address in bits
  parameter p_data_sz = 32,      // size of mem message data in bits
  parameter p_src_max_delay = 0, // max random delay for source
  parameter p_sink_max_delay = 0 // max random delay for sink
)(
  input  clk,
  input  reset,
  output done
);

  // Local parameters

  localparam c_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz);
  localparam c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz);

  // Test source for port 0

  wire                    memreq0_val;
  wire                    memreq0_rdy;
  wire [c_req_msg_sz-1:0] memreq0_msg;

  wire                    src0_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src0
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq0_val),
    .rdy         (memreq0_rdy),
    .msg         (memreq0_msg),

    .done        (src0_done)
  );

  // Test source for port 1

  wire                    memreq1_val;
  wire                    memreq1_rdy;
  wire [c_req_msg_sz-1:0] memreq1_msg;

  wire                    src1_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src1
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq1_val),
    .rdy         (memreq1_rdy),
    .msg         (memreq1_msg),

    .done        (src1_done)
  );

  // Test memory

  wire                     memresp0_val;
  wire                     memresp0_rdy;
  wire [c_resp_msg_sz-1:0] memresp0_msg;

  wire                     memresp1_val;
  wire                     memresp1_rdy;
  wire [c_resp_msg_sz-1:0] memresp1_msg;

  vc_TestComposition#(p_mem_sz,p_addr_sz,p_data_sz) mem
  //vc_TestDualPortMem#(p_mem_sz,p_addr_sz,p_data_sz) mem
  (
    .clk         (clk),
    .reset       (reset),

    .memreq0_val  (memreq0_val),
    .memreq0_rdy  (memreq0_rdy),
    .memreq0_msg  (memreq0_msg),

    .memresp0_val (memresp0_val),
    .memresp0_rdy (memresp0_rdy),
    .memresp0_msg (memresp0_msg),

    .memreq1_val  (memreq1_val),
    .memreq1_rdy  (memreq1_rdy),
    .memreq1_msg  (memreq1_msg),

    .memresp1_val (memresp1_val),
    .memresp1_rdy (memresp1_rdy),
    .memresp1_msg (memresp1_msg)
  );

  // Test sink for port 0

  wire sink0_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink0
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp0_val),
    .rdy   (memresp0_rdy),
    .msg   (memresp0_msg),

    .done  (sink0_done)
  );

  // Test sink for port 1

  wire sink1_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink1
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp1_val),
    .rdy   (memresp1_rdy),
    .msg   (memresp1_msg),

    .done  (sink1_done)
  );

  // Done when both source and sink are done for both ports

  assign done = src0_done & sink0_done & src1_done & sink1_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestMemReqRespPort" )

  //----------------------------------------------------------------------
  // localparams
  //----------------------------------------------------------------------

  localparam c_req_rd  = `VC_MEM_REQ_MSG_TYPE_READ;
  localparam c_req_wr  = `VC_MEM_REQ_MSG_TYPE_WRITE;
  localparam c_req_ad  = `VC_MEM_REQ_MSG_TYPE_AMOADD;
  localparam c_req_an  = `VC_MEM_REQ_MSG_TYPE_AMOAND;
  localparam c_req_or  = `VC_MEM_REQ_MSG_TYPE_AMOOR;
  localparam c_req_ax  = `VC_MEM_REQ_MSG_TYPE_AMOXCH;

  localparam c_resp_rd = `VC_MEM_RESP_MSG_TYPE_READ;
  localparam c_resp_wr = `VC_MEM_RESP_MSG_TYPE_WRITE;
  localparam c_resp_ad = `VC_MEM_RESP_MSG_TYPE_AMOADD;
  localparam c_resp_an = `VC_MEM_RESP_MSG_TYPE_AMOAND;
  localparam c_resp_or = `VC_MEM_RESP_MSG_TYPE_AMOOR;
  localparam c_resp_ax = `VC_MEM_RESP_MSG_TYPE_AMOXCH;

  //----------------------------------------------------------------------
  // TestBasic_srcdelay0_sinkdelay0
  //----------------------------------------------------------------------

  wire t0_done;
  reg  t0_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (0),
    .p_sink_max_delay (0)
  )
  t0
  (
    .clk   (clk),
    .reset (t0_reset),
    .done  (t0_done)
  );

  // Port 0 Source-Sink helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req0;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req1;
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
    t0_req0[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req0[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t0_req0[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req0[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req1[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req1[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 500;
    t0_req1[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req1[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t0_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t0_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    // Port 0 Source-Sink

    t0.src0.src.m[index]   = t0_req0;
    t0.sink0.sink.m[index] = t0_resp;

    // Port 1 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between port 0 and port 1 requests.

    t0.src1.src.m[index]   = t0_req1;
    t0.sink1.sink.m[index] = t0_resp;
  end
  endtask

  // Actual test case
  initial begin
    $dumpfile("pcache-TestMemReqRespPort.vcd");
    $dumpvars;
  end

  `VC_TEST_CASE_BEGIN( 1, "TestBasic_srcdelay0_sinkdelay0" )
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
    t0_mk_req_resp(18,  c_req_ax, 16'h0010, 2'd0, 32'hdeadbeef, c_resp_ax, 2'd0, 32'h99be99ef ); // a.xch word  0x0010
    t0_mk_req_resp(19,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'hdeadbeef ); // read  word  0x0010

    #1;   t0_reset = 1'b1;
    #20;  t0_reset = 1'b0;
    #500; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay3_sinkdelay10
  //----------------------------------------------------------------------

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    .p_mem_sz         (1024),
    .p_addr_sz        (16),
    .p_data_sz        (32),
    .p_src_max_delay  (3),
    .p_sink_max_delay (10)
  )
  t1
  (
    .clk   (clk),
    .reset (t1_reset),
    .done  (t1_done)
  );

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req0;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req1;
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
    t1_req0[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req0[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr;
    t1_req0[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req0[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req1[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req1[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 500;
    t1_req1[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req1[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_resp[`VC_MEM_RESP_MSG_TYPE_FIELD(32)]  = resp_type;
    t1_resp[`VC_MEM_RESP_MSG_LEN_FIELD(32)]   = resp_len;
    t1_resp[`VC_MEM_RESP_MSG_DATA_FIELD(32)]  = resp_data;

    // Port 0 Source-Sink

    t1.src0.src.m[index]   = t1_req0;
    t1.sink0.sink.m[index] = t1_resp;

    // Port 1 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between port 0 and port 1 requests.

    t1.src1.src.m[index]   = t1_req1;
    t1.sink1.sink.m[index] = t1_resp;
  end
  endtask

  // Actual test case

  `VC_TEST_CASE_BEGIN( 2, "TestBasic_srcdelay3_sinkdelay10" )
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
    t1_mk_req_resp(18,  c_req_ax, 16'h0010, 2'd0, 32'hdeadbeef, c_resp_ax, 2'd0, 32'h99be99ef ); // a.xch word  0x0010
    t1_mk_req_resp(19,  c_req_rd, 16'h0010, 2'd0, 32'hxxxxxxxx, c_resp_rd, 2'd0, 32'hdeadbeef ); // read  word  0x0010

    #1;   t1_reset = 1'b1;
    #20;  t1_reset = 1'b0;
    #5000; `VC_TEST_CHECK( "Is sink finished?", t1_done )

  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 2 )
endmodule

