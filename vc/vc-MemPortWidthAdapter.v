//========================================================================
// Verilog Components: Mem Port Width Adapter
//========================================================================


`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"

module vc_MemPortWidthAdapter
#(
  parameter p_addr_sz = 32,      // size of mem message address in bits
  parameter p_proc_data_sz = 32,   // size of mem message address in bits
  parameter p_mem_data_sz = 128, // size of mem message address in bits

  // Local constants not meant to be set from outside the module
  parameter c_proc_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_proc_data_sz),
  parameter c_proc_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_proc_data_sz),
  parameter c_mem_req_msg_sz  = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_mem_data_sz),
  parameter c_mem_resp_msg_sz = `VC_MEM_RESP_MSG_SZ(p_mem_data_sz)
)(
  input                           procreq_val,
  output                          procreq_rdy,
  input  [c_proc_req_msg_sz-1:0]  procreq_msg,

  output                          procresp_val,
  input                           procresp_rdy,
  output [c_proc_resp_msg_sz-1:0] procresp_msg,

  output                          memreq_val,
  input                           memreq_rdy,
  output [c_mem_req_msg_sz-1:0]   memreq_msg,

  input                           memresp_val,
  output                          memresp_rdy,
  input  [c_mem_resp_msg_sz-1:0]  memresp_msg
);

  localparam c_proc_req_msg_type_sz  = `VC_MEM_REQ_MSG_TYPE_SZ(p_addr_sz,p_proc_data_sz);
  localparam c_proc_req_msg_addr_sz  = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_proc_data_sz);
  localparam c_proc_req_msg_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_proc_data_sz);
  localparam c_proc_req_msg_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_proc_data_sz);

  localparam c_mem_req_msg_type_sz  = `VC_MEM_REQ_MSG_TYPE_SZ(p_addr_sz,p_mem_data_sz);
  localparam c_mem_req_msg_addr_sz  = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_mem_data_sz);
  localparam c_mem_req_msg_len_sz   = `VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_mem_data_sz);
  localparam c_mem_req_msg_data_sz  = `VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_mem_data_sz);

  localparam c_proc_resp_msg_type_sz = `VC_MEM_RESP_MSG_TYPE_SZ(p_proc_data_sz);
  localparam c_proc_resp_msg_len_sz  = `VC_MEM_RESP_MSG_LEN_SZ(p_proc_data_sz);
  localparam c_proc_resp_msg_data_sz = `VC_MEM_RESP_MSG_DATA_SZ(p_proc_data_sz);

  localparam c_mem_resp_msg_type_sz = `VC_MEM_RESP_MSG_TYPE_SZ(p_mem_data_sz);
  localparam c_mem_resp_msg_len_sz  = `VC_MEM_RESP_MSG_LEN_SZ(p_mem_data_sz);
  localparam c_mem_resp_msg_data_sz = `VC_MEM_RESP_MSG_DATA_SZ(p_mem_data_sz);

  localparam c_zero_pad = c_mem_req_msg_data_sz - c_proc_req_msg_data_sz;
  localparam c_zero_off = c_mem_req_msg_data_sz - 1;

  //----------------------------------------------------------------------
  // Request Conversion
  //----------------------------------------------------------------------

  // Valrdy signals

  assign memreq_val   = procreq_val;
  assign procreq_rdy  = memreq_rdy;
  assign procresp_val = memresp_val;
  assign memresp_rdy  = procresp_rdy;

  wire [c_proc_req_msg_type_sz-1:0] procreq_msg_type;
  wire [c_proc_req_msg_addr_sz-1:0] procreq_msg_addr;
  wire [c_proc_req_msg_len_sz-1:0]  procreq_msg_len;
  wire [c_proc_req_msg_data_sz-1:0] procreq_msg_data;

  // Unpack the narrow request

  vc_MemReqMsgFromBits#(p_addr_sz,p_proc_data_sz) procreq_msg_from_bits
  (
    .bits (procreq_msg),
    .type (procreq_msg_type),
    .addr (procreq_msg_addr),
    .len  (procreq_msg_len),
    .data (procreq_msg_data)
  );

  wire [c_mem_req_msg_type_sz-1:0] memreq_msg_type = procreq_msg_type;
  wire [c_mem_req_msg_addr_sz-1:0] memreq_msg_addr = procreq_msg_addr;
  // Adjust length
  wire [c_mem_req_msg_len_sz-1:0]  memreq_msg_len
    = ( procreq_msg_len == 0 ) ? (c_proc_req_msg_data_sz / 8)
                               : procreq_msg_len;
  // Add zero padding
  wire [c_mem_req_msg_data_sz-1:0] memreq_msg_data
    = {{c_zero_pad{1'b0}}, procreq_msg_data};

  // Repack as a wide request

  vc_MemReqMsgToBits#(p_addr_sz,p_mem_data_sz) memreq_msg_to_bits
  (
    .type (memreq_msg_type),
    .addr (memreq_msg_addr),
    .len  (memreq_msg_len),
    .data (memreq_msg_data),
    .bits (memreq_msg)
  );

  //----------------------------------------------------------------------
  // Response Conversion
  //----------------------------------------------------------------------

  wire [c_mem_resp_msg_type_sz-1:0]  memresp_msg_type;
  wire [c_mem_resp_msg_len_sz-1:0]   memresp_msg_len;
  wire [c_mem_resp_msg_data_sz-1:0]  memresp_msg_data;

  // Unpack the wide response

  vc_MemRespMsgFromBits#(p_mem_data_sz) memresp_msg_from_bits
  (
    .bits (memresp_msg),
    .type (memresp_msg_type),
    .len  (memresp_msg_len),
    .data (memresp_msg_data)
  );

  wire [c_proc_resp_msg_type_sz-1:0] procresp_msg_type = memresp_msg_type;
  // Adjust length
  wire [c_proc_resp_msg_len_sz-1:0]  procresp_msg_len
    = ( memresp_msg_len == c_proc_resp_msg_data_sz ) ? 0
                                                     : memresp_msg_len;
  // Remove zero padding
  wire [c_proc_resp_msg_data_sz-1:0] procresp_msg_data
    = memresp_msg_data[c_zero_off:0];

  // Repack the narrow response

  vc_MemRespMsgToBits#(p_proc_data_sz) procresp_msg_to_bits
  (
    .type (procresp_msg_type),
    .len  (procresp_msg_len),
    .data (procresp_msg_data),
    .bits (procresp_msg)
  );

endmodule
