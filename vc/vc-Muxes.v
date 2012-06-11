//========================================================================
// Verilog Components: Muxes
//========================================================================

`ifndef VC_MUXES_V
`define VC_MUXES_V

//------------------------------------------------------------------------
// 2 Input Mux
//------------------------------------------------------------------------

module vc_Mux2 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1,
  input              sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      1'd0 : out = in0;
      1'd1 : out = in1;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 3 Input Mux
//------------------------------------------------------------------------

module vc_Mux3 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2,
  input      [1:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      2'd0 : out = in0;
      2'd1 : out = in1;
      2'd2 : out = in2;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 4 Input Mux
//------------------------------------------------------------------------

module vc_Mux4 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3,
  input      [1:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      2'd0 : out = in0;
      2'd1 : out = in1;
      2'd2 : out = in2;
      2'd3 : out = in3;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 4 Input Mux (with one-hot select)
//------------------------------------------------------------------------

module vc_Mux4_1hot #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3,
  input      [3:0]   sel_1hot,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel_1hot )
      4'b0001 : out = in0;
      4'b0010 : out = in1;
      4'b0100 : out = in2;
      4'b1000 : out = in3;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 5 Input Mux
//------------------------------------------------------------------------

module vc_Mux5 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3, in4,
  input      [2:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      3'd0 : out = in0;
      3'd1 : out = in1;
      3'd2 : out = in2;
      3'd3 : out = in3;
      3'd4 : out = in4;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 6 Input Mux
//------------------------------------------------------------------------

module vc_Mux6 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3, in4, in5,
  input      [2:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      3'd0 : out = in0;
      3'd1 : out = in1;
      3'd2 : out = in2;
      3'd3 : out = in3;
      3'd4 : out = in4;
      3'd5 : out = in5;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 7 Input Mux
//------------------------------------------------------------------------

module vc_Mux7 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3, in4, in5, in6,
  input      [2:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      3'd0 : out = in0;
      3'd1 : out = in1;
      3'd2 : out = in2;
      3'd3 : out = in3;
      3'd4 : out = in4;
      3'd5 : out = in5;
      3'd6 : out = in6;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

//------------------------------------------------------------------------
// 8 Input Mux
//------------------------------------------------------------------------

module vc_Mux8 #( parameter W = 1 )
(
  input      [W-1:0] in0, in1, in2, in3, in4, in5, in6, in7,
  input      [2:0]   sel,
  output reg [W-1:0] out
);

  always @(*)
  begin
    case ( sel )
      3'd0 : out = in0;
      3'd1 : out = in1;
      3'd2 : out = in2;
      3'd3 : out = in3;
      3'd4 : out = in4;
      3'd5 : out = in5;
      3'd6 : out = in6;
      3'd7 : out = in7;
      default : out = {W{1'bx}};
    endcase
  end

endmodule

`endif

