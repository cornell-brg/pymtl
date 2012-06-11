//========================================================================
// Verilog Components: Register Files
//========================================================================

`ifndef VC_REGFILES_V
`define VC_REGFILES_V

`include "vc-Misc.v"
`include "vc-StateElements.v"

//------------------------------------------------------------------------
// 1w1r register file using flip-flops
//------------------------------------------------------------------------

module vc_Regfile_1w1r_pf
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                    clk,
  input      [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output reg [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                    wen_p,   // Wen (sample on rising clk edge)
  input      [ADDR_SZ-1:0] waddr_p, // Wr addr (sample on rising clk edge)
  input      [DATA_SZ-1:0] wdata_p  // Wr data (sample on rising clk edge)
);

  reg [DATA_SZ-1:0] rfile[ENTRIES-1:0];

  // Combinational read - we use a for loop instead of rfile[raddr] to
  // avoid index out of range warnings during synthesis when the number
  // of entries is not a power of 2.

  // assign rdata = rfile[raddr];

  wire [ENTRIES-1:0] raddr_dec;

  vc_Decoder#(ADDR_SZ,ENTRIES) readIdxDecoder
  (
    .in  (raddr),
    .out (raddr_dec)
  );

  integer readIdx;
  always @(*)
  begin
    rdata = {DATA_SZ{1'b0}};
    for ( readIdx = 0; readIdx < ENTRIES; readIdx = readIdx + 1 )
      rdata = rdata | ({DATA_SZ{raddr_dec[readIdx]}} & rfile[readIdx]);
  end

  // Write on positive clock edge

  wire [ENTRIES-1:0] waddr_dec_p;

  vc_Decoder#(ADDR_SZ,ENTRIES) writeIdxDecoder
  (
    .in  (waddr_p),
    .out (waddr_dec_p)
  );

  integer writeIdx;
  always @( posedge clk )
  begin
    for ( writeIdx = 0; writeIdx < ENTRIES; writeIdx = writeIdx + 1 )
      if ( wen_p && waddr_dec_p[writeIdx] )
        rfile[writeIdx] <= wdata_p;
  end

endmodule

//------------------------------------------------------------------------
// 1w1r register file using flip-flops (with reset)
//------------------------------------------------------------------------

module vc_Regfile_rst_1w1r_pf
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

  reg [DATA_SZ-1:0] rfile[ENTRIES-1:0];

  // Combinational read

  assign rdata = rfile[raddr];

  // Write on positive clock edge

  genvar i;
  generate
    for ( i = 0; i < ENTRIES; i = i+1 )
    begin : wport
      always @( posedge clk )
        if ( reset_p )
          rfile[i] <= RESET_VALUE;
        else if ( wen_p && (i == waddr_p) )
          rfile[i] <= wdata_p;
    end
  endgenerate

endmodule

//------------------------------------------------------------------------
// 1w2r register file using flip-flops
//------------------------------------------------------------------------

module vc_Regfile_1w2r_pf
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

  reg [DATA_SZ-1:0] rfile[ENTRIES-1:0];

  // Combinational read

  assign rdata0 = rfile[raddr0];
  assign rdata1 = rfile[raddr1];

  // Write on positive clock edge

  always @( posedge clk )
    if ( wen_p )
      rfile[waddr_p] <= wdata_p;

endmodule

//------------------------------------------------------------------------
// 1w1r register file using level-high latches
//------------------------------------------------------------------------

module vc_Regfile_1w1r_hl
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

  reg [DATA_SZ-1:0] rfile[ENTRIES-1:0];

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

  assign rdata = rfile[raddr];

  // Write on positive clock edge

  always @(*)
    if ( clk && wen_latched_pn )
      rfile[waddr_latched_pn] <= wdata_p;

endmodule

//------------------------------------------------------------------------
// 1w1r register File using level-low latches
//------------------------------------------------------------------------

module vc_Regfile_1w1r_ll
#(
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input  [ADDR_SZ-1:0] raddr,   // Read address (combinational input)
  output [DATA_SZ-1:0] rdata,   // Read data (combinational on raddr)
  input                wen_n,   // Write en (sample on falling clk edge)
  input  [ADDR_SZ-1:0] waddr_n, // Write addr (sample on falling clk edge)
  input  [DATA_SZ-1:0] wdata_n  // Write data (sample on falling clk edge)
);

  reg [DATA_SZ-1:0] rfile[ENTRIES-1:0];

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
    .clk  (clk),
    .d_n  (waddr_n),
    .q_np (waddr_latched_np)
  );

  // Combinational read

  assign rdata = rfile[raddr];

  // Write on positive clock edge

  always @(*)
    if ( clk && wen_latched_np )
      rfile[waddr_latched_np] <= wdata_n;

endmodule

`endif

