//========================================================================
// Verilog Components: Registers
//========================================================================

// Note that we place the register output earlier in the port list since
// this is one place we might actually want to use positional port
// binding like this:
//
//  wire [p_nbits-1:0] result_B;
//  vc_Reg#(p_nbits) result_AB( clk, result_B, result_A );

`ifndef VC_REGS_V
`define VC_REGS_V

`include "vc-assert.v"

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop
//------------------------------------------------------------------------

module vc_Reg
#(
  parameter p_nbits = 1
)(
  input                clk, // Clock input
  output [p_nbits-1:0] q,   // Data output
  input  [p_nbits-1:0] d    // Data input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    q <= d;

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop
//------------------------------------------------------------------------
// Just a copy of vc_Reg used for testing explicit module names

module vc_RegExplicitModuleName
#(
  parameter p_nbits = 1
)(
  input                clk, // Clock input
  output [p_nbits-1:0] q,   // Data output
  input  [p_nbits-1:0] d    // Data input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    q <= d;

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with reset
//------------------------------------------------------------------------

module vc_ResetReg
#(
  parameter p_nbits       = 1,
  parameter p_reset_value = 0
)(
  input                clk,   // Clock input
  input                reset, // Sync reset input (sampled on rising edge)
  output [p_nbits-1:0] q,     // Data output
  input  [p_nbits-1:0] d      // Data input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    q <= reset ? p_reset_value : d;

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with enable
//------------------------------------------------------------------------

module vc_EnReg
#(
  parameter p_nbits = 1
)(
  input                clk,   // Clock input
  input                reset, // Sync reset input (sampled on rising edge)
  output [p_nbits-1:0] q,     // Data output
  input  [p_nbits-1:0] d,     // Data input (sampled on rising clk edge)
  input                en     // Enable input (sampled on rising clk edge)
);

  reg q;

  always @( posedge clk )
    if ( en )
      q <= d;

  // Assertions

  always @( posedge clk )
    if ( !reset )
      `VC_ASSERT_NOT_X( en );

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with enable and reset
//------------------------------------------------------------------------

module vc_EnResetReg
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

`endif /* VC_REGS_V */

