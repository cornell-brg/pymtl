//========================================================================
// Verilog Components: Arithmetic Components
//========================================================================

`ifndef VC_ARITH_V
`define VC_ARITH_V

//------------------------------------------------------------------------
// Adders
//------------------------------------------------------------------------

module vc_Adder #( parameter W = 1 )
(
  input  [W-1:0] in0, in1,
  input          cin,
  output [W-1:0] out,
  output         cout
);

  assign {cout,out} = in0 + in1 + cin;

endmodule

module vc_Adder_simple #( parameter W = 1 )
(
  input  [W-1:0] in0, in1,
  output [W-1:0] out
);

  assign out = in0 + in1;

endmodule

//------------------------------------------------------------------------
// Subtractor
//------------------------------------------------------------------------

module vc_Subtractor #( parameter W = 1 )
(
  input  [W-1:0] in0, in1,
  output [W-1:0] out
);

  assign out = in0 - in1;

endmodule

//------------------------------------------------------------------------
// Incrementer
//------------------------------------------------------------------------

module vc_Inc #( parameter W = 1, parameter INC = 1 )
(
  input  [W-1:0] in,
  output [W-1:0] out
);

  assign out = in + INC;

endmodule

//------------------------------------------------------------------------
// Zero-Extension
//------------------------------------------------------------------------

module vc_ZeroExtend #( parameter W_IN = 1, parameter W_OUT = 8 )
(
  input  [W_IN-1:0]  in,
  output [W_OUT-1:0] out
);

  assign out = { {(W_OUT-W_IN){1'b0}}, in };

endmodule

//------------------------------------------------------------------------
// Sign-Extension
//------------------------------------------------------------------------

module vc_SignExtend #( parameter W_IN = 1, parameter W_OUT = 8 )
(
  input  [W_IN-1:0]  in,
  output [W_OUT-1:0] out
);

  assign out = { {(W_OUT-W_IN){in[W_IN-1]}}, in };

endmodule

//------------------------------------------------------------------------
// Equal comparator
//------------------------------------------------------------------------

module vc_EQComparator #( parameter W = 1 )
(
  input  [W-1:0] in0,
  input  [W-1:0] in1,
  output         out
);

  assign out = ( in0 == in1 );

endmodule

//------------------------------------------------------------------------
// Less-Than Comparator
//------------------------------------------------------------------------

module vc_LTComparator #( parameter W = 1 )
(
  input  [W-1:0] in0,
  input  [W-1:0] in1,
  output         out
);

  assign out = ( in0 < in1 );

endmodule

`endif

