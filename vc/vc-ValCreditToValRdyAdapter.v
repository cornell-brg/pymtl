//=======================================================================
// Val-Credit To Val-Rdy Adapter
//=======================================================================

`ifndef VC_VAL_CREDIT_TO_VAL_RDY_ADAPTER
`define VC_VAL_CREDIT_TO_VAL_RDY_ADAPTER

`include "vc-Queues.v"

module vc_ValCreditToValRdyAdapter
#(
  parameter MSG_SZ = 32,
  parameter BUFFER_ENTRIES = 4,
  parameter BUFFER_ADDR_SZ = 2
)(
  input               clk,
  input               reset,

  input  [MSG_SZ-1:0] i_msg,
  input               i_val,
  output              o_credit,

  output [MSG_SZ-1:0] o_msg,
  output              o_val,
  input               i_rdy
);

  vc_Queue_pf
  #(
    `VC_QUEUE_BYPASS,
    MSG_SZ,
    BUFFER_ENTRIES,
    BUFFER_ADDR_SZ
  ) inputQ(
    .clk      (clk),
    .reset    (reset),
    .enq_bits (i_msg),
    .enq_val  (i_val),
    .deq_bits (o_msg),
    .deq_val  (o_val),
    .deq_rdy  (i_rdy)
  );

  assign o_credit = o_val & i_rdy;

endmodule

`endif
