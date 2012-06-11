//=============================================================
// Crossbar
//=============================================================
// 3 input, 3 output crossbar

`ifndef VC_CROSSBAR_V
`define VC_CROSSBAR_V

`include "vc-Muxes.v"

module vc_Crossbar#(parameter BIT_WIDTH = 32)
(
  input  [BIT_WIDTH-1:0] in0,
  input  [BIT_WIDTH-1:0] in1,
  input  [BIT_WIDTH-1:0] in2,
 
  input  [1:0]           sel0,
  input  [1:0]           sel1,
  input  [1:0]           sel2,
 
  output [BIT_WIDTH-1:0] out0,
  output [BIT_WIDTH-1:0] out1,
  output [BIT_WIDTH-1:0] out2
);

  vc_Mux3#(BIT_WIDTH) out0_mux
  (
    .in0 (in0),
    .in1 (in1),
    .in2 (in2),
    .sel (sel0),
    .out (out0)
  );
 
  vc_Mux3#(BIT_WIDTH) out1_mux
  (
    .in0 (in0),
    .in1 (in1),
    .in2 (in2),
    .sel (sel1),
    .out (out1)
  );
 
  vc_Mux3#(BIT_WIDTH) out2_mux
  (
    .in0 (in0),
    .in1 (in1),
    .in2 (in2),
    .sel (sel2),
    .out (out2)
  );

endmodule

`endif
