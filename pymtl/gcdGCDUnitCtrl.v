//=========================================================================
// RTL Model of GCD Unit Control
//-------------------------------------------------------------------------
//

module gcdGCDUnitCtrl
( 
  input clk,
  input reset,

  input operands_val,
  output reg operands_rdy,

  output reg result_val,
  input result_rdy,

  output reg [1:0] sel_A,
  output reg sel_B,
  output reg en_A,
  output reg en_B,
  input is_A_lt_B,
  input is_B_neq_0
);

  localparam IDLE = 2'd0;
  localparam ACTIVE = 2'd1;
  localparam DONE = 2'd2;

  reg [1:0] state_reg;
  reg [1:0] state_next;

  always @(posedge clk)
  begin
    if (reset)
      state_reg <= IDLE;
    else
      state_reg <= state_next;
  end

  always @(*)
  begin
    state_next = state_reg;

    case (state_reg)
    IDLE:
      begin
        if (operands_val)
          state_next = ACTIVE;
      end
    ACTIVE:
      begin
        if (!is_A_lt_B && !is_B_neq_0)
          state_next = DONE;
      end
    DONE:
      begin
        if (result_rdy)
          state_next = IDLE;
      end
    endcase
  end

  always @(*)
  begin
    operands_rdy = 1'b0;
    result_val = 1'b0;
    sel_A = 2'd0;
    sel_B = 1'b0;
    en_A = 1'b0;
    en_B = 1'b0;

    case (state_reg)
    IDLE:
      begin
        operands_rdy = 1'b1;
        en_A = 1'b1;
        en_B = 1'b1;
      end
    ACTIVE:
      begin
        if (is_A_lt_B)
        begin
          sel_A = 2'd1;
          sel_B = 1'd1;
          en_A = 1'b1;
          en_B = 1'b1;
        end
        else if (is_B_neq_0)
        begin
          sel_A = 2'd2;
          en_A = 1'b1;
        end
      end
    DONE:
      begin
        result_val = 1'b1;
      end
    endcase
  end

endmodule
