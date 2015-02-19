//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with enable and reset
//------------------------------------------------------------------------

`include "vc-assert.v"

module EnResetReg
#(
  parameter p_nbits       = 1,
  parameter p_reset_value = 0
)(
  input                clk,   // Clock input
  input                reset, // Sync reset input (sampled on rising edge)
  output [p_nbits-1:0] q,     // Data output
  input  [p_nbits-1:0] d,     // Data input (sampled on rising clk edge)
  input                en     // Enable input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    if ( reset || en )
      q <= reset ? p_reset_value : d;

  // Assertions

  always @( posedge clk )
    if ( !reset )
      `VC_ASSERT_NOT_X( en );

endmodule
