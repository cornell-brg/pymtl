//------------------------------------------------------------------------
// Postive-edge triggered flip-flop
//------------------------------------------------------------------------
module RegVRTL
#(
  parameter p_nbits = 1
)(
  input                clk,   // Clock input
  input                reset, // Clock input
  output [p_nbits-1:0] q,     // Data output
  input  [p_nbits-1:0] d      // Data input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    q <= d;

endmodule
