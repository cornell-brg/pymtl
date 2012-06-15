`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"
`include "vc-Assert.v"
`include "vc-Queues.v"
`include "vgen-TestMemReqRespPort.v"

module vgen_Magic4PortMem
#(
  parameter p_mem_sz = 1024,
  parameter p_addr_sz = 16,
  parameter p_data_sz = 16,
  parameter c_req_msg_sz = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter c_data_byte_sz = p_data_sz/8,
  parameter c_num_blocks = p_mem_sz/c_data_byte_sz,
  parameter c_physical_block_addr_sz = $clog2(c_num_blocks),
  parameter c_block_offset_sz = $clog2(c_data_byte_sz),
  parameter c_req_msg_len_sz = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_data_sz),
  parameter c_req_msg_data_sz = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_data_sz)
)
(
  input clk,
  input reset,
  input  [1-1:0] memreq0_val,
  output [1-1:0] memreq0_rdy,
  input  [c_req_msg_sz-1:0] memreq0_msg,
  output [1-1:0] memresp0_val,
  input  [1-1:0] memresp0_rdy,
  output [c_resp_msg_sz-1:0] memresp0_msg,
  input  [1-1:0] memreq1_val,
  output [1-1:0] memreq1_rdy,
  input  [c_req_msg_sz-1:0] memreq1_msg,
  output [1-1:0] memresp1_val,
  input  [1-1:0] memresp1_rdy,
  output [c_resp_msg_sz-1:0] memresp1_msg,
  input  [1-1:0] memreq2_val,
  output [1-1:0] memreq2_rdy,
  input  [c_req_msg_sz-1:0] memreq2_msg,
  output [1-1:0] memresp2_val,
  input  [1-1:0] memresp2_rdy,
  output [c_resp_msg_sz-1:0] memresp2_msg,
  input  [1-1:0] memreq3_val,
  output [1-1:0] memreq3_rdy,
  input  [c_req_msg_sz-1:0] memreq3_msg,
  output [1-1:0] memresp3_val,
  input  [1-1:0] memresp3_rdy,
  output [c_resp_msg_sz-1:0] memresp3_msg
);
  wire [c_physical_block_addr_sz-1:0]   physical_block_addr_M0;
  wire [p_data_sz-1:0]                  read_block_M0;
  wire                                  write_en_M0;
  wire [c_req_msg_len_sz:0]          memreq_msg_len_modified_M0;
  wire [c_block_offset_sz-1:0]          block_offset_M0;
  wire [c_req_msg_data_sz-1:0]          memreq_msg_data_modified_M0;
  wire                                  arb_amo_en0;

  wire [c_physical_block_addr_sz-1:0]   physical_block_addr_M1;
  wire [p_data_sz-1:0]                  read_block_M1;
  wire                                  write_en_M1;
  wire [c_req_msg_len_sz:0]          memreq_msg_len_modified_M1;
  wire [c_block_offset_sz-1:0]          block_offset_M1;
  wire [c_req_msg_data_sz-1:0]          memreq_msg_data_modified_M1;
  wire                                  arb_amo_en1;

  wire [c_physical_block_addr_sz-1:0]   physical_block_addr_M2;
  wire [p_data_sz-1:0]                  read_block_M2;
  wire                                  write_en_M2;
  wire [c_req_msg_len_sz:0]          memreq_msg_len_modified_M2;
  wire [c_block_offset_sz-1:0]          block_offset_M2;
  wire [c_req_msg_data_sz-1:0]          memreq_msg_data_modified_M2;
  wire                                  arb_amo_en2;

  wire [c_physical_block_addr_sz-1:0]   physical_block_addr_M3;
  wire [p_data_sz-1:0]                  read_block_M3;
  wire                                  write_en_M3;
  wire [c_req_msg_len_sz:0]          memreq_msg_len_modified_M3;
  wire [c_block_offset_sz-1:0]          block_offset_M3;
  wire [c_req_msg_data_sz-1:0]          memreq_msg_data_modified_M3;
  wire                                  arb_amo_en3;

  wire [4-1:0]                         amo_grants;

  vc_TestReqRespMemPort#(
    .p_mem_sz (p_mem_sz),
    .p_addr_sz (p_addr_sz),
    .p_data_sz (p_data_sz)
  )
  port0
  (
    .clk (clk),
    .reset (reset),
    .memreq_val (memreq0_val),
    .memreq_rdy (memreq0_rdy),
    .memreq_msg (memreq0_msg),
    .memresp_val (memresp0_val),
    .memresp_rdy (memresp0_rdy),
    .memresp_msg (memresp0_msg),
    .physical_block_addr_M (physical_block_addr_M0),
    .read_block_M (read_block_M0),
    .write_en_M (write_en_M0),
    .memreq_msg_len_modified_M (memreq_msg_len_modified_M0),
    .block_offset_M (block_offset_M0),
    .memreq_msg_data_modified_M (memreq_msg_data_modified_M0),
    .arb_amo_en (arb_amo_en0),
    .amo_grant (amo_grants[0])
  );
  vc_TestReqRespMemPort#(
    .p_mem_sz (p_mem_sz),
    .p_addr_sz (p_addr_sz),
    .p_data_sz (p_data_sz)
  )
  port1
  (
    .clk (clk),
    .reset (reset),
    .memreq_val (memreq1_val),
    .memreq_rdy (memreq1_rdy),
    .memreq_msg (memreq1_msg),
    .memresp_val (memresp1_val),
    .memresp_rdy (memresp1_rdy),
    .memresp_msg (memresp1_msg),
    .physical_block_addr_M (physical_block_addr_M1),
    .read_block_M (read_block_M1),
    .write_en_M (write_en_M1),
    .memreq_msg_len_modified_M (memreq_msg_len_modified_M1),
    .block_offset_M (block_offset_M1),
    .memreq_msg_data_modified_M (memreq_msg_data_modified_M1),
    .arb_amo_en (arb_amo_en1),
    .amo_grant (amo_grants[1])
  );
  vc_TestReqRespMemPort#(
    .p_mem_sz (p_mem_sz),
    .p_addr_sz (p_addr_sz),
    .p_data_sz (p_data_sz)
  )
  port2
  (
    .clk (clk),
    .reset (reset),
    .memreq_val (memreq2_val),
    .memreq_rdy (memreq2_rdy),
    .memreq_msg (memreq2_msg),
    .memresp_val (memresp2_val),
    .memresp_rdy (memresp2_rdy),
    .memresp_msg (memresp2_msg),
    .physical_block_addr_M (physical_block_addr_M2),
    .read_block_M (read_block_M2),
    .write_en_M (write_en_M2),
    .memreq_msg_len_modified_M (memreq_msg_len_modified_M2),
    .block_offset_M (block_offset_M2),
    .memreq_msg_data_modified_M (memreq_msg_data_modified_M2),
    .arb_amo_en (arb_amo_en2),
    .amo_grant (amo_grants[2])
  );
  vc_TestReqRespMemPort#(
    .p_mem_sz (p_mem_sz),
    .p_addr_sz (p_addr_sz),
    .p_data_sz (p_data_sz)
  )
  port3
  (
    .clk (clk),
    .reset (reset),
    .memreq_val (memreq3_val),
    .memreq_rdy (memreq3_rdy),
    .memreq_msg (memreq3_msg),
    .memresp_val (memresp3_val),
    .memresp_rdy (memresp3_rdy),
    .memresp_msg (memresp3_msg),
    .physical_block_addr_M (physical_block_addr_M3),
    .read_block_M (read_block_M3),
    .write_en_M (write_en_M3),
    .memreq_msg_len_modified_M (memreq_msg_len_modified_M3),
    .block_offset_M (block_offset_M3),
    .memreq_msg_data_modified_M (memreq_msg_data_modified_M3),
    .arb_amo_en (arb_amo_en3),
    .amo_grant (amo_grants[3])
  );

  reg [p_data_sz-1:0] m[c_num_blocks-1:0];
  wire [4-1:0] amo_reqs;

  assign amo_reqs[0] = arb_amo_en0;
  assign read_block_M0 = m[physical_block_addr_M0];
  integer wr0_i;
  always @( posedge clk ) begin
    if ( write_en_M0 ) begin
      for ( wr0_i = 0; wr0_i < memreq_msg_len_modified_M0; wr0_i = wr0_i + 1 ) begin
       m[physical_block_addr_M0][ (block_offset_M0*8) + (wr0_i*8) +: 8 ]
         <= memreq_msg_data_modified_M0[ (wr0_i*8) +: 8 ];
      end
    end
  end
  assign amo_reqs[1] = arb_amo_en1;
  assign read_block_M1 = m[physical_block_addr_M1];
  integer wr1_i;
  always @( posedge clk ) begin
    if ( write_en_M1 ) begin
      for ( wr1_i = 0; wr1_i < memreq_msg_len_modified_M1; wr1_i = wr1_i + 1 ) begin
       m[physical_block_addr_M1][ (block_offset_M1*8) + (wr1_i*8) +: 8 ]
         <= memreq_msg_data_modified_M1[ (wr1_i*8) +: 8 ];
      end
    end
  end
  assign amo_reqs[2] = arb_amo_en2;
  assign read_block_M2 = m[physical_block_addr_M2];
  integer wr2_i;
  always @( posedge clk ) begin
    if ( write_en_M2 ) begin
      for ( wr2_i = 0; wr2_i < memreq_msg_len_modified_M2; wr2_i = wr2_i + 1 ) begin
       m[physical_block_addr_M2][ (block_offset_M2*8) + (wr2_i*8) +: 8 ]
         <= memreq_msg_data_modified_M2[ (wr2_i*8) +: 8 ];
      end
    end
  end
  assign amo_reqs[3] = arb_amo_en3;
  assign read_block_M3 = m[physical_block_addr_M3];
  integer wr3_i;
  always @( posedge clk ) begin
    if ( write_en_M3 ) begin
      for ( wr3_i = 0; wr3_i < memreq_msg_len_modified_M3; wr3_i = wr3_i + 1 ) begin
       m[physical_block_addr_M3][ (block_offset_M3*8) + (wr3_i*8) +: 8 ]
         <= memreq_msg_data_modified_M3[ (wr3_i*8) +: 8 ];
      end
    end
  end

  vc_RoundRobinArb#(
    .NUM_REQS (4)
  )
  arb
  (
    .clk (clk),
    .reset (reset),
    .reqs (amo_reqs),
    .grants (amo_grants)
  );
endmodule
