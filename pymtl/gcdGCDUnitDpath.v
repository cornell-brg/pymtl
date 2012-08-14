//=========================================================================
// RTL Model of GCD Unit Datpath
//-------------------------------------------------------------------------
//

module gcdGCDUnitDpath#( parameter W = 16 )
( 
  input clk,

  input [W-1:0] in_A,
  input [W-1:0] in_B,
  output [W-1:0] out,

  input [1:0] sel_A,
  input sel_B,
  input en_A,
  input en_B,
  output is_A_lt_B,
  output is_B_neq_0
);

  reg [W-1:0] A_reg;
  reg [W-1:0] B_reg;
  wire [W-1:0] A_next;
  wire [W-1:0] B_next;

  assign A_next
    = sel_A == 2'd0 ? in_A
    : sel_A == 2'd1 ? B_reg
    : sel_A == 2'd2 ? A_reg - B_reg
    : {W{1'bx}};

  assign B_next
    = sel_B == 1'd0 ? in_B
    : sel_B == 1'd1 ? A_reg
    : {W{1'bx}};

  always @(posedge clk)
  begin
    if (en_A) A_reg <= A_next;
    if (en_B) B_reg <= B_next;
  end

  assign out = A_reg;
  
  assign is_A_lt_B = A_reg < B_reg;
  assign is_B_neq_0 = (|B_reg);
  
endmodule
