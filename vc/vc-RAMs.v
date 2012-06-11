//========================================================================
// Verilog Components: RAMs
//========================================================================

`ifndef VC_RAMS_V
`define VC_RAMS_V

`include "vc-StateElements.v"

//------------------------------------------------------------------------
// 1w1r RAM using flip-flops
//-----------------------------------------------------------------------

module vc_RAM_1w1r_pf
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)
(
  input                clk,
  input  [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                wen_p,   // Write enable (sample on rising clk edge)
  input  [ADDR_SZ-1:0] waddr_p, // Write addr (sample on rising clk edge)
  input  [DATA_SZ-1:0] wdata_p  // Write data (sample on rising clk edge)
);

  reg [DATA_SZ-1:0] mem[ENTRIES-1:0];

  // Combinational read

  assign rdata = mem[raddr];

  // Write on positive clock edge

  always @( posedge clk )
    if ( wen_p )
      mem[waddr_p] <= wdata_p;

endmodule

//------------------------------------------------------------------------
// 1w1r RAM using flip-flops (with reset)
//------------------------------------------------------------------------

module vc_RAM_rst_1w1r_pf
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1,
  parameter RESET_VALUE = 0
)(
  input                clk,
  input                reset_p,
  input  [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                wen_p,   // Write enable (sample on rising clk edge)
  input  [ADDR_SZ-1:0] waddr_p, // Write addr (sample on rising clk edge)
  input  [DATA_SZ-1:0] wdata_p  // Write data (sample on rising clk edge)
);

  reg [DATA_SZ-1:0] mem[ENTRIES-1:0];

  // Combinational read

  assign rdata = mem[raddr];

  // Write on positive clock edge

  genvar i;
  generate
    for ( i = 0; i < ENTRIES; i = i+1 )
    begin : wport
      always @( posedge clk )
        if ( reset_p )
          mem[i] <= RESET_VALUE;
        else if ( wen_p && (i == waddr_p) )
          mem[i] <= wdata_p;
    end
  endgenerate

endmodule

//------------------------------------------------------------------------
// 1w2r RAM using flip-flops
//------------------------------------------------------------------------

module vc_RAM_1w2r_pf
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input  [ADDR_SZ-1:0] raddr0,  // Read 0 address (combinational input)
  output [DATA_SZ-1:0] rdata0,  // Read 0 data (combinational on raddr)
  input  [ADDR_SZ-1:0] raddr1,  // Read 1 address (combinational input)
  output [DATA_SZ-1:0] rdata1,  // Read 1 data (combinational on raddr)
  input                wen_p,   // Write enable (sample on rising clk edge)
  input  [ADDR_SZ-1:0] waddr_p, // Write addr (sample on rising clk edge)
  input  [DATA_SZ-1:0] wdata_p  // Write data (sample on rising clk edge)
);

  reg [DATA_SZ-1:0] mem[ENTRIES-1:0];

  // Combinational read

  assign rdata0 = mem[raddr0];
  assign rdata1 = mem[raddr1];

  // Write on positive clock edge

  always @( posedge clk )
    if ( wen_p )
      mem[waddr_p] <= wdata_p;

endmodule

//------------------------------------------------------------------------
// 1w1r RAM using level-high latches
//------------------------------------------------------------------------

module vc_RAM_1w1r_hl
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input  [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                wen_p,   // Write enable (sample on rising clk edge)
  input  [ADDR_SZ-1:0] waddr_p, // Write addr (sample on rising clk edge)
  input  [DATA_SZ-1:0] wdata_p  // Write data (sample on rising clk edge)
);

  reg [DATA_SZ-1:0] mem[ENTRIES-1:0];

  // Latch the write enable and write address with level-low latches

  wire wen_latched_pn;
  wire waddr_latched_pn;

  vc_Latch_ll#(1) wen_ll
  (
    .clk  (clk),
    .d_p  (wen_p),
    .q_pn (wen_latched_pn)
  );

  vc_Latch_ll#(1) waddr_ll
  (
    .clk  (clk),
    .d_p  (waddr_p),
    .q_pn (waddr_latched_pn)
  );

  // Combinational read

  assign rdata = mem[raddr];

  // Write on positive clock edge

  always @(*)
    if ( clk && wen_latched_pn )
      mem[waddr_latched_pn] <= wdata_p;

endmodule

//------------------------------------------------------------------------
// 1w1r RAM using level-low latches
//------------------------------------------------------------------------

module vc_RAM_1w1r_ll
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)
(
  input                clk,
  input  [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                wen_n,   // Write en (sample on falling clk edge)
  input  [ADDR_SZ-1:0] waddr_n, // Write addr (sample on falling clk edge)
  input  [DATA_SZ-1:0] wdata_n  // Write data (sample on falling clk edge)
);

  reg [DATA_SZ-1:0] mem[ENTRIES-1:0];

  // Latch the write enable and write address with level-low latches

  wire wen_latched_np;
  wire waddr_latched_np;

  vc_Latch_hl#(1) wen_hl
  (
    .clk  (clk),
    .d_n  (wen_n),
    .q_np (wen_latched_np)
  );

  vc_Latch_hl#(1) waddr_hl
  (
    .clk(clk),
    .d_n(waddr_n),
    .q_np(waddr_latched_np)
  );

  // Combinational read

  assign rdata = mem[raddr];

  // Write on positive clock edge

  always @(*)
    if ( clk && wen_latched_np )
      mem[waddr_latched_np] <= wdata_n;

endmodule

`endif

