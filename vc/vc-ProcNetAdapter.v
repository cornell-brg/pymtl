//=========================================================================
// vc-ProcNetAdapter: Processor-Network Interface Adapter
//=========================================================================

`ifndef PROC_NET_ADAPTER_V
`define PROC_NET_ADAPTER_V

`include "vc-NetMsg.v"
`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"

module vc_ProcNetAdapter
#(
  parameter p_router_id     =  0,  // id of the router we're attached to
  parameter p_num_nodes     =  4,  // number of nodes in the network
  parameter p_addr_sz       =  8,  // size of mem message address in bits
  parameter p_data_sz       = 32,  // size of mem message data in bits
  parameter p_dest_offset   =  4,  // offset to dest field in bits
  parameter p_max_requests  = 16,  // number of in flight requests,
                                   // 0 = infinite
  parameter p_banked_cache  =  1,  // if we are using a banked cache
                                   // calculate the dest using the addr,
                                   // otherwise always set dest=0

  // Local constants not meant to be set from outside the module

  parameter c_srcdest_sz        = $clog2(p_num_nodes),
  parameter c_memreq_msg_sz     = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_memresp_msg_sz    = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter c_reqnet_msg_sz     = `VC_NET_MSG_SZ(c_memreq_msg_sz,c_srcdest_sz),
  parameter c_respnet_msg_sz    = `VC_NET_MSG_SZ(c_memresp_msg_sz,c_srcdest_sz),
  parameter c_req_count_sz      = $clog2(32)  // Max inflight req is 31!
)(
  input clk,
  input reset,

  // Processor Memory Request Port

  input [c_memreq_msg_sz-1:0]     memreq_msg,
  input                           memreq_val,
  output                          memreq_rdy,

  // Request Network Port

  output [c_reqnet_msg_sz-1:0]     netin_msg,
  output                           netin_val,
  input                            netin_rdy,

  // Response Network Port

  input [c_respnet_msg_sz-1:0]    netout_msg,
  input                           netout_val,
  output                          netout_rdy,

  // Processor Memory Response Port

  output [c_memresp_msg_sz-1:0]  memresp_msg,
  output                         memresp_val,
  input                          memresp_rdy
);

  //----------------------------------------------------------------------
  // Request Path
  //----------------------------------------------------------------------
  localparam c_memreq_addr_sz = `VC_MEM_REQ_MSG_ADDR_SZ(p_addr_sz,p_data_sz);
  localparam c_line_nbytes    = p_data_sz/8;    // data size (bytes)
  localparam c_off_sz  = $clog2(c_line_nbytes); // offset size (bits)

  // source is always just our router id
  wire [c_srcdest_sz-1:0] src_router = p_router_id;
  wire [c_srcdest_sz-1:0] dest_router;
  wire [c_memreq_addr_sz-1:0] addr;

  // calculate destination by pulling off bank index bits
  assign addr = memreq_msg[`VC_MEM_REQ_MSG_ADDR_FIELD(p_addr_sz,p_data_sz)];
  assign dest_router = (p_banked_cache == 0) ? 0 :
                       addr[(p_dest_offset + c_srcdest_sz - 1):p_dest_offset];

  vc_NetMsgToBits
  #(
    c_memreq_msg_sz,  // payload size in bits
    c_srcdest_sz      // number of src/dest bits
  )
  insert_payload
  (
    // inputs
    .dest( dest_router ),
    .src( src_router ),
    .payload( memreq_msg ),
    // output
    .bits( netin_msg )
  );

  //----------------------------------------------------------------------
  // Control Logic
  //----------------------------------------------------------------------
  // This control logic keeps track of the number of in flight requests,
  // and won't allow any more requests to go out if the req_count variable
  // exceeds the provided p_max_requests parameter.  The increment/
  // decrement logic is a bit more complicated than it could be because
  // when testing with TestSource/TestSinks, it was possible for the
  // req_count to become negative (responses arriving before reqeusts
  // go out.  To prevent this, the memresp_val/netout_rdy signals were set
  // to zero to prevent handling of responses when req_count == 0. This
  // caused **another** side-effect where you couldn't send a request
  // the same cycle a response arrived ifp_max_requests == 1.  To fix
  // this the ``not_busy`` logic was added (acts like a PipeQueue).

  reg [c_req_count_sz-1:0] req_count;

  wire req  = netin_val  && netin_rdy;
  wire resp = netout_val && netout_rdy;

  // Swap the dest and src for the response message
  always @ (posedge clk) begin
    if (reset)
      req_count = 0;
    else if ( req && !resp )
      req_count = req_count + 1;
    else if ( resp && !req )
      req_count = req_count - 1;
  end

  wire not_busy = (p_max_requests == 0) || (req_count < p_max_requests) ||
              ((req_count >= p_max_requests) && netout_val && netout_rdy);
  assign netin_val  = memreq_val && not_busy;
  assign memreq_rdy = netin_rdy  && not_busy;

  //----------------------------------------------------------------------
  // Response Path
  //----------------------------------------------------------------------
  vc_NetMsgFromBits
  #(
    c_memresp_msg_sz,  // payload size in bits
    c_srcdest_sz       // number of src/dest bits
  )
  extract_payload
  (
    // inputs
    .bits( netout_msg ),
    // output
    .dest(),
    .src(),
    .payload( memresp_msg )
  );

  assign memresp_val = (req_count == 0) ? 1'b0 : netout_val;
  assign netout_rdy  = (req_count == 0) ? 1'b0 : memresp_rdy;

endmodule

`endif
