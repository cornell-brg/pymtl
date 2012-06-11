//========================================================================
// Val-Rdy to Val-Credit Adapter
//========================================================================

`ifndef VC_VAL_RDY_TO_VAL_CREDIT_ADAPTER
`define VC_VAL_RDY_TO_VAL_CREDIT_ADAPTER

`include "vc-StateElements.v"
`include "vc-Counter.v"

module vc_ValRdyToValCreditAdapter
#(
  parameter MSG_SZ = 32,
  parameter MAX_CREDIT_COUNT = 4,
  parameter CREDIT_COUNT_SZ = 3
)(
  input               clk,
  input               reset,

  input  [MSG_SZ-1:0] i_msg,
  input               i_val,
  output              o_rdy,

  output [MSG_SZ-1:0] o_msg,
  output              o_val,
  input               i_credit
);

  wire                       credit_increment = i_credit;
  wire                       credit_decrement = o_val;
  wire [CREDIT_COUNT_SZ-1:0] credit_count;
  wire                       credits_depleted;

  assign o_msg = i_msg;
  assign o_val = i_val & o_rdy;

  vc_Counter
  #(
    .BIT_WIDTH(CREDIT_COUNT_SZ),
    .MAX_COUNT(MAX_CREDIT_COUNT)
  ) credit_counter(
    .clk       (clk),
    .reset     (reset),
    .increment (credit_increment),
    .decrement (credit_decrement),
    .count     (credit_count),
    .zero      (credits_depleted)
  );

  assign o_rdy = ~credits_depleted;

endmodule

`endif
