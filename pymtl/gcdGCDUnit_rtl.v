//=========================================================================
// RTL Model of GCD Unit
//-------------------------------------------------------------------------
//
`include "gcdGCDUnitCtrl.v"
`include "gcdGCDUnitDpath.v"

module gcdGCDUnit_rtl#( parameter W = 16 ) 
( 
  input          clk,
  input          reset,

  input  [W-1:0] operands_bits_A,
  input  [W-1:0] operands_bits_B,  
  input          operands_val,
  output         operands_rdy,

  output [W-1:0] result_bits_data,
  output         result_val,
  input          result_rdy

);

  wire [1:0] sel_A;
  wire sel_B;
  wire en_A;
  wire en_B;
  wire is_A_lt_B;
  wire is_B_neq_0;

  // Instantiate control unit
  
  gcdGCDUnitCtrl ctrl
  ( 
    .clk(clk),
    .reset(reset),

    .operands_val(operands_val),
    .operands_rdy(operands_rdy),

    .result_val(result_val),
    .result_rdy(result_rdy),

    .sel_A(sel_A),
    .sel_B(sel_B),
    .en_A(en_A),
    .en_B(en_B),
    .is_A_lt_B(is_A_lt_B),
    .is_B_neq_0(is_B_neq_0)
  );

  // Instantiate datapath

  gcdGCDUnitDpath#(W) dpath
  ( 
    .clk(clk),

    .in_A(operands_bits_A),
    .in_B(operands_bits_B),
    .out(result_bits_data),

    .sel_A(sel_A),
    .sel_B(sel_B),
    .en_A(en_A),
    .en_B(en_B),
    .is_A_lt_B(is_A_lt_B),
    .is_B_neq_0(is_B_neq_0)
  );
  
endmodule
