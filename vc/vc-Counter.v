//=========================================================================
// Counter
//=========================================================================

`ifndef VC_COUNTER_V
`define VC_COUNTER_V

`include "vc-StateElements.v"

module vc_Counter
#(
  parameter BIT_WIDTH = 3,
  parameter MAX_COUNT = 4
)(
  input                  clk,
  input                  reset,
  input                  increment,
  input                  decrement,
  output [BIT_WIDTH-1:0] count,
  output                 zero
);

  localparam [BIT_WIDTH-1:0] CONST_ONE  = 1;
  localparam [BIT_WIDTH-1:0] CONST_ZERO = 0;

  wire [BIT_WIDTH-1:0] count_next = (increment && ~decrement && (count < MAX_COUNT)) ? count + CONST_ONE :
                                    (decrement && ~increment && (count > 0))         ? count - CONST_ONE :
                                                                                       count;

  assign zero = (count == CONST_ZERO);

  vc_RDFF_pf#(.W(BIT_WIDTH), .RESET_VALUE(MAX_COUNT)) count_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .d_p     (count_next),
    .q_np    (count)
  );

endmodule

`endif
