//========================================================================
// Unit Tests: Test Source/Sink
//========================================================================

`include "vc-TestRandDelaySource.v"
`include "vc-TestRandDelaySink.v"
`include "vc-TestDecaPortMem.v"
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

  // Test source for port 2

  wire                    memreq2_val;
  wire                    memreq2_rdy;
  wire [c_req_msg_sz-1:0] memreq2_msg;

  wire                    src2_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src2
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq2_val),
    .rdy         (memreq2_rdy),
    .msg         (memreq2_msg),

    .done        (src2_done)
  );

  // Test source for port 3

  wire                    memreq3_val;
  wire                    memreq3_rdy;
  wire [c_req_msg_sz-1:0] memreq3_msg;

  wire                    src3_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src3
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq3_val),
    .rdy         (memreq3_rdy),
    .msg         (memreq3_msg),

    .done        (src3_done)
  );

  // Test source for port 4

  wire                    memreq4_val;
  wire                    memreq4_rdy;
  wire [c_req_msg_sz-1:0] memreq4_msg;

  wire                    src4_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src4
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq4_val),
    .rdy         (memreq4_rdy),
    .msg         (memreq4_msg),

    .done        (src4_done)
  );

  // Test source for port 5

  wire                    memreq5_val;
  wire                    memreq5_rdy;
  wire [c_req_msg_sz-1:0] memreq5_msg;

  wire                    src5_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src5
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq5_val),
    .rdy         (memreq5_rdy),
    .msg         (memreq5_msg),

    .done        (src5_done)
  );

  // Test source for port 6

  wire                    memreq6_val;
  wire                    memreq6_rdy;
  wire [c_req_msg_sz-1:0] memreq6_msg;

  wire                    src6_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src6
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq6_val),
    .rdy         (memreq6_rdy),
    .msg         (memreq6_msg),

    .done        (src6_done)
  );

  // Test source for port 7

  wire                    memreq7_val;
  wire                    memreq7_rdy;
  wire [c_req_msg_sz-1:0] memreq7_msg;

  wire                    src7_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src7
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq7_val),
    .rdy         (memreq7_rdy),
    .msg         (memreq7_msg),

    .done        (src7_done)
  );

  // Test source for port 8

  wire                    memreq8_val;
  wire                    memreq8_rdy;
  wire [c_req_msg_sz-1:0] memreq8_msg;

  wire                    src8_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src8
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq8_val),
    .rdy         (memreq8_rdy),
    .msg         (memreq8_msg),

    .done        (src8_done)
  );

  // Test source for port 9

  wire                    memreq9_val;
  wire                    memreq9_rdy;
  wire [c_req_msg_sz-1:0] memreq9_msg;

  wire                    src9_done;

  vc_TestRandDelaySource#(c_req_msg_sz,1024,p_src_max_delay) src9
  (
    .clk         (clk),
    .reset       (reset),

    .val         (memreq9_val),
    .rdy         (memreq9_rdy),
    .msg         (memreq9_msg),

    .done        (src9_done)
  );

  // Test memory

  wire                     memresp0_val;
  wire                     memresp0_rdy;
  wire [c_resp_msg_sz-1:0] memresp0_msg;

  wire                     memresp1_val;
  wire                     memresp1_rdy;
  wire [c_resp_msg_sz-1:0] memresp1_msg;

  wire                     memresp2_val;
  wire                     memresp2_rdy;
  wire [c_resp_msg_sz-1:0] memresp2_msg;

  wire                     memresp3_val;
  wire                     memresp3_rdy;
  wire [c_resp_msg_sz-1:0] memresp3_msg;

  wire                     memresp4_val;
  wire                     memresp4_rdy;
  wire [c_resp_msg_sz-1:0] memresp4_msg;

  wire                     memresp5_val;
  wire                     memresp5_rdy;
  wire [c_resp_msg_sz-1:0] memresp5_msg;

  wire                     memresp6_val;
  wire                     memresp6_rdy;
  wire [c_resp_msg_sz-1:0] memresp6_msg;

  wire                     memresp7_val;
  wire                     memresp7_rdy;
  wire [c_resp_msg_sz-1:0] memresp7_msg;

  wire                     memresp8_val;
  wire                     memresp8_rdy;
  wire [c_resp_msg_sz-1:0] memresp8_msg;

  wire                     memresp9_val;
  wire                     memresp9_rdy;
  wire [c_resp_msg_sz-1:0] memresp9_msg;

  vc_TestDecaPortMem#(p_mem_sz,p_addr_sz,p_data_sz) mem
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
    .memresp1_msg (memresp1_msg),

    .memreq2_val  (memreq2_val),
    .memreq2_rdy  (memreq2_rdy),
    .memreq2_msg  (memreq2_msg),

    .memresp2_val (memresp2_val),
    .memresp2_rdy (memresp2_rdy),
    .memresp2_msg (memresp2_msg),

    .memreq3_val  (memreq3_val),
    .memreq3_rdy  (memreq3_rdy),
    .memreq3_msg  (memreq3_msg),

    .memresp3_val (memresp3_val),
    .memresp3_rdy (memresp3_rdy),
    .memresp3_msg (memresp3_msg),

    .memreq4_val  (memreq4_val),
    .memreq4_rdy  (memreq4_rdy),
    .memreq4_msg  (memreq4_msg),

    .memresp4_val (memresp4_val),
    .memresp4_rdy (memresp4_rdy),
    .memresp4_msg (memresp4_msg),

    .memreq5_val  (memreq5_val),
    .memreq5_rdy  (memreq5_rdy),
    .memreq5_msg  (memreq5_msg),

    .memresp5_val (memresp5_val),
    .memresp5_rdy (memresp5_rdy),
    .memresp5_msg (memresp5_msg),

    .memreq6_val  (memreq6_val),
    .memreq6_rdy  (memreq6_rdy),
    .memreq6_msg  (memreq6_msg),

    .memresp6_val (memresp6_val),
    .memresp6_rdy (memresp6_rdy),
    .memresp6_msg (memresp6_msg),

    .memreq7_val  (memreq7_val),
    .memreq7_rdy  (memreq7_rdy),
    .memreq7_msg  (memreq7_msg),

    .memresp7_val (memresp7_val),
    .memresp7_rdy (memresp7_rdy),
    .memresp7_msg (memresp7_msg),
    
    .memreq8_val  (memreq8_val),
    .memreq8_rdy  (memreq8_rdy),
    .memreq8_msg  (memreq8_msg),

    .memresp8_val (memresp8_val),
    .memresp8_rdy (memresp8_rdy),
    .memresp8_msg (memresp8_msg),

    .memreq9_val  (memreq9_val),
    .memreq9_rdy  (memreq9_rdy),
    .memreq9_msg  (memreq9_msg),

    .memresp9_val (memresp9_val),
    .memresp9_rdy (memresp9_rdy),
    .memresp9_msg (memresp9_msg)

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

  // Test sink for port 2

  wire sink2_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink2
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp2_val),
    .rdy   (memresp2_rdy),
    .msg   (memresp2_msg),

    .done  (sink2_done)
  );

  // Test sink for port 3

  wire sink3_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink3
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp3_val),
    .rdy   (memresp3_rdy),
    .msg   (memresp3_msg),

    .done  (sink3_done)
  );

  // Test sink for port 4

  wire sink4_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink4
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp4_val),
    .rdy   (memresp4_rdy),
    .msg   (memresp4_msg),

    .done  (sink4_done)
  );

  // Test sink for port 5

  wire sink5_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink5
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp5_val),
    .rdy   (memresp5_rdy),
    .msg   (memresp5_msg),

    .done  (sink5_done)
  );

  // Test sink for port 6

  wire sink6_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink6
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp6_val),
    .rdy   (memresp6_rdy),
    .msg   (memresp6_msg),

    .done  (sink6_done)
  );

  // Test sink for port 7

  wire sink7_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink7
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp7_val),
    .rdy   (memresp7_rdy),
    .msg   (memresp7_msg),

    .done  (sink7_done)
  );

  // Test sink for port 8

  wire sink8_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink8
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp8_val),
    .rdy   (memresp8_rdy),
    .msg   (memresp8_msg),

    .done  (sink8_done)
  );

  // Test sink for port 9

  wire sink9_done;

  vc_TestRandDelaySink#(c_resp_msg_sz,1024,p_sink_max_delay) sink9
  (
    .clk   (clk),
    .reset (reset),

    .val   (memresp9_val),
    .rdy   (memresp9_rdy),
    .msg   (memresp9_msg),

    .done  (sink9_done)
  );

  // Done when both source and sink are done for both ports

  assign done = src0_done & sink0_done & src1_done & sink1_done
              & src2_done & sink2_done & src3_done & sink3_done
              & src4_done & sink4_done & src5_done & sink5_done
              & src6_done & sink6_done & src7_done & sink7_done
              & src8_done & sink8_done & src9_done & sink9_done;

endmodule

//------------------------------------------------------------------------
// Main Tester Module
//------------------------------------------------------------------------

module tester;

  `VC_TEST_SUITE_BEGIN( "vc-TestDecaPortMem" )

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
    //.p_mem_sz         (1024),
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

  // Helper tasks

  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req0;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req1;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req2;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req3;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req4;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req5;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req6;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req7;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req8;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t0_req9;
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
    t0_req1[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 400;
    t0_req1[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req1[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req2[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req2[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 800;
    t0_req2[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req2[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req3[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req3[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +1200;
    t0_req3[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req3[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req4[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req4[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +1600;
    t0_req4[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req4[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req5[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req5[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2000;
    t0_req5[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req5[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req6[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req6[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2400;
    t0_req6[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req6[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req7[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req7[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2800;
    t0_req7[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req7[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req8[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req8[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +3200;
    t0_req8[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req8[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t0_req9[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t0_req9[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +3600;
    t0_req9[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t0_req9[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

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

    // Port 2 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src2.src.m[index]   = t0_req2;
    t0.sink2.sink.m[index] = t0_resp;

    // Port 3 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src3.src.m[index]   = t0_req3;
    t0.sink3.sink.m[index] = t0_resp;

    // Port 4 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src4.src.m[index]   = t0_req4;
    t0.sink4.sink.m[index] = t0_resp;

    // Port 5 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src5.src.m[index]   = t0_req5;
    t0.sink5.sink.m[index] = t0_resp;

    // Port 6 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src6.src.m[index]   = t0_req6;
    t0.sink6.sink.m[index] = t0_resp;

    // Port 7 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src7.src.m[index]   = t0_req7;
    t0.sink7.sink.m[index] = t0_resp;

    // Port 8 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src8.src.m[index]   = t0_req8;
    t0.sink8.sink.m[index] = t0_resp;

    // Port 9 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t0.src9.src.m[index]   = t0_req9;
    t0.sink9.sink.m[index] = t0_resp;
  end
  endtask

  // Actual test case

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
    #1000; `VC_TEST_CHECK( "Is sink finished?", t0_done )

  end
  `VC_TEST_CASE_END

  //----------------------------------------------------------------------
  // TestBasic_srcdelay3_sinkdelay10
  //----------------------------------------------------------------------

  wire t1_done;
  reg  t1_reset = 1;

  TestHarness
  #(
    //.p_mem_sz         (1024),
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
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req2;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req3;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req4;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req5;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req6;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req7;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req8;
  reg [`VC_MEM_REQ_MSG_SZ(16,32)-1:0] t1_req9;
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
    t1_req1[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 400;
    t1_req1[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req1[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req2[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req2[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr + 800;
    t1_req2[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req2[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req3[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req3[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +1200;
    t1_req3[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req3[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req4[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req4[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +1600;
    t1_req4[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req4[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req5[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req5[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2000;
    t1_req5[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req5[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req6[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req6[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2400;
    t1_req6[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req6[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req7[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req7[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +2800;
    t1_req7[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req7[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req8[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req8[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +3200;
    t1_req8[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req8[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

    t1_req9[`VC_MEM_REQ_MSG_TYPE_FIELD(16,32)] = req_type;
    t1_req9[`VC_MEM_REQ_MSG_ADDR_FIELD(16,32)] = req_addr +3600;
    t1_req9[`VC_MEM_REQ_MSG_LEN_FIELD(16,32)]  = req_len;
    t1_req9[`VC_MEM_REQ_MSG_DATA_FIELD(16,32)] = req_data;

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

    // Port 2 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src2.src.m[index]   = t1_req2;
    t1.sink2.sink.m[index] = t1_resp;

    // Port 3 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src3.src.m[index]   = t1_req3;
    t1.sink3.sink.m[index] = t1_resp;

    // Port 4 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src4.src.m[index]   = t1_req4;
    t1.sink4.sink.m[index] = t1_resp;

    // Port 5 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src5.src.m[index]   = t1_req5;
    t1.sink5.sink.m[index] = t1_resp;

    // Port 6 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src6.src.m[index]   = t1_req6;
    t1.sink6.sink.m[index] = t1_resp;

    // Port 7 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src7.src.m[index]   = t1_req7;
    t1.sink7.sink.m[index] = t1_resp;
    
    // Port 8 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src8.src.m[index]   = t1_req8;
    t1.sink8.sink.m[index] = t1_resp;

    // Port 9 Source-Sink
    //--------------------------------------------------------------------
    // Set the address to a large enough offset that there will not be
    // overlap between all ports.

    t1.src9.src.m[index]   = t1_req9;
    t1.sink9.sink.m[index] = t1_resp;

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

