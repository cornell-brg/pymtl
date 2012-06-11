//========================================================================
// Verilog Components: State Elements
//========================================================================

`ifndef VC_STATE_ELEMENTS_V
`define VC_STATE_ELEMENTS_V

`include "vc-Assert.v"

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop
//------------------------------------------------------------------------

module vc_DFF_pf #( parameter W = 1 )
(
  input              clk,      // Clock input
  input      [W-1:0] d_p,      // Data input (sampled on rising clk edge)
  output reg [W-1:0] q_np      // Data output
);

  always @( posedge clk )
    q_np <= d_p;

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with reset
//------------------------------------------------------------------------

module vc_RDFF_pf #( parameter W = 1, parameter RESET_VALUE = 0 )
(
  input              clk,      // Clock input
  input              reset_p,  // Sync reset input (sampled on rising edge)
  input      [W-1:0] d_p,      // Data input (sampled on rising clk edge)
  output reg [W-1:0] q_np      // Data output
);

  always @( posedge clk )
    q_np <= reset_p ? RESET_VALUE : d_p;

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with enable
//------------------------------------------------------------------------

module vc_EDFF_pf #( parameter W = 1 )
(
  input              clk,     // Clock input
  input      [W-1:0] d_p,     // Data input (sampled on rising clk edge)
  input              en_p,    // Enable input (sampled on rising clk edge)
  output reg [W-1:0] q_np     // Data output
);

  always @( posedge clk )
    if ( en_p ) q_np <= d_p;

  //`ifndef SYNTHESIS
  //  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, en_p, "en_p" );
  //`endif

endmodule

//------------------------------------------------------------------------
// Postive-edge triggered flip-flop with enable and reset
//------------------------------------------------------------------------

module vc_ERDFF_pf #( parameter W = 1, parameter RESET_VALUE = 0 )
(
  input              clk,     // Clock input
  input              reset_p, // Sync reset input (sampled on rising edge)
  input      [W-1:0] d_p,     // Data input (sampled on rising clk edge)
  input              en_p,    // Enable input (sampled on rising clk edge)
  output reg [W-1:0] q_np     // Data output
);

  always @( posedge clk )
    if ( reset_p || en_p ) q_np <= reset_p ? RESET_VALUE : d_p;

  //`ifndef SYNTHESIS
  //  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, en_p, "en_p" );
  //`endif

endmodule

//------------------------------------------------------------------------
// Negative-edge triggered flip-flop
//------------------------------------------------------------------------

module vc_DFF_nf #( parameter W = 1 )
(
  input              clk,     // Clock input
  input      [W-1:0] d_p,     // Data input (sampled on rising clk edge)
  output reg [W-1:0] q_np     // Data output (sampled on rising clk edge)
);

  always @( posedge clk )
    q_np <= d_p;

endmodule

//------------------------------------------------------------------------
// Negative-edge triggered flip-flop with enable
//------------------------------------------------------------------------

module vc_EDFF_nf #( parameter W = 1 )
(
  input              clk,    // Clock input
  input      [W-1:0] d_n,    // Data input (sampled on falling clk edge)
  input              en_n,   // Enable input (sampled on falling clk edge)
  output reg [W-1:0] q_pn    // Data output
);

  always @( posedge clk )
    if ( en_n ) q_pn <= d_n;

  `ifndef SYNTHESIS  
    `VC_ASSERT_NOT_X_NEGEDGE_MSG( clk, en_n, "en_n" );
  `endif

endmodule

//------------------------------------------------------------------------
// Level-High Latch
//------------------------------------------------------------------------

module vc_Latch_hl #( parameter W = 1 )
(
  input              clk,    // Clock input
  input      [W-1:0] d_n,    // Data input (sampled on falling clk edge)
  output reg [W-1:0] q_np    // Data output
);

  always @(*)
    if ( clk ) q_np <= d_n;

endmodule

//------------------------------------------------------------------------
// Level-High Latch with Enable
//------------------------------------------------------------------------

module vc_ELatch_hl #( parameter W = 1 )
(
  input              clk,    // Clock input
  input              en_p,   // Enable input (sampled on rising clk edge)
  input      [W-1:0] d_n,    // Data input (sampled on falling clk edge)
  output reg [W-1:0] q_np    // Data output
);

  // We latch the enable signal with a level-low latch to make sure
  // that it is stable for the entire time clock is high.

  reg en_latched_pn;
  always @(*)
    if ( ~clk )
      en_latched_pn <= en_p;

  always @(*)
    if ( clk && en_latched_pn )
      q_np <= d_n;

  `ifndef SYNTHESIS
    `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, en_p, "en_p" );
  `endif

endmodule

//------------------------------------------------------------------------
// Level-Low Latch
//------------------------------------------------------------------------

module vc_Latch_ll #( parameter W = 1 )
(
  input              clk,    // Clock input
  input      [W-1:0] d_p,    // Data input (sampled on rising clk edge)
  output reg [W-1:0] q_pn    // Data output
);

  always @(*)
    if ( ~clk ) q_pn <= d_p;

endmodule

//------------------------------------------------------------------------
// Level-High Latch with Enable
//------------------------------------------------------------------------

module vc_ELatch_ll #( parameter W = 1 )
(
  input              clk,    // Clock input
  input              en_n,   // Enable input (sampled on falling clk edge)
  input      [W-1:0] d_p,    // Data input (sampled on rising clk edge)
  output reg [W-1:0] q_pn    // Data output
);

  // We latch the enable signal with a level-high latch to make sure
  // that it is stable for the entire time clock is low.

  reg en_latched_np;
  always @(*)
    if ( clk )
      en_latched_np <= en_n;

  always @(*)
    if ( ~clk && en_latched_np )
      q_pn <= d_p;

  `ifndef SYNTHESIS
    `VC_ASSERT_NOT_X_NEGEDGE_MSG( clk, en_n, "en_n" );
  `endif

endmodule

`endif

