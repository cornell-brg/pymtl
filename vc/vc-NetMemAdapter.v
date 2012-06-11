//=========================================================================
// vc-NetMemAdapter: Network-Memory Interface Adapter
//=========================================================================

`ifndef NET_MEM_ADAPTER_V
`define NET_MEM_ADAPTER_V

`include "vc-NetMsg.v"
`include "vc-MemReqMsg.v"
`include "vc-MemRespMsg.v"

module vc_NetMemAdapter
#(
  parameter p_num_nodes     =  4,  // number of nodes in the network
  parameter p_addr_sz       =  8,  // size of mem message address in bits
  parameter p_data_sz       = 32,  // size of mem message data in bits

  // Local constants not meant to be set from outside the module

  parameter c_srcdest_sz        = $clog2(p_num_nodes),
  parameter c_memreq_msg_sz     = `VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz),
  parameter c_memresp_msg_sz    = `VC_MEM_RESP_MSG_SZ(p_data_sz),
  parameter c_reqnet_msg_sz     = `VC_NET_MSG_SZ(c_memreq_msg_sz,c_srcdest_sz),
  parameter c_respnet_msg_sz    = `VC_NET_MSG_SZ(c_memresp_msg_sz,c_srcdest_sz)
)
(
  input clk,
  input reset,

  // Request Network Port

  input [c_reqnet_msg_sz-1:0]    netout_msg,
  input                          netout_val,
  output                         netout_rdy,

  // Memory Request Port

  output [c_memreq_msg_sz-1:0]   memreq_msg,
  output                         memreq_val,
  input                          memreq_rdy,

  // Memory Response Port

  input [c_memresp_msg_sz-1:0]   memresp_msg,
  input                          memresp_val,
  output                         memresp_rdy,

  // Response Network Port

  output [c_respnet_msg_sz-1:0]    netin_msg,
  output                           netin_val,
  input                            netin_rdy
);

  //----------------------------------------------------------------------
  // Request Path
  //----------------------------------------------------------------------
  wire [c_srcdest_sz-1:0] req_src;
  wire [c_srcdest_sz-1:0] req_dest;

  vc_NetMsgFromBits
  #(
    c_memreq_msg_sz,  // payload size in bits
    c_srcdest_sz      // number of src/dest bits
  )
  extract_payload
  (
    // inputs
    .bits( netout_msg ),
    // output
    .dest( req_dest ),
    .src( req_src ),
    .payload( memreq_msg )
  );

  //----------------------------------------------------------------------
  // Control Logic
  //----------------------------------------------------------------------
  // The adapter needs to keep track of the src and dest of the memory
  // request received from the network so that when the memory responds we
  // know where to send it.  To do this, we create some very simple queue
  // logic here: enqueue when val & rdy are true on the netout (input)
  // port, dequeue when both val & rdy are true on the netin (exit) port.
  // On the response path we can wire the memresp val & rdy directly to
  // the netout val & rdy.  The request path is trickier: we can't allow
  // any more requests until the response has been sent successfully, so
  // we add some extra logic to to disable the memreq_val and the
  // netout_rdy when a request is being processed.  We add a
  // PipeQueue-like optimization that allows a request (enqueue) to
  // occur the same cycle as a response.

  reg [c_srcdest_sz-1:0] resp_src;
  reg [c_srcdest_sz-1:0] resp_dest;
  reg full;

  wire enq = netout_val && netout_rdy;
  wire deq = netin_val  && netin_rdy;

  // Swap the dest and src for the response message
  always @ (posedge clk) begin
    if ( enq ) resp_src  <= req_dest;
    if ( enq ) resp_dest <= req_src;
    if ( enq || deq || reset ) full <= reset ? 1'b0 : enq;
  end

  wire not_busy = !full || (full && netin_val && netin_rdy);
  assign memreq_val = netout_val && not_busy;
  assign netout_rdy = memreq_rdy && not_busy;
  // memreq_msg output wired up directly to vc_NetMsgFromBits module

  //----------------------------------------------------------------------
  // Response Path
  //----------------------------------------------------------------------
  vc_NetMsgToBits
  #(
    c_memresp_msg_sz,  // payload size in bits
    c_srcdest_sz       // number of src/dest bits
  )
  insert_payload
  (
    // inputs
    .dest( resp_dest ),
    .src( resp_src ),
    .payload( memresp_msg ),
    // output
    .bits( netin_msg )
  );

  assign netin_val   = memresp_val;
  assign memresp_rdy =   netin_rdy;
  // netin_msg output wired up directly to vc_NetMsgToBits module

endmodule

`endif
